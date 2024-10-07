import math
from typing import Any

import pytest
from pytest_mock import MockerFixture

from metricq import HistoryClient, TimeAggregate, Timestamp, TimeValue, history_pb2
from metricq.exceptions import HistoryError, InvalidHistoryResponse
from metricq.history_client import HistoryResponse, HistoryResponseType

pytestmark = pytest.mark.asyncio


@pytest.fixture
def history_client() -> HistoryClient:
    return HistoryClient(token="history-test", url="amqps://invalid./")


DEFAULT_METRIC = "test.foo"


def mock_history_response(**response_fields: Any) -> HistoryResponse:
    response_fields.setdefault("error", "")
    return HistoryResponse(
        proto=history_pb2.HistoryResponse(**response_fields),
    )


@pytest.fixture
def empty_history_response() -> HistoryResponse:
    return mock_history_response(time_delta=[], aggregate=[], value=[])


def patch_history_data_request(
    mocker: MockerFixture, response: HistoryResponse
) -> None:
    async def mocked(
        _client: HistoryClient, *args: Any, **_kwargs: Any
    ) -> HistoryResponse:
        return response

    mocker.patch(f"{__name__}.HistoryClient.history_data_request", mocked)


def test_iterate_empty_history_response(
    empty_history_response: HistoryResponse,
) -> None:
    assert empty_history_response.mode is HistoryResponseType.EMPTY
    assert len(empty_history_response) == 0
    assert len(list(empty_history_response.values())) == 0
    assert len(list(empty_history_response.aggregates())) == 0


async def test_history_aggregate(
    history_client: HistoryClient, mocker: MockerFixture
) -> None:
    time = Timestamp(0)
    aggregate = history_pb2.HistoryResponse.Aggregate()

    response = mock_history_response(
        time_delta=[time.posix_ns],
        aggregate=[aggregate],
    )

    patch_history_data_request(mocker, response)

    assert await history_client.history_aggregate(
        DEFAULT_METRIC
    ) == TimeAggregate.from_proto(timestamp=time, proto=aggregate)


def test_history_aggregate_with_zero_count(
    history_client: HistoryClient, mocker: MockerFixture
) -> None:
    time = Timestamp(0)
    aggregate = history_pb2.HistoryResponse.Aggregate(count=0)

    response = mock_history_response(
        time_delta=[time.posix_ns],
        aggregate=[aggregate],
    )

    patch_history_data_request(mocker, response)

    agg = TimeAggregate.from_proto(timestamp=time, proto=aggregate)

    assert math.isnan(agg.mean_sum)


async def test_history_no_aggregate(
    history_client: HistoryClient,
    mocker: MockerFixture,
    empty_history_response: HistoryResponse,
) -> None:
    patch_history_data_request(mocker, empty_history_response)

    with pytest.raises(InvalidHistoryResponse):
        await history_client.history_aggregate(DEFAULT_METRIC)


async def test_history_error(
    history_client: HistoryClient,
    mocker: MockerFixture,
    empty_history_response: HistoryResponse,
) -> None:
    patch_history_data_request(mocker, empty_history_response)

    with pytest.raises(HistoryError):
        mock_history_response(error="A test error")


async def test_history_last_value(
    history_client: HistoryClient, mocker: MockerFixture
) -> None:
    time = Timestamp(0)
    value = 42.23

    response = mock_history_response(
        time_delta=[time.posix_ns],
        value=[value],
    )

    patch_history_data_request(mocker, response)

    assert await history_client.history_last_value(DEFAULT_METRIC) == TimeValue(
        timestamp=time, value=value
    )


async def test_history_no_last_value(
    history_client: HistoryClient,
    mocker: MockerFixture,
    empty_history_response: HistoryResponse,
) -> None:
    patch_history_data_request(mocker, empty_history_response)

    assert await history_client.history_last_value(DEFAULT_METRIC) is None


async def test_timelime_empty(
    history_client: HistoryClient,
    mocker: MockerFixture,
    empty_history_response: HistoryResponse,
) -> None:
    patch_history_data_request(mocker, empty_history_response)

    assert list(await history_client.history_raw_timeline(DEFAULT_METRIC)) == []


async def test_get_metrics_historic_only(
    history_client: HistoryClient,
    mocker: MockerFixture,
) -> None:
    """Assert that :meth:`metricq.HistoryClient.get_metrics` behaves exactly
    like :meth:`metricq.Client.get_metrics` by default, except that
    :code:`historic=True` is passed.
    """
    result = mocker.sentinel.RESULT

    async def assert_historic_true(
        self: HistoryClient, *args: Any, historic: bool, **kwargs: Any
    ) -> Any:
        assert historic
        return result

    mocker.patch("metricq.Client.get_metrics", assert_historic_true)

    assert await history_client.get_metrics(selector=DEFAULT_METRIC) is result


@pytest.mark.parametrize(("historic_override"), [True, False])
async def test_get_metrics_historic_override(
    historic_override: bool,
    history_client: HistoryClient,
    mocker: MockerFixture,
) -> None:
    """Assert that any override for :code:`historic` when calling
    :meth:`metricq.HistoryClient.get_metrics` is forwarded to
    :meth:`metricq.Client.get_metrics`.
    """

    async def assert_historic_false(
        self: Any, *args: Any, historic: bool, **kwargs: Any
    ) -> None:
        assert historic == historic_override

    mocker.patch("metricq.Client.get_metrics", assert_historic_false)

    await history_client.get_metrics(
        selector=DEFAULT_METRIC, historic=historic_override
    )
