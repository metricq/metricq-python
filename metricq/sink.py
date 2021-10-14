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

from abc import abstractmethod
from asyncio import CancelledError, Task
from typing import Any, Dict, List, Optional, Set, Union

import aio_pika
from aio_pika.queue import Queue

from .data_client import DataClient
from .datachunk_pb2 import DataChunk
from .logging import get_logger
from .types import JsonDict, Metric, Timestamp

logger = get_logger(__name__)


class Sink(DataClient):
    """A base class intended to be subclassed to create user-defined :term:`Sinks<Sink>`.

    See :ref:`sink-how-to` for an introduction how to implement a Sink.

    Args:
        add_uuid:
            whether to append a randomly generated UUID to this Sink's :term:`Token`.
            This is useful to distinguish different instances of the same Sink.
    """

    def __init__(self, *args: Any, add_uuid: bool = True, **kwargs: Any):
        super().__init__(*args, add_uuid=add_uuid, **kwargs)

        self._data_queue: Optional[Queue] = None
        self._data_consumer_tag: Optional[str] = None
        self._subscribed_metrics: Set[str] = set()
        self._subscribe_args: Dict[str, Any] = dict()
        self._resubscribe_task: Optional[Task[None]] = None

    async def _declare_data_queue(self, name: str) -> None:
        assert self.data_channel is not None
        self._data_queue = await self.data_channel.declare_queue(
            name=name, robust=False, passive=True
        )

    async def sink_config(self, dataQueue: str, **kwargs: Any) -> None:
        await self.data_config(**kwargs)
        await self._declare_data_queue(dataQueue)

        assert self._data_queue is not None

        logger.info("starting sink consume")
        self._data_consumer_tag = await self._data_queue.consume(self._on_data_message)

    def _on_data_connection_reconnect(
        self, sender: Any, connection: aio_pika.Connection
    ) -> None:
        logger.info("Sink data connection ({}) reestablished!", connection)

        if self._resubscribe_task is not None and not self._resubscribe_task.done():
            logger.warning(
                "Sink data connection was reestablished, but another resubscribe task is still running!"
            )
            self._resubscribe_task.cancel()

        self._resubscribe_task = self.event_loop.create_task(
            self._resubscribe(connection)
        )

        def resubscribe_done(task: Task[None]) -> None:
            try:
                exception = task.exception()
                if exception is None:
                    self._data_connection_watchdog.set_established()
                else:
                    logger.error(
                        f"Resubscription failed with an unhandled exception: {exception}"
                    )
                    raise exception
            except CancelledError:
                logger.warning("Resubscribe task was cancelled!")

        self._resubscribe_task.add_done_callback(resubscribe_done)

    async def _resubscribe(self, connection: aio_pika.Connection) -> None:
        assert self._data_queue is not None
        # Reuse manager-assigned data queue name for resubscription.
        self._subscribe_args.update(dataQueue=self._data_queue.name)

        metrics = tuple(self._subscribed_metrics)
        logger.info(
            "Resubscribing to {} metric(s) with RPC parameters {}...",
            len(metrics),
            self._subscribe_args,
        )
        response = await self.rpc(
            "sink.subscribe", metrics=metrics, **self._subscribe_args
        )
        assert response is not None
        await self._declare_data_queue(response["dataQueue"])

        logger.debug("Restarting consume...")
        await self._data_queue.consume(
            self._on_data_message, consumer_tag=self._data_consumer_tag
        )

    async def subscribe(
        self,
        metrics: List[Metric],
        expires: Union[None, int, float] = None,
        metadata: Optional[bool] = None,
        **kwargs: Any,
    ) -> JsonDict:
        """Subscribe to a list of metrics.

        Args:
            metrics: names of the metrics to subscribe to
            expires: queue expiration time in seconds
            metadata: whether to return metric metadata in the response, defaults to ``True``

        Returns:
            rpc response
        """

        if self._data_queue is not None:
            kwargs.update(dataQueue=self._data_queue.name)

        if expires is not None:
            kwargs.update(expires=expires)

        if metadata is not None:
            kwargs.update(metadata=metadata)

        response = await self.rpc("sink.subscribe", metrics=metrics, **kwargs)
        assert response is not None

        self._subscribed_metrics.update(metrics)
        # Save the subscription RPC args in case we need to resubscribe (after a reconnect).
        self._subscribe_args = kwargs

        if self._data_queue is None:
            await self.sink_config(**response)
        return response

    async def unsubscribe(self, metrics: List[Metric]) -> None:
        assert self._data_queue
        await self.rpc(
            "sink.unsubscribe", dataQueue=self._data_queue.name, metrics=metrics
        )

        self._subscribed_metrics.difference_update(metrics)

        # If we just unsubscribed from all metrics, reset the subscription args
        # to their defaults.
        if not self._subscribed_metrics:
            self._subscribe_args = dict()

    async def _on_data_message(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process(requeue=True):
            body = message.body
            from_token = message.app_id
            metric = message.routing_key

            logger.debug("received message from {}", from_token)
            data_response = DataChunk()
            data_response.ParseFromString(body)

            await self._on_data_chunk(metric, data_response)

    async def _on_data_chunk(self, metric: Metric, data_chunk: DataChunk) -> None:
        """ Only override this if absolutely necessary for performance """
        last_timed = 0
        zipped_tv = zip(data_chunk.time_delta, data_chunk.value)
        for time_delta, value in zipped_tv:
            last_timed += time_delta
            await self.on_data(metric, Timestamp(last_timed), value)

    @abstractmethod
    async def on_data(self, metric: Metric, timestamp: Timestamp, value: float) -> None:
        """A Callback that is invoked for every data point received for any of the metrics this client is subscribed to.

        User-defined :term:`Sinks<Sink>` need to override this method to handle incoming data points.

        Args:
            metric: name of the metric for which a new data point arrived
            timestamp: timepoint at which this metric was measured
            value: value of the metric at time of measurement
        """


class DurableSink(Sink):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, add_uuid=False, **kwargs)

    async def connect(self) -> None:
        await super().connect()

        response = await self.rpc("sink.register")
        assert response is not None
        logger.info("register response: {}", response)

        await self.rpc_dispatch("config", **response["config"])
