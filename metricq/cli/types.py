from typing import Any, Callable, TypeVar, Union

import click

FC = TypeVar("FC", bound=Union[Callable[..., Any], click.Command])
