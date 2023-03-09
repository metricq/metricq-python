from typing import Any, Dict

from .time_aggregate import TimeAggregate
from .time_value import TimeValue
from .timedelta import Timedelta
from .timestamp import Timestamp

Metric = str
"""Type alias for strings that represent metric names
"""

JsonDict = Dict[str, Any]
"""Type alias for dicts that represent JSON data
"""


__all__ = ["TimeAggregate", "TimeValue", "Timedelta", "Timestamp", "Metric", "JsonDict"]
