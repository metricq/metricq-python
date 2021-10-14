# Copyright (c) 2018, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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
import uuid
from asyncio import CancelledError, Task
from asyncio.futures import Future
from enum import Enum, auto
from typing import Any, Dict, Iterator, List, Optional

import aio_pika
from aiormq import ChannelInvalidStateError

from . import history_pb2
from .client import Client, _GetMetricsResult
from .connection_watchdog import ConnectionWatchdog
from .exceptions import (
    HistoryError,
    InvalidHistoryResponse,
    PublishFailed,
    ReconnectTimeout,
)
from .logging import get_logger
from .rpc import rpc_handler
from .types import TimeAggregate, Timedelta, Timestamp, TimeValue
from .version import __version__  # noqa: F401 - shut up flake8, automatic version str

logger = get_logger(__name__)


class HistoryRequestType(Enum):
    """The type of metric data to request.

    Use the value below to select which to request in :meth:`.HistoryClient.history_data_request`.
    See :class:`HistoryResponse` for a distinction between `raw values` and `aggregates`.
    """

    AGGREGATE_TIMELINE = history_pb2.HistoryRequest.AGGREGATE_TIMELINE
    """Retrieve a timeline of aggregates with the specified `max_interval` each.
    """

    AGGREGATE = history_pb2.HistoryRequest.AGGREGATE
    """Retrieve a single aggregate over the specified duration.
    """

    LAST_VALUE = history_pb2.HistoryRequest.LAST_VALUE
    """Only retrieve the last data point recorded for a metric.
    """

    FLEX_TIMELINE = history_pb2.HistoryRequest.FLEX_TIMELINE
    """Retrieve either aggregates or raw values, depending on the `max_interval.`
    """


class HistoryResponseType(Enum):
    """The type of a history response.

    See :attr:`HistoryResponse.mode` how these values should be interpreted
    in the context of a :class:`HistoryResponse`.
    """

    EMPTY = auto()
    """The response contains no values at all.
    """

    AGGREGATES = auto()
    """The response contains a list of aggregates.
    """

    VALUES = auto()
    """The response contains a list of time-value pairs.
    """

    LEGACY = auto()
    """The response is in an unspecified legacy format.
    """


