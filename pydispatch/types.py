import sys
from collections.abc import Callable
from typing import TypeAlias

if sys.version_info >= (3, 13):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

P = ParamSpec('P', default=...)
EventCallback: TypeAlias = Callable[P, object]
EventArgs: TypeAlias = tuple[object, ...]
EventKwargs: TypeAlias = dict[str, object]
EventArguments: TypeAlias = tuple[EventArgs, EventKwargs]
EventWaitResult: TypeAlias = tuple[list[object] | EventArgs, EventKwargs]
