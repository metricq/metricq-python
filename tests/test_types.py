from logging import getLogger
from math import pow
from random import Random

import pytest

from metricq.types import Timedelta

logger = getLogger(__name__)


@pytest.fixture
def time_delta_random():
    return Timedelta(8295638928)


@pytest.fixture
def time_delta_1us():
    return Timedelta(1_000)


@pytest.fixture
def time_delta_1ms():
    return Timedelta(1_000_000)


@pytest.fixture
def time_delta_1s():
    return Timedelta(1_000_000_000)


@pytest.fixture
def time_delta_10s():
    return Timedelta(10_000_000_000)


@pytest.fixture
def time_delta_1min():
    return Timedelta(1_000_000_000 * 60)


@pytest.fixture
def time_delta_1h():
    return Timedelta(1_000_000_000 * 3600)


@pytest.fixture
def time_delta_1d():
    return Timedelta(1_000_000_000 * 3600 * 24)


def test_timedelta_to_string(
    time_delta_random,
    time_delta_1us,
    time_delta_1ms,
    time_delta_1s,
    time_delta_10s,
    time_delta_1min,
    time_delta_1h,
    time_delta_1d,
):

    assert time_delta_random.precise_string == "8295638928ns"
    assert time_delta_1us.precise_string == "1μs"
    assert time_delta_1ms.precise_string == "1ms"
    assert time_delta_1s.precise_string == "1s"
    assert time_delta_10s.precise_string == "10s"
    assert time_delta_1min.precise_string == "1min"
    assert time_delta_1h.precise_string == "1h"
    assert time_delta_1d.precise_string == "1d"


def timedelta_random_list():
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


def powers_of_ten():
    for i in range(17):
        yield Timedelta(pow(10, i))


@pytest.mark.parametrize(
    "values",
    [
        [Timedelta(0)],
        powers_of_ten(),
        timedelta_random_list(),
    ],
)
def test_timedelta_precise_string_roundtrip(values):
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
def test_timedelta_from_string(input, expected_ns):
    assert Timedelta.from_string(input) == Timedelta(expected_ns)
