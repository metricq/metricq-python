from logging import getLogger
from math import isclose
from random import Random
from typing import Generator, List, Union

import pytest

from metricq.exceptions import NonMonotonicTimestamps
from metricq.types import TimeAggregate, Timedelta, Timestamp

logger = getLogger(__name__)


@pytest.fixture
def timestamp() -> Timestamp:
    return Timestamp.from_iso8601("2021-03-03T18:00:00Z")


@pytest.fixture
def time_delta_random() -> Timedelta:
    return Timedelta(8295638928)


@pytest.fixture
def time_delta_1us() -> Timedelta:
    return Timedelta(1_000)


@pytest.fixture
def time_delta_1ms() -> Timedelta:
    return Timedelta(1_000_000)


@pytest.fixture
def time_delta_1s() -> Timedelta:
    return Timedelta(1_000_000_000)


@pytest.fixture
def time_delta_10s() -> Timedelta:
    return Timedelta(10_000_000_000)


@pytest.fixture
def time_delta_1min() -> Timedelta:
    return Timedelta(1_000_000_000 * 60)


@pytest.fixture
def time_delta_1h() -> Timedelta:
    return Timedelta(1_000_000_000 * 3600)


@pytest.fixture
def time_delta_1d() -> Timedelta:
    return Timedelta(1_000_000_000 * 3600 * 24)


def test_timedelta_to_string(
    time_delta_random: Timedelta,
    time_delta_1us: Timedelta,
    time_delta_1ms: Timedelta,
    time_delta_1s: Timedelta,
    time_delta_10s: Timedelta,
    time_delta_1min: Timedelta,
    time_delta_1h: Timedelta,
    time_delta_1d: Timedelta,
) -> None:

    assert time_delta_random.precise_string == "8295638928ns"
    assert time_delta_1us.precise_string == "1μs"
    assert time_delta_1ms.precise_string == "1ms"
    assert time_delta_1s.precise_string == "1s"
    assert time_delta_10s.precise_string == "10s"
    assert time_delta_1min.precise_string == "1min"
    assert time_delta_1h.precise_string == "1h"
    assert time_delta_1d.precise_string == "1d"


def timedelta_random_list() -> Generator[Timedelta, None, None]:
    """Generate a stream of random Timedeltas of different magnitudes, with
    varying amounts of trailing zeroes.  The durations (in nanoseconds) look
    like this::

               1 to 17 digits total
                  (num_digits)
                       |
            .----------+----------.
            xxxxxxxxx00000000000000
            '---+---'
                |
            1 to num_digits
          leading random digits
          (num_leading_digits)
    """
    rng = Random(72438990202596743)

    for num_digits in range(1, 17):
        for num_leading_digits in range(1, num_digits):
            random = rng.randrange(
                10 ** num_leading_digits, 10 ** (num_leading_digits + 1)
            )
            ts = random * (10 ** (num_digits - num_leading_digits))

            logger.debug(
                f"num_digits={num_digits:2}, "
                f"num_leading_digits={num_leading_digits:2}, "
                f"random={random:20}, "
                f"ts={ts}, "
            )
            yield Timedelta(ts)


def powers_of_ten() -> Generator[Timedelta, None, None]:
    for i in range(17):
        yield Timedelta(10 ** i)


@pytest.mark.parametrize(
    "values",
    [
        [Timedelta(0)],
        powers_of_ten(),
        timedelta_random_list(),
    ],
)
def test_timedelta_precise_string_roundtrip(values: List[Timedelta]) -> None:
    for t in values:
        assert Timedelta.from_string(t.precise_string) == t


@pytest.mark.parametrize(
    "input, expected_ns",
    [
        ("0", 0),
        ("1ns", 1),
        ("1.3456s", 1_345_600_000),
        ("1.5ms", 1_500_000),
        ("60", 60 * 1_000_000_000),
        ("1min", 60 * 1_000_000_000),
        ("89384152596986340ns", 89384152596986340),
    ],
)
def test_timedelta_from_string(input: str, expected_ns: int) -> None:
    assert Timedelta.from_string(input) == Timedelta(expected_ns)


