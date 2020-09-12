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
import pytest

from metricq.rpc import RPCDispatcher, rpc_handler


class SimpleDispatcher(RPCDispatcher):
    def __init__(self, number):
        self.number = number

    @rpc_handler("number")
    async def handle_number(self):
        return self.number

    @rpc_handler("repeat")
    async def handle_repeat(self, name):
        return self.number * name


class SubDispatcher(SimpleDispatcher):
    @rpc_handler("sub_double_number")
    async def handle_sub_double_number(self):
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
async def test_dispatch_simple(number: int, function: str, kwargs: dict, result):
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
async def test_dispatch_sub(function: str, kwargs: dict, result):
    assert await SubDispatcher(3).rpc_dispatch(function, **kwargs) == result


class UnknownFunctionDispatcher(RPCDispatcher):
    pass


@pytest.mark.asyncio
async def test_dispatch_unknown_function():
    with pytest.raises(KeyError):
        await UnknownFunctionDispatcher().rpc_dispatch("unknown")
