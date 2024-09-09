import logging
from typing import Callable, cast

import click
import click_log  # type: ignore
from click import option
from dotenv import find_dotenv, load_dotenv

from .. import get_logger
from .params import FC, TemplateStringParam

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
