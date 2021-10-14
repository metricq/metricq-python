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

from abc import ABCMeta
from collections import defaultdict
from collections.abc import Awaitable
from typing import Any, Callable, DefaultDict, Dict, List, Optional, Tuple

RPCHandlerType = Callable[..., Optional[Any]]


class RPCMeta(ABCMeta):
    """
    The created classes will have an _rpc_handlers attribute which contains
    lists of handlers for each rpc tag.
    In each list, the base-class rpc handlers will be before the child class ones
    """

    def __new__(
        mcs: type,
        name: str,
        bases: Tuple[type, ...],
        attrs: Dict[Any, Any],
        **kwargs: Any,
    ) -> "RPCMeta":
        rpc_handlers: DefaultDict[str, List[RPCHandlerType]] = defaultdict(list)
        for base in bases:
            try:
                for function_tag, handlers in base._rpc_handlers.items():  # type: ignore
                    rpc_handlers[function_tag] += handlers
            except AttributeError:
                pass

        for handler in attrs.values():
            try:
                function_tags = getattr(handler, "__rpc_tags")
                for function_tag in function_tags:
                    rpc_handlers[function_tag].append(handler)
            except AttributeError:
                # oops, not an rpc handler
                pass

        attrs["_rpc_handlers"] = rpc_handlers
        # Mypy complains about arguments of super(). Seems like this issue:
        # https://github.com/python/mypy/issues/9282
        return super().__new__(mcs, name, bases, attrs)  # type: ignore


class RPCDispatcher(metaclass=RPCMeta):
    _rpc_handlers: DefaultDict[str, List[RPCHandlerType]] = defaultdict(list)

    async def rpc_dispatch(self, function: str, **kwargs: Any) -> Any:
        """Dispatch an incoming (or fake) RPC to all handlers, beginning with the base class handlers

        :meta private:

        Return values are only allowed for unique RPC handlers.
        Only keyword arguments are supported in RPCs.

        Args:
            function: the tag of the function to be called.

        Warning:
            Do not rename the :literal:`function` argument.
            It must be called :literal:`function` because it is called directly with the json dict.

        Raises:
            KeyError: if no corresponding handler is defined.
            TypeError: if a handler is not an class:`Awaitable`.
            TypeError: if multiple handlers are defined that return a :literal:`not None` value.
        """
        if function not in self._rpc_handlers:
            raise KeyError("Missing rpc handler for {}".format(function))

        for handler in self._rpc_handlers[function]:
            task = handler(self, **kwargs)
            if not isinstance(task, Awaitable):
                raise TypeError(
                    "RPC handler for {} is not a coroutine".format(function)
                )
            rv = await task
            if len(self._rpc_handlers[function]) == 1:
                return rv
            elif rv is not None:
                raise TypeError(
                    "multiple RPC handlers attempting to return a non-none value which is not permitted."
                )


def rpc_handler(
    *function_tags: str,
) -> Callable[[RPCHandlerType], RPCHandlerType]:
    """A Decorator to mark an :code:`async` method as an RPC handler

    Arguments:
        function_tags:
            The names of the RPCs that this method should handle

    Example:

        .. code-block:: python

            from metricq import Source, rpc_handler

            class MySource(Source):

                ...

                @rpc_handler("config")
                async def on_config(self, **config):
                    print(f"Received configuration: {config}")

                ...

    Note:
        This only has an effect on methods of classes implementing MetricQ clients (see :class:`Client`),
        i.e. :class:`Sink`, :class:`Source`, :class:`IntervalSource`, :class:`HistoryClient`, etc.
    """

    def decorator(handler: RPCHandlerType) -> RPCHandlerType:
        setattr(handler, "__rpc_tags", function_tags)
        return handler

    return decorator
