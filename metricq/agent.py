# Copyright (c) 2018, ZIH,
# Technische Universitaet Dresden,
# Federal Republic of Germany
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of metricq nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import asyncio
import functools
import json
import signal
import ssl
import textwrap
import time
import traceback
import uuid
from contextlib import suppress
from typing import Callable, Dict, Optional, Tuple, Union

import aio_pika
from aio_pika.exceptions import ChannelInvalidStateError
from yarl import URL

from .connection_watchdog import ConnectionWatchdog
from .exceptions import (
    AgentStopped,
    ConnectFailed,
    PublishFailed,
    ReceivedSignal,
    ReconnectTimeout,
    RPCError,
)
from .logging import get_logger
from .rpc import RPCDispatcher
from .version import __version__

logger = get_logger(__name__)
timer = time.monotonic


class Agent(RPCDispatcher):
    LOG_MAX_WIDTH = 200

    def __init__(
        self,
        token,
        management_url,
        *,
        connection_timeout: Union[int, float] = 600,
        event_loop=None,
        add_uuid=False,
    ):
        self.token = f"{token}.{uuid.uuid4().hex}" if add_uuid else token

        self._event_loop = event_loop
        self._stop_in_progress = False
        self._stop_future: Optional[asyncio.Future[None]] = None
        self._cancel_on_exception = False

        self._management_url = management_url
        self._management_broadcast_exchange_name = "metricq.broadcast"
        self._management_exchange_name = "metricq.management"

        self._management_connection = None
        self._management_connection_watchdog = ConnectionWatchdog(
            on_timeout_callback=lambda watchdog: self._schedule_stop(
                ReconnectTimeout(
                    f"Failed to reestablish {watchdog.connection_name} after {watchdog.timeout} seconds"
                )
            ),
            timeout=connection_timeout,
            connection_name="management connection",
        )
        self._management_channel: Optional[aio_pika.RobustChannel] = None

        self.management_rpc_queue: Optional[aio_pika.Queue] = None

        self._management_broadcast_exchange = None
        self._management_exchange = None

        self._rpc_response_handlers: Dict[str, Tuple[Callable, bool]] = dict()
        logger.info(
            "Initialized Agent `{}` (running version `metricq=={}`)",
            type(self).__qualname__,
            __version__,
        )

    def derive_address(self, address: str):
        """Add the credentials from the management connection to the provided address

        :meta private:
        """
        management_obj = URL(self._management_url)
        vhost_prefix = "vhost:"
        if address.startswith(vhost_prefix):
            derived_obj = management_obj.with_path(address[len(vhost_prefix) :])
        else:
            address_obj = URL(address)
            derived_obj = address_obj.with_user(management_obj.user).with_password(
                management_obj.password
            )
        return str(derived_obj)

    @property
    def event_loop(self):
        # TODO maybe we should instead **TRY** to get the loop of the current context
        if self._event_loop is None:
            logger.debug("Getting current or new")
            try:
                self._event_loop = asyncio.get_event_loop()
            except RuntimeError:
                # Until python 3.6, it may raise instead of creating a new one
                self._event_loop = asyncio.new_event_loop()
        return self._event_loop

    @event_loop.setter
    def event_loop(self, loop):
        assert self._event_loop is None
        self._event_loop = loop

    async def make_connection(self, url):
        if url.startswith("amqps"):
            ssl_options = {
                "cert_reqs": ssl.CERT_REQUIRED,
                "ssl_version": ssl.PROTOCOL_TLS | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3,
            }
        else:
            ssl_options = None

        connection = await aio_pika.connect_robust(
            url, loop=self.event_loop, reconnect_interval=30, ssl_options=ssl_options
        )

        # How stupid that we can't easily add the handlers *before* actually connecting.
        # We could make our own RobustConnection object, but then we loose url parsing convenience
        connection.add_reconnect_callback(self._on_reconnect)
        connection.add_close_callback(self._on_close)

        return connection

    async def connect(self):
        """Connect to the MetricQ network"""
        logger.info(
            "establishing management connection to {}",
            URL(self._management_url).with_password("***"),
        )

        self._management_connection = await self.make_connection(self._management_url)
        self._management_connection.add_close_callback(
            self._on_management_connection_close
        )

        self._management_connection.add_reconnect_callback(
            self._on_management_connection_reconnect
        )

        self._management_channel = await self._management_connection.channel()
        self.management_rpc_queue = await self._management_channel.declare_queue(
            "{}-rpc".format(self.token), exclusive=True
        )

        self._management_connection_watchdog.start(loop=self.event_loop)
        self._management_connection_watchdog.set_established()

    def run(
        self, catch_signals=("SIGINT", "SIGTERM"), cancel_on_exception=False
    ) -> None:
        """Run an Agent by calling :py:meth:`connect` and waiting for it to be stopped via :meth:`stop`.

        If :py:meth:`connect` raises an exception, ConnectFailed is
        raised, with the offending exception attached as a cause.  Any
        exception passed to :py:meth:`stop` is reraised.

        :param catch_signals:
            Call :py:meth:`on_signal` if any of theses signals were raised.
        :type catch_signals: list[str]
        :param bool cancel_on_exception:
            Stop the running Agent when an unhandled exception occurs.  The
            exception is reraised from this method.

        :raises Exception:
            Any exception passed to :py:meth:`stop`, or any exception raised by
            :py:meth:`connect`.
        """
        self._cancel_on_exception = cancel_on_exception
        self.event_loop.set_exception_handler(self.on_exception)
        for signame in catch_signals:
            try:
                self.event_loop.add_signal_handler(
                    getattr(signal, signame), functools.partial(self.on_signal, signame)
                )
            except RuntimeError as error:
                logger.warning(
                    "failed to setup signal handler for {}: {}", signame, error
                )

        async def wait_for_stop():
            connect_task = self.event_loop.create_task(self.connect())
            stopped_task = self.event_loop.create_task(self.stopped())

            pending = {stopped_task, connect_task}
            while pending:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_COMPLETED
                )

                # Check for successful connection, if connect() failed with
                # an unhandled exception, raise ConnectFailed and attach
                # the unhandled exception as its cause.
                if connect_task in done:
                    exc = connect_task.exception()
                    if exc is not None:
                        logger.error(
                            "Failed to connect {}: {} ({})",
                            type(self).__qualname__,
                            exc,
                            type(exc).__qualname__,
                        )
                        raise ConnectFailed("Failed to connect Agent") from exc

                # If the Agent was stopped explicitly, return `None`.  If it was
                # stopped because of an exception, reraise it.
                if stopped_task in done:
                    return stopped_task.result()

        try:
            logger.debug("Running event loop {}...", self.event_loop)
            self.event_loop.run_until_complete(wait_for_stop())
        finally:
            self.event_loop.stop()
            self.event_loop.run_until_complete(self.event_loop.shutdown_asyncgens())

            with suppress(AttributeError):  # needs python 3.7
                all_tasks = asyncio.all_tasks(self.event_loop)
                logger.debug("Tasks remaining when stopping Agent: {}", len(all_tasks))

            logger.debug("Event loop completed, exiting...")

    async def rpc(
        self,
        exchange: aio_pika.Exchange,
        routing_key: str,
        response_callback=None,
        timeout=60,
        cleanup_on_response=True,
        **kwargs,
    ):
        """Invoke an RPC over the network.

        Args:
            function:
                Name of the RPC to invoke
            exchange:
                RabbitMQ exchange on which the request is published
            routing_key:
                Routing key must be at most 255 bytes (UTF-8)
            response_callback:
                If given, this callable will be invoked with any response once it arrives.
                In this case, this function immediately returns :literal:`None`.

                If omitted (or :literal:`None`), this function will wait for and return the first response instead.
            timeout:
                After the timeout, a response will not be dispatched to the handler.
            cleanup_on_response:
                If set, only the first response will be dispatched.
                Must be :literal:`True` when no :code:`response_callback` is given.
            kwargs:
                Any additional arguments that are forwarded as arguments to the RPC itsel.

                Note:
                    Argument names are required to be in :literal:`"javaScriptSnakeCase"`.

        Returns:
            :literal:`None` if :code:`response_callback` is given,
            otherwise a :class:`dict` containing the RPC response.

        :meta private:
        :raises PublishError: if the RPC fails to be published
        :raises RPCError: if the remote returns an error
        :raises TypeError: if the :code:`function` keyword-only argument is missing
        :raises TypeError: if :code:`response_callback is None and cleanup_on_response=True`
        :raises ValueError: if the routing key is longer than 255 bytes
        """
        function = kwargs.get("function")
        if function is None:
            raise TypeError(
                "rpc() is missing required keyword-only argument: 'function'"
            )
        if len(routing_key.encode("utf-8")) > 255:
            raise ValueError(
                "Metric names (amqp routing keys) must be at most 255 bytes long"
            )

        assert self.management_rpc_queue is not None

        time_begin = timer()

        correlation_id = self._make_correlation_id()
        body = json.dumps(kwargs)
        logger.debug(
            "sending RPC {}, ex: {}, rk: {}, ci: {}, args: {}",
            function,
            exchange.name,
            routing_key,
            correlation_id,
            textwrap.shorten(body, width=self.LOG_MAX_WIDTH),
        )
        msg = aio_pika.Message(
            body=body.encode(),
            correlation_id=correlation_id,
            app_id=self.token,
            reply_to=self.management_rpc_queue.name,
            content_type="application/json",
        )

        if response_callback is None:
            request_future = self.event_loop.create_future()

            if not cleanup_on_response:
                # We must cleanup when we use the future otherwise we get errors
                # trying to set the future result multiple times ... after the future was
                # already evaluated
                raise TypeError(
                    "Neither a response_callback was given nor cleanup_on_response was set."
                )

            def default_response_callback(**response_kwargs):
                assert not request_future.done()
                logger.debug("rpc completed in {} s", timer() - time_begin)
                if "error" in response_kwargs:
                    request_future.set_exception(RPCError(response_kwargs["error"]))
                else:
                    request_future.set_result(response_kwargs)

            response_callback = default_response_callback
        else:
            request_future = None

        self._rpc_response_handlers[correlation_id] = (
            response_callback,
            cleanup_on_response,
        )

        try:
            await exchange.publish(msg, routing_key=routing_key)
        except ChannelInvalidStateError as e:
            errmsg = (
                f"Failed to issue RPC request '{function!r}' to exchange ''{exchange}'"
            )
            logger.error("{}: {}", errmsg, e)
            raise PublishFailed(errmsg) from e

        def cleanup():
            self._rpc_response_handlers.pop(correlation_id, None)

        if request_future:
            try:
                return await asyncio.wait_for(request_future, timeout=timeout)
            except TimeoutError as te:
                logger.error(
                    "timeout when waiting for RPC response future {}", correlation_id
                )
                cleanup()
                raise te
        elif timeout:
            self.event_loop.call_later(timeout, cleanup)

    async def rpc_consume(self, extra_queues=[]):
        """Start consuming RPCs

        :meta private:

        Typically this is called at the end of :meth:`Client.connect` once the Agent is prepared to handle RPCs.

        Args:
            extra_queues: additional queues on which to receive RPCs
        """
        logger.info("starting RPC consume")
        queues = [self.management_rpc_queue] + extra_queues
        await asyncio.gather(
            *[queue.consume(self._on_management_message) for queue in queues],
            loop=self.event_loop,
        )

    def on_signal(self, signal):
        """Callback invoked when a signal is received.

        Override this method for custom signal handling.
        By default it schedules the Client to stop by calling :meth:`stop`.
        """
        logger.info("Received signal {}, stopping...", signal)
        self._schedule_stop(
            exception=None if signal == "SIGINT" else ReceivedSignal(signal)
        )

    def on_exception(self, loop: asyncio.AbstractEventLoop, context):
        logger.error("Exception in event loop: {}".format(context["message"]))

        with suppress(KeyError):
            logger.error("Future: {}", context["future"])

        with suppress(KeyError):
            logger.error("Handle: {}", context["handle"])

        ex: Optional[Exception] = context.get("exception")
        if ex is not None:
            is_keyboard_interrupt = isinstance(ex, KeyboardInterrupt)
            if self._cancel_on_exception or is_keyboard_interrupt:
                if not is_keyboard_interrupt:
                    logger.error(
                        "Stopping Agent on unhandled exception ({})",
                        type(ex).__qualname__,
                    )
                self._schedule_stop(exception=ex, loop=loop)
            else:
                logger.error(
                    f"Agent {type(self).__qualname__} encountered an unhandled exception",
                    exc_info=(ex.__class__, ex, ex.__traceback__),
                )

    def _schedule_stop(
        self,
        exception: Optional[Exception] = None,
        loop: asyncio.AbstractEventLoop = None,
    ):
        loop = self.event_loop if loop is None else loop
        loop.create_task(self.stop(exception=exception))

    async def stop(self, exception: Optional[Exception] = None):
        """Stop a running Agent.

        :param exception:
            An optional exception that will be raised by :py:meth:`run` if given.
            If the Agent was not started from :py:meth:`run`, see :py:meth:`stopped`
            how to retrieve this exception.
        """
        if self._stop_in_progress:
            logger.debug("Stop in progress! ({})", exception)
            return
        else:
            self._stop_in_progress = True

            logger.info("Stopping Agent {} ({})...", type(self).__qualname__, exception)

            await asyncio.shield(self._close())

            if self._stop_future is None:
                # No task is waiting for the Agent to stop.
                if exception is not None:
                    # Wrap the exception (to preserve traceback information)
                    # and reraise it.
                    raise AgentStopped("Agent stopped unexpectedly") from exception
                else:
                    return
            else:
                assert not self._stop_future.done()
                if exception is None:
                    self._stop_future.set_result(None)
                else:
                    self._stop_future.set_exception(exception)

    async def stopped(self):
        """Wait for this Agent to stop.

        If the agent stopped unexpectedly, this method raises an exception.

        :raises AgentStoppedError:
            if the Agent was stopped via :meth:`stop` and an exception was passed
        :raises Exception:
            if the Agent encountered any other unhandled exception
        """
        if self._stop_future is None:
            self._stop_future = self.event_loop.create_future()
        await self._stop_future

    async def _close(self):
        logger.info("Closing management channel and connection...")
        await self._management_connection_watchdog.stop()
        if self._management_channel:
            await self._management_channel.close()
            self._management_channel = None
        if self._management_connection:
            await self._management_connection.close()
            self._management_connection = None
        self._management_broadcast_exchange = None
        self._management_exchange = None

    def _make_correlation_id(self):
        return "metricq-rpc-py-{}-{}".format(self.token, uuid.uuid4().hex)

    async def _on_management_message(self, message: aio_pika.IncomingMessage):
        """
        :param message: This is either an RPC or an RPC response

        :raises PublishError: if the reply could not be published
        """
        assert self._management_channel is not None
        assert self._management_channel.default_exchange is not None

        async with message.process(requeue=True):
            time_begin = timer()
            body = message.body.decode()
            from_token = message.app_id
            correlation_id = message.correlation_id

            logger.debug(
                "received message from {}, correlation id: {}, reply_to: {}, length: {}\n{}",
                from_token,
                correlation_id,
                message.reply_to,
                len(body),
                textwrap.shorten(body, width=self.LOG_MAX_WIDTH),
            )
            arguments = json.loads(body)
            arguments["from_token"] = from_token

            function = arguments.get("function")
            if function is not None:
                logger.debug("message is an RPC")
                try:
                    response = await self.rpc_dispatch(**arguments)
                except Exception as e:
                    logger.error(
                        "error handling RPC {} ({}): {}",
                        function,
                        type(e),
                        traceback.format_exc(),
                    )
                    response = {"error": str(e)}
                if response is None:
                    response = dict()
                duration = timer() - time_begin
                body = json.dumps(response)
                logger.debug(
                    "RPC response to {}, correlation id: {}, length: {}, time: {} s\n{}",
                    from_token,
                    correlation_id,
                    len(body),
                    duration,
                    textwrap.shorten(body, width=self.LOG_MAX_WIDTH),
                )
                await self._management_connection_watchdog.established()
                try:
                    await self._management_channel.default_exchange.publish(
                        aio_pika.Message(
                            body=body.encode(),
                            correlation_id=correlation_id,
                            content_type="application/json",
                            app_id=self.token,
                        ),
                        routing_key=message.reply_to,
                    )
                except ChannelInvalidStateError as e:
                    errmsg = (
                        "Failed to reply to '{message.reply_to}' for RPC '{function!r}'"
                    )
                    logger.error("{}: {}", errmsg, e)
                    raise PublishFailed(errmsg) from e
            else:
                logger.debug("message is an RPC response")
                try:
                    handler, cleanup = self._rpc_response_handlers[correlation_id]
                except KeyError:
                    logger.error(
                        "received RPC response with unknown correlation id {} from {}",
                        correlation_id,
                        from_token,
                    )
                    # We do not throw here, no requeue for this!
                    return
                if cleanup:
                    del self._rpc_response_handlers[correlation_id]

                if not handler:
                    return

                # Allow simple handlers that are not coroutines
                # But only None to not get any confusion
                r = handler(**arguments)
                if r is not None:
                    await r

    def _on_reconnect(self, sender, connection):
        logger.info("Reconnected to {}", connection)

    def _on_close(self, sender, exception):
        if isinstance(exception, asyncio.CancelledError):
            logger.debug("Connection closed regularly")
            return
        logger.info(
            "Connection closed: {} ({})", exception, type(exception).__qualname__
        )

    def _on_management_connection_reconnect(self, sender, _connection):
        self._management_connection_watchdog.set_established()

    def _on_management_connection_close(self, sender, _exception: Optional[Exception]):
        self._management_connection_watchdog.set_closed()
