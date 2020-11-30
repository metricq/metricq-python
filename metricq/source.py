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
from abc import abstractmethod
from typing import Any, Dict, Optional

import aio_pika
from aiormq import ChannelInvalidStateError

from .agent import PublishFailedError
from .data_client import DataClient
from .datachunk_pb2 import DataChunk
from .logging import get_logger
from .rpc import rpc_handler
from .source_metric import SourceMetric
from .types import Timestamp

logger = get_logger(__name__)

MetadataDict = Dict[str, Any]


class MetricSendError(PublishFailedError):
    """Exception raised when sending a data point for a metric failed.

    The underlying exception is attached as a cause.
    """

    pass


class Source(DataClient):
    """A MetricQ :term:`Source`.

    See :ref:`source-how-to` on how to implement a new Source.

    Example:
        .. code-block::

            from metricq import Source, Timestamp, rpc_handler

            from asyncio import sleep
            from random import randint

            class SomeSensorSource(Source):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

                @rpc_handler("config")
                async def _on_config(self, **config):
                    await self.declare_metrics(["example.some_sensor"])

                async def get_some_sensor_value(self):
                    await sleep(randint(0, 5))
                    return Timestamp.now(), randint(0, 10)

                async def task(self):
                    while True:
                        time, value = await self.get_some_sensor_value()
                        await self.send("example.some_sensor", time, value)

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = dict()
        self._chunk_size: int = 1

    @property
    def chunk_size(self) -> Optional[int]:
        """Number of :term:`data points<Data Point>` collected into a chunk before being sent.

        Initially, this value is set to :code:`1`, so any data point is sent immediately.
        If set to :code:`None`, automatic chunking is disabled and data points must be sent off to the network manually using :meth:`flush`.

        To reduce network and packet overhead, it may be advisable to send multiple data points at once.
        Be aware that there is an `overhead-latency trade-off` to be made:
        If your Source produces one data point every :math:`10` seconds, having a :code:`chunk_size` of :code:`10` means that it takes almost :math:`2` minutes (:math:`100` s) before a chunk is is sent.
        If instead it produces :math:`1000` data points per second, network load can be reduced by setting a value of :code:`1000` without affecting latency too much.
        """
        return None if self._chunk_size == 0 else self._chunk_size

    @chunk_size.setter
    def chunk_size(self, chunk_size: Optional[int]):
        if chunk_size is None:
            self._chunk_size = 0
        else:
            self._chunk_size = chunk_size

    async def connect(self):
        await super().connect()
        response = await self.rpc("source.register")
        assert response is not None
        logger.info("register response: {}", response)
        await self.data_config(**response)

        self.data_exchange = await self.data_channel.declare_exchange(
            name=response["dataExchange"], passive=True
        )

        if "config" in response:
            await self.rpc_dispatch("config", **response["config"])

        self.event_loop.create_task(self.task())

    @abstractmethod
    def task(self):
        """Override this with your main task for generating data points.

        The task is started after the source has connected and received its initial configuration.

        Note:
            This task is not restarted if it fails.
            You are responsible for handling all relevant exceptions.
        """
        pass

    def __getitem__(self, id):
        if id not in self.metrics:
            self.metrics[id] = SourceMetric(id, self, chunk_size=self.chunk_size)
        return self.metrics[id]

    async def declare_metrics(self, metrics: Dict[str, MetadataDict]):
        """Declare a set of :term:`metrics<Metric>` this Source produces values for.

        Before producing :term:`data points<Data Point>` for some metric, a Source must have declared that Metric.

        Args:
            metrics:
                A dictionary mapping metrics to their metadata.
                The metadata is given as a dictionary mapping metadata-keys (strings)
                to arbitrary values.

        Example:
            .. code-block:: python

                from metricq import Source, rpc_handler

                class MySource(Source):

                    ...

                    @rpc_handler("config")
                    async def on_config(self, **config):
                        ...
                        await self.declare_metrics({
                            "example.temperature": {
                                "description": "an example temperature reading"
                                "unit": "C",
                                "rate": config["rate"],
                                "some_arbitrary_metadata": {
                                    "foo": "bar",
                                },
                            },
                        })
        """
        logger.debug("declare_metrics({})", metrics)
        await self.rpc("source.declare_metrics", metrics=metrics)

    async def send(self, metric: str, time: Timestamp, value):
        """Send a :term:`data point<Data Point>` for a Metric.

        Args:
            metric: name of a metric
            timestamp: timepoint at which this metric was measured
            value: value of the metric at time of measurement

        Note:
            Data points are not sent immediately, instead they are collected and sent in chunks.
            See :attr:`chunk_size` how to control chunking behaviour.

        Raises:
            MetricSendError: if sending a data point failed

        Warning:
            In case of failure, unsent data points remain buffered.
            An attempt at sending them is made once :meth:`flush` is triggered,
            either manually or on the next call to :meth:`send`.

            In particular you should not call this method again with the same data point,
            even if the first call failed.
            Otherwise duplicate data points will be sent, which results in an invalid :term:`metric<Metric>`.
        """
        logger.debug("send({},{},{})", metric, time, value)
        metric_object = self[metric]
        assert metric_object is not None
        await metric_object.send(time, value)

    async def flush(self):
        """Flush all unsent data points to the network immediately.

        If automatic chunking is turned off (:attr:`chunk_size` is :literal:`None`),
        use this method to send data points.
        """
        await asyncio.gather(*[m.flush() for m in self.metrics.values() if not m.empty])

    async def _send(self, metric, data_chunk: DataChunk):
        """
        Actual send of a chunk,
        don't call from anywhere other than SourceMetric
        """
        msg = aio_pika.Message(data_chunk.SerializeToString())
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

    @rpc_handler("config")
    async def _source_config(self, **kwargs):
        logger.info("received config {}", kwargs)
