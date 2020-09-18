# Copyright (c) 2020, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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

from .types import Timestamp
from .logging import get_logger
from .sink import Sink
import aio_pika
from .datachunk_pb2 import DataChunk

logger = get_logger(__name__)


class DataError(Exception):
    pass


class Drain(Sink):
    def __init__(self, *args, queue, metrics=[], **kwargs):
        super().__init__(*args, add_uuid=True, **kwargs)
        if len(queue) == 0:
            raise DataError("Queue must not be empty")
        self._metrics_queue = queue
        self._metrics = metrics

    def add(self, metric):
        if metric is str:
            self._metrics.append(metric)
        else:
            for m in metric:
                self._metrics.append(m)

    async def connect(self):
        await super().connect()
        assert len(self._metrics) > 0

        response = await self.rpc(
            "sink.unsubscribe", data_queue=self._metrics_queue, metrics=self._metrics
        )
        assert len(self._metrics_queue) > 0
        self.sink_config(response)

    async def _on_metrics_message(
        self, message: aio_pika.IncomingMessage
    ):  # keine Refs gefunden!!!!

        if message.type == "end":
            with message.process():
                logger.debug("received end message")
                await self.rpc("sink.release", dataQueue=self._metrics_queue)
                return

        await super()._on_metrics_message(message)


class SimpleDrain(Drain):
    def __init__(self, *args, queue, **kwargs):
        super().__init__(*args, queue=queue, **kwargs)
        self._metrics_data = {}

    def get(self):
        return self._metrics_data

    def at(self, metric):
        return self._metrics_data[metric]

    async def on_data(self, metric: str, time: Timestamp, value):
        self._metrics_data[metric].append((time, value))

    async def connect(self):
        await super().connect()
        for m in self._metrics:
            self._metrics_data[m] = []
