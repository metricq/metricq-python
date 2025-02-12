from metricq import get_logger
from metricq.cli import command


logger = get_logger()


logger.info("global scope")


@command(default_token="logging_test")
def run(server, token):
    logger.warning("in run")


if __name__ == "__main__":
    run()
