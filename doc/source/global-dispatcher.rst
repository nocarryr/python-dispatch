.. _global-dispatcher:

Global Dispatcher
=================

.. currentmodule:: pydispatch

.. versionadded:: 0.2.2

At the module-level, most of the functionality of :class:`~.dispatch.Dispatcher`
can be used directly as a `singleton`_ instance.  Note that this interface only
supports event dispatching (not :ref:`properties`).

When used this way, the concept is similar to the `Signals Framework`_ found in Django.

Basic Usage
-----------

Events can be registered using :func:`register_event`, connected to callbacks
using :func:`bind` and dispatched with the :func:`emit` function.

>>> import pydispatch

>>> def my_callback(message, **kwargs):
...     print(f'my_callback: "{message}"')

>>> # register 'event_a' as an event and bind it to my_callback
>>> pydispatch.register_event('event_a')
>>> pydispatch.bind(event_a=my_callback)

>>> # emit the event
>>> pydispatch.emit('event_a', 'hello')
my_callback: "hello"

>>> # unbind the callback
>>> pydispatch.unbind(my_callback)
>>> pydispatch.emit('event_a', 'still there?')

>>> # (Nothing printed)


The @receiver Decorator
-----------------------

To simplify binding callbacks to events, the :func:`~decorators.receiver` decorator may be used.

>>> from pydispatch import receiver

>>> @receiver('event_a')
... def my_callback(message, **kwargs):
...     print(f'my_callback: "{message}"')

>>> pydispatch.emit('event_a', 'hello again!')
my_callback: "hello again!"

Note that there is currently no way to :func:`unbind` a callback defined in this way.


Arguments
^^^^^^^^^

If the event name has not been registered beforehand, the ``cache`` and ``auto_register``
arguments to :func:`~decorators.receiver` may be used

cache
"""""

The ``cache`` argument stores the callback and will bind it to the event
once it is registered.

>>> # No event named 'foo' exists yet
>>> @receiver('foo', cache=True)
... def on_foo(message, **kwargs):
...     print(f'on_foo: "{message}"')

>>> # on_foo will be connected after the call to register_event
>>> pydispatch.register_event('foo')
>>> pydispatch.emit('foo', 'bar')
on_foo: "bar"

auto_register
"""""""""""""

The ``auto_register`` argument will immediately register the event if it does not exist

>>> @receiver('bar', auto_register=True)
... def on_bar(message, **kwargs):
...     print(f'on_bar: "{message}"')

>>> pydispatch.emit('bar', 'baz')
on_bar: "baz"


Async Support
^^^^^^^^^^^^^

If the decorated callback is a :term:`coroutine function` or method,
the :class:`EventLoop <asyncio.BaseEventLoop>` returned by
:func:`asyncio.get_event_loop` will be used as the ``loop`` argument to
:func:`bind_async`.

This will in most cases be the desired behavior unless multiple event loops
(in separate threads) are being used.



.. _singleton: https://en.wikipedia.org/wiki/Singleton_pattern
.. _Signals Framework: https://docs.djangoproject.com/en/4.2/topics/signals/