class HistoryResponse:
    """Response to a history request containing the historical data.

    Providers of historical data send either `raw values` (`time-value` pairs, see :class:`.TimeValue`)
    or `aggregates` (see :class:`.TimeAggregate`).

    The data is accessed by iterating over either :meth:`values` or :meth:`aggregates`.
    If the response is of the wrong type, these methods might fail and raise :exc:`ValueError`.
    Match on the value of :attr:`mode` determine whether this response contains raw values or aggregates.
    Alternatively, pass :code:`convert=True` to either :meth:`values` or :meth:`aggregates`
    to transparently convert the data to the desired type.
    """

    def __init__(
        self,
        proto: history_pb2.HistoryResponse,
        request_duration: Optional[float] = None,
    ):
        """HistoryResponse objects are created by the HistoryClient methods.

        Don't bother instantiating on your own.

        :meta private:
        """
        self.request_duration = request_duration
        count = len(proto.time_delta)
        if proto.error != "":
            raise HistoryError(f"request failed on database: {proto.error}")

        elif count == 0:
            self._mode = HistoryResponseType.EMPTY
            if (
                len(proto.value_min) != 0
                or len(proto.value_max) != 0
                or len(proto.aggregate) != 0
                or len(proto.value) != 0
            ):
                raise InvalidHistoryResponse("time_delta empty, but values present")

        elif len(proto.aggregate) == count:
            self._mode = HistoryResponseType.AGGREGATES
            if len(proto.value) != 0:
                raise InvalidHistoryResponse("values and aggregates present")

        elif len(proto.value) == count:
            self._mode = HistoryResponseType.VALUES
            if len(proto.aggregate) != 0:
                raise InvalidHistoryResponse("aggregates and values present")

        elif len(proto.value_avg) == count:
            self._mode = HistoryResponseType.LEGACY
            if (
                len(proto.value_min) != count
                or len(proto.value_max) != count
                or len(proto.aggregate) != 0
                or len(proto.value) != 0
            ):
                raise InvalidHistoryResponse("inconsistent counts in legacy format")

        else:
            raise InvalidHistoryResponse("no value count matches time_delta count")

        self._proto = proto

    def __len__(self) -> int:
        return len(self._proto.time_delta)

    @property
    def mode(self) -> HistoryResponseType:
        """The type of response at hand.

        This determines the behavior of :meth:`aggregates` and :meth:`values`:

        :attr:`mode` is :attr:`~HistoryResponseType.VALUES`:
            :meth:`values` will return a iterator of :class:`~metricq.TimeValue`.
            :meth:`aggregates` will fail with :exc:`ValueError`, except if called with :code:`convert=True`.
        :attr:`mode` is :attr:`~HistoryResponseType.AGGREGATES`:
            :meth:`aggregates` will return a iterator of :class:`~metricq.TimeAggregate`.
            :meth:`values` will fail with :exc:`ValueError`, except if called with :code:`convert=True`.
        :attr:`mode` is :attr:`~HistoryResponseType.EMPTY`:
            Both :meth:`values` and :meth:`aggregates` return an empty iterator.
        :attr:`mode` is :attr:`~HistoryResponseType.LEGACY`:
            Both :meth:`values` and :meth:`aggregates` will raise :exc:`ValueError` unless called with :code:`convert=True`.

        .. warning::
            The values listed here might be *non-exhaustive*, new ones might be added in the future.
            If matching on a value of :class:`HistoryResponseType`, make sure to include a *catch-all* case::

                if response.mode is HistoryResponseType.VALUES:
                    ...
                elif response.mode is HistoryResponseType.AGGREGATES:
                    ...
                else:
                    # catch-all case, handle it cleanly

        """
        return self._mode

    def values(self, convert: bool = False) -> Iterator[TimeValue]:
        """An iterator over all data points included in this response.

        Args:
            convert:
                Convert values transparently if response does not contain raw values.
                If the response contains aggregates, this will yield the mean value of each aggregate.

        Raises:
            :class:`ValueError`:
                if :code:`convert=False` and the response does not contain raw values.
        """
        time_ns = 0
        if self._mode is HistoryResponseType.VALUES:
            for time_delta, value in zip(self._proto.time_delta, self._proto.value):
                time_ns = time_ns + time_delta
                yield TimeValue(Timestamp(time_ns), value)
            return
        elif self._mode is HistoryResponseType.EMPTY:
            return

        if not convert:
            raise ValueError(
                "Attempting to access values of HistoryResponse.values in wrong mode: {}".format(
                    self._mode
                )
            )

        if self._mode is HistoryResponseType.AGGREGATES:
            for time_delta, proto_aggregate in zip(
                self._proto.time_delta, self._proto.aggregate
            ):
                time_ns = time_ns + time_delta
                timestamp = Timestamp(time_ns)
                aggregate = TimeAggregate.from_proto(timestamp, proto_aggregate)
                yield TimeValue(timestamp, aggregate.mean)
            return

        if self._mode is HistoryResponseType.LEGACY:
            for time_delta, average in zip(
                self._proto.time_delta, self._proto.value_avg
            ):
                time_ns = time_ns + time_delta
                yield TimeValue(Timestamp(time_ns), average)
            return

        raise ValueError("Invalid HistoryResponse mode")

    def aggregates(self, convert: bool = False) -> Iterator[TimeAggregate]:
        """An iterator over aggregates contained in this response.

        Args:
            convert:
                Convert values to aggregates transparently if response does not contain aggregates.
                If the response contains `raw values`, this will yield an aggregate for each value.

        Raises:
            ValueError:
                if :code:`convert=False` and the underlying response does not contain aggregates
            NonMonotonicTimestamps:
                if the underling data has mode :attr:`~HistoryResponseType.VALUES` and
                timestamps are not strictly monotonically increasing
        """
        time_ns = 0
        if self._mode is HistoryResponseType.AGGREGATES:
            for time_delta, proto_aggregate in zip(
                self._proto.time_delta, self._proto.aggregate
            ):
                time_ns = time_ns + time_delta
                timestamp = Timestamp(time_ns)
                yield TimeAggregate.from_proto(timestamp, proto_aggregate)
            return
        elif self._mode is HistoryResponseType.EMPTY:
            return

        if not convert:
            raise ValueError(
                "Attempting to access values of HistoryResponse.aggregates in wrong mode: {}".format(
                    self._mode
                )
            )

        if len(self) == 0:
            return

        if self._mode is HistoryResponseType.VALUES:
            time_ns = self._proto.time_delta[0]
            previous_timestamp = Timestamp(time_ns)
            # First interval is useless here
            for time_delta, value in zip(
                self._proto.time_delta[1:], self._proto.value[1:]
            ):
                time_ns = time_ns + time_delta
                timestamp = Timestamp(time_ns)
                yield TimeAggregate.from_value_pair(
                    previous_timestamp, timestamp, value
                )
                previous_timestamp = timestamp
            return

        if self._mode is HistoryResponseType.LEGACY:
            for time_delta, minimum, maximum, average in zip(
                self._proto.time_delta,
                self._proto.value_min,
                self._proto.value_max,
                self._proto.value_avg,
            ):
                time_ns = time_ns + time_delta
                # That of course only makes sense if you just use mean or mean_sum
                # We don't do the nice intervals here...
                yield TimeAggregate(
                    timestamp=Timestamp(time_ns),
                    minimum=minimum,
                    maximum=maximum,
                    sum=average,
                    count=1,
                    integral_ns=0,
                    active_time=Timedelta(0),
                )
            return

        raise ValueError("Invalid HistoryResponse mode")


