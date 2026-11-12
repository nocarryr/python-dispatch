from typing import TypeAlias

EventArgs: TypeAlias = tuple[object, ...]
EventKwargs: TypeAlias = dict[str, object]
EventArguments: TypeAlias = tuple[EventArgs, EventKwargs]
EventWaitResult: TypeAlias = tuple[list[object] | EventArgs, EventKwargs]
