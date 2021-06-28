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

import asyncio
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
        self._queue = queue
        self._metrics = metrics

        self.data: dict[str, tuple] = {}
        for m in self._metrics:
            self.data[m] = []

    async def connect(self):
        await super().connect()
        assert len(self._metrics) > 0

        response = await self.rpc("sink.unsubscribe", dataQueue=self._queue, metrics=self._metrics)

        assert len(self._queue) > 0
        await self.sink_config(**response)

    async def _on_data_message(self, message: aio_pika.IncomingMessage):

        if message.type == "end":
            with message.process():
                logger.debug("received end message")
                await self.rpc("sink.release", dataQueue=self._queue)
                asyncio.create_task(self.stop())
                return

        await super()._on_data_message(message)

    async def on_data(self, metric: str, time: Timestamp, value):
        self.data[metric].append((time, value))