class HistoryClient(Client):
    """A MetricQ client to access historical metric data."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.data_server_address: Optional[str] = None
        self.history_connection: Optional[aio_pika.RobustConnection] = None
        self.history_channel: Optional[aio_pika.RobustChannel] = None
        self.history_exchange: Optional[aio_pika.Exchange] = None
        self.history_response_queue: Optional[aio_pika.Queue] = None

        self._history_connection_watchdog = ConnectionWatchdog(
            on_timeout_callback=lambda watchdog: self._schedule_stop(
                ReconnectTimeout(
                    f"Failed to reestablish {watchdog.connection_name} after {watchdog.timeout} seconds"
                )
            ),
            timeout=kwargs.get("connection_timeout", 60),
            connection_name="history connection",
        )

        self._request_futures: Dict[str, Future[HistoryResponse]] = dict()
        self._reregister_task: Optional[Task[None]] = None

    async def connect(self) -> None:
        """Connect to the MetricQ network and register this HistoryClient."""
        await super().connect()
        response = await self.rpc("history.register")
        logger.debug("register response: {}", response)

        assert response is not None

        self.data_server_address = self.derive_address(response["dataServerAddress"])
        self.history_connection = await self.make_connection(
            self.data_server_address,
            connection_name="history connection {}".format(self.token),
        )
        self.history_connection.add_close_callback(self._on_history_connection_close)
        self.history_connection.add_reconnect_callback(
            self._on_history_connection_reconnect  # type: ignore
        )

        self.history_channel = await self.history_connection.channel()
        assert self.history_channel is not None
        self.history_exchange = await self.history_channel.declare_exchange(
            name=response["historyExchange"], passive=True
        )
        await self._declare_history_queue(response["historyQueue"])

        if "config" in response:
            await self.rpc_dispatch("config", **response["config"])

        self._history_connection_watchdog.start(loop=self.event_loop)
        self._history_connection_watchdog.set_established()

        await self._history_consume()

    async def stop(self, exception: Optional[Exception] = None) -> None:
        logger.info("closing history channel and connection.")
        await self._history_connection_watchdog.stop()
        if self.history_channel:
            await self.history_channel.close()  # type: ignore
            self.history_channel = None
        if self.history_connection:
            # We need not pass anything as exception to this close. It will only hurt.
            await self.history_connection.close()  # type: ignore
            self.history_connection = None
        self.history_exchange = None
        await super().stop(exception)

    async def get_metrics(self, *args: Any, **kwargs: Any) -> _GetMetricsResult:
        """Retrieve information for **historic** metrics matching a selector pattern.

        This is like :meth:`Client.get_metrics`, but sets :code:`historic=True` by default.
        See documentation there for a detailed description of the remaining arguments.
        """
        kwargs.setdefault("historic", True)
        return await super().get_metrics(*args, **kwargs)

    async def history_data_request(
        self,
        metric: str,
        start_time: Optional[Timestamp],
        end_time: Optional[Timestamp],
        interval_max: Optional[Timedelta],
        request_type: HistoryRequestType = HistoryRequestType.AGGREGATE_TIMELINE,
        timeout: float = 60,
    ) -> HistoryResponse:
        """Request historical data points of a metric.

        Args:
            metric:
                The metric of interest.
            start_time:
                Only include data points from this point in time onward.
            end_time:
                Only include data points up to this point in time.
            interval_max:
                Maximum time between data points in response.
            request_type:
                The type of metric data to request.
                See :class:`.HistoryRequestType`.
            timeout:
                Operation timeout in seconds.

        Raises:
            ValueError: if metric is empty or longer than 255 bytes
        """
        if not metric:
            raise ValueError("Metric must be a non-empty string")
        if len(metric.encode("utf-8")) > 255:
            raise ValueError(
                "Metric names (amqp routing keys) must be at most 255 bytes long"
            )

        correlation_id = "mq-history-py-{}-{}".format(self.token, uuid.uuid4().hex)

        logger.debug(
            "running history request for {} ({}-{},{}) with correlation id {}",
            metric,
            start_time,
            end_time,
            interval_max,
            correlation_id,
        )

        request = history_pb2.HistoryRequest()
        if start_time is not None:
            request.start_time = start_time.posix_ns
        if end_time is not None:
            request.end_time = end_time.posix_ns
        if interval_max is not None:
            request.interval_max = interval_max.ns
        if request_type is not None:
            request.type = request_type.value

        assert self.history_response_queue is not None

        msg = aio_pika.Message(
            body=request.SerializeToString(),
            correlation_id=correlation_id,
            reply_to=self.history_response_queue.name,
        )

        self._request_futures[correlation_id] = asyncio.Future(loop=self.event_loop)
        assert self.history_exchange is not None
        await self._history_connection_watchdog.established()

        try:
            # TOC/TOU hazard: by the time we publish, the data connection might
            # be gone again, even if we waited for it to be established before.
            await self.history_exchange.publish(msg, routing_key=metric)
        except ChannelInvalidStateError as e:
            # Trying to publish on a closed channel results in a ChannelInvalidStateError
            # from aiormq.  Let's wrap that in a more descriptive error.
            raise PublishFailed(
                f"Failed to publish data chunk for metric '{metric!r}' "
                f"on exchange '{self.history_exchange}' ({self.history_connection})"
            ) from e

        try:
            result = await asyncio.wait_for(
                self._request_futures[correlation_id], timeout=timeout
            )
        finally:
            del self._request_futures[correlation_id]
        return result

    async def history_aggregate(
        self,
        metric: str,
        start_time: Optional[Timestamp] = None,
        end_time: Optional[Timestamp] = None,
        timeout: float = 60,
    ) -> TimeAggregate:
        """Aggregate values of a metric for the specified span of time.

        Args:
            metric:
                Name of the metric to aggregate.
            start_time:
                Only aggregate values from this point in time onward.
                If omitted, aggregation starts at the first data point of this metric.
            end_time:
                Only aggregate values up to this point in time.
                If omitted, aggregation includes the most recent values of this metric.
            timeout:
                Operation timeout in seconds.

        Returns:
            A single aggregate over values of this metric, including minimum/maximum/average/etc. values.

        Raises:
            ~exceptions.InvalidHistoryResponse:
        """
        response: HistoryResponse = await self.history_data_request(
            metric=metric,
            start_time=start_time,
            end_time=end_time,
            interval_max=None,
            request_type=HistoryRequestType.AGGREGATE,
            timeout=timeout,
        )

        if len(response) == 1:
            return next(response.aggregates())
        else:
            raise InvalidHistoryResponse(
                f"contains {len(response)} aggregates, expected 1"
            )

    async def history_aggregate_timeline(
        self,
        metric: str,
        *,
        interval_max: Timedelta,
        start_time: Optional[Timestamp] = None,
        end_time: Optional[Timestamp] = None,
        timeout: float = 60,
    ) -> Iterator[TimeAggregate]:
        """Aggregate values of a metric in multiple steps.

        Each aggregate spans values *at most* :literal:`interval_max` apart.
        Aggregates are returned in order, consecutive aggregates span consecutive values of this metric.
        Together, all aggregates span all values from :literal:`start_time` to :literal:`end_time`, inclusive.

        Args:
            metric:
                Name of the metric to aggregate.
            interval_max:
                Maximum timespan of values covered by each aggregate.
            start_time:
                Only aggregate values from this point in time onward.
                If omitted, aggregation starts at the first data point of this metric.
            end_time:
                Only aggregate values up to this point in time.
                If omitted, aggregation includes the most recent values of this metric.
            timeout:
                Operation timeout in seconds.

        Returns:
            An iterator over aggregates for this metric.

        Raises:
            ~exceptions.InvalidHistoryResponse:
        """
        response: HistoryResponse = await self.history_data_request(
            metric=metric,
            start_time=start_time,
            end_time=end_time,
            interval_max=interval_max,
            request_type=HistoryRequestType.AGGREGATE_TIMELINE,
            timeout=timeout,
        )

        try:
            return response.aggregates()
        except ValueError:
            raise InvalidHistoryResponse("AGGREGATE_TIMELINE contains no aggregates")

    async def history_last_value(
        self, metric: str, timeout: float = 60
    ) -> Optional[TimeValue]:
        """Fetch the last value recorded for a metric.

        If this metric has no values recorded, return :literal:`None`.

        Args:
            metric:
                Name of the metric of interest.
            timeout:
                Operation timeout in seconds.

        Raises:
            ~exceptions.InvalidHistoryResponse:
        """
        result = await self.history_data_request(
            metric,
            start_time=None,
            end_time=None,
            interval_max=None,
            request_type=HistoryRequestType.LAST_VALUE,
            timeout=timeout,
        )

        try:
            return next(result.values(), None)
        except ValueError:
            raise InvalidHistoryResponse("LAST_VALUE returned more than 1 value")

    async def history_raw_timeline(
        self,
        metric: str,
        start_time: Optional[Timestamp] = None,
        end_time: Optional[Timestamp] = None,
        timeout: float = 60,
    ) -> Iterator[TimeValue]:
        """Retrieve raw values of a metric within the specified span of time.

        Omitting both :literal:`start_time` and :literal:`end_time` yields all values recorded for this metric,
        omitting either one yields values up to/starting at a point in time.

        Args:
            metric:
                Name of the metric.
            start_time:
                Only retrieve values from this point in time onward.
                If omitted, include all values before :literal:`end_time`.
            end_time:
                Only aggregate values up to this point in time.
                If omitted, include all values after :literal:`start_time`.
            timeout:
                Operation timeout in seconds.

        Returns:
            An iterator over values of this metric.

        Raises:
            ~exceptions.InvalidHistoryResponse:
        """
        response: HistoryResponse = await self.history_data_request(
            metric=metric,
            start_time=start_time,
            end_time=end_time,
            interval_max=Timedelta(0),
            request_type=HistoryRequestType.FLEX_TIMELINE,
            timeout=timeout,
        )

        try:
            return response.values(convert=False)
        except ValueError:
            raise InvalidHistoryResponse("Response contained no values")

    @rpc_handler("config")
    async def _history_config(self, **kwargs: Any) -> None:
        logger.info("received config {}", kwargs)

    async def _history_consume(self, extra_queues: List[aio_pika.Queue] = []) -> None:
        logger.info("starting history consume")
        assert self.history_response_queue is not None
        queues = [self.history_response_queue] + extra_queues
        await asyncio.gather(
            *[queue.consume(self._on_history_response) for queue in queues],
            loop=self.event_loop,
        )

    async def _on_history_response(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process(requeue=True):
            body = message.body
            from_token = message.app_id
            correlation_id = message.correlation_id
            request_duration = float(message.headers.get("x-request-duration", "-1"))

            logger.debug(
                "received message from {}, correlation id: {}, reply_to: {}",
                from_token,
                correlation_id,
                message.reply_to,
            )
            history_response_pb = history_pb2.HistoryResponse()
            history_response_pb.ParseFromString(body)

            future = self._request_futures.get(correlation_id)

            # Make sure this message corresponds to a request we sent
            if future is None:
                logger.error(
                    "received history response with unknown correlation id {} "
                    "from {}",
                    correlation_id,
                    from_token,
                )
                return

            # Ensure we did not already handle this response
            if future.done():
                logger.error(
                    "history response from {} with correlation ID {} was handled already",
                    from_token,
                    correlation_id,
                )
                return

            # Parse the history response.  If the database returned an error,
            # raise HistoryError in the code awaiting the parsed response.
            try:
                history_response = HistoryResponse(
                    history_response_pb, request_duration
                )

                logger.debug("message is a history response")
                future.set_result(history_response)
            except HistoryError as e:
                logger.debug("message is a history response containing an error: {}", e)
                future.set_exception(e)

    def _on_history_connection_close(
        self, sender: Any, _exception: Optional[BaseException]
    ) -> None:
        self._history_connection_watchdog.set_closed()

    def _on_history_connection_reconnect(
        self, sender: Any, connection: aio_pika.Connection
    ) -> None:
        logger.info("History connection ({}) reestablished!", connection)

        if self._reregister_task is not None and not self._reregister_task.done():
            logger.warning(
                "History connection was reestablished, but another reregister task is still running!"
            )
            self._reregister_task.cancel()

        self._reregister_task = self.event_loop.create_task(
            self._reregister(connection)
        )

        def reregister_done(task: Task[None]) -> None:
            try:
                exception = task.exception()
                if exception is None:
                    self._history_connection_watchdog.set_established()
                else:
                    logger.error(
                        f"Reregister failed with an unhandled exception: {exception}"
                    )
                    raise exception
            except CancelledError:
                logger.warning("Reregister task was cancelled!")

        self._reregister_task.add_done_callback(reregister_done)

    async def _reregister(self, connection: aio_pika.Connection) -> None:
        logger.info(
            "Reregistering as history client...",
        )
        response = await self.rpc("history.register")

        assert response is not None
        assert self.history_exchange is not None
        assert response["historyExchange"] == self.history_exchange.name
        assert (
            self.derive_address(response["dataServerAddress"])
            == self.data_server_address
        )

        await self._declare_history_queue(response["historyQueue"])

        if "config" in response:
            await self.rpc_dispatch("config", **response["config"])

        logger.debug("Restarting consume...")
        await self._history_consume()

    async def _declare_history_queue(self, name: str) -> None:
        # The manager declares the queue and we only connect to that queue with passive=True
        # But when a disconnect happens, the queue gets deleted. Therefore, there is no
        # way, how a robust connection could reconnect to that queue. Hence, we set
        # robust=False and handle the reconnect ourselfs.
        # (See self._on_history_connection_reconnect())
        assert self.history_channel is not None
        self.history_response_queue = await self.history_channel.declare_queue(
            name=name, passive=True, robust=False
        )
