from math import isnan
from typing import Any, Generator, Optional, cast
from unittest.mock import AsyncMock, create_autospec

import pytest

from metricq import Timedelta, Timestamp
from metricq.datachunk_pb2 import DataChunk
from metricq.source import Source
from metricq.source_metric import ChunkSize, SourceMetric

pytestmark = pytest.mark.asyncio


_Metric = Generator[tuple[Timestamp, float], None, None]


@pytest.fixture(scope="module")
def metric() -> _Metric:
    def _metric() -> _Metric:
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
def test_chunk_size_valid(chunk_size: Optional[int], chunked: SourceMetric) -> None:
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
def test_chunk_size_invalid(
    chunked: _Chunked, invalid: Any, exc_type: type[Exception]
) -> None:
    with pytest.raises(exc_type):
        # this test pushes invalid type, hence the ignore
        chunked.chunk_size = invalid  # type: ignore


@pytest.fixture
def source() -> Source:
    source = create_autospec(Source, spec_set=True)
    return cast(Source, source)


@pytest.fixture
def source_metric(source: Source) -> SourceMetric:
    return SourceMetric(id="test.metric", source=source)


def test_source_metric_chunk_size_invalid(source: Source) -> None:
    with pytest.raises(ValueError):
        SourceMetric("test.foo", source=source, chunk_size=0)


def test_source_metric_empty_after_init(source: Source) -> None:
    source_metric = SourceMetric(id="test.metric", source=source)

    assert source_metric.empty


async def test_source_metric_default_send_immediately(
    source_metric: SourceMetric, metric: _Metric
) -> None:
    await source_metric.send(*next(metric))

    # the actual source is a mocked object, hence mypy sad.
    source_metric.source._send.assert_called_once()  # type: ignore


async def test_source_metric_no_send_if_empty(source_metric: SourceMetric) -> None:
    assert source_metric.empty

    await source_metric.flush()

    # the actual source is a mocked object, hence mypy sad.
    assert not source_metric.source._send.called  # type: ignore


async def test_source_metric_send_chunked(
    source_metric: SourceMetric, metric: _Metric
) -> None:
    source_metric.chunk_size = 2

    await source_metric.send(*next(metric))
    # the actual source is a mocked object, hence mypy sad.
    assert not source_metric.source._send.called  # type: ignore

    await source_metric.send(*next(metric))
    # the actual source is a mocked object, hence mypy sad.
    assert source_metric.source._send.called  # type: ignore
    assert source_metric.empty

    await source_metric.send(*next(metric))
    # the actual source is a mocked object, hence mypy sad.
    assert len(source_metric.source._send.mock_calls) == 1  # type: ignore


async def test_source_send_no_chunking(
    source_metric: SourceMetric, metric: _Metric
) -> None:
    source_metric.chunk_size = None

    for _ in range(50):
        await source_metric.send(*next(metric))

    assert not source_metric.source._send.called  # type: ignore

    chunk = source_metric.chunk
    assert len(chunk.time_delta) == 50
    assert len(chunk.value) == 50

    await source_metric.flush()

    assert source_metric.empty
    source_metric.source._send.assert_called_once_with(source_metric.id, chunk)  # type: ignore


async def test_source_send_error_value_is_none(source_metric: SourceMetric) -> None:
    async def send(metric: SourceMetric, chunk: DataChunk) -> None:
        assert len(chunk.value) == 1 and isnan(chunk.value[0])

    # Replace the send call by a mock and inspect it there.  We cannot inspect
    # the chunk from mock_calls after the call to error since the chunk will
    # have been reset already, so it would always be empty.
    source_metric.source.attach_mock(AsyncMock(side_effect=send), "_send")  # type: ignore

    await source_metric.error(Timestamp(0))
