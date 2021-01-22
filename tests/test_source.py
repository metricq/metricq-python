from typing import Type
from unittest.mock import AsyncMock, call, patch

import pytest

from metricq.source import Source
from metricq.source_metric import SourceMetric

pytestmark = pytest.mark.asyncio


class _TestSource(Source):
    async def task(self):
        assert False, "This should not be run"

    rpc: AsyncMock


@pytest.fixture
def source():

    with patch("metricq.source.Source.rpc"):
        source = _TestSource(token="source-test", management_url="amqps://test.invalid")
        yield source


def test_source_metric_chunk_size_invalid(source):
    with pytest.raises(ValueError):
        SourceMetric("test.foo", source=source, chunk_size=0)


@pytest.mark.parametrize(
    "chunk_size",
    [1, 42, None],
)
def test_chunk_size_valid(source: _TestSource, chunk_size):
    source.chunk_size = chunk_size
    assert source.chunk_size == chunk_size


@pytest.mark.parametrize(
    ("invalid", "exc_type"),
    [
        (0, ValueError),
        (-1, ValueError),
        (4.2, TypeError),
        ("2", TypeError),
    ],
)
def test_chunk_size_invalid(source: _TestSource, invalid, exc_type: Type[Exception]):
    with pytest.raises(exc_type):
        source.chunk_size = invalid
