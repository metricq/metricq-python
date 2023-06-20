import datetime
from functools import total_ordering
from typing import Union, overload

from dateutil import tz
from dateutil.parser import isoparse as dateutil_isoparse

from .timedelta import Timedelta


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
        """
        Create a Timestamp from an aware datetime object. If you have a naive
        datetime object, consider using :meth:`from_local_datetime` instead.
        """
        if dt.tzinfo is None:
            raise TypeError(
                "cannot to parse naive datetime with `from_datetime`, "
                "consider using `from_local_datetime` if applicable"
            )
        delta = dt - Timestamp._EPOCH
        seconds = (delta.days * 24 * 3600) + delta.seconds
        microseconds = seconds * 1000000 + delta.microseconds
        return Timestamp(microseconds * 1000)

    @classmethod
    def from_local_datetime(cls, dt: datetime.datetime) -> "Timestamp":
        """
        Create a timestamp from a naive :class:`datetime` object that uses the
        local timezone.
        If you have a proper aware object, use :meth:`from_datetime` instead.

        This function uses `dateutil.tz.gettz()` which uses `/etc/localtime`.
        Using naive datetime object can be error-prone. Naive local times are
        ambiguous during daylight savings time adjustments.
        If you have to use this function, your workflow is probably broken.
        """
        if dt.tzinfo is not None:
            raise TypeError(
                "refusing to parse aware datetime with `from_local_datetime`, "
                "use `from_datetime` instead."
            )
        return cls.from_datetime(dt.replace(tzinfo=tz.gettz()))

    @classmethod
    def from_iso8601(cls, iso_string: str) -> "Timestamp":
        """Create a Timestamp from a `ISO 8601` date-time string.

        >>> Timestamp.from_iso8601("1970-01-01T00:00:00.0Z") == Timestamp(0)
        True

        This is a convenience method that parses the date-time string into a
        :class:`python:datetime.datetime` using
        :meth:`dateutil:dateutil.parser.isoparse`,
        and then calls :meth:`from_datetime` to create a :class:`Timestamp` from that.

        The provided `iso_string` must include timezone information. To parse
        local time strings, you must convert them yourself and use
        :meth:`from_local_datetime`. Or better yet, somehow create an aware
        :class:`python:datetime.datetime` and use :meth:`from_datetime`.

        Note:
            The parser only supports up to *6 sub-second digits*,
            further digits are simply dropped.
            If you need to parse timestamps with higher precision,
            you need to convert the string to nanoseconds yourself.

        Args:
            iso_string: a date-time string in `ISO 8601` format including a
                        timezone specifier.
        """
        dt = dateutil_isoparse(iso_string)
        if dt.tzinfo is None:
            raise TypeError("provided timestamp does not include timezone info")
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
    def __sub__(self, other: Timedelta) -> "Timestamp":
        ...

    @overload
    def __sub__(self, other: "Timestamp") -> Timedelta:
        ...

    def __sub__(
        self, other: Union[Timedelta, "Timestamp"]
    ) -> Union["Timestamp", Timedelta]:
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

    def __hash__(self) -> int:
        return hash(self._value)

    def __mod__(self, other: Timedelta) -> Timedelta:
        """
        Args:
            other: a time duration

        Returns:
            the remainder of the division of this timestamp (time since epoch) by a
            timedelta.
        """
        return Timedelta(self._value % other.ns)

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
