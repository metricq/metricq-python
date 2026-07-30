#!/usr/bin/env python3
# Copyright (c) 2019, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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

from typing import Any

import click

import metricq
from metricq import Metric
from metricq.cli import metricq_command
from metricq.cli.decorator import metricq_metric_option
from metricq.logging import get_logger

logger = get_logger()


# Unlike a plain Sink, a DurableSink registers under its fixed Token (no
# random UUID suffix) and receives a persistent configuration via the
# `sink.register` RPC. That means it reconnects to the *same* data queue
# every time it (re)starts, so data published while it was completely down
# is not lost -- it's waiting in the queue when it comes back. A plain Sink
# gets a fresh UUID (and therefore a fresh, empty queue) every time the
# process restarts.
class DummyDurableSink(metricq.DurableSink):
    """A :term:`Sink` which, given a list of Metrics, will print their values as they arrive from the MetricQ network."""

    def __init__(self, metrics: list[Metric], *args: Any, **kwargs: Any):
        logger.info("initializing DummyDurableSink")
        self._metrics = metrics
        super().__init__(*args, **kwargs)

    @metricq.rpc_handler("config")
    async def _on_config(self, **config: Any) -> None:
        logger.info("DummyDurableSink config: {}", config)

    async def connect(self) -> None:
        # First, register and let the base class complete the handshake.
        await super().connect()

        # After the connection is established, subscribe to the list of
        # requested metrics.  For each metric, we will receive every data
        # point sent to MetricQ from this point on -- including whatever
        # accumulated in our durable queue while we were disconnected.
        await self.subscribe(self._metrics)

    async def on_data(
        self, metric: str, timestamp: metricq.Timestamp, value: float
    ) -> None:
        click.echo(
            click.style("{}: {}, {}".format(metric, timestamp, value), fg="bright_green")
        )


@metricq_command(default_token="sink-py-durable-dummy")
@metricq_metric_option(multiple=True)
def source(server: str, token: str, metric: list[Metric]) -> None:
    sink = DummyDurableSink(metrics=metric, token=token, url=server)
    sink.run()


if __name__ == "__main__":
    source()