def test_timedelta_sub_timestamp_raises_type_error(
    time_delta_10s: Timedelta, timestamp: Timestamp
) -> None:
    """Assert that one cannot subtract a Timestamp from a Timedelta.

    Previously, the type annotations on Timedelta.__sub__ suggested
    that this was possible.
    """
    with pytest.raises(TypeError):
        time_delta_10s - timestamp  # type: ignore


@pytest.mark.parametrize(
    ("ns", "factor", "expected_ns"),
    [
        (3, 0.5, 6),  # Division by a float results in integer nanoseconds
        (3, 2.0, 1),  # Decimals are truncated
        (3, 2, 1),
        (3, 0.2, 15),
        # True division casts to float first, use floor division
        (89384152596986340, 1, 89384152596986336),
    ],
)
def test_timedelta_truediv(
    ns: int, factor: Union[int, float], expected_ns: int
) -> None:
    timedelta = Timedelta(ns)

    assert (timedelta / factor) == Timedelta(expected_ns)


@pytest.mark.parametrize(
    ("ns", "factor", "expected_ns"),
    [
        (3, 2, 1),
        # Floor division does not lose precision, as noted here:
        # https://www.python.org/dev/peps/pep-0238/#semantics-of-true-division
        (89384152596986340, 1, 89384152596986340),
        # Floor division by floats yields *surprising* results, this is actively discouraged
        (3, 0.2, 14),
    ],
)
def test_timedelta_floordiv(ns: int, factor: int, expected_ns: int) -> None:
    timedelta = Timedelta(ns)

    assert (timedelta // factor) == Timedelta(expected_ns)


@pytest.mark.parametrize("random_timedelta", timedelta_random_list())
def test_timedelta_random_floordiv_one(random_timedelta: Timedelta) -> None:
    assert random_timedelta // 1 == random_timedelta


def test_timeaggregate_from_value(timestamp: Timestamp) -> None:
    VALUE = 42.0
    agg = TimeAggregate.from_value(timestamp=timestamp, value=VALUE)

    assert agg.timestamp == timestamp
    assert agg.active_time == Timedelta(0)
    assert agg.count == 1

    assert agg.minimum == VALUE
    assert agg.maximum == VALUE
    assert agg.sum == VALUE
    assert agg.integral_ns == 0

    assert isclose(agg.mean, VALUE)
    assert isclose(agg.mean_sum, VALUE)

    with pytest.raises(ZeroDivisionError):
        agg.mean_integral


def test_timeaggregate_from_value_pair(
    timestamp: Timestamp, time_delta_10s: Timedelta
) -> None:
    VALUE = 42.0
    later = timestamp + time_delta_10s

    agg = TimeAggregate.from_value_pair(
        timestamp_before=timestamp, timestamp=later, value=VALUE
    )

    assert agg.timestamp == timestamp
    assert agg.active_time == time_delta_10s
    assert agg.count == 1

    assert agg.minimum == VALUE
    assert agg.maximum == VALUE
    assert agg.sum == VALUE
    assert agg.integral_ns == time_delta_10s.ns * VALUE

    assert isclose(agg.mean, VALUE)
    assert isclose(agg.mean_integral, VALUE)
    assert isclose(agg.mean_sum, VALUE)


def test_timeaggregate_from_value_pair_non_monotonic(
    timestamp: Timestamp, time_delta_10s: Timedelta
) -> None:
    later = timestamp + time_delta_10s

    with pytest.raises(NonMonotonicTimestamps):
        TimeAggregate.from_value_pair(
            timestamp_before=later, timestamp=timestamp, value=42.0
        )


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        # Sanity check
        ("1970-01-01T00:00:00Z", Timestamp(0)),
        # Parser supports sub-second digits
        ("1970-01-01T00:00:00.0Z", Timestamp(0)),
        # Parser drops sub-microsecond digits
        ("1970-01-01T00:00:00.000001337Z", Timestamp(1000)),
        # Timezones other that UTC are supported
        ("1970-01-01T00:00:00-01:00", Timestamp(Timedelta.from_string("1h").ns)),
    ],
)
def test_timestamp_from_iso8601(date_string: str, expected: Timestamp) -> None:
    assert Timestamp.from_iso8601(date_string) == expected
