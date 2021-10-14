# Copyright (c) 2020, ZIH,
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
import logging
from typing import Any, Dict, Tuple

import pytest

from metricq.rpc import RPCDispatcher, rpc_handler


class SimpleDispatcher(RPCDispatcher):
    def __init__(self, number: int) -> None:
        self.number = number

    @rpc_handler("number")
    async def handle_number(self) -> int:
        return self.number

    @rpc_handler("repeat")
    async def handle_repeat(self, name: str) -> str:
        return self.number * name


class SubDispatcher(SimpleDispatcher):
    @rpc_handler("sub_double_number")
    async def handle_sub_double_number(self) -> float:
        return self.number * 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "number, function, kwargs, result",
    [
        (1, "number", {}, 1),
        (2, "number", {}, 2),
        (1, "repeat", {"name": "foo"}, "foo"),
        (2, "repeat", {"name": "foo"}, "foofoo"),
    ],
)
async def test_dispatch_simple(
    number: int, function: str, kwargs: Dict[Any, Any], result: str
) -> None:
    assert await SimpleDispatcher(number).rpc_dispatch(function, **kwargs) == result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "function, kwargs, result",
    [
        ("number", {}, 3),
        ("repeat", {"name": "foo"}, "foofoofoo"),
        ("sub_double_number", {}, 6),
    ],
)
async def test_dispatch_sub(function: str, kwargs: Dict[Any, Any], result: str) -> None:
    assert await SubDispatcher(3).rpc_dispatch(function, **kwargs) == result


class UnknownFunctionDispatcher(RPCDispatcher):
    pass


@pytest.mark.asyncio
async def test_dispatch_unknown_function() -> None:
    with pytest.raises(KeyError):
        await UnknownFunctionDispatcher().rpc_dispatch("unknown")


class InvalidDispatcher:
    @rpc_handler("not_async")
    def not_async(self) -> Tuple[()]:
        return ()


class DuplicateHandlersDispatcher(RPCDispatcher):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    @rpc_handler("duplicate_no_conflict")
    async def no_conflict_1(self) -> None:
        self.logger.info("no_conflict_1")
        return None

    @rpc_handler("duplicate_no_conflict")
    async def no_conflict_2(self) -> None:
        self.logger.info("no_conflict_2")
        return None

    @rpc_handler("duplicate_conflict")
    async def conflict1(self) -> int:
        return 1

    @rpc_handler("duplicate_conflict")
    async def conflict2(self) -> int:
        return 2


@pytest.fixture
def duplicate_handlers_dispatcher() -> DuplicateHandlersDispatcher:
    return DuplicateHandlersDispatcher()


@pytest.mark.asyncio
async def test_dispatch_multiple_handlers_no_return_value(
    caplog: pytest.LogCaptureFixture,
    duplicate_handlers_dispatcher: DuplicateHandlersDispatcher,
) -> None:
    """An RPCDispatcher is allowed to register multiple handlers for the same
    function, as long as they all return None."""
    caplog.set_level(logging.INFO)

    assert (
        await duplicate_handlers_dispatcher.rpc_dispatch("duplicate_no_conflict")
    ) is None

    # Check that both handlers ran.
    assert "no_conflict_1" in caplog.text
    assert "no_conflict_2" in caplog.text


@pytest.mark.asyncio
async def test_dispatch_no_multiple_handlers_with_return_values(
    duplicate_handlers_dispatcher: DuplicateHandlersDispatcher,
) -> None:
    """Test the negative of :func:`test_dispatch_multiple_handlers_no_return_value`.

    An RPCDispatcher may not register multiple handlers for the same function if
    at least one of them returns a non-None value.
    """
    with pytest.raises(TypeError):
        await duplicate_handlers_dispatcher.rpc_dispatch("duplicate_conflict")
