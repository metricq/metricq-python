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


def assert_declare_metrics(source: _TestSource, metrics):
    assert source.rpc.call_args_list == [
        call("source.declare_metrics", metrics=metrics)
    ]


async def test_source_declare_metrics_augment_chunk_size(source: _TestSource):
    """Assert that chunkSize is added to metadata when declaring metrics"""
    source.chunk_size = 42
    await source.declare_metrics({"test.foo": {}})

    assert_declare_metrics(source, metrics={"test.foo": {"chunkSize": 42}})


async def test_source_declare_metrics_augment_chunk_size_override(source: _TestSource):
    """Assert that chunkSize in metadata can be overridden per-metric"""

    source["test.chunk-size.override"].chunk_size = 1337
    source["test.chunk-size.disabled"].chunk_size = None

    await source.declare_metrics(
        {
            # Use default chunk size (Source.chunk_size)
            "test.chunk-size.default": {},
            # Override with value set on SourceMetric
            "test.chunk-size.override": {},
            # Override with an explicitly provided metadata key
            "test.chunk-size.override-explicit": {"chunkSize": 99},
            # A SourceMetric with chunking disabled (chunk_size=0) sets chunkSize=None
            "test.chunk-size.disabled": {},
        }
    )

    assert_declare_metrics(
        source,
        metrics={
            "test.chunk-size.default": {"chunkSize": source.chunk_size},
            "test.chunk-size.override": {"chunkSize": 1337},
            "test.chunk-size.override-explicit": {"chunkSize": 99},
            "test.chunk-size.disabled": {"chunkSize": None},
        },
    )
