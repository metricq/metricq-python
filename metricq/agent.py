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
import textwrap
import threading
import time
import traceback
import uuid
from collections.abc import Callable, Iterable, Mapping
from contextlib import suppress
from itertools import chain
from typing import Any, Optional, TypeVar
from warnings import warn

import aio_pika
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
from .timeseries import JsonDict
from .version import __version__

logger = get_logger(__name__)
timer = time.monotonic

T = TypeVar("T")

_global_thread_lock = threading.Lock()


class Agent(RPCDispatcher):
    """
    Base class for all MetricQ agents - i.e. clients that are connected to the
    RabbitMQ MetricQ network.

    The lifetime of an agent works as follows:

    * create an instance
    * ``await`` :meth:`connect`
    * ``await`` :meth:`stop`

    :meth:`stop` is automatically invoked if the connection is lost and the reconnect
    timeout is exceeded. It may also be called manually to stop the agent.

    To indefinitely wait for the agent to stop, use :meth:`stopped`.

    Usually, :meth:`connect` and  :meth:`stop` are not called directly, but instead:

    * The class (via its child :class:`Client`) is used as an asynchronous context
      manager, e.g. ``async with Client(...) as agent:``. In that case,
      :meth:`connect` and :meth:`stop` are called as part of the context.

    * The synchronous :meth:`run` method is called, which:

      * sets up a signal handler for ``SIGINT`` and ``SIGTERM`` that calls :meth:`stop`.
      * sets up a loop exception handler that calls :meth:`stop`.
      * calls :meth:`connect` and :meth:`stopped` to run indefinitely until
        :meth:`stop` is called.

    Within :meth:`stop`, the Agent will invoke :meth:`teardown` to allow the all child
    classes to perform any necessary cleanup. Implementations of :meth:`teardown` should
    call ``super().teardown()``, possibly in an ``asyncio.gather``. :meth:`stop`
    wraps the invocation of :meth:`teardown` in a timeout (``_close_timeout``) and logs any
    errors during cleanup, possibly passing it to anyone waiting for :meth:`stopped`.
    """

    LOG_MAX_WIDTH = 200

    def __init__(
        self,
        token: str,
        url: Optional[str] = None,
        *,
        connection_timeout: int | float = 600,
        add_uuid: bool = False,
        management_url: Optional[str] = None,
    ):
        """
        Args:
            token: The token of the agent.
            url:
                The amqp(s) URL of the MetricQ management network.
            add_uuid:
                Whether to add a UUID to the token. This is used for transient clients
                without centralized configuration.
            connection_timeout:
                The timeout (in seconds) for reconnecting.
        """
        self.token = f"{token}.{uuid.uuid4().hex}" if add_uuid else token

        if management_url is not None:
            warn(
                "using deprecated 'management_url' argument, please use 'url' instead",
                DeprecationWarning,
            )
            if url is not None:
                raise TypeError(
                    "cannot use both 'url' and 'management_url', use only 'url'"
                )
            url = management_url

        if url is None:
            raise TypeError("missing required positional argument 'url'")

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_in_progress = False
        self._cancel_on_exception = False
        self._close_timeout = connection_timeout

        # Cannot create it here because creating a future requires a running event loop
        self.__stop_future: Optional[asyncio.Future[None]] = None

        self._management_url = url
        self._management_broadcast_exchange_name = "metricq.broadcast"
        self._management_exchange_name = "metricq.management"

        self._management_connection: Optional[
            aio_pika.abc.AbstractRobustConnection
        ] = None
        self._management_connection_watchdog = ConnectionWatchdog(
            on_timeout_callback=lambda watchdog: self._schedule_stop(
                ReconnectTimeout(
                    f"Failed to reestablish {watchdog.connection_name} after {watchdog.timeout} seconds"
                )
            ),
            timeout=connection_timeout,
            connection_name="management connection",
        )
        self._management_channel: Optional[aio_pika.abc.AbstractChannel] = None

        self.management_rpc_queue: Optional[aio_pika.abc.AbstractQueue] = None

        self._management_broadcast_exchange: Optional[
            aio_pika.abc.AbstractExchange
        ] = None
        self._management_exchange: Optional[aio_pika.abc.AbstractExchange] = None

        self._rpc_response_handlers: dict[
            str, tuple[Callable[..., None], bool]
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

    @property
    def _stop_future(self) -> asyncio.Future[None]:
        if self.__stop_future is None:
            self.__stop_future = self._event_loop.create_future()
        return self.__stop_future

    async def make_connection(
        self, url: str, connection_name: str
    ) -> aio_pika.abc.AbstractRobustConnection:
        url_obj = URL(url).with_query(
            {"reconnect_interval": 5, "fail_fast": 1, "name": connection_name}
        )
        connection = await aio_pika.connect_robust(
            url_obj,
            # If the following bugfix released, we can MAYBE use the following code again
            # instead of hacking the url query parameters
            # https://github.com/mosquito/aio-pika/pull/531
            # reconnect_interval=30,
            # fail_fast=True,
            # name=connection_name,
        )

        # How stupid that we can't easily add the handlers *before* actually connecting.
        # We could make our own RobustConnection object, but then we loose url parsing convenience
        connection.reconnect_callbacks.add(self._on_reconnect)
        connection.close_callbacks.add(self._on_close)

        return connection

    async def connect(self) -> None:
        """Connect to the MetricQ network"""
        logger.info(
            "establishing management connection to {}",
            URL(self._management_url).with_password("******"),
        )

        try:
            connection = await self.make_connection(
                self._management_url,
                connection_name="management connection {}".format(self.token),
            )
            self._management_connection = connection
            connection.close_callbacks.add(self._on_management_connection_close)
            connection.reconnect_callbacks.add(self._on_management_connection_reconnect)

            self._management_channel = await connection.channel()
            assert self._management_channel is not None
            self.management_rpc_queue = await self._management_channel.declare_queue(
                "{}-rpc".format(self.token), exclusive=True
            )
        except Exception as e:
            logger.error(
                "Failed to connect {}: {} ({})",
                type(self).__qualname__,
                e,
                type(e).__qualname__,
            )
            raise ConnectFailed("Failed to connect Agent") from e

        self._management_connection_watchdog.start()
        self._management_connection_watchdog.set_established()

    def run(
        self,
        catch_signals: Iterable[str] = ("SIGINT", "SIGTERM"),
        cancel_on_exception: bool = False,
        use_uvloop: Optional[bool] = None,
    ) -> None:
        """Run an Agent by calling :meth:`connect` and waiting for it to be stopped via :meth:`stop`.

        If :meth:`connect` raises an exception, :exc:`.ConnectFailed` is
        raised, with the offending exception attached as a cause.  Any
        exception passed to :meth:`stop` is reraised.

        Args:
            catch_signals:
                Call :meth:`on_signal` if any of these signals were raised.
            cancel_on_exception:
                Stop the running Agent when an unhandled exception occurs.
                The exception is reraised from this method.
            use_uvloop:
                Use uvloop as the asyncio event loop. If ``None``, uvloop is used if available.
                If ``True``, uvloop is used and an ImportError is raised if it is not available.
                If ``False``, uvloop is not used even if it is available.

        Raises:
            ConnectFailed:
                Failed to :meth:`connect` to the MetricQ network.
                The source exception is attached as a cause.
            Exception: Any exception passed to :meth:`stop`.
        """
        self._cancel_on_exception = cancel_on_exception
        coro = self._wait_for_stop(catch_signals)

        if use_uvloop is True or use_uvloop is None:
            try:
                import uvloop

                logger.debug("Installing uvloop")
                uvloop.install()
            except ImportError:
                if use_uvloop:
                    logger.error("Failed to import uvloop as requested.")
                    raise
                logger.debug("uvloop not available, falling back to asyncio.")
        logger.debug("Starting runner.")
        asyncio.run(coro)
        logger.debug("runner completed.")

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
        exchange: aio_pika.abc.AbstractExchange,
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
                # We must clean up when we use the future otherwise we get errors
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

        # May VTTI be with you ༼ つ ╹ ╹ ༽つ
        assert callable(response_callback)

        self._rpc_response_handlers[correlation_id] = (
            response_callback,
            cleanup_on_response,
        )

        try:
            await exchange.publish(msg, routing_key=routing_key)
        except aio_pika.exceptions.ChannelInvalidStateError as e:
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

    async def rpc_consume(self, extra_queues: Iterable[aio_pika.Queue] = []) -> None:
        """Start consuming RPCs

        :meta private:

        Typically, this is called at the end of :meth:`Client.connect` once the
        Agent is prepared to handle RPCs.

        Args:
            extra_queues: additional queues on which to receive RPCs
        """
        logger.info("starting RPC consume")
        assert self.management_rpc_queue is not None
        queues = chain([self.management_rpc_queue], extra_queues)
        await asyncio.gather(
            *[queue.consume(self._on_management_message) for queue in queues]
        )

    def on_signal(self, signal: str) -> None:
        """Callback invoked when a signal is received.

        Override this method for custom signal handling.
        By default, it schedules the Client to stop by calling :meth:`stop`.

        Args:
            signal: Name of the signal that occurred, e.g. :code:`"SIGTERM"`,
                    :code:`"SIGINT"`, etc.
        """
        logger.info("Received signal {}, stopping...", signal)
        self._schedule_stop(
            exception=None if signal == "SIGINT" else ReceivedSignal(signal)
        )

    def on_exception(
        self, loop: asyncio.AbstractEventLoop, context: Mapping[str, Any]
    ) -> None:
        logger.error("Exception in event loop: {}".format(context["message"]))
        if loop.is_closed():
            logger.error("Received exception in closed loop.")
        elif loop != self._event_loop:
            logger.error(
                f"Exception happened in a loop {loop} "
                f"other than the internal loop {self._event_loop}. "
                "This should never happen."
            )

        with suppress(KeyError):
            logger.error("Future: {}", context["future"])

        with suppress(KeyError):
            logger.error("Handle: {}", context["handle"])

        ex: Optional[Exception] = context.get("exception")
        if ex is not None:
            is_keyboard_interrupt = isinstance(ex, KeyboardInterrupt)
            if (
                self._cancel_on_exception or is_keyboard_interrupt
            ) and loop.is_running():
                if not is_keyboard_interrupt:
                    logger.error(
                        "Stopping Agent on unhandled exception ({})",
                        type(ex).__qualname__,
                    )
                self._schedule_stop(exception=ex)
            else:
                logger.error(
                    f"Agent {type(self).__qualname__} encountered an unhandled exception",
                    exc_info=(ex.__class__, ex, ex.__traceback__),
                )

    def _schedule_stop(
        self,
        exception: Optional[Exception] = None,
    ) -> None:
        self._event_loop.create_task(self.stop(exception=exception, silent=True))

    async def stop(
        self, exception: Optional[BaseException] = None, silent: bool = False
    ) -> None:
        """
        Stop a running Agent. When calling stop multiple times, all but the
        first call will be ignored. It will inform anyone waiting for
        :meth:`stopped` about the completion or the given exception.

        Args:
            exception:
                An optional exception that will be raised by :meth:`run` if given.
                If the Agent was not started from :meth:`run`, see :meth:`stopped`
                how to retrieve this exception.
            silent:
                If set to :code:`True`, a passed exception will not be raised.

        Raises:
            AgentStopped:
                If an ``exception`` is given or an exception occurred while closing
                the connection(s) and ``silent==False``.
        """
        if self._stop_in_progress:
            logger.warning(
                "Stop in progress, ignoring (exception: {}, silent: {})",
                exception,
                silent,
            )
            return

        self._stop_in_progress = True

        logger.info("Stopping Agent {} ({})...", type(self).__qualname__, exception)

        try:
            # I tried so hard to `shield` this call
            # But in the end, it doesn't even matter
            # The task is canceled, the loop is closed
            # But in the end, it doesn't even matter
            #
            # I tried to close connections clean,
            # A perfect end, that's what I mean,
            # But when the network grew stale,
            # My efforts were to no avail.
            #
            # The close packets, they couldn't send,
            # A deadlock near, I can't pretend,
            # So I added a timeout here,
            # To break free from the chains of fear.
            await asyncio.wait_for(self.teardown(), self._close_timeout)
        except BaseException as close_exception:
            logger.error("Error while closing Agent: {}", close_exception)
            if not exception:
                exception = close_exception

        assert not self._stop_future.done()
        if exception is None:
            self._stop_future.set_result(None)
        else:
            self._stop_future.set_exception(exception)

        if not silent and exception is not None:
            raise AgentStopped("Agent stopped with error") from exception

    async def stopped(self) -> None:
        """Wait for this Agent to stop.

        If the agent stopped unexpectedly, this method raises an exception.

        Raises:
            AgentStopped:
                The Agent was stopped via :meth:`stop` and an exception was passed.
            Exception:
                The Agent encountered any other unhandled exception.
        """
        await self._stop_future

    async def teardown(self) -> None:
        """
        .. Important::
            Do not call this function, it is called indirectly by :meth:`Agent.stop`.

        Close all connections and channels. Child classes should implement this
        method to close their own connections and channels and call
        ``super().teardown()``.
        """
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

    def _make_correlation_id(self) -> str:
        return "metricq-rpc-py-{}-{}".format(self.token, uuid.uuid4().hex)

    async def _on_management_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        """Callback invoked when a message is received.

        Args:
            message: Either an RPC request or an RPC response.

        Raises:
            PublishFailed: The reply could not be published.
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
                if not message.reply_to:
                    logger.warning(
                        "RPC request from {} has no reply_to, ignoring",
                        from_token,
                    )
                    return
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
                except aio_pika.exceptions.ChannelInvalidStateError as e:
                    errmsg = (
                        "Failed to reply to '{message.reply_to}' for RPC '{function!r}'"
                    )
                    logger.error("{}: {}", errmsg, e)
                    raise PublishFailed(errmsg) from e
            else:
                logger.debug("message is an RPC response")
                if correlation_id is None:
                    logger.error(
                        "received RPC response from {} without correlation id, ignoring",
                        from_token,
                    )
                    return
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

                # I'd agree here with Mypy that handler is always truthy here. There should
                # not be an entry in _rpc_response_handler with a handler of None.
                # Either there is no entry in the first place, or the entry is valid.
                # May VTTI be with you. \(^-^)/
                assert handler is not None

                # Allow simple handlers that are not coroutines
                # But only None to not get any confusion
                r = handler(**arguments)
                if r is not None:
                    await r

    def _on_reconnect(self, sender: aio_pika.abc.AbstractRobustConnection) -> None:
        logger.info("Reconnected to {}", sender)

    def _on_close(
        self,
        sender: aio_pika.abc.AbstractRobustConnection,
        exception: Optional[BaseException],
    ) -> None:
        if isinstance(exception, asyncio.CancelledError):
            logger.debug("Connection closed regularly")
            return
        logger.info(
            "Connection closed: {} ({})", exception, type(exception).__qualname__
        )

    def _on_management_connection_reconnect(
        self, sender: aio_pika.abc.AbstractRobustConnection
    ) -> None:
        self._management_connection_watchdog.set_established()

    def _on_management_connection_close(
        self,
        sender: aio_pika.abc.AbstractRobustConnection,
        _exception: Optional[BaseException],
    ) -> None:
        self._management_connection_watchdog.set_closed()
