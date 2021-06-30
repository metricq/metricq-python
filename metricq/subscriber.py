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

from typing import List, Union

from .client import Client
from .logging import get_logger
from .drain import Drain

logger = get_logger(__name__)


class Subscriber(Client):
    def __init__(
        self,
        *args,
        add_uuid=True,
        metrics: List[str] = [],
        connection_timeout: Union[int, float] = 60,
        **kwargs,
    ):
        """Subscribes to a list of metrics and

        Args:
            add_uuid (bool, optional): If true, it will add a uuid. Defaults to True.
            metrics (List[str], optional): List of metrics that you want to subscribe to. Defaults to [].
            connection_timeout (Union[int, float], optional): Request timeout time. Defaults to 60.
        """
        super().__init__(
            *args, add_uuid=add_uuid, connection_timeout=connection_timeout, **kwargs
        )
        self._metrics = metrics
        self._timeout = connection_timeout

        self._args = args
        self._kwargs = kwargs

    async def connect(self, **kwargs):
        await super().connect()

        response = await self.rpc("sink.subscribe", metrics=self._metrics, **kwargs)

        self.queue = response["dataQueue"]
        await self.stop()

        return self.queue

    async def simple_drain(self):
        """Returns the incoming data.

        Yields:
            tuple[str, Timestamp, float]: Tuple of the Metric, Timestamp and the Value
        """
        async with Drain(
            *self._args,
            **self._kwargs,
            queue=self.queue,
            metrics=self._metrics
        ) as drain:
            async for metric, time, value in drain:
                yield metric, time, value

                
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args, **kwargs):
        pass