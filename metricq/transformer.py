import asyncio
from abc import abstractmethod
from typing import Dict, Optional

from aio_pika import IncomingMessage, Message, Queue
from aio_pika.exceptions import ChannelInvalidStateError

from .data_client import DataClient
from .datachunk_pb2 import DataChunk
from .logging import get_logger
from .source import MetricSendError
from .source_metric import SourceMetric
from .types import Timestamp

logger = get_logger(__name__)


class MetricContainer:
    def __init__(self, sender: DataClient, **metrics: SourceMetric):
        self.metrics: Dict[str, SourceMetric] = metrics
        self.chunk_size = 1
        self.sender = sender

    def declare(self, id: str, chunk_size=1) -> SourceMetric:
        metric = SourceMetric(id, self.sender, chunk_size=chunk_size)
        self.metrics[id] = metric
        return metric

    def __getitem__(self, id: str) -> SourceMetric:
        try:
            return self.metrics[id]
        except KeyError:
            return self.declare(id)


class Transformer(DataClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.output_metrics = MetricContainer(sender=self)
        self._data_queue: Optional[Queue] = None
        self._data_consumer_tag: Optional[str] = None

    async def connect(self):
        await super().connect()

        response = await self.rpc("transformer.register")

        await self.data_config(**response)

        self.data_exchange = await self.data_channel.declare_exchange(
            name=response["dataExchange"],
            passive=True,
        )

        config = response.get("config", None)
        if config is not None:
            await self.rpc_dispatch("config", **config)

    async def subscribe(self, metrics: str, **kwargs):
        if self._data_queue is not None:
            kwargs["dataQueue"] = self._data_queue.name
        response = await self.rpc("sink.subscribe", metrics=metrics, **kwargs)

        if self._data_queue is None:
            await self.transformer_config(**response)

    async def transformer_config(self, dataQueue, **kwargs):
        await self.data_config(**kwargs)
        await self._declare_data_queue(dataQueue)

        logger.info("starting transformer consume")
        self._data_consumer_tag = await self._data_queue.consume(self._on_data_message)

    async def _on_data_message(self, message: IncomingMessage):
        async with message.process(requeue=True):
            body = message.body
            from_token = message.app_id
            metric = message.routing_key

            logger.debug("received message from {}", from_token)
            data_response = DataChunk()
            data_response.ParseFromString(body)

            await self._on_data_chunk(metric, data_response)

    async def _declare_data_queue(self, name: str):
        self._data_queue = await self.data_channel.declare_queue(
            name=name, robust=False, passive=True
        )

    async def declare_metrics(self, metrics):
        await self.rpc("transformer.declare_metrics", metrics=metrics)

    async def send(self, metric, time: Timestamp, value):
        """
        Logical send.
        Dispatches to the SourceMetric for chunking
        """
        logger.debug("send({},{},{})", metric, time, value)
        metric_object = self.output_metrics[metric]
        assert metric_object is not None
        await metric_object.send(time, value)

    async def flush(self):
        await asyncio.gather(
            *[m.flush() for m in self.output_metrics.values() if not m.empty]
        )

    async def _send(self, metric, data_chunk: DataChunk):
        """
        Actual send of a chunk,
        don't call from anywhere other than SourceMetric
        """
        msg = Message(data_chunk.SerializeToString())
        await self._data_connection_watchdog.established()
        try:
            # TOC/TOU hazard: by the time we publish, the data connection might
            # be gone again, even if we waited for it to be established before.
            await self.data_exchange.publish(msg, routing_key=metric, mandatory=False)
        except ChannelInvalidStateError as e:
            # Trying to publish on a closed channel results in a ChannelInvalidStateError
            # from aiormq.  Let's wrap that in a more descriptive error.
            raise MetricSendError(
                f"Failed to publish data chunk for metric {metric!r} "
                f"on exchange {self.data_exchange} ({self.data_connection})"
            ) from e

    async def _on_data_chunk(self, metric, data_chunk: DataChunk):
        """ Only override this if absolutely necessary for performance """
        last_timed = 0
        zipped_tv = zip(data_chunk.time_delta, data_chunk.value)
        for time_delta, value in zipped_tv:
            last_timed += time_delta
            await self.on_data(metric, Timestamp(last_timed), value)

    @abstractmethod
    async def on_data(self, metric, timestamp, value):
        pass
