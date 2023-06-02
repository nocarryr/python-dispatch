from typing import Union, Iterable, Iterator, Callable
import asyncio

import pydispatch
from .dispatch import DoesNotExistError, _GLOBAL_DISPATCHER
from .utils import iscoroutinefunction, WeakMethodContainer

__all__ = ('receiver',)

class CallbackCache:
    def __init__(self):
        self.cache = {}

    def add(self, name: str, func: Callable):
        wr_contain = self.cache.get(name)
        if wr_contain is None:
            wr_contain = WeakMethodContainer()
            self.cache[name] = wr_contain
        wr_contain.add_method(func)

    def get(self, name: str) -> Iterator[Callable]:
        wr_contain = self.cache.get(name)
        if wr_contain is not None:
            del self.cache[name]
            yield from wr_contain.iter_methods()
        yield from []

    def __contains__(self, name: str) -> bool:
        return name in self.cache


_CACHED_CALLBACKS = CallbackCache()


def receiver(
    event_name: Union[str, Iterable[str]],
    cache: bool = False,
    auto_register: bool = False
):
    """Decorator to bind a function or method to the :ref:`global-dispatcher`

    Examples:

        >>> import pydispatch

        >>> pydispatch.register_event('foo')

        >>> @pydispatch.receiver('foo')
        ... def on_foo(value, **kwargs):
        ...     print(f'on_foo: "{value}"')

        >>> pydispatch.emit('foo', 'spam')
        on_foo: "spam"

        Using the *cache* argument

        >>> @pydispatch.receiver('bar', cache=True)
        ... def on_bar(value, **kwargs):
        ...     print(f'on_bar: "{value}"')

        >>> pydispatch.register_event('bar')
        >>> pydispatch.emit('bar', 'eggs')
        on_bar: "eggs"

        Using *auto_register*

        >>> @pydispatch.receiver('baz', auto_register=True)
        ... def on_baz(value, **kwargs):
        ...     print(f'on_baz: "{value}"')

        >>> pydispatch.emit('baz', 'ham')
        on_baz: "ham"

        Receiving multiple events

        >>> @pydispatch.receiver(['event_one', 'event_two'], auto_register=True)
        ... def on_event_one_or_two(value, **kwargs):
        ...     print(value)

        >>> pydispatch.emit('event_one', 1)
        1
        >>> pydispatch.emit('event_two', 2)
        2


    Arguments:
        event_name: Event name (or names) to bind the callback to.
            Can be a string or an :term:`iterable` of strings
        cache: If the event does not exist yet and this is ``True``,
            the callback will be held in a cache until it has been registered.
            If ``False``, a :class:`~.DoesNotExistError` will be raised.
            (Default is ``False``)
        auto_register: If the event does not exist and this is ``True``,
            it will be registered on the :ref:`global-dispatcher`.
            (Default is ``False``)

    .. versionadded:: 0.2.2
    """
    def _decorator(func: Callable):
        is_async = iscoroutinefunction(func)

        if isinstance(event_name, str):
            event_names = [event_name]
        else:
            event_names = event_name
        bind_kwargs = {ev:func for ev in event_names}
        if auto_register or cache:
            for name in event_names:
                if not _GLOBAL_DISPATCHER._has_event(name):
                    if auto_register:
                        pydispatch.register_event(name)
                    elif cache:
                        _CACHED_CALLBACKS.add(name, func)
                        del bind_kwargs[name]
        if len(bind_kwargs):
            if is_async:
                bind_kwargs['__aio_loop__'] = asyncio.get_event_loop()
            pydispatch.bind(**bind_kwargs)
        return func
    return _decorator


def _post_register_hook(*names):
    """Called in :func:`pydispatch.register_event` to search for cached callbacks
    """
    for name in names:
        if name not in _CACHED_CALLBACKS:
            continue
        bind_kwargs = {name:cb for cb in _CACHED_CALLBACKS.get(name)}
        is_async = any((iscoroutinefunction(cb) for cb in bind_kwargs.values()))
        if is_async:
            loop = asyncio.get_event_loop()
            pydispatch.bind_async(loop, **bind_kwargs)
        else:
            pydispatch.bind(**bind_kwargs)
