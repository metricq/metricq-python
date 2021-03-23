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
from contextlib import suppress

import aio_pika
import click
import click_completion
import click_log
import numpy as np
import termplotlib as tpl

import metricq
from metricq.datachunk_pb2 import DataChunk
from metricq.logging import get_logger

logger = get_logger()

click_log.basic_config(logger)
logger.setLevel("INFO")
logger.handlers[0].formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] [%(name)-20s] %(message)s"
)

click_completion.init()


class InspectSink(metricq.Sink):
    def __init__(self, metric: str, histo: bool, *args, **kwargs):
        self._metric = metric
        self.tokens = set()
        self.histo = histo
        self.timestamps = []
        self.last_timestamp = None
        self.intervals = []
        self.values = []
        super().__init__(*args, **kwargs)

    async def connect(self):
        await super().connect()

        await self.subscribe([self._metric])

    async def _on_data_message(self, message: aio_pika.IncomingMessage):
        async with message.process(requeue=True):
            body = message.body
            from_token = None
            with suppress(AttributeError):
                from_token = message.client_id
            metric = message.routing_key

            self.tokens.add(from_token if from_token else "N/A")

            data_response = DataChunk()
            data_response.ParseFromString(body)

            await self._on_data_chunk(metric, data_response)

    async def on_data(self, metric: str, timestamp: metricq.Timestamp, value: float):
        click.echo(click.style("{}: {}".format(timestamp, value), fg="bright_blue"))
        self.timestamps.append(timestamp.posix)
        if self.last_timestamp:
            self.intervals.append(timestamp.posix - self.last_timestamp)
        self.last_timestamp = timestamp.posix
        self.values.append(value)

    def on_signal(self, signal):
        try:
            click.echo()
            click.echo(
                click.style(
                    "Received messages from: {}".format(", ".join(self.tokens)),
                    fg="bright_red",
                )
            )

            if self.histo and self.last_timestamp:
                self.print_histograms()

        finally:
            super().on_signal(signal)

    def print_histogram(self, values):
        counts, bin_edges = np.histogram(values)
        fig = tpl.figure()
        fig.hist(counts, bin_edges, orientation="horizontal", force_ascii=False)
        fig.show()

    def print_histograms(self):
        click.echo(
            click.style(
                "Distribution of the duration between consecutive data points in seconds",
                fg="yellow",
            )
        )
        click.echo()

        self.print_histogram(self.intervals)

        click.echo()
        click.echo()

        click.echo(
            click.style("Distribution of the values of the data points", fg="yellow")
        )
        click.echo()

        self.print_histogram(self.values)


@click.command()
@click.option("--server", default="amqp://localhost/")
@click.option("--token", default="metricq-inspect")
@click.option("--histo", is_flag=True)
@click.argument("metric", required=True, nargs=1)
@click_log.simple_verbosity_option(logger)
def source(server, token, metric, histo):
    # Initialize the DummySink class with a list of metrics given on the
    # command line.
    sink = InspectSink(metric=metric, token=token, management_url=server, histo=histo)

    # Run the sink.  This call will block until the connection is closed.
    sink.run()


if __name__ == "__main__":
    source()
