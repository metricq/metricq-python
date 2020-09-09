import pytest

from ..metricq.types import *


@pytest.fixture
def time_delta_random():
    return Timedelta(8295638928)


@pytest.fixture
def time_delta_1s():
    return Timedelta(1_000_000_000)


@pytest.fixture
def time_delta_1d():
    return Timedelta(1_000_000_000 * 3600 * 24)


def test_timedelta_to_string():
    td1 = time_delta_random()
    td2 = time_delta_1s()
    td3 = time_delta_1d()

    assert td1.precise_string == "8295638928ns"
    assert td1.precise_string == "1s"
    assert td1.precise_string == "1d"


def test_timedelta_to_string_and_reverse():
    td1 = time_delta_random()
    td2 = time_delta_1s()
    td3 = time_delta_1d()

    assert Timedelta.from_string(td1.precise_string) == td1
    assert Timedelta.from_string(td2.precise_string) == td2
    assert Timedelta.from_string(td3.precise_string) == td3

