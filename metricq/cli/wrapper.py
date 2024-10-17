import logging
import re
import socket
import time
from functools import wraps
from logging.handlers import SysLogHandler
from typing import Callable, Optional, cast

import click
import click_log  # type: ignore
from click import option
from dotenv import find_dotenv, load_dotenv

from .. import get_logger
from .params import TemplateStringParam
from .types import FC

# We do not interpolate (i.e. replace ${VAR} with corresponding environment variables).
# That is because we want to be able to interpolate ourselves for metrics and tokens
# using the same syntax. If it was only ${USER} for the token, we could use the
# override functionality, but most unfortunately there is no standard environment
# variable for the hostname. Even $HOST on zsh is not actually part of the environment.
# ``override=false`` just means that environment variables have priority over the
# env files.
load_dotenv(dotenv_path=find_dotenv(".metricq"), interpolate=False, override=False)


def metricq_server_option() -> Callable[[FC], FC]:
    return option(
        "--server",
        type=TemplateStringParam(),
        metavar="URL",
        required=True,
        help="MetricQ server URL.",
    )


def metricq_token_option(default: str) -> Callable[[FC], FC]:
    return option(
        "--token",
        type=TemplateStringParam(),
        metavar="CLIENT_TOKEN",
        default=default,
        show_default=True,
        help="A token to identify this client on the MetricQ network.",
    )


def get_metric_command_looger() -> logging.Logger:
    logger = get_logger()
    logger.setLevel(logging.WARNING)
    click_log.basic_config(logger)

    return logger


def metricq_command(
    default_token: str, client_version: str | None = None
) -> Callable[[FC], click.Command]:
    logger = get_metric_command_looger()

    log_decorator = cast(
        Callable[[FC], FC], click_log.simple_verbosity_option(logger, default="warning")
    )
    context_settings = {"auto_envvar_prefix": "METRICQ"}
    epilog = (
        "All options can be passed as environment variables prefixed with 'METRICQ_'."
        "I.e., 'METRICQ_SERVER=amqps://...'.\n"
        "\n"
        "You can also create a '.metricq' file in the current or home directory that "
        "contains environment variable settings in the same format.\n"
        "\n"
        "Some options, including server and token, can contain placeholders for $USER "
        "and $HOST."
    )

    def decorator(func: FC) -> click.Command:
        return click.version_option(version=client_version)(
            log_decorator(
                metricq_token_option(default_token)(
                    metricq_server_option()(
                        click.command(context_settings=context_settings, epilog=epilog)(
                            func
                        )
                    )
                )
            )
        )

    return decorator


def metric_input(
    required: bool = True, default: Optional[str] = None
) -> Callable[[FC], FC]:
    valid_metric_regex = r"([a-zA-Z][a-zA-Z0-9_]+\.)+[a-zA-Z][a-zA-Z0-9_]+"

    def decorator(func):  # type: ignore
        @click.option("--metric", default=default, help="Metric input")
        @wraps(func)
        def wrapper(*args, metric, **kwargs):  # type: ignore
            if metric is not None:
                if not re.match(valid_metric_regex, metric):
                    raise ValueError(f"Invalid metric format: {metric}")

            if metric is None and required:
                raise Exception("Input metric is missing.")

            return func(*args, metric=metric, **kwargs)

        return wrapper

    return decorator


class SyslogFormatter(logging.Formatter):
    def __init__(self, *args, name: str = "metricq", **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.program = name

    def format(self, record: logging.LogRecord) -> str:
        severity_map = {
            logging.CRITICAL: 2,  # LOG_CRIT
            logging.ERROR: 3,  # LOG_ERR
            logging.WARNING: 4,  # LOG_WARNING
            logging.INFO: 6,  # LOG_INFO
            logging.DEBUG: 7,  # LOG_DEBUG
        }
        severity = severity_map.get(record.levelno, 6)

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        hostname = socket.gethostname()
        pid = record.process
        program = self.program
        pri = (SysLogHandler.LOG_USER * 8) + severity

        # Format the header as "<PRI> TIMESTAMP HOSTNAME PROGRAM[PID]: MESSAGE"
        syslog_header = f"<{pri}> {timestamp} {hostname} {program}[{pid}]: "

        message = super().format(record)
        return syslog_header + message


def metric_syslog(
    required: bool = True, default: Optional[str] = None
) -> Callable[[FC], FC]:
    validation_regex = r"^((?:(?:\d{1,3}\.){3}\d{1,3})|(?:[a-zA-Z0-9-]{1,63}\.?)+[a-zA-Z]{2,63}):([0-9]{1,5})$"

    def decorator(func):  # type: ignore
        @click.option("--syslog", default=default, help="Syslog url")
        @wraps(func)
        def wrapper(*args, syslog, **kwargs):  # type: ignore
            if syslog is not None:
                if not re.match(validation_regex, syslog):
                    raise ValueError(
                        "The syslog input is malformed. Use the following syntax: ip:port or hostname:port"
                    )
                logger = get_logger()

                ip, port = syslog.split(":")
                program_name = "metricq-process"

                if kwargs.get("token") is not None:
                    program_name = str(kwargs.get("token"))

                handler = SysLogHandler(
                    address=(ip, int(port)), facility=SysLogHandler.LOG_USER
                )
                handler.setFormatter(SyslogFormatter(name=program_name))
                logger.addHandler(handler)

            return func(*args, **kwargs)

        return wrapper

    return decorator
