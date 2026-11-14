:mod:`pydispatch.dispatch`
==========================

.. automodule:: pydispatch.dispatch

Dispatcher class
----------------

.. autoclass:: pydispatch.dispatch.Dispatcher
    :members:

Event class
-----------

An :class:`~pydispatch.dispatch.Event` can optionally specify the arguments
accepted by its listeners and emission calls for static type checking::

    from pydispatch import Event

    changed: Event[[int, str]] = Event("changed")

    def on_changed(value: int, label: str) -> None:
        print(value, label)

    changed.add_listener(on_changed)
    changed(42, "temperature")

Async functions and bound methods with compatible signatures can also be
registered. Async listeners still require the ``__aio_loop__`` argument.
Listeners must be Python functions or bound methods; arbitrary callable objects
are not supported by the weak-reference storage.
This typing is opt-in and does not check arguments at runtime; unparameterized
events remain dynamically typed. An awaited event returns its arguments as a
tuple and dictionary without preserving their individual static types.

Events accessed by name through :class:`~pydispatch.dispatch.Dispatcher` remain
dynamic: the type checker does not associate an event name with a signature.

.. versionchanged:: 0.3.0
    Events may be parameterized with their listener argument types.

.. autoclass:: pydispatch.dispatch.Event
    :members:


Exceptions
----------

.. autoclass:: pydispatch.dispatch.DoesNotExistError
    :members:

.. autoclass:: pydispatch.dispatch.ExistsError
    :members:

.. autoclass:: pydispatch.dispatch.EventExistsError
    :members:

.. autoclass:: pydispatch.dispatch.PropertyExistsError
    :members:
