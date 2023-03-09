from collections.abc import Generator
from typing import Optional
from unittest.mock import AsyncMock, call, patch

import pytest

from metricq.source import Source

pytestmark = pytest.mark.asyncio


class _TestSource(Source):
    async def task(self) -> None:
        assert False, "This should not be run"

    rpc: AsyncMock


@pytest.fixture
def source() -> Generator[Source, None, None]:
    with patch("metricq.source.Source.rpc"):
        source = _TestSource(token="source-test", management_url="amqps://test.invalid")
        yield source


def assert_declare_metrics(
    source: _TestSource, metrics: dict[str, dict[str, Optional[int]]]
) -> None:
    assert source.rpc.call_args_list == [
        call("source.declare_metrics", metrics=metrics)
    ]


async def test_source_declare_metrics_augment_chunk_size(source: _TestSource) -> None:
    """Assert that chunkSize is added to metadata when declaring metrics"""
    source.chunk_size = 42
    await source.declare_metrics({"test.foo": {}})

    assert_declare_metrics(source, metrics={"test.foo": {"chunkSize": 42}})


async def test_source_declare_metrics_augment_chunk_size_override(
    source: _TestSource,
) -> None:
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
