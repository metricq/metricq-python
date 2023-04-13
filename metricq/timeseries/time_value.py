from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Dict

from deprecated.sphinx import deprecated

from .timestamp import Timestamp


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

    def __iter__(self) -> Iterator[Timestamp | float]:
        return iter([self.timestamp, self.value])

    @deprecated(
        version="5.0.0",
        reason=(
            "Use the individual properties instead and select an appropriate "
            "timestamp type."
        ),
    )
    # using Dict as return type to work around https://github.com/python/mypy/issues/15047
    def dict(self) -> Dict[str, Any]:
        """
        returns a dict representing the TimeValue instance.
        Keys are `timestamp` and `value`
        """
        return {
            "timestamp": self.timestamp.posix_ns,
            "value": self.value,
        }
