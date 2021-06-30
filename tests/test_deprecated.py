"""Test the @deprecated decorator

It should trigger deprecation warnings in both synchronous and asynchronous
contexts.
"""


import pytest

from metricq._deprecation import deprecated


def test_deprecated_decorator():
    @deprecated(reason="use frob instead")
    def foo(bar, *, baz=None):
        assert bar and baz

    with pytest.deprecated_call():
        foo(1, baz=True)


@pytest.mark.asyncio
async def test_deprecated_decorator_async():
    @deprecated(reason="use afrob instead")
    async def async_foo(bar, *, baz=None):
        assert bar and baz

    with pytest.deprecated_call():
        await async_foo(1, baz=True)
