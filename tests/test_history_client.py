from unittest.mock import create_autospec

import pytest
from pytest_mock import MockerFixture

from metricq import history_pb2
from metricq.history_client import (
    HistoryClient,
    HistoryResponse,
    InvalidHistoryResponse,
)
from metricq.types import TimeAggregate, Timestamp, TimeValue

pytestmark = pytest.mark.asyncio


@pytest.fixture
def history_client() -> HistoryClient:
    return HistoryClient(token="history-test", management_url="amqps://invalid./")


DEFAULT_METRIC = "test.foo"


def mock_history_response(mocker: MockerFixture, **response_fields) -> None:
    async def mocked(_client, *args, **_kwargs):
        proto = create_autospec(
            history_pb2.HistoryResponse, spec_set=True, **response_fields
        )
        return HistoryResponse(proto=proto)

    mocker.patch(f"{__name__}.HistoryClient.history_data_request", mocked)


def mock_empty_history_response(mocker, metric: str):
    mock_history_response(mocker, metric=metric, time_delta=[], aggregate=[], value=[])


async def test_history_aggregate(history_client: HistoryClient, mocker: MockerFixture):
    TIME = Timestamp(0)
    AGGREGATE = create_autospec(history_pb2.HistoryResponse.Aggregate, set_spec=True)

    mock_history_response(
        mocker,
        metric=DEFAULT_METRIC,
        time_delta=[TIME.posix_ns],
        aggregate=[AGGREGATE],
    )

    assert await history_client.history_aggregate(
        DEFAULT_METRIC
    ) == TimeAggregate.from_proto(timestamp=TIME, proto=AGGREGATE)


async def test_history_no_aggregate(
    history_client: HistoryClient, mocker: MockerFixture
):
    mock_empty_history_response(mocker, DEFAULT_METRIC)

    with pytest.raises(InvalidHistoryResponse):
        await history_client.history_aggregate(DEFAULT_METRIC)


async def test_history_last_value(history_client: HistoryClient, mocker: MockerFixture):
    TIME = Timestamp(0)
    VALUE = mocker.sentinel.VALUE

    mock_history_response(
        mocker,
        metric=DEFAULT_METRIC,
        time_delta=[TIME.posix_ns],
        value=[VALUE],
    )

    assert await history_client.history_last_value(DEFAULT_METRIC) == TimeValue(
        timestamp=TIME, value=VALUE
    )


async def test_history_no_last_value(
    history_client: HistoryClient, mocker: MockerFixture
):
    mock_empty_history_response(mocker, DEFAULT_METRIC)

    with pytest.raises(AssertionError):
        await history_client.history_last_value(DEFAULT_METRIC)
