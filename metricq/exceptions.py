# Copyright (c) 2021, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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

"""
This module defines custom Exception classes for MetricQ.
In general, they are used for errors in the interaction with other agents.
Contrary, misuse of the API generally yields specific built-in errors, i.e., TypeError, ValueError, and, KeyError.
AssertionError / assert is only used for checking invariants within the library itself.
"""

from typing import Any


class RemoteError(Exception):
    """The remote has replied with an error."""


class RPCError(RemoteError):
    """An RPC returned an error code.

    This could be an issue with the input or on the other side.
    """


class HistoryError(RemoteError):
    """The database replied with an error to a history request.

    This could either be an issue with the request or of the database.
    """


class MessageError(Exception):
    """Something is semantically wrong within a received message."""


class InvalidHistoryResponse(MessageError):
    """A response to a history request could not be decoded."""

    def __init__(self, extra_message: str):
        super().__init__(
            (
                "Failed to parse inconsistent history response message: {}."
                + "This is probably not the callers fault, but caused by the db."
            ).format(extra_message)
        )


class NonMonotonicTimestamps(MessageError):
    """Timestamps in a history response are not strictly monotonic."""


class AgentStopped(Exception):
    """The agent was stopped unexpectedly.

    There is probably something wrong with the network.
    """


class ReceivedSignal(AgentStopped):
    """The agent was stopped by a specific signal."""

    def __init__(self, signal: str, *args: Any):
        self.signal = signal
        super().__init__(f"Received signal {signal} while running Agent", *args)


class ConnectFailed(AgentStopped):
    """The connection attempt of the agent failed."""


class ReconnectTimeout(AgentStopped):
    """An agent reconnect timed out."""


class PublishFailed(Exception):
    """Publishing to an exchange failed unexpectedly.

    The source exception is always attached as a cause.
    """
