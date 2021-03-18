from unittest.mock import AsyncMock, patch

import pytest

from metricq.interval_source import IntervalSource
from metricq.types import Timedelta

pytestmark = pytest.mark.asyncio


class _TestIntervalSource(IntervalSource):
    async def update(self):
        assert False, "This should not be run"

    rpc: AsyncMock


@pytest.fixture
def interval_source():

    with patch("metricq.interval_source.IntervalSource.rpc"):
        source = _TestIntervalSource(
            token="source-interval-test", management_url="amqps://test.invalid"
        )
        yield source


@pytest.mark.parametrize(
    ("period", "normalized"),
    [
        (Timedelta(1337), Timedelta(1337)),
        (4, Timedelta.from_s(4)),
    ],
)
def test_period_setter_normalizing(
    interval_source: _TestIntervalSource, period, normalized
):
    """Internally, the interval source period is normalized to a Timedelta"""
    assert interval_source.period is None

    interval_source.period = period
    assert interval_source.period == normalized


def test_period_no_reset(interval_source: _TestIntervalSource):
    """Currently, the interval source period cannot be reset to None"""

    with pytest.raises(TypeError):
        # type checking warns you that this is not supported
        interval_source.period = None  # type: ignore
