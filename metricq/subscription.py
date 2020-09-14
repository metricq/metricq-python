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

from typing import List

from .client import Client
from .drain import Drain
from .logging import get_logger

logger = get_logger(__name__)


class Subscription(Client):
    def __init__(
        self,
        *args,
        add_uuid=True,
        metrics: List[str],
        **kwargs,
    ):
        """Subscribes to a list of metrics and

        Args:
            add_uuid (bool, optional): If true, it will add a uuid. Defaults to True.
            metrics (List[str], optional): List of metrics that you want to subscribe to. Defaults to [].
            connection_timeout (Union[int, float], optional): Request timeout time. Defaults to 60.
        """
        if not metrics:
            raise ValueError("Metrics list must not be empty")

        super().__init__(*args, add_uuid=add_uuid, **kwargs)
        self._metrics = metrics

        self._args = args
        self._kwargs = kwargs

    async def connect(self, **kwargs) -> None:
        await super().connect()

        response = await self.rpc("sink.subscribe", metrics=self._metrics, **kwargs)

        self.queue = response["dataQueue"]
        await self.stop()

    def drain(self, **kwargs) -> Drain:
        """Returns a fully configured instance of a Drain, by using the given settings used for the subscription.

        Returns:
            Drain: Fully configured instance of a Drain
        """
        new_kwargs = self._kwargs
        new_kwargs.update(kwargs)
        return Drain(*self._args, **new_kwargs, queue=self.queue, metrics=self._metrics)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        pass
