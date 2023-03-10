from dataclasses import dataclass
from typing import Any, Iterator

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

    def dict(self) -> dict[str, Any]:
        """
        returns a dict representing the TimeValue instance.
        Keys are `timestamp` and `value`
        """
        return {
            "timestamp": self.timestamp.posix_ns,
            "value": self.value,
        }
