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

import asyncio
from abc import abstractmethod
from typing import Any, Optional, Union

from .exceptions import PublishFailed
from .logging import get_logger
from .source import Source
from .types import Timedelta, Timestamp

logger = get_logger(__name__)


class IntervalSource(Source):
    """A :term:`Source` producing metrics at regular intervals of time.

    Use an :class:`IntervalSource` if you want to produce data points at a constant rate,
    without having to worry about getting the timing right.
    Put your code producing data points into :meth:`update`, which gets called
    at the specified intervals.

    The :class:`IntervalSource` handles missed deadlines for you:
    If the code in :meth:`update` takes longer than :attr:`period` to execute,
    it will skip the next updates until it caught up, otherwise keeping a
    constant update rate.


    Keyword Args:
        period: time between consecutive updates, in number of seconds or as :class:`Timedelta`

    Example:
        Sending an incrementing counter once a second::

            from metricq import IntervalSource, rpc_handler

            class Counter(IntervalSource):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, period=Timedelta.from_s(1), **kwargs)
                    self.counter = 0

                @rpc_handler("config")
                async def _on_config(self, **_config):
                    await self.declare_metrics(["example.counter"])

                async def update(self):
                    await self.send("example.counter", time=Timestamp.now(), value=self.counter)
                    self.counter += 1
    """

    def __init__(
        self, *args: Any, period: Union[float, Timedelta, None] = None, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self._period: Optional[Timedelta]
        if period is None:
            self._period = None
        else:
            self.period = period  # type: ignore # https://github.com/python/mypy/issues/3004
        self._interval_task_stop_future: Optional[asyncio.Future[None]] = None

    @property
    def period(self) -> Optional[Timedelta]:
        """Time interval at which :meth:`update` is called.

        Initially, this is set to :code:`None`.
        *Must* be set to a :class:`Timedelta` before :meth:`update` is run for the first time.

        To change the update period at a later time, overwrite this value.
        The change will be picked up before :meth:`update` is run the next time.

        Note:
            Setting this value to :code:`None` in application code is *not* supported and will raise a :exc:`TypeError`.
            In particular:

                * Once set, the period *cannot* be reset to :code:`None` to stop the :meth:`update` task.
                * There's no need to initialize this value to :code:`None`,
                  :class:`IntervalSource` takes care of that.

        Exceptions:
            TypeError: if a period-reset is attempted by assigning :code:`None`

        .. versionchanged:: 2.0.0
            Return period as :class:`Timedelta` instead of a number of seconds.
        """
        if self._period is None:
            return None
        return self._period

    @period.setter
    def period(self, duration: Union[float, Timedelta]) -> None:
        if isinstance(duration, Timedelta):
            self._period = duration
        elif duration is None:
            # Raise a descriptive exception if someone tries to reset the period.
            raise TypeError(
                "Setting the IntervalSource update period to None is not supported"
            )
        else:
            self._period = Timedelta.from_s(duration)

    async def task(self) -> None:
        self._interval_task_stop_future = self.event_loop.create_future()
        deadline = Timestamp.now()
        while True:
            try:
                await self.update()
            except PublishFailed as e:
                # This is a "normal" case, when we lost the connection.
                # During the reconnection phase, we need to save the task from
                # being cancelled.
                logger.debug("Failed to send metric value: {}", e)

            try:
                if self._period is None:
                    raise ValueError(
                        "IntervalSource.period not set before running task"
                    )
                deadline += self._period
                now = Timestamp.now()
                while now >= deadline:
                    logger.warn("Missed deadline {}, it is now {}", deadline, now)
                    deadline += self._period

                timeout = (deadline - now).s
                await asyncio.wait_for(
                    asyncio.shield(self._interval_task_stop_future), timeout=timeout
                )
                self._interval_task_stop_future.result()
                logger.info("stopping IntervalSource task")
                break
            except asyncio.TimeoutError:
                # This is the normal case, just continue with the loop
                continue

    async def stop(self, exception: Optional[Exception] = None) -> None:
        logger.debug("stop()")
        if self._interval_task_stop_future is not None:
            self._interval_task_stop_future.set_result(None)
        await super().stop(exception)

    @abstractmethod
    async def update(self) -> None:
        """A user-provided method called at intervals given by :attr:`period`.

        Override this method to produce data points at a constant rate.
        """
