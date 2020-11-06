#!/usr/bin/env python

import logging

import click
import click_log

from metricq import rpc_handler
from metricq.logging import get_logger
from metricq.transformer import Transformer

logger = get_logger()

click_log.basic_config(logger)
logger.setLevel("INFO")
logger.handlers[0].formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)-8s] [%(name)-20s] %(message)s"
)


class DummyTransformer(Transformer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factors = dict()

    @rpc_handler("config")
    async def on_config(self, **config):
        translations = config["metrics"]
        output_metrics = [str(metric["output"]) for metric in translations]
        input_metrics = [str(metric["input"]) for metric in translations]

        self.output_metrics.chunk_size = 10

        await self.subscribe(input_metrics)
        await self.declare_metrics(metrics=output_metrics)

        self.factors = {t["input"]: (t["output"], t["factor"]) for t in translations}

    async def on_data(self, metric, timestamp, value):
        output, factor = self.factors[metric]
        logger.info(
            "Got message: ({}) {:.4f} -> {:.4f} ({})",
            metric,
            value,
            value * factor,
            output,
        )
        await self.send(output, timestamp, value * factor)


@click.command()
@click.option("--server", default="amqp://localhost/")
@click.option("--token", default="transformer-py-dummy")
@click_log.simple_verbosity_option(logger)
def transfom(server, token):
    transfomer = DummyTransformer(token=token, management_url=server)

    # run the sink. This call will block until the connection is closed.
    transfomer.run()


if __name__ == "__main__":
    transfom()
