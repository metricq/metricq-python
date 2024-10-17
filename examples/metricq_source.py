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

import random
from typing import Any

import metricq
from metricq.cli import metricq_command
from metricq.logging import get_logger

logger = get_logger()


class DummySource(metricq.IntervalSource):
    def __init__(self, *args: Any, **kwargs: Any):
        logger.info("initializing DummySource")
        super().__init__(*args, **kwargs)

    @metricq.rpc_handler("config")
    async def _on_config(self, **config: Any) -> None:
        logger.info("DummySource config: {}", config)

        # Set the update period
        rate = config["rate"]
        self.period = 1 / rate

        # Supply some metadata for the metric declared below
        metadata = {
            "rate": rate,
            "description": "A simple dummy metric providing random values, sent from a python DummySource",
            "unit": "",  # unit-less metrics indicate this with an empty string
        }
        await self.declare_metrics({"test.py.dummy": metadata})

    async def update(self) -> None:
        # Send a random value at the current time:
        await self.send(
            "test.py.dummy", time=metricq.Timestamp.now(), value=random.random()
        )


@metricq_command(default_token="source-py-dummy")
def source(server: str, token: str) -> None:
    src = DummySource(token=token, url=server)
    src.run()


if __name__ == "__main__":
    source()
