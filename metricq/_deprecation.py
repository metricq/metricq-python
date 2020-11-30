import asyncio
import contextlib
import functools
import warnings


@contextlib.contextmanager
def warn_deprecated(func, reason):
    with warnings.catch_warnings():
        warnings.simplefilter("always", category=DeprecationWarning)
        name = func.__qualname__
        warnings.warn(
            f"{name}() is deprecated: {reason}", DeprecationWarning, stacklevel=4
        )

        yield


class deprecated:
    def __init__(self, *, reason):
        self.reason = reason

    def __call__(self, func):
        @functools.wraps(func)
        async def async_wrapped(*args, **kwargs):
            with warn_deprecated(func, self.reason):
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            with warn_deprecated(func, self.reason):
                return func(*args, **kwargs)

        return async_wrapped if asyncio.iscoroutine(func) else wrapped
