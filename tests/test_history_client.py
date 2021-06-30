from unittest.mock import create_autospec

import pytest
from pytest_mock import MockerFixture

from metricq import HistoryClient, TimeAggregate, Timestamp, TimeValue, history_pb2
from metricq.exceptions import HistoryError, InvalidHistoryResponse
from metricq.history_client import HistoryResponse, HistoryResponseType

pytestmark = pytest.mark.asyncio


@pytest.fixture
def history_client() -> HistoryClient:
    return HistoryClient(token="history-test", management_url="amqps://invalid./")


DEFAULT_METRIC = "test.foo"


def mock_history_response(**response_fields) -> HistoryResponse:
    response_fields.setdefault("error", "")
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
    assert empty_history_response.mode is HistoryResponseType.EMPTY
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


async def test_history_error(
    history_client: HistoryClient,
    mocker: MockerFixture,
    empty_history_response: HistoryResponse,
):
    patch_history_data_request(mocker, empty_history_response)

    with pytest.raises(HistoryError):
        mock_history_response(error="A test error")


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

    assert await history_client.history_last_value(DEFAULT_METRIC) is None


async def test_timelime_empty(
    history_client: HistoryClient, mocker: MockerFixture, empty_history_response
):
    patch_history_data_request(mocker, empty_history_response)

    assert list(await history_client.history_raw_timeline(DEFAULT_METRIC)) == []


async def test_get_metrics_historic_only(
    history_client: HistoryClient,
    mocker: MockerFixture,
):
    """Assert that :meth:`metricq.HistoryClient.get_metrics` behaves exactly
    like :meth:`metricq.Client.get_metrics` by default, except that
    :code:`historic=True` is passed.
    """
    RESULT = mocker.sentinel.RESULT

    async def assert_historic_true(self, *args, historic, **kwargs):
        assert historic
        return RESULT

    mocker.patch("metricq.Client.get_metrics", assert_historic_true)

    assert await history_client.get_metrics(selector=DEFAULT_METRIC) is RESULT


@pytest.mark.parametrize(("historic_override"), [True, False])
async def test_get_metrics_historic_override(
    historic_override: bool,
    history_client: HistoryClient,
    mocker: MockerFixture,
):
    """Assert that any override for :code:`historic` when calling
    :meth:`metricq.HistoryClient.get_metrics` is forwarded to
    :meth:`metricq.Client.get_metrics`.
    """

    async def assert_historic_false(self, *args, historic, **kwargs):
        assert historic == historic_override

    mocker.patch("metricq.Client.get_metrics", assert_historic_false)

    await history_client.get_metrics(
        selector=DEFAULT_METRIC, historic=historic_override
    )
