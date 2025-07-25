#!/usr/bin/env python3
# Copyright (c) 2018, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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

import asyncio
import pprint
from datetime import timedelta

import click

import metricq

logger = metricq.get_logger()


async def aget_history(
    server: str, token: str, metric: str, list_metrics: bool, list_metadata: bool
) -> None:
    async with metricq.HistoryClient(token=token, url=server) as client:
        if list_metrics:
            metrics = await client.get_metrics(metric, metadata=False)
            click.echo(
                click.style(
                    "metrics matching {}:\n{}".format(metric, metrics), fg="bright_blue"
                )
            )
            return

        if list_metadata:
            metadata = await client.get_metrics(metric)
            pp = pprint.PrettyPrinter(indent=4)
            click.echo(
                click.style(
                    "metrics matching {}:\n{}".format(metric, pp.pformat(metadata)),
                    fg="bright_blue",
                )
            )
            return

        now = metricq.Timestamp.now()
        last_timevalue = await client.history_last_value(metric)
        assert last_timevalue is not None
        click.echo(
            click.style(
                "Last entry: {} ({} ago) value: {}".format(
                    last_timevalue.timestamp,
                    now - last_timevalue.timestamp,
                    last_timevalue.value,
                ),
                fg="bright_blue",
            )
        )

        delta = metricq.Timedelta.from_timedelta(timedelta(seconds=600))
        start_time = now - delta
        interval_max = metricq.Timedelta.from_timedelta(timedelta(seconds=10))
        result = await client.history_data_request(
            metric, start_time=start_time, end_time=now, interval_max=interval_max
        )

        click.echo("Values in the last {}".format(delta))
        for aggregate in result.aggregates():
            click.echo(aggregate)


@metricq.cli.command(default_token="history-py-dummy")
@metricq.cli.metric_option()
@click.option("--list-metrics", is_flag=True)
@click.option("--list-metadata", is_flag=True)
def get_history(
    server: str, token: str, metric: str, list_metrics: bool, list_metadata: bool
) -> None:
    if not (list_metrics or list_metadata) and metric is None:
        metric = "example.quantity"
    asyncio.run(aget_history(server, token, metric, list_metrics, list_metadata))


if __name__ == "__main__":
    get_history()
