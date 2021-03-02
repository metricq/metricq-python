from math import isnan
from typing import Generator, Tuple, Type
from unittest.mock import AsyncMock, create_autospec

import pytest

from metricq.datachunk_pb2 import DataChunk
from metricq.source import Source
from metricq.source_metric import ChunkSize, SourceMetric
from metricq.types import Timedelta, Timestamp

pytestmark = pytest.mark.asyncio


_Metric = Generator[Tuple[Timestamp, float], None, None]


@pytest.fixture(scope="module")
def metric() -> _Metric:
    def _metric():
        timestamp = Timestamp(0)
        delta = Timedelta.from_s(1)
        value = 0.0

        while True:
            yield (timestamp, value)
            timestamp += delta
            value += 1.0

    return _metric()


class _Chunked:
    chunk_size = ChunkSize()


@pytest.fixture
def chunked() -> _Chunked:
    return _Chunked()


@pytest.mark.parametrize(
    "chunk_size",
    [1, 42, None],
)
def test_chunk_size_valid(chunk_size, chunked):
    chunked.chunk_size = chunk_size
    assert chunked.chunk_size == chunk_size


@pytest.mark.parametrize(
    ("invalid", "exc_type"),
    [
        (0, ValueError),
        (-1, ValueError),
        (4.2, TypeError),
        ("2", TypeError),
    ],
)
def test_chunk_size_invalid(chunked: _Chunked, invalid, exc_type: Type[Exception]):
    with pytest.raises(exc_type):
        chunked.chunk_size = invalid


@pytest.fixture
def source():
    source = create_autospec(Source, spec_set=True)
    return source


@pytest.fixture
def source_metric(source):
    return SourceMetric(id="test.metric", source=source)


def test_source_metric_chunk_size_invalid(source):
    with pytest.raises(ValueError):
        SourceMetric("test.foo", source=source, chunk_size=0)


def test_source_metric_empty_after_init(source):
    source_metric = SourceMetric(id="test.metric", source=source)

    assert source_metric.empty


async def test_source_metric_default_send_immediately(
    source_metric: SourceMetric, metric: _Metric
):
    await source_metric.send(*next(metric))

    source_metric.source._send.assert_called_once()


async def test_source_metric_no_send_if_empty(source_metric: SourceMetric):
    assert source_metric.empty

    await source_metric.flush()

    assert not source_metric.source._send.called


async def test_source_metric_send_chunked(source_metric: SourceMetric, metric: _Metric):
    source_metric.chunk_size = 2

    await source_metric.send(*next(metric))
    assert not source_metric.source._send.called

    await source_metric.send(*next(metric))
    assert source_metric.source._send.called
    assert source_metric.empty

    await source_metric.send(*next(metric))
    assert len(source_metric.source._send.mock_calls) == 1


async def test_source_send_no_chunking(source_metric: SourceMetric, metric: _Metric):
    source_metric.chunk_size = None

    for _ in range(50):
        await source_metric.send(*next(metric))

    assert not source_metric.source._send.called

    chunk = source_metric.chunk
    assert len(chunk.time_delta) == 50
    assert len(chunk.value) == 50

    await source_metric.flush()

    assert source_metric.empty
    source_metric.source._send.assert_called_once_with(source_metric.id, chunk)


async def test_source_send_error_value_is_none(source_metric: SourceMetric):
    async def send(metric, chunk: DataChunk):
        assert len(chunk.value) == 1 and isnan(chunk.value[0])

    # Replace the send call by a mock and inspect it there.  We cannot inspect
    # the chunk from mock_calls after the call to error since the chunk will
    # have been reset already, so it would always be empty.
    source_metric.source.attach_mock(AsyncMock(side_effect=send), "_send")

    await source_metric.error(Timestamp(0))
