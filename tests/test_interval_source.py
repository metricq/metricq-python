from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest

from metricq.interval_source import IntervalSource
from metricq.types import Timedelta

pytestmark = pytest.mark.asyncio


class _TestIntervalSource(IntervalSource):
    async def update(self) -> None:
        assert False, "This should not be run"

    rpc: AsyncMock


@pytest.fixture
def interval_source() -> Generator[IntervalSource, None, None]:

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
    interval_source: _TestIntervalSource, period: Timedelta, normalized: Timedelta
) -> None:
    """Internally, the interval source period is normalized to a Timedelta"""
    assert interval_source.period is None

    interval_source.period = period
    assert interval_source.period == normalized


def test_period_no_reset(interval_source: _TestIntervalSource) -> None:
    """Currently, the interval source period cannot be reset to None"""

    with pytest.raises(TypeError, match=r"Setting .* to None is not supported"):
        interval_source.period = None


def test_period_no_explicit_init() -> None:
    """Some clients were explicitly initializing the update period to None.
    *Don't do that.*

    Make sure that ignoring this advise raises a TypeError.
    """
    with patch("metricq.interval_source.IntervalSource.rpc"):

        class _FaultySource(_TestIntervalSource):
            def __init__(self) -> None:
                super().__init__(
                    token="source-interval-test", management_url="amqps://test.invalid"
                )

                self.period = None

        with pytest.raises(TypeError, match=r"Setting .* to None is not supported"):
            _FaultySource()