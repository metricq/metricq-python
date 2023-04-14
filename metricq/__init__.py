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

from . import exceptions
from .agent import Agent
from .client import Client
from .data_client import DataClient
from .drain import Drain
from .history_client import HistoryClient
from .interval_source import IntervalSource
from .logging import get_logger
from .rpc import rpc_handler
from .sink import DurableSink, Sink
from .source import Source
from .subscription import Subscriber
from .synchronous_source import SynchronousSource
from .timeseries import (
    JsonDict,
    MetadataDict,
    Metric,
    TimeAggregate,
    Timedelta,
    Timestamp,
    TimeValue,
)
from .version import __version__

# Please keep sorted alphabetically to avoid merge conflicts
__all__ = [
    "Agent",
    "Client",
    "DataClient",
    "Drain",
    "DurableSink",
    "exceptions",
    "get_logger",
    "HistoryClient",
    "IntervalSource",
    "JsonDict",
    "MetadataDict",
    "Metric",
    "rpc_handler",
    "Sink",
    "Source",
    "Subscriber",
    "SynchronousSource",
    "TimeAggregate",
    "Timedelta",
    "Timestamp",
    "TimeValue",
    "__version__",
]
