from types import TracebackType
from typing import Any, Optional, TypeVar

import pandas as pd

from ..history_client import HistoryClient
from ..timeseries import JsonDict

# With Python 3.11 use typing.Self instead
Self = TypeVar("Self", bound="PandasHistoryClient")


class PandasHistoryClient:
    """
    This can be used similarly to a :class:`metricq.HistoryClient`, but the data
    methods return pandas structures.

    Note:
        Consider this class experimental, the type signatures may change at any time.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        self._client = HistoryClient(*args, **kwargs)

    async def connect(self) -> None:
        """
        Connect to the MetricQ network.
        You can either use this method, or use the class as an async context manager.
        """
        await self._client.connect()

    async def stop(self) -> None:
        """
        Stop the client and disconnect from the MetricQ network.
        Do not call this if you use the class as an async context manager.
        """
        await self._client.stop()

    @property
    def client(self) -> HistoryClient:
        """
        Access the underlying :class:`metricq.HistoryClient` instance.
        """
        return self._client

    async def get_metrics(self, *args: Any, **kwargs: Any) -> dict[str, JsonDict]:
        """
        The method works like :meth:`metricq.Client.get_metrics`, but sets
        :code:`historic=True` by default. See documentation there for a detailed
        description of the remaining arguments.
        """
        return await self._client.get_metrics(*args, **kwargs)

    async def history_aggregate_timeline(
        self, *args: Any, **kwargs: Any
    ) -> pd.DataFrame:
        """
        The method works like :meth:`metricq.HistoryClient.history_aggregate_timeline`,
        but returns a :class:`pandas.DataFrame`.
        The dataframe will have the following columns:

        * timestamp
        * minimum
        * maximum
        * sum
        * count
        * integral_ns
        * active_time
        * mean
        * mean_integral
        * mean_sum
        * integral_s

        For details of those, see the documentation of :class:`metricq.TimeAggregate`.
        """
        data = await self._client.history_aggregate_timeline(*args, **kwargs)
        columns = [
            "timestamp",
            "minimum",
            "maximum",
            "sum",
            "count",
            "integral_ns",
            "active_time",
            "mean",
            "mean_integral",
            "mean_sum",
            "integral_s",
        ]

        return pd.DataFrame(
            (
                (
                    {
                        "timestamp": pd.Timestamp(
                            aggregate.timestamp.posix_ns, unit="ns"
                        ),
                        "active_time": pd.Timedelta(
                            aggregate.active_time.ns, unit="ns"
                        ),
                    }
                    | {
                        attr: getattr(aggregate, attr)
                        for attr in columns
                        if attr not in ("timestamp", "active_time")
                    }
                )
                for aggregate in data
            ),
            columns=columns,
        )

    async def history_raw_timeline(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        """
        The method works like :meth:`metricq.HistoryClient.history_raw_timeline`,
        but returns a :class:`pandas.DataFrame` instead of a list of
        :class:`metricq.TimeValue` objects.
        The dataframe will have the following columns:

        * timestamp
        * value
        """
        data = await self._client.history_raw_timeline(*args, **kwargs)
        return pd.DataFrame(
            (
                {
                    "timestamp": pd.Timestamp(time_value.timestamp.posix_ns, unit="ns"),
                    "value": time_value.value,
                }
                for time_value in data
            ),
            columns=["timestamp", "value"],
        )

    async def __aenter__(self: Self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.stop()
