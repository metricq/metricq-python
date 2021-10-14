# Copyright (c) 2018, ZIH,
# Technische Universitaet Dresden,
# Federal Republic of Germany
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of metricq nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Any, Dict, Iterator, Union, overload

from dateutil.parser import isoparse as dateutil_isoparse

from . import history_pb2
from .exceptions import NonMonotonicTimestamps


@total_ordering
class Timedelta:
    """A (possibly negative) duration of time

    Args:
        nanoseconds: duration in nanoseconds

    Supported operations:
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | Operation        | Types                                            | Result                                                                                    |
        +==================+==================================================+===========================================================================================+
        | :code:`d1 + d2`  | * :code:`d1`, :code:`d2`: :class:`Timedelta`     | the sum of the duration of :code:`d1` and :code:`d2` as a :class:`Timedelta` object       |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d + dt`   | * :code:`d`: :class:`Timedelta`                  | the combined duration of :code:`d` and                                                    |
        |                  | * :code:`dt`: :class:`python:datetime.timedelta` | :code:`Timedelta.from_timedelta(dt)` as a :class:`Timedelta` object                       |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d + t`    | * :code:`d`: :class:`Timedelta`                  | a :class:`Timestamp` offset by duration :code:`d`                                         |
        |                  | * :code:`t`: :class:`Timestamp`                  | (the same as :code:`t + d`, see :class:`Timestamp.__add__`)                               |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d1 == d2` | * :code:`d1`, :code:`d2`: :class:`Timedelta`     | :code:`True` if :code:`d1` and :code:`d2` describe the same duration of time              |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d == dt`  | * :code:`d`: :class:`Timedelta`                  | :code:`True` if :code:`d.datetime == dt`                                                  |
        |                  | * :code:`dt`: :class:`python:datetime.timedelta` | (see :class:`python:datetime.timedelta`)                                                  |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d1 < d2`  | * :code:`d1`, :code:`d2`: :class:`Timedelta`     | :code:`True` if :code:`d1` is shorter than :code:`d2`                                     |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d < dt`   | * :code:`d`: :class:`Timedelta`                  | :code:`True` if :code:`d.datetime < dt`                                                   |
        |                  | * :code:`dt`: :class:`python:datetime.timedelta` | (see :class:`python:datetime.timedelta`)                                                  |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d * c`    | * :code:`d`: :class:`Timedelta`                  | The duration scaled by the factor :code:`c`, truncated to nanosecond precision            |
        |                  | * :code:`c`: :class:`float` or :class:`int`      | See :meth:`__mul__`.                                                                      |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d / c`    | * :code:`d`: :class:`Timedelta`                  | The duration divided by :code:`c`, truncated to nanosecond precision.                     |
        |                  | * :code:`c`: :class:`float`                      | See :meth:`__truediv__`.                                                                  |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+
        | :code:`d // n`   | * :code:`d`: :class:`Timedelta`                  | The duration divided by an *integer* factor :code:`n`, truncated to nanosecond precision. |
        |                  | * :code:`n`: :class:`int`                        | See :meth:`__floordiv__`.                                                                 |
        +------------------+--------------------------------------------------+-------------------------------------------------------------------------------------------+

        In addition to :code:`<` and :code:`=`, all other relational operations are supported and behave as you would expect.
    """

    def __init__(self, nanoseconds: int):
        self._value = nanoseconds

    @staticmethod
    def from_timedelta(delta: datetime.timedelta) -> "Timedelta":
        """Convert from a standard ``timedelta`` object.

        Args:
            delta: a standard :class:`python:datetime.timedelta` object
        Returns:
            A :class:`Timedelta` object
        """
        seconds = (delta.days * 24 * 3600) + delta.seconds
        microseconds = seconds * 1000000 + delta.microseconds
        return Timedelta(microseconds * 1000)

    @staticmethod
    def from_string(duration_str: str) -> "Timedelta":
        """Parse a human-readable string representation of a duration.

        >>> "One day has {} seconds".format(Timedelta.from_string("1 day"))
        'One day has 86400.0s seconds'

        Args:
            duration_str:
                A duration string in the form of "`<number> <unit>`".
                Accepted units are:

                    ============ ========= =====================================
                    Name         short     long
                    ============ ========= =====================================
                    Seconds      ``"s"``   ``"second"``,      ``"seconds"``
                    Milliseconds ``"ms"``  ``"millisecond"``, ``"milliseconds"``
                    Microseconds ``"us"``  ``"microsecond"``, ``"microseconds"``
                    Nanoseconds  ``"ns"``  ``"nanosecond"``,  ``"nanoseconds"``
                    Minutes      ``"min"`` ``"minute"``,      ``"minutes"``
                    Hours        ``"h"``   ``"hour"``,        ``"hours"``
                    Days         ``"d"``   ``"day"``,         ``"days"``
                    ============ ========= =====================================

        Returns:
            The parsed :class:`Timedelta` object

        Raises:
            ValueError: if the string is not of the correct format or an invalid unit was specified
        """

        m = re.fullmatch(
            r"""
            \s*
                (?P<value_integral>[+-]?\d*)
                (?P<value_fractional>([.,]\d*)?)
            \s*
                (?P<unit>[^\d]*)
            \s*
            """,
            duration_str,
            flags=re.X,
        )
        if not m:
            raise ValueError(
                'invalid duration string {}, not of form "number unit"'.format(
                    duration_str
                )
            )

        groups = m.groupdict()
        value: float = int(groups["value_integral"])

        if groups["value_fractional"]:
            value += float(groups["value_fractional"].replace(",", "."))

        unit = groups["unit"]

        if unit in ("", "s", "second", "seconds"):
            return Timedelta(int(value * 1_000_000_000))
        if unit in ("ms", "millisecond", "milliseconds"):
            return Timedelta(int(value * 1_000_000))
        if unit in ("us", "microsecond", "microseconds", "μs"):
            return Timedelta(int(value * 1_000))
        if unit in ("ns", "nanosecond", "nanoseconds"):
            return Timedelta(int(value))
        if unit in ("min", "minute", "minutes"):
            return Timedelta(int(value * 1_000_000_000 * 60))
        if unit in ("h", "hour", "hours"):
            return Timedelta(int(value * 1_000_000_000 * 3600))
        if unit in ("d", "day", "days"):
            return Timedelta(int(value * 1_000_000_000 * 3600 * 24))
        raise ValueError("invalid duration unit {}".format(unit))

    @staticmethod
    def from_us(microseconds: float) -> "Timedelta":
        """Create a duration from a number of microseconds

        Args:
            microseconds: number of microseconds
        Returns:
            A :class:`Timedelta` object
        """
        return Timedelta(int(microseconds * 1e3))

    @staticmethod
    def from_ms(milliseconds: float) -> "Timedelta":
        """Create a duration from a number of milliseconds

        Args:
            milliseconds: number of milliseconds
        Returns:
            A :class:`Timedelta` object
        """
        return Timedelta(int(milliseconds * 1e6))

    @staticmethod
    def from_s(seconds: float) -> "Timedelta":
        """Create a duration from a number of seconds

        Args:
            seconds: number of seconds
        Returns:
            A :class:`Timedelta` object
        """
        return Timedelta(int(seconds * 1e9))

    @property
    def precise_string(self) -> str:
        if self._value % 1_000 != 0:
            return f"{self._value}ns"

        elif self._value % 1_000_000 != 0:
            return f"{self._value // 1_000}μs"

        elif self._value % 1_000_000_000 != 0:
            return f"{self._value // 1_000_000}ms"

        elif self._value % (1_000_000_000 * 60) != 0:
            return f"{self._value // 1_000_000_000}s"

        elif self._value % (1_000_000_000 * 3600) != 0:
            return f"{self._value // (1_000_000_000 * 60)}min"

        elif self._value % (1_000_000_000 * 3600 * 24) != 0:
            return f"{self._value // (1_000_000_000 * 3600)}h"

        return f"{self._value // (1_000_000_000 * 3600 * 24)}d"

    @property
    def ns(self) -> int:
        """Number of nanoseconds in this duration"""
        return self._value

    @property
    def us(self) -> float:
        """Number of microseconds in this duration"""
        return self._value / 1e3

    @property
    def ms(self) -> float:
        """Number of milliseconds in this duration"""
        return self._value / 1e6

    @property
    def s(self) -> float:
        """Number of seconds in this duration"""
        return self._value / 1e9

    @property
    def timedelta(self) -> datetime.timedelta:
        """This duration as a standard :class:`python:datetime.timedelta` object"""
        microseconds = self._value // 1000
        return datetime.timedelta(microseconds=microseconds)

    @overload
    def __add__(self, other: "Timedelta") -> "Timedelta":
        ...

    @overload
    def __add__(self, other: "Timestamp") -> "Timestamp":
        ...

    @overload
    def __add__(self, other: datetime.timedelta) -> "Timedelta":
        ...

    def __add__(
        self, other: Union["Timedelta", "Timestamp", datetime.timedelta]
    ) -> Union["Timedelta", "Timestamp"]:
        if isinstance(other, Timedelta):
            return Timedelta(self._value + other._value)
        if isinstance(other, datetime.timedelta):
            return self + Timedelta.from_timedelta(other)
        # Fallback to Timestamp.__add__
        return other + self

    @overload
    def __sub__(self, other: "Timedelta") -> "Timedelta":
        ...

    @overload
    def __sub__(self, other: datetime.timedelta) -> "Timedelta":
        ...

    def __sub__(self, other: Union["Timedelta", datetime.timedelta]) -> "Timedelta":
        if isinstance(other, Timedelta):
            return Timedelta(self._value - other._value)
        if isinstance(other, datetime.timedelta):
            return self - Timedelta.from_timedelta(other)
        raise TypeError(
            "invalid type to subtract from Timedelta: {}".format(type(other))
        )

    def __floordiv__(self, factor: int) -> "Timedelta":
        """Divide a duration by an integer factor.

        >>> td = Timedelta.from_s(10) // 3
        >>> td.s
        3.333333333
        >>> td.precise_string
        '3333333333ns'

        This divides the number of nanoseconds in this duration by `factor`
        using `Floor Division <https://www.python.org/dev/peps/pep-0238/#semantics-of-floor-division>`_,
        i.e. for some :code:`n: int` and :code:`td: Timedelta` we have

        >>> assert (td // n).ns == td.ns // n

        Note:
            Floor Division produces *surprising* results for :code:`float` arguments
            (i.e. :code:`3 // 0.2 == 14.0`).
            Use :meth:`__truediv__` if you want to scale a duration by a non-integer factor.
        """
        return Timedelta(int(self._value // factor))

    def __truediv__(self, factor: float) -> "Timedelta":
        """Divide a duration by a (floating point) factor.

        >>> (Timedelta.from_s(10) / 2.5).precise_string
        '4s'

        This divides the number of nanoseconds in this duration by `factor`
        using `True Division <https://www.python.org/dev/peps/pep-0238/#semantics-of-true-division>`_,
        but truncates the result to an :code:`int`:

        >>> assert (td / x).ns == int(td.ns / x)

        where :code:`td: Timedelta` and :code:`x: float`.

        Note:
            Use :meth:`__floordiv__` if you know that the factor is an integer,
            this will prevent rounding errors.
        """
        return Timedelta(int(self._value / factor))

    def __mul__(self, factor: float) -> "Timedelta":
        """Scale a duration by a :class:`float` factor."""
        return Timedelta(int(self._value * factor))

    def __str__(self) -> str:
        """A string containing the number of seconds of this duration

        >>> "One day has {} seconds".format(Timedelta.from_string("1 day"))
        'One day has 86400.0s seconds'
        """
        return "{}s".format(self.s)

    def __repr__(self) -> str:
        return f"Timedelta({self.ns})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, datetime.timedelta):
            return self.timedelta == other
        if isinstance(other, Timedelta):
            return self._value == other._value
        return NotImplemented

    def __lt__(self, other: Union["Timedelta", datetime.timedelta]) -> bool:
        if isinstance(other, datetime.timedelta):
            return self.timedelta < other
        return self._value < other._value


@total_ordering
class Timestamp:
    """A MetricQ Timestamp

    Args:
        nanoseconds: number of nanoseconds elapsed since the UNIX epoch
    """

    _EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    def __init__(self, nanoseconds: int):
        self._value = nanoseconds
        """Timestamp value in nanoseconds since :const:`Timestamp._EPOCH`,

        :meta private:
        """

    @classmethod
    def from_posix_seconds(cls, seconds: float) -> "Timestamp":
        """Create a Timestamp from a POSIX timestamp

        Args:
            seconds: number of seconds since the UNIX epoch

        Returns:
            :class:`Timestamp`
        """
        return Timestamp(int(seconds * 1e9))

    @classmethod
    def from_datetime(cls, dt: datetime.datetime) -> "Timestamp":
        """Create a Timestamp from an aware datetime object

        Args:
            dt: an aware datetime object

        Returns:
            :class:`Timestamp`
        """
        delta = dt - Timestamp._EPOCH
        seconds = (delta.days * 24 * 3600) + delta.seconds
        microseconds = seconds * 1000000 + delta.microseconds
        return Timestamp(microseconds * 1000)

    @classmethod
    def from_iso8601(cls, iso_string: str) -> "Timestamp":
        """Create a Timestamp from a `ISO 8601` date-time string.

        >>> Timestamp.from_iso8601("1970-01-01T00:00:00.0Z") == Timestamp(0)
        True

        This is a convenience method that parses the date-time string into a
        :class:`python:datetime.datetime` using
        :meth:`dateutil:dateutil.parser.isoparse`,
        and then calls :meth:`from_datetime` to create a :class:`Timestamp` from that.

        Note:
            The parser only supports up to *6 sub-second digits*,
            further digits are simply dropped.
            If you need to parse timestamps with higher precision,
            you need to convert the string to nanoseconds yourself.

        Args:
            iso_string: a date-time string in `ISO 8601` format.
        """
        dt = dateutil_isoparse(iso_string)
        return cls.from_datetime(dt)

    @classmethod
    def ago(cls, delta: Timedelta) -> "Timestamp":
        """Return a timestamp `delta` in the past.

        This is equivalent to::

            Timestamp.now() - delta

        Args:
            delta: the time difference to now
        """
        return cls.now() - delta

    @classmethod
    def from_now(cls, delta: Timedelta) -> "Timestamp":
        """Return a timestamp `delta` in the future.

        This is equivalent to::

            Timestamp.now() + delta

        Args:
            delta: the time difference to now
        """
        return cls.now() + delta

    @classmethod
    def now(cls) -> "Timestamp":
        """Return a Timestamp corresponding to "now"

        Returns:
            :class:`Timestamp`
        """
        return cls.from_datetime(datetime.datetime.now(datetime.timezone.utc))

    @property
    def posix_ns(self) -> int:
        """Number of nanoseconds since the UNIX epoch"""
        return self._value

    @property
    def posix_us(self) -> float:
        """Number of microseconds since the UNIX epoch"""
        return self._value / 1000

    @property
    def posix_ms(self) -> float:
        """Number of milliseconds since the UNIX epoch"""
        return self._value / 1000000

    @property
    def posix(self) -> float:
        """Number of seconds since the UNIX epoch"""
        return self._value / 1000000000

    @property
    def datetime(self) -> datetime.datetime:
        """Create an aware UTC datetime object

        All MetricQ timestamps are POSIX timestamps, hence UTC.
        """
        # We use timedelta in the hope that this doesn't break
        # on non-POSIX systems, where fromtimestamp apparently may omit leap seconds
        # but our MetricQ timestamps are true UNIX timestamps without leap seconds
        microseconds = self._value // 1000
        return Timestamp._EPOCH + datetime.timedelta(microseconds=microseconds)

    def __add__(self, delta: Timedelta) -> "Timestamp":
        """Return the timestamp `delta` in the future (or in the past, if `delta` is negative), relative to a :class:`Timestamp` instance.

        >>> epoch = Timestamp(0)
        >>> a_week_later = epoch + Timedelta.from_string("7 days")
        >>> str(a_week_later)
        '[604800000000000] 1970-01-08 01:00:00+01:00'

        Args:
            delta: a time duration, possibly negative

        Returns:
            :class:`Timestamp`
        """
        return Timestamp(self._value + delta.ns)

    @overload
    def __sub__(self, other: "Timedelta") -> "Timestamp":
        ...

    @overload
    def __sub__(self, other: "Timestamp") -> "Timedelta":
        ...

    def __sub__(
        self, other: Union["Timedelta", "Timestamp"]
    ) -> Union["Timestamp", "Timedelta"]:
        if isinstance(other, Timedelta):
            return Timestamp(self._value - other.ns)
        if isinstance(other, Timestamp):
            return Timedelta(self._value - other._value)
        raise TypeError(
            "Invalid type to subtract from Timestamp: {}".format(type(other))
        )

    def __lt__(self, other: "Timestamp") -> bool:
        """Compare whether this timestamp describes a time before another timestamp.

        >>> now = Timestamp.now()
        >>> later = now + Timedelta.from_s(10)
        >>> now < later
        True

        Together with :meth:`__eq__`, all relational operations (``<=``, ``>``, ``!=``, etc.) are supported.
        Timestamps are `totally ordered` (as supplied by :func:`python:functools.total_ordering`).

        Args:
            other: another timestamp
        """

        return self._value < other._value

    def __eq__(self, other: object) -> bool:
        """Check whether two :class:`Timestamps<Timestamp>` refer to the same instance of time:

        >>> now = Timestamp.now()
        >>> later = now + Timedelta.from_s(10)
        >>> now == later
        False

        Args:
            other: another timestamp
        """
        if not isinstance(other, Timestamp):
            return NotImplemented

        return self._value == other._value

    def __str__(self) -> str:
        """Yield a human-readable date-time string in the local timezone:

        >>> # in UTC+01:00, it was already 1 in the night when the UNIX epoch happened
        >>> str(Timestamp(0))
        '[0] 1970-01-01 01:00:00+01:00'
        """

        # Note we convert to local timezone with astimezone for printing
        return "[{}] {}".format(self.posix_ns, str(self.datetime.astimezone()))

    def __repr__(self) -> str:
        return f"Timestamp({self.posix_ns})"


@dataclass(frozen=True)
class TimeValue:
    """A `timestamp-value` pair.

    Unpack it like so:

    >>> tv = TimeValue(Timestamp.now(), 42.0)
    >>> (timestamp, value) = tv

    """

    __slots__ = ("timestamp", "value")

    timestamp: Timestamp
    value: float

    def __iter__(self) -> Iterator[Union["Timestamp", float]]:
        return iter((self.timestamp, self.value))


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


Metric = str
"""Type alias for strings that represent metric names
"""

JsonDict = Dict[str, Any]
"""Type alias for dicts that represent JSON data
"""
