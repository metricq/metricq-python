#!/usr/bin/env python3
# Copyright (c) 2020, ZIH, Technische Universitaet Dresden, Federal Republic of Germany
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
import logging

import aio_pika

import click
import click_completion
import click_log

import metricq

logger = metricq.get_logger()
logger.setLevel(logging.WARN)
click_log.basic_config(logger)
logger.handlers[0].formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] [%(name)-20s] %(message)s"
)

click_completion.init()


class MetricQSpy(metricq.HistoryClient):
    def __init__(self, server):
        super().__init__("spy", server, add_uuid=True)

    async def spy(self, patterns):
        await self.connect()

        for pattern in patterns:
            result = await self.get_metrics(selector=pattern, metadata=True)

            for metric, metadata in result.items():
                click.echo(click.style(metric, fg="cyan"), nl=False)
                click.echo(metadata)

                if "historic" in metadata and metadata["historic"]:
                    try:
                        await self.history_data_request(
                            metric,
                            start_time=metricq.Timestamp.ago(
                                metricq.Timedelta.from_s(60)
                            ),
                            end_time=metricq.Timestamp.now(),
                            interval_max=metricq.Timedelta.from_s(60),
                            timeout=5,
                        )
                    except asyncio.TimeoutError:
                        pass

        await self.stop()

    async def _on_history_response(self, message: aio_pika.Message):
        click.echo("Stored on: ", nl=False)
        click.echo(click.style(message.app_id, fg="red"))

        await super()._on_history_response(message)


@click.command()
@click_log.simple_verbosity_option(logger)
@click.option("--server", default="amqp://localhost/")
@click.argument("metrics", required=True, nargs=-1)
def discover_command(server, metrics):
    d = MetricQSpy(server)

    asyncio.run(d.spy(metrics))


if __name__ == "__main__":
    discover_command()
