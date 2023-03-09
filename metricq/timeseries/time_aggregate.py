from dataclasses import dataclass
from typing import Any

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
        if self.active_time.ns > 0:
            return self.mean_integral
        else:
            return self.mean_sum

    @property
    def mean_integral(self) -> float:
        return self.integral_ns / self.active_time.ns

    @property
    def mean_sum(self) -> float:
        return self.sum / self.count

    def dict(self) -> dict[str, Any]:
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
