import datetime
import re
from functools import total_ordering
from typing import TYPE_CHECKING, Union, overload

if TYPE_CHECKING:
    from .timestamp import Timestamp


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
        The type is hashable.
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
        """
        An exact string representation of the duration preserving all nanosecond digits.
        If possible, a human-readable string is returned, e.g. ``100ms``.
        The result of this can be parsed by :meth:`from_string` without losing
        precision.
        """

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

    @overload
    def __floordiv__(self, other: int) -> "Timedelta":
        ...

    @overload
    def __floordiv__(self, other: "Timedelta") -> int:
        ...

    def __floordiv__(self, other: Union[int, "Timedelta"]) -> Union["Timedelta", int]:
        """Divide a duration by an integer or another :class:`Timedelta`.

        >>> td = Timedelta.from_s(10) // 3
        >>> td.s
        3.333333333
        >>> td.precise_string
        '3333333333ns'

        This divides the number of nanoseconds in this duration by `factor`
        using `Floor Division <https://www.python.org/dev/peps/pep-0238/#semantics-of-floor-division>`_,
        i.e. for some :code:`n: int` and :code:`td: Timedelta` we have

        >>> assert (td // n).ns == td.ns // n

        Division by another  :class:`Timedelta` yields an integral result:

        >>> assert Timedelta.from_s(10) // Timedelta.from_s(3) == 3

        Note:
            Floor Division produces *surprising* results for :code:`float` arguments
            and is therefore not supported here (i.e. :code:`3 // 0.2 == 14.0`).
            Use :meth:`__truediv__` if you want to scale a duration by a non-integer factor.
        """
        if isinstance(other, Timedelta):
            return self._value // other._value
        return Timedelta(self._value // other)

    @overload
    def __truediv__(self, other: float) -> "Timedelta":
        ...

    @overload
    def __truediv__(self, other: "Timedelta") -> float:
        ...

    def __truediv__(
        self, other: Union[float, "Timedelta"]
    ) -> Union["Timedelta", float]:
        """Divide a duration by a floating point or :class:`Timedelta`.

        >>> (Timedelta.from_s(10) / 2.5).precise_string
        '4s'

        This divides the number of nanoseconds in this duration by `factor`
        using `True Division <https://www.python.org/dev/peps/pep-0238/#semantics-of-true-division>`_,
        but truncates the result to an :code:`int`:

        >>> assert (td / x).ns == int(td.ns / x)

        where :code:`td: Timedelta` and :code:`x: float`.

        Division by another :class:`Timedelta` instead yields a :class:`float` result.

        Note:
            Use :meth:`__floordiv__` if you know that the divisor is an integer,
            this will prevent rounding errors.
        """
        if isinstance(other, Timedelta):
            return self._value / other._value
        return Timedelta(int(self._value / other))

    def __mul__(self, factor: float) -> "Timedelta":
        """Scale a duration by a :class:`float` factor."""
        return Timedelta(int(self._value * factor))

    def __mod__(self, other: "Timedelta") -> "Timedelta":
        """Return the remainder of the division of two durations."""
        return Timedelta(self._value % other._value)

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

    def __hash__(self) -> int:
        return hash(self._value)

    def __lt__(self, other: Union["Timedelta", datetime.timedelta]) -> bool:
        if isinstance(other, datetime.timedelta):
            return self.timedelta < other
        return self._value < other._value
