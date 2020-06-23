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


class MetricQDiscover(metricq.Agent):
    def __init__(self, server):
        super().__init__("discover", server, add_uuid=True)

    async def discover(self):
        await self.connect()
        await self.rpc_consume()

        self._management_broadcast_exchange = await self._management_channel.declare_exchange(
            name=self._management_broadcast_exchange_name,
            type=aio_pika.ExchangeType.FANOUT,
            durable=True,
        )

        await self.rpc(
            self._management_broadcast_exchange,
            "discover",
            response_callback=self.on_discover,
            function="discover",
            cleanup_on_response=False,
        )

        await asyncio.sleep(30)

    def on_discover(self, from_token, **kwargs):
        if "error" in kwargs:
            logger.warning(
                "Agent '{}' failed to properly respond to discover: {}",
                from_token,
                kwargs["error"],
            )
            return

        if "alive" in kwargs:
            alive = kwargs["alive"]
        else:
            logger.warning(
                f"Agent '{from_token}' misses 'alive' attribute in discover response"
            )
            alive = True

        if "startingTime" in kwargs:
            startingTime = kwargs["startingTime"]
        else:
            logger.warning(
                f"Agent '{from_token}' misses 'startingTime' attribute in discover response"
            )

        if "uptime" in kwargs:
            uptime = kwargs["uptime"]
        else:
            uptime = -1e9

        click.echo(click.style(from_token, fg="cyan"), nl=False)
        alive = "✔️" if alive else "❌"
        click.echo(f": {alive} {startingTime} (up for {int(uptime//1e9)} sec)")


@click.command()
@click_log.simple_verbosity_option(logger)
@click.option("--server", default="amqp://localhost/")
def discover_command(server):
    d = MetricQDiscover(server)

    asyncio.run(d.discover())


if __name__ == "__main__":
    discover_command()
