import logging
import sys
from typing import Any, Callable, Optional, TypeVar, Union, cast

import click
import click_log  # type: ignore
from click import Context, option
from dotenv import find_dotenv, load_dotenv

from .. import get_logger
from .params import MetricParam, TemplateStringParam
from .syslog import SyslogFormatter, get_syslog_handler

# We do not interpolate (i.e. replace ${VAR} with corresponding environment variables).
# That is because we want to be able to interpolate ourselves for metrics and tokens
# using the same syntax. If it was only ${USER} for the token, we could use the
# override functionality, but most unfortunately there is no standard environment
# variable for the hostname. Even $HOST on zsh is not actually part of the environment.
# ``override=false`` just means that environment variables have priority over the
# env files.
load_dotenv(dotenv_path=find_dotenv(".metricq"), interpolate=False, override=False)


FC = TypeVar("FC", bound=Union[Callable[..., Any], click.Command])


def metricq_syslog_option() -> Callable[[FC], FC]:
    """
    Exposes the -\\-syslog option as a click param.

    The program will try read the 'token' from the click params.
    if the token is not set, the default value of 'metricq.program' will be used.
    That's why the @metricq_syslog_option should be the 2nd decorator in the chain.

    It is recommended to use the :py:func:`~metricq.cli.decorator.metricq_command` decorator instead of using this
    function directly.
    """

    def enable_syslog(ctx: Context, param: Any | None, value: Optional[str]) -> None:
        if value is not None:
            logger = get_logger()
            if value == "":
                value = None

            program_name = ctx.params.get("token", sys.argv[0])

            handler = get_syslog_handler(value)
            handler.setFormatter(SyslogFormatter(name=program_name))
            logger.addHandler(handler)

    return option(
        "--syslog",
        help="Enable syslog logging by specifying the a Unix socket or host:port for the logger. If --syslog is set "
        "but no value is specified, the default of localhost:514 will be used.",
        callback=enable_syslog,
        expose_value=False,
        is_flag=False,
        flag_value="",
    )


def metricq_server_option() -> Callable[[FC], FC]:
    """
    Allows the User to provide a -\\-server option. This option has no input validation and therefore can be any string.

    It is recommended to use the :py:func:`~metricq.cli.decorator.metricq_command` decorator instead
    of using this function directly.

    """
    return option(
        "--server",
        type=TemplateStringParam(),
        metavar="URL",
        required=True,
        help="MetricQ server URL.",
    )


def metricq_token_option(default: str) -> Callable[[FC], FC]:
    """
    Allows the User to provide a -\\-metric option. The input must follow the specification provided
    `here <https://github.com/metricq/metricq/wiki/Metrics#selecting-good-metric-names>`_.

    It is recommended to use the :py:func:`~metricq.cli.decorator.metricq_command` decorator instead of using this
    function directly.
    """
    return option(
        "--token",
        type=TemplateStringParam(),
        metavar="CLIENT_TOKEN",
        default=default,
        show_default=True,
        help="A token to identify this client on the MetricQ network.",
    )


def metricq_metric_option(
    default: Optional[str] = None, multiple: bool = False, required: bool = False
) -> Callable[[FC], FC]:
    """
    The metric option can be used to select one or more metrics the program should use.
    The metric can be set with the -\\-metric or -m parameter. If no default value is set, the parameter is required.
    The Metric syntax is specified by the :py:class:`~metricq.cli.params.MetricParam`.

    Args:
        default: The default metric. Defaults to `None`. You can only set one default, even if the program allows
                multiple inputs.
        multiple: If `True`, allows multiple metrics to be specified. Defaults to `False`.
        required: If `True`, makes the -\\-metric option required. Defaults to `False`. If required is set and no
                default is provided, at least one metric input is required.

    **Example**::

        @metricq_command(default_token="example.program")
        @metricq_metricq_option(required=true, default="example.metric")
        def metric_example(
            server: str, token: str, metric: str
        ) -> None:
            # Initialize the DummySink class with a list of metrics given on the
            # command line.
            sink = DummySink(metrics=metric, token=token, url=server)

            # Run the sink. This call will block until the connection is closed.
            sink.run()

        @metricq_command(default_token="example.program")
        @metricq_metricq_option(required=true, multiple=True) # <-- multiple is set
        def multi_metric_example(
            server: str, token: str, metric: List[str]
        ) -> None:
            sink = DummySink(metrics=metric, token=token, url=server)
            sink.run()

    """
    response_default = default if (default is None or not multiple) else [default]
    help = "Use the -–metric / -m parameter to specify which metric the program should use."
    if multiple:
        help += " Can be used multiple times to specify several metrics."

    return option(
        "--metric",
        "-m",
        type=MetricParam(),
        metavar="METRIC",
        show_default=True,
        required=required,
        default=response_default,
        multiple=multiple,
        help=help,
    )


def get_metric_command_logger() -> logging.Logger:
    logger = get_logger()
    logger.setLevel(logging.WARNING)
    click_log.basic_config(logger)

    return logger


def metricq_command(
    default_token: str, client_version: str | None = None
) -> Callable[[FC], click.Command]:
    """Standardized wrapper for click commands

    Args:
        default_token: default token that will be used if no token is provided
        client_version: version of the client

    Returns:
        Callable[[FC], click.Command]: click command

    The :py:func:`~metricq.cli.wrapper.metricq_command` is the first parameter of any given click/cli command. The main purpose is to provide the most used parameters.
    These parameters are 'server' and 'token'.

    -  -\\-server:
        The Server param is used to specify the amqp url of the Network. for example: amqp://localhost/

        The server param can be set using the environment variable METRICQ_SERVER or adding the --server {value} option to the cli command

    -  -\\-token:
        The Token is used to identify each program on the metricq network. for example: sink-py-dummy

        The token param can be set using the environment variable METRICQ_TOKEN or adding the --token {value} option
        to the cli command

    -  -\\-syslog:
        The Syslog param is used to enable syslog. It can be used with or without parameter.

        If used without parameter (for example: ``metricq-check --syslog`` ) the Syslog will default to localhost:514.

        You can also specify a Unix socket (for example: /dev/log) or a custom host (for example: example.com:514)
        by adding the value to the syslog flag (for example: ``metricq-check --syslog example.com:514``)


    Full example:
    ``metricq-check --server amqp://localhost/ --token sink-py-dummy --syslog``

    **Example**::

        @metricq_command(default_token="source-py-dummy")
        def dummy(
            server: str, token: str
        ) -> None:
            src = DummySource(token=token, url=server)
            src.run()


        if __name__ == "__main__":
            dummy()

    """
    logger = get_metric_command_logger()

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
                        metricq_syslog_option()(
                            click.command(
                                context_settings=context_settings, epilog=epilog
                            )(func)
                        )
                    )
                )
            )
        )

    return decorator
