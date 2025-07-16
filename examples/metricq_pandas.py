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
from datetime import timedelta

import click

import metricq
from metricq.pandas import PandasHistoryClient

logger = metricq.get_logger()


async def aget_history(server: str, token: str, metric: str) -> None:
    async with PandasHistoryClient(token=token, url=server) as client:
        now = metricq.Timestamp.now()

        delta = metricq.Timedelta.from_timedelta(timedelta(seconds=600))
        start_time = now - delta
        interval_max = metricq.Timedelta.from_timedelta(timedelta(seconds=10))

        aggregate_timeline = await client.history_aggregate_timeline(
            metric, start_time=start_time, end_time=now, interval_max=interval_max
        )
        click.echo(f"Resulting aggregate timeline for {metric}")
        click.echo(aggregate_timeline.describe())
        click.echo("dtypes:")
        click.echo(aggregate_timeline.dtypes)
        click.echo("full data:")
        click.echo("----------")
        click.echo(aggregate_timeline)
        click.echo("----------")

        raw_timeline = await client.history_raw_timeline(
            metric, start_time=start_time, end_time=now
        )
        click.echo(f"Resulting raw timeline for {metric}")
        click.echo(raw_timeline.describe())
        click.echo("dtypes:")
        click.echo(raw_timeline.dtypes)
        click.echo("full data:")
        click.echo("----------")
        click.echo(raw_timeline)
        click.echo("----------")


@metricq.cli.command(default_token="history-py-dummy")
@metricq.cli.metric_option(default="example.quantity")
def get_history(server: str, token: str, metric: str) -> None:
    asyncio.run(aget_history(server, token, metric))


if __name__ == "__main__":
    get_history()
