import pytest
from math import pow

from ..metricq.types import Timedelta


@pytest.fixture
def time_delta_random():
    return Timedelta(8295638928)


@pytest.fixture
def time_delta_1s():
    return Timedelta(1_000_000_000)


@pytest.fixture
def time_delta_1d():
    return Timedelta(1_000_000_000 * 3600 * 24)


@pytest.fixture
def time_delta_generate_random_list(count=1000):
    l = []

    v = 8295638928
    increase = 1243899020259
    mult = 5
    mod = 9987868812

    for _ in range(count):
        l.append(Timedelta(v // 20 * pow(10, v % 20)))
        v = (v * mult + increase) % mod

    return l


def test_timedelta_to_string():
    td1 = time_delta_random()
    td2 = time_delta_1s()
    td3 = time_delta_1d()

    assert td1.precise_string == "8295638928ns"
    assert td2.precise_string == "1s"
    assert td3.precise_string == "1d"


def test_timedelta_to_string_and_reverse():

    for t in time_delta_generate_random_list():
        assert Timedelta.from_string(t.precise_string) == t

