from typing import TypeAlias

EventWaitResult: TypeAlias = tuple[list[object] | tuple[object, ...], dict[str, object]]
