from dataclasses import dataclass
from typing import Any, Dict

from deprecated.sphinx import deprecated

from .. import history_pb2
from ..exceptions import NonMonotonicTimestamps
from .timedelta import Timedelta
from .timestamp import Timestamp


@dataclass(frozen=True)
class TimeAggregate:
    """Summary of a metric's values within a certain period of time."""

    __slots__ = (
        "timestamp",
        "minimum",
        "maximum",
        "sum",
        "count",
        "integral_ns",
        "active_time",
    )

    timestamp: Timestamp
    """starting time of this aggregate"""
    minimum: float
    """minimum value"""
    maximum: float
    """maximum value"""
    sum: float
    """sum of all values"""
    count: int
    """total number of values"""
    integral_ns: float
    """Integral of values in this aggregate over its active time, nanoseconds-based"""
    active_time: Timedelta
    """time spanned by this aggregate"""

    @staticmethod
    def from_proto(
        timestamp: Timestamp, proto: history_pb2.HistoryResponse.Aggregate
    ) -> "TimeAggregate":
        return TimeAggregate(
            timestamp=timestamp,
            minimum=proto.minimum,
            maximum=proto.maximum,
            sum=proto.sum,
            count=proto.count,
            integral_ns=proto.integral,
            active_time=Timedelta(proto.active_time),
        )

    @staticmethod
    def from_value(timestamp: Timestamp, value: float) -> "TimeAggregate":
        return TimeAggregate(
            timestamp=timestamp,
            minimum=value,
            maximum=value,
            sum=value,
            count=1,
            integral_ns=0,
            active_time=Timedelta(0),
        )

    @staticmethod
    def from_value_pair(
        timestamp_before: Timestamp, timestamp: Timestamp, value: float
    ) -> "TimeAggregate":
        """Create a TimeAggregate from a pair of timestamps (class:`Timestamp`) and one value

        Raises:
            NonMonotonicTimestamps: if the two timestamps are not strictly monotonic
        """
        # Can't use (https://github.com/python/mypy/issues/4610)
        # if timestamp_before >= timestamp:
        if not timestamp_before < timestamp:
            raise NonMonotonicTimestamps(
                "Timestamps in HistoryResponse are not strictly monotonic ({} -> {})".format(
                    timestamp_before, timestamp
                )
            )
        delta = timestamp - timestamp_before
        return TimeAggregate(
            timestamp=timestamp_before,
            minimum=value,
            maximum=value,
            sum=value,
            count=1,
            integral_ns=delta.ns * value,
            active_time=delta,
        )

    @property
    def integral_s(self) -> float:
        """Integral of values in this aggregate over its active time, seconds-based"""
        return self.integral_ns / 1e9

    @property
    def mean(self) -> float:
        """
        Mean value of this aggregate.
        This is the general way to access the mean value if nothing specific
        is known about the underlying raw data.

        It may involve a heuristic to decide between :attr:`mean_integral` and
        :attr:`mean_sum`. Currently, it defaults to :attr:`mean_integral`.
        """
        if self.active_time.ns > 0:
            return self.mean_integral
        else:
            return self.mean_sum

    @property
    def mean_integral(self) -> float:
        """
        Mean value of this aggregate, calculated from the integral.
        Use this if you want to explicitly force this property.

        In the HTA context, this should only be `NaN` if the aggregate interval
        is outside the of the interval from the earliest to the latest
        measurement point.
        """
        return self.integral_ns / self.active_time.ns

    @property
    def mean_sum(self) -> float:
        """
        Mean value of this aggregate, calculated from the sum.
        This can be useful when the underlying metric should be at regular
        intervals, but there are gaps in the data. Otherwise,
        :attr:`mean_integral` or just :attr:`mean` are more appropriate.

        This value will be `NaN` if there are no raw data points in the
        aggregate interval.
        """
        return self.sum / self.count if self.count != 0 else float("NaN")

    @deprecated(
        version="5.0.0",
        reason=(
            "Use the individual properties instead and chose between "
            "`mean_integral` and `mean_sum` based on your use-case"
        ),
    )
    # using Dict as return type to work around https://github.com/python/mypy/issues/15047
    def dict(self) -> Dict[str, Any]:
        """
        returns a dict representing the TimeAggregate instance.
        Keys are `timestamp`, `minimum`, `mean`, `maximum`, and `count`.
        """
        return {
            "minimum": self.minimum,
            "mean": self.mean,
            "maximum": self.maximum,
            "count": self.count,
            "timestamp": self.timestamp.posix_ns,
        }
