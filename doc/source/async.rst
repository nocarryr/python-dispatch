asyncio support
===============

.. versionadded:: 0.1.0

Callbacks
---------

Callbacks can also be :term:`coroutine functions <coroutine function>`
(defined using :keyword:`async def` or decorated with
:func:`@asyncio.coroutine <asyncio.coroutine>`).  For this to work properly,
the :class:`event loop <~asyncio.BaseEventLoop>` they belong to **must**
be specified. This requirement is in place to prevent issues when multiple event
loops are in use (via threads, etc).

The loop can be specified using the :any:`Dispatcher.bind_async` method,
or passed as a keyword argument to :any:`Dispatcher.bind`.

Examples
^^^^^^^^

bind_async method
"""""""""""""""""

.. doctest:: bind_async

    >>> import asyncio
    >>> from pydispatch import Dispatcher
    >>> class MyEmitter(Dispatcher):
    ...     _events_ = ['on_state']
    ...     async def trigger(self):
    ...         await asyncio.sleep(1)
    ...         self.emit('on_state')
    >>> class MyAsyncListener(object):
    ...     def __init__(self):
    ...         self.event_received = asyncio.Event()
    ...     async def on_emitter_state(self, *args, **kwargs):
    ...         print('received on_state event')
    ...         self.event_received.set()
    ...     async def wait_for_event(self):
    ...         await self.event_received.wait()
    >>> loop = asyncio.get_event_loop()
    >>> emitter = MyEmitter()
    >>> listener = MyAsyncListener()
    >>> # Pass the event loop as first argument to "bind_async"
    >>> emitter.bind_async(loop, on_state=listener.on_emitter_state)
    >>> loop.run_until_complete(emitter.trigger())
    >>> loop.run_until_complete(listener.wait_for_event())
    received on_state event

bind (with keyword argument)
""""""""""""""""""""""""""""

.. doctest:: bind_async_kw

    >>> import asyncio
    >>> from pydispatch import Dispatcher
    >>> class MyEmitter(Dispatcher):
    ...     _events_ = ['on_state']
    ...     async def trigger(self):
    ...         await asyncio.sleep(1)
    ...         self.emit('on_state')
    >>> class MyAsyncListener(object):
    ...     def __init__(self):
    ...         self.event_received = asyncio.Event()
    ...     async def on_emitter_state(self, *args, **kwargs):
    ...         print('received on_state event')
    ...         self.event_received.set()
    ...     async def wait_for_event(self):
    ...         await self.event_received.wait()
    >>> loop = asyncio.get_event_loop()
    >>> emitter = MyEmitter()
    >>> listener = MyAsyncListener()
    >>> # Pass the event loop using __aio_loop__
    >>> emitter.bind(on_state=listener.on_emitter_state, __aio_loop__=loop)
    >>> loop.run_until_complete(emitter.trigger())
    >>> loop.run_until_complete(listener.wait_for_event())
    received on_state event

Async (awaitable) Events
------------------------

Event (and :any:`Property`) objects are :term:`awaitable`. This allows event
subscription without callbacks in an async environment. The :any:`Event` instance
itself must first be obtained using the :any:`Dispatcher.get_dispatcher_event`
method. Any positional and keyword arguments from the event are returned as a
two-tuple::

    async def wait_for_event(event_name):
        event = emitter.get_dispatcher_event(event_name)
        args, kwargs = await event
        return args, kwargs

    loop.run_until_complete(wait_for_event('on_state'))

This can also be done with :any:`Property` objects

.. doctest:: async_properties

    >>> import asyncio
    >>> from pydispatch import Dispatcher, Property
    >>> class MyEmitter(Dispatcher):
    ...     value = Property()
    ...     async def change_values(self):
    ...         for i in range(5):
    ...             await asyncio.sleep(.1)
    ...             self.value = i
    ...         return 'done'
    >>> class MyAsyncListener(object):
    ...     async def wait_for_values(self, emitter):
    ...         # Get the Event object for the Property
    ...         event = emitter.get_dispatcher_event('value')
    ...         # await the event until the value reaches 4
    ...         while True:
    ...             args, kwargs = await event
    ...             instance, value = args
    ...             print(value)
    ...             if value >= 4:
    ...                 break
    ...         return 'done'
    >>> loop = asyncio.get_event_loop()
    >>> emitter = MyEmitter()
    >>> listener = MyAsyncListener()
    >>> coros = [emitter.change_values(), listener.wait_for_values(emitter)]
    >>> loop.run_until_complete(asyncio.gather(*coros))
    0
    1
    2
    3
    4
    ['done', 'done']
