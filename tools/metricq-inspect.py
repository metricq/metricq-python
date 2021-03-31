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
logger.handlers[0].formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] [%(name)-20s] %(message)s"
)

click_completion.init()


class InspectSink(metricq.Sink):
    def __init__(
        self,
        metric: str,
        intervals_histogram: bool,
        chunk_sizes_histogram: bool,
        values_histogram: bool,
        print_data: bool,
        *args,
        **kwargs,
    ):
        self._metric = metric
        self.tokens = {}

        self.print_intervals = intervals_histogram
        self.print_chunk_sizes = chunk_sizes_histogram
        self.print_values = values_histogram
        self.print_data = print_data

        self.timestamps = []
        self.last_timestamp = None
        self.intervals = []
        self.values = []
        self.chunk_sizes = []
        super().__init__(*args, **kwargs)

    async def connect(self):
        await super().connect()

        await self.subscribe([self._metric])

        click.echo(
            click.style(
                f"Inspecting the metric '{self._metric}'... (Hit ctrl+C to stop)",
                fg="green",
            )
        )

    async def _on_data_message(self, message: aio_pika.IncomingMessage):
        async with message.process(requeue=True):
            body = message.body
            from_token = None
            with suppress(AttributeError):
                from_token = message.client_id
            metric = message.routing_key

            if from_token not in self.tokens:
                self.tokens[from_token] = 0

            self.tokens[from_token] += 1

            data_response = DataChunk()
            data_response.ParseFromString(body)

            self.chunk_sizes.append(len(data_response.value))

            await self._on_data_chunk(metric, data_response)

    async def on_data(self, metric: str, timestamp: metricq.Timestamp, value: float):
        if self.print_data:
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
                    "Received messages from: ",
                    fg="bright_red",
                )
            )

            for token, messages in self.tokens.items():
                click.echo(
                    click.style(
                        "{}: {}".format(token if token else "<unknown>", messages),
                        fg="bright_red",
                    )
                )

            click.echo()

            self.print_histograms()
        finally:
            super().on_signal(signal)

    def print_histogram(self, values):
        counts, bin_edges = np.histogram(values, bins="doane")
        fig = tpl.figure()
        labels = [
            "[{:#.6g} - {:#.6g})".format(bin_edges[k], bin_edges[k + 1])
            for k in range(len(bin_edges) - 2)
        ]
        labels.append(
            "[{:#.6g} - {:#.6g}]".format(
                bin_edges[len(bin_edges) - 2], bin_edges[len(bin_edges) - 1]
            )
        )
        fig.barh(counts, labels=labels)
        fig.show()

    def print_chunk_sizes_histogram(self):
        click.echo(
            click.style(
                "Distribution of the chunk sizes",
                fg="yellow",
            )
        )
        click.echo()

        self.print_histogram(self.chunk_sizes)

        click.echo()
        click.echo()

    def print_intervals_histogram(self):
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

    def print_values_histogram(self):
        click.echo(
            click.style("Distribution of the values of the data points", fg="yellow")
        )
        click.echo()

        self.print_histogram(self.values)

    def print_histograms(self):
        if self.print_chunk_sizes:
            self.print_chunk_sizes_histogram()

        if self.print_intervals and self.last_timestamp:
            self.print_intervals_histogram()

        if self.print_values:
            self.print_values_histogram()


@click.command(
    short_help="A tool usable to get an idea about the *current* behavior of a given metric. By definition, this only exploits live data."
)
@click.option("--server", default="amqp://localhost/")
@click.option("--token", default="metricq-inspect")
@click.option(
    "--intervals-histogram/--no-intervals-histogram",
    "-i/-I",
    default=True,
    help="Show an histogram of the observed distribution of durations between data points.",
)
@click.option(
    "--values-histogram/--no-values-histogram",
    "-h/-H",
    default=True,
    help="Show an histogram of the observed metric values.",
)
@click.option(
    "--chunk-sizes-histogram/--no-chunk-sizes-histogram",
    "-c/-C",
    default=False,
    help="Show an histogram of the observed chunk sizes of all messages received.",
)
@click.option("--print-data-points/--no-print-data-points", "-d/-D", default=False)
@click.argument("metric", required=True, nargs=1)
@click_log.simple_verbosity_option(logger, default="WARNING")
def main(
    server,
    token,
    metric,
    intervals_histogram,
    values_histogram,
    chunk_sizes_histogram,
    print_data_points,
):
    sink = InspectSink(
        metric=metric,
        token=token,
        management_url=server,
        intervals_histogram=intervals_histogram,
        chunk_sizes_histogram=chunk_sizes_histogram,
        values_histogram=values_histogram,
        print_data=print_data_points,
    )
    sink.run()


if __name__ == "__main__":
    main()
