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

import math
from typing import Any, Optional, cast

from . import source
from .datachunk_pb2 import DataChunk
from .types import Metric, Timestamp


class ChunkSize:
    def __set_name__(self, owner: Any, name: str) -> None:
        self._field_name = f"_{name}"

    def __get__(self, instance: "SourceMetric", cls: Optional[type] = None) -> int:
        return cast(int, getattr(instance, self._field_name))

    def __set__(self, instance: "SourceMetric", chunk_size: Optional[int]) -> None:
        if chunk_size is not None:
            if not isinstance(chunk_size, int):
                raise TypeError("chunk_size must be `None` or a positive integer")
            if not chunk_size >= 1:
                raise ValueError(f"chunk_size must be at least 1 ({chunk_size} < 1)")

        setattr(instance, self._field_name, chunk_size)


class SourceMetric:
    chunk_size = ChunkSize()
    """Chunk size of this metric.

    If set to :literal:`None`, chunking is disabled.
    See :attr:`Source.chunk_size` for more information.
    """

    def __init__(
        self, id: Metric, source: "source.Source", chunk_size: Optional[int] = 1
    ):
        self.id = id
        self.source = source

        self.chunk_size = chunk_size
        self.previous_timestamp = 0
        self.chunk = DataChunk()

    def append(self, time: Timestamp, value: float) -> None:
        """
        Like send, but synchronous and will never flush
        """
        timestamp = time.posix_ns
        self.chunk.time_delta.append(timestamp - self.previous_timestamp)
        self.previous_timestamp = timestamp
        self.chunk.value.append(value)

        assert len(self.chunk.time_delta) == len(self.chunk.value)

    async def send(self, time: Timestamp, value: float) -> None:
        self.append(time, value)

        if self.chunk_size is None:
            return  # Chunking is disabled

        if self.chunk_size <= len(self.chunk.time_delta):
            await self.flush()

    async def error(self, time: Timestamp) -> None:
        await self.send(time, math.nan)

    @property
    def empty(self) -> bool:
        assert len(self.chunk.time_delta) == len(self.chunk.value)
        return len(self.chunk.time_delta) == 0

    async def flush(self) -> None:
        assert len(self.chunk.time_delta) == len(self.chunk.value)
        if len(self.chunk.time_delta) == 0:
            return

        await self.source._send(self.id, self.chunk)
        del self.chunk.time_delta[:]
        del self.chunk.value[:]
        self.previous_timestamp = 0
