import asyncio
from collections.abc import Iterator
from unittest.mock import AsyncMock, patch

import pytest

from metricq import Sink
from metricq.timeseries import Metric, Timestamp

pytestmark = pytest.mark.asyncio


class _TestSink(Sink):
    async def on_data(
        self, metric: Metric, timestamp: Timestamp, value: float
    ) -> None:
        pass

    rpc: AsyncMock


@pytest.fixture
def sink() -> Iterator[_TestSink]:
    with patch("metricq.sink.Sink.rpc"):
        sink = _TestSink(token="sink-test", url="amqps://test.invalid")
        sink._data_queue = AsyncMock(name="fake-data-queue")
        sink._data_queue.name = "sink-test-data"
        sink._resubscribe_retry_delay = 0
        yield sink


async def test_resubscribe_retries_after_failed_rpc(sink: _TestSink) -> None:
    """A sink.subscribe RPC failure (e.g. a Nack during cluster instability)
    must not leave the sink permanently unsubscribed -- it should be retried
    until it succeeds."""
    sink.rpc.side_effect = [
        Exception("boom"),
        Exception("boom again"),
        {"dataQueue": "sink-test-data"},
    ]

    with patch.object(sink, "_declare_data_queue", AsyncMock()) as declare_queue:
        await sink._resubscribe(connection=None)  # type: ignore[arg-type]

    assert sink.rpc.await_count == 3
    declare_queue.assert_awaited_once_with("sink-test-data")
    assert sink._data_queue is not None
    sink._data_queue.consume.assert_awaited_once()  # type: ignore[attr-defined]


async def test_resubscribe_cancellation_is_not_swallowed(sink: _TestSink) -> None:
    """Cancelling the resubscribe task (e.g. because the connection dropped
    again) must still propagate as CancelledError, not be treated as just
    another retryable failure."""
    sink._resubscribe_retry_delay = 100
    sink.rpc.side_effect = Exception("boom")

    task: "asyncio.Task[None]" = asyncio.ensure_future(
        sink._resubscribe(connection=None)  # type: ignore[arg-type]
    )
    await asyncio.sleep(0)  # let it reach the sleep() between retries
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task
