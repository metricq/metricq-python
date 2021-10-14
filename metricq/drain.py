# Copyright (c) 2021, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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
from inspect import Traceback
from typing import Any, List, Optional, Tuple, cast

import aio_pika

from .logging import get_logger
from .sink import Sink
from .types import Timestamp

logger = get_logger(__name__)


class Drain(Sink):
    def __init__(self, *args: Any, queue: str, metrics: List[str], **kwargs: Any):
        """Drain the given queue of all buffered metric data

        Args:
            queue: The name of the queue that contains the subscribed data.
            metrics: List of metrics that you want to subscribe to.
        """
        super().__init__(*args, add_uuid=True, **kwargs)
        if not metrics:
            raise ValueError("Metrics list must not be empty")
        if not queue:
            raise ValueError("Queue must not be empty")
        self._queue = queue
        self._metrics = metrics

        self._data: asyncio.Queue[Tuple[str, Timestamp, float]] = asyncio.Queue()

    async def connect(self) -> None:
        await super().connect()
        assert len(self._metrics) > 0

        response = await self.rpc(
            "sink.unsubscribe", dataQueue=self._queue, metrics=self._metrics
        )

        assert response is not None
        assert len(self._queue) > 0
        await self.sink_config(**response)

    async def _on_data_message(self, message: aio_pika.IncomingMessage) -> None:
        if message.type == "end":
            async with message.process():
                logger.debug("received end message")
                await self.rpc("sink.release", dataQueue=self._queue)
                asyncio.create_task(self.stop())
                await self._data.put(cast(Tuple[str, Timestamp, float], ()))

                return

        await super()._on_data_message(message)

    async def on_data(self, metric: str, time: Timestamp, value: float) -> None:
        await self._data.put((metric, time, value))

    async def __aenter__(self) -> "Drain":
        """Allows to use the Drain as a context manager.

        The connection to MetricQ will automatically established and closed.

        Use it like this::

            async with Drain(...) as drain:
                pass

        """

        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[Traceback],
    ) -> None:
        await self.stopped()

    def __aiter__(self) -> "Drain":
        """Allows to asynchronously iterate over all metric data as it gets received.

        Use it like this::

            async for metric, time, value in my_drain:
                pass

        """
        return self

    async def __anext__(self) -> Tuple[str, Timestamp, float]:
        try:
            metric, time, value = await self._data.get()
        except ValueError:
            # Value Error is part of control flow
            # -> raised on empty tuple at the end, inserted with the end message
            raise StopAsyncIteration()
        return metric, time, value
