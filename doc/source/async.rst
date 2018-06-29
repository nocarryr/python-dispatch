asyncio support
===============

.. versionadded:: 0.1.0a1

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

::

    import asyncio
    from pydispatch import Dispatcher

    class MyEmitter(Dispatcher):
        events = ['on_state']

    class MyAsyncListener(object):
        def __init__(self):
            self.event_received = asyncio.Event()
        async def on_emitter_state(self, *args, **kwargs):
            self.event_received.set()

    loop = asyncio.get_event_loop()
    emitter = MyEmitter()
    listener = MyAsyncListener()

    # Pass the event loop as first argument to "bind_async"
    emitter.bind_async(loop, on_state=listener.on_emitter_state)

    async def trigger_and_wait_for_event():
        await asyncio.sleep(1)

        emitter.emit('on_state')

        # listener.event_received should be set from "on_emitter_state"
        await listener.event_received.wait()

    loop.run_until_complete(trigger_and_wait_for_event())

bind (with keyword argument)
""""""""""""""""""""""""""""

::

    import asyncio
    from pydispatch import Dispatcher

    class MyEmitter(Dispatcher):
        events = ['on_state']

    class MyAsyncListener(object):
        def __init__(self):
            self.event_received = asyncio.Event()
        async def on_emitter_state(self, *args, **kwargs):
            self.event_received.set()

    loop = asyncio.get_event_loop()
    emitter = MyEmitter()
    listener = MyAsyncListener()

    # Pass the event loop using __aio_loop__
    emitter.bind(on_state=listener.on_emitter_state, __aio_loop__=loop)

    async def trigger_and_wait_for_event():
        await asyncio.sleep(1)

        emitter.emit('on_state')

        # listener.event_received should be set from "on_emitter_state"
        await listener.event_received.wait()

    loop.run_until_complete(trigger_and_wait_for_event())

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

This can also be done with :any:`Property` objects::

    import asyncio
    from pydispatch import Dispatcher, Property


    class MyEmitter(Dispatcher):
        value = Property()
        async def change_values(self):
            for i in range(10):
                await asyncio.sleep(.1)
                self.value = i

    class MyAsyncListener(object):
        async def wait_for_value(self, emitter):
            event = emitter.get_dispatcher_event('value')
            while True:
                args, kwargs = await event
                instance, value = args
                print(value)
                if value >= 9:
                    break

    loop = asyncio.get_event_loop()
    emitter = MyEmitter()
    listener = MyAsyncListener()

    # Make the emitter value iterate from 0-9
    asyncio.ensure_future(emitter.change_values())

    # Listens for changes, then exits after value reaches 9
    loop.run_until_complete(listener.wait_for_value(emitter))
