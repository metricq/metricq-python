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

import logging
from typing import Any

import click
import click_completion  # type: ignore
import click_log  # type: ignore

import metricq
from metricq.logging import get_logger

logger = get_logger()

click_log.basic_config(logger)
logger.setLevel("INFO")
logger.handlers[0].formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] [%(name)-20s] %(message)s"
)

click_completion.init()


# To implement a MetricQ Sink, subclass metricq.Sink
class DummySink(metricq.Sink):
    """A simple :term:`Sink` which, given a list of Metrics, will print their values as they arrive from the MetricQ network."""

    def __init__(self, metrics: list[str], *args: Any, **kwargs: Any):
        logger.info("initializing DummySink")
        # `metrics` contains the names of Metrics for which this Sink should print values
        self._metrics = metrics
        super().__init__(*args, **kwargs)

    # Override connect() to subscribe to the Metrics of interest after a connection has been established.
    async def connect(self) -> None:
        # First, let the base class connect to the MetricQ network.
        await super().connect()

        # After the connection is established, subscribe to the list of
        # requested metrics.  For each metric, we will receive every data point
        # which sent is to MetricQ from this point on.
        await self.subscribe(self._metrics)

    # The data handler, this method is called for every data point we receive
    async def on_data(
        self, metric: str, timestamp: metricq.Timestamp, value: float
    ) -> None:
        # For this example, we just print the datapoints to standard output
        click.echo(
            click.style("{}: {}, {}".format(metric, timestamp, value), fg="bright_blue")
        )


@click.command()
@click.option("--server", default="amqp://localhost/")
@click.option("--token", default="sink-py-dummy")
@click.option("-m", "--metrics", multiple=True, required=True)
@click_log.simple_verbosity_option(logger)  # type: ignore
def source(server: str, token: str, metrics: list[str]) -> None:
    # Initialize the DummySink class with a list of metrics given on the
    # command line.
    sink = DummySink(metrics=metrics, token=token, management_url=server)

    # Run the sink.  This call will block until the connection is closed.
    sink.run()


if __name__ == "__main__":
    source()
