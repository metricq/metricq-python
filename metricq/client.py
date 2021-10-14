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

from socket import gethostname
from sys import version_info as sys_version
from typing import Any, Dict, Optional, Sequence, Union, cast

from .agent import Agent
from .logging import get_logger
from .rpc import rpc_handler
from .types import JsonDict, Timestamp
from .version import __version__

logger = get_logger(__name__)


_GetMetricsResult = Union[Sequence[str], Sequence[Dict[str, Any]]]


class Client(Agent):
    def __init__(self, *args: Any, client_version: Optional[str] = None, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.starting_time = Timestamp.now()
        self._client_version: Optional[str] = (
            client_version if client_version is not None else self._find_version()
        )

        logger.info(
            "Initializing client (version: {})", self._client_version or "unknown"
        )

    def _find_version(self) -> Optional[str]:
        client_cls = type(self)
        client_name = client_cls.__qualname__

        try:
            from inspect import getmodule

            logger.debug(
                "Looking for client version of {}...",
                client_name,
            )

            # We can ignore the undefined attribute error here as we check for exceptions anyway
            client_version = cast(str, getmodule(client_cls).__version__)  # type: ignore[union-attr]

            logger.debug("Client {} has version {!r}", client_name, client_version)

            return client_version
        except Exception as e:
            logger.warning("Failed to find version of {}: {}", client_name, e)
            return None

    @property
    def name(self) -> str:
        return "client-" + self.token

    async def connect(self) -> None:
        await super().connect()

        assert self._management_channel is not None

        self._management_broadcast_exchange = (
            await self._management_channel.declare_exchange(
                name=self._management_broadcast_exchange_name, passive=True
            )
        )

        self._management_exchange = await self._management_channel.declare_exchange(
            name=self._management_exchange_name, passive=True
        )

        assert self.management_rpc_queue is not None
        await self.management_rpc_queue.bind(
            exchange=self._management_broadcast_exchange, routing_key="#"
        )

        await self.rpc_consume()

    # The superclass has extra parameters, which we fill in in the overloads of the subclasses.
    # So this is fine! But mypy complains and we carefully considered the feedback.
    async def rpc(  # type: ignore
        self, function: str, *args: Any, **kwargs: Any
    ) -> Optional[JsonDict]:
        """Invoke an RPC on the management exchange

        Args:
            function:
                Name of the RPC to invoke
            kwargs:
                Additional arguments are forwarded to :meth:`Agent.rpc`.

                :code:`exchange`, :code:`routing_key`, and :code:`cleanup_on_response`
                are not allowed in :code:`kwargs`.

                Note:
                    Argument names are required to be in :literal:`"javaScriptSnakeCase"`.

        Raises:
            PublishFailed: if the RPC could not be published
            RPCError: if the remote returns an error
        """
        logger.debug("Waiting for management connection to be reestablished...")
        await self._management_connection_watchdog.established()
        assert self._management_exchange is not None
        return await super().rpc(
            function=function,
            exchange=self._management_exchange,
            routing_key=function,
            cleanup_on_response=True,
            **kwargs,
        )

    @rpc_handler("discover")
    async def _on_discover(self, **kwargs: Any) -> JsonDict:
        logger.info("responding to discover")
        now = Timestamp.now()
        uptime: int = (now - self.starting_time).ns

        response = {
            "alive": True,
            "currentTime": now.datetime.isoformat(),
            "startingTime": self.starting_time.datetime.isoformat(),
            "uptime": uptime,
            "metricqVersion": f"metricq-python/{__version__}",
            "pythonVersion": f"{sys_version.major}.{sys_version.minor}.{sys_version.micro}",
            "hostname": gethostname(),
        }

        if self._client_version is not None:
            response["version"] = self._client_version

        return response

    async def get_metrics(
        self,
        selector: Union[str, Sequence[str], None] = None,
        metadata: bool = True,
        historic: Optional[bool] = None,
        timeout: Optional[float] = None,
        prefix: Optional[str] = None,
        infix: Optional[str] = None,
        limit: Optional[int] = None,
        hidden: Optional[bool] = None,
    ) -> _GetMetricsResult:
        """Retrieve information for metrics matching a selector pattern.

        Args:
            selector:
                Either:

                * a regex matching parts of the metric name
                * a sequence of metric names
            historic:
                Only include metrics with the :literal:`historic` flag set.
            metadata:
                If true, include metric metadata in the response.
            timeout:
                Operation timeout in seconds.
            prefix:
                Filter results by prefix on the key.
            infix:
                Filter results by infix on the key.
            limit:
                Maximum number of matches to return.
            hidden:
                Only include metrics where :literal:`hidden` is :literal:`True`/:literal:`False`. If not set return all
                matching metrics.

        Returns:
            *
                a dictionary mapping matching metric names to their
                :ref:`metadata<metric-metadata>` (if :code:`metadata=True`)
            * otherwise, a sequence of matching metric names
        """
        arguments: Dict[str, Any] = {"format": "object" if metadata else "array"}
        if selector is not None:
            arguments["selector"] = selector
        if timeout is not None:
            arguments["timeout"] = timeout
        if historic is not None:
            arguments["historic"] = historic
        if prefix is not None:
            arguments["prefix"] = prefix
        if infix is not None:
            arguments["infix"] = infix
        if limit is not None:
            arguments["limit"] = limit
        if hidden is not None:
            arguments["hidden"] = hidden

        # Note: checks are done in the manager (e.g. must not have prefix and historic/selector at the same time)

        result = await self.rpc("get_metrics", **arguments)
        assert result is not None
        return cast(_GetMetricsResult, result["metrics"])
