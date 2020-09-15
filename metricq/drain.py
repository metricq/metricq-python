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

from .logging import get_logger
from .sink import Sink
import aio_pika
from .datachunk_pb2 import DataChunk

logger = get_logger(__name__)


class Drain(Sink):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, True, **kwargs)
        self._data_queue = queue
        self._metrics = []

    def add(self, metric):
        if metric is str:
            self._metrics.append(metric)
        else:
            for m in metric:
                self._metrics.append(m)

    async def _on_connected(self):
        assert self._metrics.count() > 0

        response = await self.rpc(
            "sink.unsubscribe", data_queue=self._data_queue, metrics=self._metrics
        )
        self._unsubscribe_complete(response)
        assert self._data_queue.count() > 0

    def _unsubscribe_complete(self, response):
        assert not self._data_queue.empty()
        self.sink_config(response)

    async def _on_data_message(self, message: aio_pika.IncomingMessage):

        if message.type() == "end":  # idk if this is correct
            self.data_channel.channel.basic_ack(message.delivery_tag)
            logger.debug("received end message")
            await self.rpc("sink.release", data_queue=self._data_queue)
            return

        super()._on_data_message(message)


class SimpleDrain(Drain):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(queue, *args, **kwargs)
        self._data = {}

    def get(self):
        return self._data

    def at(self, metric):
        return self._data[metric]

    def on_data(self, id: str, chunk: DataChunk):
        for tv in chunk:
            self._data[id].append(tv)

    def _on_connected(self):
        super()._on_connected()
        for m in self._metrics:
            self._data[m] = []
