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

from inspect import Traceback
from typing import Any, List, Optional, Union

from .client import Client
from .drain import Drain
from .logging import get_logger
from .types import Timedelta

logger = get_logger(__name__)


class Subscriber(Client):
    def __init__(
        self,
        *args: Any,
        expires: Union[Timedelta, int, float],
        metrics: List[str],
        **kwargs: Any,
    ):
        """Subscribes to a list of metrics

        Args:
            metrics (List[str], optional): List of metrics that you want to subscribe to.
            expires (Union[Timedelta, int, float]): The lifetime of the subscription queue in seconds.
        """
        if not metrics:
            raise ValueError("Metrics list must not be empty")

        super().__init__(*args, **kwargs)
        self._metrics = metrics

        if isinstance(expires, Timedelta):
            self.expires = expires
        else:
            self.expires = Timedelta.from_s(expires)

        if self.expires < Timedelta(0) or self.expires == Timedelta(0):
            raise ValueError("expires must be greater than zero")

        self._args = args
        self._kwargs = kwargs

        self.queue: Optional[str] = None
        """The name of the queue that is used to buffer the subscribed data

        This is only set after :meth:`.connect()` has finished.
        """

    async def connect(self, **kwargs: Any) -> None:
        """Connects to the MetricQ network, sends the subscribe request, and disconnects again.

        After it has successfully finished, the :attr:`.queue` name is set.

        .. note::

            This performes the RPC and closes the connection before the return.

        """

        await super().connect()

        response = await self.rpc(
            "sink.subscribe", metrics=self._metrics, expires=self.expires, **kwargs
        )

        assert response is not None
        self.queue = response["dataQueue"]
        await self.stop()

    def drain(self, **kwargs: Any) -> Drain:
        """Returns a fully configured instance of a Drain, by using the given settings used for the subscription.

        As the Drain is a context manager, you should use the result of this in a `with`-statement::

            async with subscriber.drain() as data:
                async for metric, time, value in data:
                    # ... process metric data

        Must only be called after :meth:`connect()` has finished successfully.

        Returns:
            Drain: Fully configured instance of a Drain
        """
        assert self.queue is not None

        new_kwargs = self._kwargs
        new_kwargs.update(kwargs)
        return Drain(*self._args, **new_kwargs, queue=self.queue, metrics=self._metrics)

    async def __aenter__(self) -> "Subscriber":
        """Allows to use the Subscriber as a context manager.

        The connection to MetricQ will automatically established and closed.

        Use it like this::

            async with Subscriber(...) as subscriber:
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
        pass
