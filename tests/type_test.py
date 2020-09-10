import pytest
from math import pow

from metricq.types import Timedelta


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


@pytest.fixture
def time_delta_generate_random_list():
    c = 4
    v = 20458290249576139
    seed = 72438990202596743
    mult = 7
    mod = 99878688123465600

    yield 0
    for l in range(0, 17, 1):
        yield Timedelta(pow(10, l))
        for _ in range(c * (l + 1)):
            d = v // 20
            p = v % (l + 1)
            r = int((d * pow(10, p)) % (pow(10, l + 1)))
            if r != 0:
                yield Timedelta(r)
            v = (v * mult + seed) % mod


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


def test_timedelta_to_string_and_reverse(time_delta_generate_random_list):

    for t in time_delta_generate_random_list:
        assert Timedelta.from_string(t.precise_string) == t

