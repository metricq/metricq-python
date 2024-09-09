#!/usr/bin/env python3
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
"""
This is an extremely advanced example for deep-dive development and debugging.
This is not used to show how MetricQ is usually used. As normal user of MetricQ
you use the derived classes of :class:`metricq.Client`, e.g.,
:class:`metricq.Source`, :class:`metricq.Sink`:, :class:`metricq.Subscriber`,
or, :class:`metricq.HistoryClient`.

This example shows how to set up a pure `metricq.Client` that can  controlled
with an aiomonitor. After this setup, you can connect to the monitor using
`telnet localhost 50101` (or `netcat`), inspect tasks and run code in a REPL.
"""
import asyncio
import logging

import aiomonitor  # type: ignore
import click_log  # type: ignore

import metricq
from metricq.cli import metricq_command

logger = metricq.get_logger()
click_log.basic_config(logger)
logger.setLevel("INFO")
logger.handlers[0].formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] [%(name)-20s] %(message)s"
)


async def run(server: str, token: str) -> None:
    async with metricq.Client(token, server) as client:
        logger.info("Client connected")
        with aiomonitor.start_monitor(
            asyncio.get_running_loop(), locals={"client": client}
        ):
            logger.debug("Monitor started")
            await client.stopped()


@metricq_command(default_token="client-py-example")
@click_log.simple_verbosity_option(logger)  # type: ignore
def main(server: str, token: str) -> None:
    asyncio.run(run(server, token))


if __name__ == "__main__":
    main()
