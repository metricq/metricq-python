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

from typing import Optional, Sequence, Union
from .logging import get_logger
from .sink import Sink
import aio_pika
from .datachunk_pb2 import DataChunk

logger = get_logger(__name__)


class Subscriber(Sink):
    def __init__(
        self,
        *args,
        add_uuid=True,
        metrics=[],
        connection_timeout: Union[int, float] = 60,
        **kwargs,
    ):
        super().__init__(
            *args, add_uuid, connection_timeout=connection_timeout, **kwargs
        )
        self._metrics = metrics
        self._timeout = connection_timeout

    def add(self, metric):
        if metric is str:
            self._metrics.append(metric)
        else:
            for m in metric:
                self._metrics.append(m)

    async def connect(self, **kwargs):
        await super().connect()

        if self._data_queue is not None:
            kwargs["dataQueue"] = self._data_queue.name
        response = await self.rpc("sink.subscribe", metrics=self._metrics, **kwargs)

        self._subscribed_metrics.update(self._metrics)
        # Save the subscription RPC args in case we need to resubscribe (after a reconnect).
        self._subscribe_args = kwargs

        return response["dataQueue"]

    @property
    def queue(self):
        return self._data_queue

    async def on_data(self, id, time, value):
        return
