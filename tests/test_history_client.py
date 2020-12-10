from unittest.mock import create_autospec

import pytest
from pytest_mock import MockerFixture

from metricq import history_pb2
from metricq.history_client import (
    HistoryClient,
    HistoryResponse,
    HistoryResponseType,
    InvalidHistoryResponse,
)
from metricq.types import TimeAggregate, Timestamp, TimeValue

pytestmark = pytest.mark.asyncio


@pytest.fixture
def history_client() -> HistoryClient:
    return HistoryClient(token="history-test", management_url="amqps://invalid./")


DEFAULT_METRIC = "test.foo"


def mock_history_response(**response_fields) -> HistoryResponse:
    proto = create_autospec(
        history_pb2.HistoryResponse, spec_set=True, **response_fields
    )
    return HistoryResponse(proto=proto)


@pytest.fixture
def empty_history_response() -> HistoryResponse:
    return mock_history_response(time_delta=[], aggregate=[], value=[])


def patch_history_data_request(
    mocker: MockerFixture, response: HistoryResponse
) -> None:
    async def mocked(_client, *args, **_kwargs):
        return response

    mocker.patch(f"{__name__}.HistoryClient.history_data_request", mocked)


def test_iterate_empty_history_response(empty_history_response):
    assert empty_history_response.mode == HistoryResponseType.EMPTY
    assert len(empty_history_response) == 0
    assert len(list(empty_history_response.values())) == 0
    assert len(list(empty_history_response.aggregates())) == 0


async def test_history_aggregate(history_client: HistoryClient, mocker: MockerFixture):
    TIME = Timestamp(0)
    AGGREGATE = create_autospec(history_pb2.HistoryResponse.Aggregate, set_spec=True)

    response = mock_history_response(
        time_delta=[TIME.posix_ns],
        aggregate=[AGGREGATE],
    )

    patch_history_data_request(mocker, response)

    assert await history_client.history_aggregate(
        DEFAULT_METRIC
    ) == TimeAggregate.from_proto(timestamp=TIME, proto=AGGREGATE)


async def test_history_no_aggregate(
    history_client: HistoryClient,
    mocker: MockerFixture,
    empty_history_response: HistoryResponse,
):
    patch_history_data_request(mocker, empty_history_response)

    with pytest.raises(InvalidHistoryResponse):
        await history_client.history_aggregate(DEFAULT_METRIC)


async def test_history_last_value(history_client: HistoryClient, mocker: MockerFixture):
    TIME = Timestamp(0)
    VALUE = mocker.sentinel.VALUE

    response = mock_history_response(
        time_delta=[TIME.posix_ns],
        value=[VALUE],
    )

    patch_history_data_request(mocker, response)

    assert await history_client.history_last_value(DEFAULT_METRIC) == TimeValue(
        timestamp=TIME, value=VALUE
    )


async def test_history_no_last_value(
    history_client: HistoryClient, mocker: MockerFixture, empty_history_response
):
    patch_history_data_request(mocker, empty_history_response)

    with pytest.raises(InvalidHistoryResponse):
        await history_client.history_last_value(DEFAULT_METRIC)
