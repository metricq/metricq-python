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
import threading
import time
import traceback
import uuid
from contextlib import suppress
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

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
from .types import JsonDict
from .version import __version__

logger = get_logger(__name__)
timer = time.monotonic

T = TypeVar("T")

_global_thread_lock = threading.Lock()


class Agent(RPCDispatcher):
    LOG_MAX_WIDTH = 200

    def __init__(
        self,
        token: str,
        management_url: str,
        *,
        connection_timeout: Union[int, float] = 600,
        add_uuid: bool = False,
    ):
        self.token = f"{token}.{uuid.uuid4().hex}" if add_uuid else token

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_in_progress = False
        self._stop_future: Optional[asyncio.Future[None]] = None
        self._cancel_on_exception = False

        self._management_url = management_url
        self._management_broadcast_exchange_name = "metricq.broadcast"
        self._management_exchange_name = "metricq.management"

        self._management_connection: Optional[aio_pika.RobustConnection] = None
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

        self._management_broadcast_exchange: Optional[aio_pika.Exchange] = None
        self._management_exchange: Optional[aio_pika.Exchange] = None

        self._rpc_response_handlers: Dict[
            str, Tuple[Callable[..., None], bool]
        ] = dict()
        logger.info(
            "Initialized Agent `{}` (running version `metricq=={}`)",
            type(self).__qualname__,
            __version__,
        )

    def derive_address(self, address: str) -> str:
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
    def _event_loop(self) -> asyncio.AbstractEventLoop:
        loop = asyncio.get_running_loop()
        if self._loop is None:
            with _global_thread_lock:
                if self._loop is None:
                    self._loop = loop
        if loop is not self._loop:
            raise RuntimeError(f"{self!r} is bound to a different event loop")
        return loop

    async def make_connection(
        self, url: str, connection_name: Optional[str] = None
    ) -> aio_pika.RobustConnection:
        ssl_options = None

        if url.startswith("amqps"):
            ssl_options = {
                "cert_reqs": ssl.CERT_REQUIRED,
                "ssl_version": ssl.PROTOCOL_TLS | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3,
            }

        client_properties = None
        if connection_name:
            # TODO remove outer client_properties with aiormq >= 5.1.1
            client_properties = {
                "client_properties": {"connection_name": connection_name}
            }

        connection: aio_pika.RobustConnection = await aio_pika.connect_robust(
            url,
            reconnect_interval=30,
            ssl_options=cast(Dict[Any, Any], ssl_options),
            client_properties=cast(Dict[Any, Any], client_properties),
        )

        # How stupid that we can't easily add the handlers *before* actually connecting.
        # We could make our own RobustConnection object, but then we loose url parsing convenience
        connection.add_reconnect_callback(self._on_reconnect)  # type: ignore
        connection.add_close_callback(self._on_close)

        return connection

    async def connect(self) -> None:
        """Connect to the MetricQ network"""
        logger.info(
            "establishing management connection to {}",
            URL(self._management_url).with_password("***"),
        )

        self._management_connection = await self.make_connection(
            self._management_url,
            connection_name="management connection {}".format(self.token),
        )
        self._management_connection.add_close_callback(
            self._on_management_connection_close
        )

        self._management_connection.add_reconnect_callback(
            self._on_management_connection_reconnect  # type: ignore
        )

        self._management_channel = await self._management_connection.channel()
        assert self._management_channel is not None
        self.management_rpc_queue = await self._management_channel.declare_queue(
            "{}-rpc".format(self.token), exclusive=True
        )

        self._management_connection_watchdog.start()
        self._management_connection_watchdog.set_established()

    def run(
        self,
        catch_signals: Iterable[str] = ("SIGINT", "SIGTERM"),
        cancel_on_exception: bool = False,
    ) -> None:
        """Run an Agent by calling :meth:`connect` and waiting for it to be stopped via :meth:`stop`.

        If :meth:`connect` raises an exception, :exc:`.ConnectFailed` is
        raised, with the offending exception attached as a cause.  Any
        exception passed to :meth:`stop` is reraised.

        Args:
            catch_signals:
                Call :meth:`on_signal` if any of theses signals were raised.
            cancel_on_exception:
                Stop the running Agent when an unhandled exception occurs.
                The exception is reraised from this method.

        Raises:
            ConnectFailed:
                Failed to :meth:`connect` to the MetricQ network.
                The source exception is attached as a cause.
            Exception: Any exception passed to :meth:`stop`.
        """
        self._cancel_on_exception = cancel_on_exception

        logger.debug("Starting event loop ...")
        asyncio.run(self._wait_for_stop(catch_signals))
        logger.debug("Event loop completed, exiting...")

    async def _wait_for_stop(self, catch_signals: Iterable[str]) -> None:
        self._event_loop.set_exception_handler(self.on_exception)
        for signame in catch_signals:
            try:
                self._event_loop.add_signal_handler(
                    getattr(signal, signame),
                    functools.partial(self.on_signal, signame),
                )
            except RuntimeError as error:
                logger.warning(
                    "failed to setup signal handler for {}: {}", signame, error
                )

        connect_task = self._event_loop.create_task(self.connect())
        stopped_task = self._event_loop.create_task(self.stopped())

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

    async def rpc(
        self,
        exchange: aio_pika.Exchange,
        routing_key: str,
        function: str,
        response_callback: Optional[Callable[..., None]] = None,
        timeout: float = 60,
        cleanup_on_response: bool = True,
        **kwargs: Any,
    ) -> Optional[JsonDict]:
        """Invoke an RPC over the network.

        .. warning::
            This function is *not part of the public API*, but is included for reference.
            Use :meth:`Client.rpc` instead.

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
                Any additional arguments that are forwarded as arguments to the RPC itself.

                Note:
                    Argument names are required to be in :literal:`"javaScriptSnakeCase"`.

        Returns:
            :literal:`None` if :code:`response_callback` is given,
            otherwise a :class:`dict` containing the RPC response.

        Raises:
            PublishFailed: Failed to publish this RPC to the network.
            RPCError: The remote returned an error.
            TypeError: The :code:`function` keyword-only argument is missing.
            TypeError: :code:`response_callback` is None but :code:`cleanup_on_response=True`
            ValueError: The routing key is longer than 255 bytes

        :meta private:
        """
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
        kwargs["function"] = function
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

        request_future = None

        if response_callback is None:
            request_future = self._event_loop.create_future()

            if not cleanup_on_response:
                # We must cleanup when we use the future otherwise we get errors
                # trying to set the future result multiple times ... after the future was
                # already evaluated
                raise TypeError(
                    "Neither a response_callback was given nor cleanup_on_response was set."
                )

            def default_response_callback(**response_kwargs: Any) -> None:
                assert request_future is not None
                assert not request_future.done()
                logger.debug("rpc completed in {} s", timer() - time_begin)
                if "error" in response_kwargs:
                    request_future.set_exception(RPCError(response_kwargs["error"]))
                else:
                    request_future.set_result(response_kwargs)

            response_callback = default_response_callback

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

        def cleanup() -> None:
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
            self._event_loop.call_later(timeout, cleanup)

        return None

    async def rpc_consume(self, extra_queues: List[aio_pika.Queue] = []) -> None:
        """Start consuming RPCs

        :meta private:

        Typically this is called at the end of :meth:`Client.connect` once the Agent is prepared to handle RPCs.

        Args:
            extra_queues: additional queues on which to receive RPCs
        """
        logger.info("starting RPC consume")
        assert self.management_rpc_queue is not None
        queues = [self.management_rpc_queue] + extra_queues
        await asyncio.gather(
            *[queue.consume(self._on_management_message) for queue in queues]
        )

    def on_signal(self, signal: str) -> None:
        """Callback invoked when a signal is received.

        Override this method for custom signal handling.
        By default it schedules the Client to stop by calling :meth:`stop`.

        Args:
            signal: Name of the signal that occurred, e.g. :code:`"SIGTERM"`, :code:`"SIGINT"`, etc.
        """
        logger.info("Received signal {}, stopping...", signal)
        self._schedule_stop(
            exception=None if signal == "SIGINT" else ReceivedSignal(signal)
        )

    def on_exception(
        self, loop: asyncio.AbstractEventLoop, context: Dict[str, Any]
    ) -> None:
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
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        loop = self._event_loop if loop is None else loop
        loop.create_task(self.stop(exception=exception))

    async def stop(self, exception: Optional[Exception] = None) -> None:
        """Stop a running Agent.

        Args:
            exception:
                An optional exception that will be raised by :meth:`run` if given.
                If the Agent was not started from :meth:`run`, see :meth:`stopped`
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

    async def stopped(self) -> None:
        """Wait for this Agent to stop.

        If the agent stopped unexpectedly, this method raises an exception.

        Raises:
            AgentStopped:
                The Agent was stopped via :meth:`stop` and an exception was passed.
            Exception:
                The Agent encountered any other unhandled exception.
        """
        if self._stop_future is None:
            self._stop_future = self._event_loop.create_future()
        await self._stop_future

    async def _close(self) -> None:
        logger.info("Closing management channel and connection...")
        await self._management_connection_watchdog.stop()
        if self._management_channel:
            await self._management_channel.close()  # type: ignore
            self._management_channel = None
        if self._management_connection:
            await self._management_connection.close()  # type: ignore
            self._management_connection = None
        self._management_broadcast_exchange = None
        self._management_exchange = None

    def _make_correlation_id(self) -> str:
        return "metricq-rpc-py-{}-{}".format(self.token, uuid.uuid4().hex)

    async def _on_management_message(self, message: aio_pika.IncomingMessage) -> None:
        """Callback invoked when a message is received.

        Args:
            message: Either an RPC request or an RPC response.

        Raises:
            PublishError: The reply could not be published.
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

    def _on_reconnect(self, sender: Any, connection: aio_pika.RobustConnection) -> None:
        logger.info("Reconnected to {}", connection)

    def _on_close(self, sender: Any, exception: Optional[BaseException]) -> None:
        if isinstance(exception, asyncio.CancelledError):
            logger.debug("Connection closed regularly")
            return
        logger.info(
            "Connection closed: {} ({})", exception, type(exception).__qualname__
        )

    def _on_management_connection_reconnect(
        self, sender: Any, connection: aio_pika.RobustConnection
    ) -> None:
        self._management_connection_watchdog.set_established()

    def _on_management_connection_close(
        self, sender: Any, _exception: Optional[BaseException]
    ) -> None:
        self._management_connection_watchdog.set_closed()
