# FROM https://stackoverflow.com/a/36294984/620382
import functools
import logging
import types
from collections.abc import Callable
from typing import Optional, TypeVar

T = TypeVar("T")


def _get_message(record: logging.LogRecord) -> str:
    """Replacement for logging.LogRecord.getMessage
    that uses the new-style string formatting for
    it's messages"""
    msg = str(record.msg)
    args = record.args
    if args:
        if not isinstance(args, tuple):
            args = (args,)
        msg = msg.format(*args)
    return msg


def _handle_wrap(fcn: Callable[..., T]) -> Callable[..., T]:
    """Wrap the handle function to replace the passed in
    record's getMessage function before calling handle"""

    @functools.wraps(fcn)
    def handle(record: logging.LogRecord) -> T:
        record.getMessage = types.MethodType(_get_message, record)  # type: ignore[method-assign]
        return fcn(record)

    return handle


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance that uses new-style string formatting"""
    log = logging.getLogger(name)
    if not hasattr(log, "_newstyle"):
        log.handle = _handle_wrap(log.handle)  # type: ignore[method-assign]
    setattr(log, "_newstyle", True)
    return log
