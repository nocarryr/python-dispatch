import asyncio
import threading
import pytest

from pydispatch import Property

class AsyncListener:
    def __init__(self, loop, mainloop):
        self.loop = loop
        self.mainloop = mainloop
        self.received_events = []
        self.received_event_data = []
        self.received_event_loops = []
        self.received_event_queue = asyncio.Queue()
        self.property_events = []
        self.property_event_kwargs = []
        self.property_event_map = {}
        self.property_event_loops = []
        self.property_queue = asyncio.Queue()
    async def on_event(self, *args, **kwargs):
        self.received_event_data.append({'args':args, 'kwargs':kwargs})
        name = kwargs.get('triggered_event')
        self.received_events.append(name)
        cur_loop = asyncio.get_event_loop()
        self.received_event_loops.append(cur_loop)
        asyncio.run_coroutine_threadsafe(self.event_queue_put({
            'name':name,
            'args':args,
            'kwargs':kwargs,
            'loop':cur_loop,
        }), loop=self.mainloop)
    async def event_queue_put(self, item):
        await self.received_event_queue.put(item)
    async def event_queue_get(self):
        item = await self.received_event_queue.get()
        self.received_event_queue.task_done()
        return item
    def clear_event_data(self):
        assert self.received_event_queue.empty()
        self.received_events.clear()
        self.received_event_data.clear()
        self.received_event_loops.clear()
    async def on_prop(self, obj, value, **kwargs):
        self.property_events.append(value)
        self.property_event_kwargs.append(kwargs)
        prop = kwargs['property']
        if prop.name not in self.property_event_map:
            self.property_event_map[prop.name] = []
        self.property_event_map[prop.name].append({'value':value, 'kwargs':kwargs})
        cur_loop = asyncio.get_event_loop()
        self.property_event_loops.append(cur_loop)
        asyncio.run_coroutine_threadsafe(self.prop_queue_put({
            'name':prop.name,
            'value':value,
            'kwargs':kwargs,
            'loop':cur_loop,
        }), loop=self.mainloop)
    async def prop_queue_put(self, item):
        await self.property_queue.put(item)
    async def prop_queue_get(self):
        item = await self.property_queue.get()
        self.property_queue.task_done()
        return item
    def clear_prop_data(self):
        assert self.property_queue.empty()
        self.property_events.clear()
        self.property_event_kwargs.clear()
        self.property_event_map.clear()
        self.property_event_loops.clear()

class LoopThread(threading.Thread):
    def __init__(self, mainloop, sender):
        super().__init__()
        self.mainloop = asyncio.get_event_loop()
        self.received_event_queue = asyncio.Queue()
        self.property_queue = asyncio.Queue()
        self.sender = sender
        self.running = threading.Event()
        self.stopped = threading.Event()
    def run(self):
        loop = self.loop = asyncio.new_event_loop()
        loop.set_debug(self.mainloop.get_debug())
        asyncio.set_event_loop(loop)
        listener = AsyncListener(loop, self.mainloop)

        # Replace the queue objects with ones that belong to mainloop
        listener.received_event_queue = self.received_event_queue
        listener.property_queue = self.property_queue

        sender = self.sender
        ev_names = sender._Dispatcher__events.keys()
        sender.bind_async(loop, **{name:listener.on_event for name in ev_names})
        prop_names = sender._Dispatcher__property_events.keys()
        sender.bind_async(loop, **{name:listener.on_prop for name in prop_names})
        self.listener = listener
        self.running.set()
        loop.run_until_complete(self.run_loop())
        self.stopped.set()
    async def run_loop(self):
        while self.running.is_set():
            await asyncio.sleep(.1)
    def stop(self):
        self.running.clear()
        self.stopped.wait()

@pytest.fixture(params=[True, False])
def loop_debug(request):
    return request.param

@pytest.mark.asyncio
async def test_simple(sender_cls, loop_debug):

    class Sender(sender_cls):
        prop_a = Property()
        prop_b = Property()
        _events_ = ['on_test_a', 'on_test_b', 'on_test_c']

    loop = asyncio.get_event_loop()
    loop.set_debug(loop_debug)

    sender = Sender()
    listener = AsyncListener(loop, loop)

    ev_names = sender._Dispatcher__events.keys()
    sender.bind_async(loop, **{name:listener.on_event for name in ev_names})
    prop_names = sender._Dispatcher__property_events.keys()
    sender.bind_async(loop, **{name:listener.on_prop for name in prop_names})

    with pytest.raises(RuntimeError) as excinfo:
        sender.bind(on_test_a=listener.on_event)
    assert 'Coroutine function given without event loop' in str(excinfo.value)

    for name in ev_names:
        sender.trigger_event(name)
        data = await listener.event_queue_get()
        assert data['name'] == name
        assert data['loop'] is loop

    for name in prop_names:
        for i in range(10):
            setattr(sender, name, i)
            data = await listener.prop_queue_get()
            assert data['name'] == name
            assert data['value'] == i
            assert data['loop'] is loop

@pytest.mark.asyncio
async def test_unbind(sender_cls, loop_debug):

    class Sender(sender_cls):
        prop_a = Property()
        prop_b = Property()
        _events_ = ['on_test_a', 'on_test_b', 'on_test_c']

    loop = asyncio.get_event_loop()
    loop.set_debug(loop_debug)

    sender = Sender()
    listener = AsyncListener(loop, loop)

    ev_names = sender._Dispatcher__events.keys()
    sender.bind_async(loop, **{name:listener.on_event for name in ev_names})
    prop_names = sender._Dispatcher__property_events.keys()
    sender.bind_async(loop, **{name:listener.on_prop for name in prop_names})

    for name in ev_names:
        sender.trigger_event(name)
        await listener.event_queue_get()

    for name in prop_names:
        for i in range(10):
            setattr(sender, name, i)
            await listener.prop_queue_get()

    # Unbind and retrigger events
    listener.clear_event_data()
    listener.clear_prop_data()

    sender.unbind(listener.on_event, listener.on_prop)

    async def check_events_unbound():
        for name in ev_names:
            # Ensure event listeners are empty
            e = sender.get_dispatcher_event(name)
            assert not len(e.aio_listeners)
            assert not len(e.aio_listeners.event_loop_map)

            # Trigger event
            sender.trigger_event(name)
        for name in prop_names:
            # Ensure event listeners are empty
            e = sender._Dispatcher__property_events[name]
            assert not len(e.aio_listeners)
            assert not len(e.aio_listeners.event_loop_map)

            # Trigger event
            val = getattr(sender, name)
            val += 1
            setattr(sender, name, val)

        # Wait for tasks to complete
        await asyncio.sleep(.5)

        assert not len(listener.received_events)
        assert not len(listener.property_events)

    await check_events_unbound()

    # Rebind events and properties to test unbinding by instance
    listener.clear_event_data()
    listener.clear_prop_data()

    sender.bind_async(loop, **{name:listener.on_event for name in ev_names})
    sender.bind_async(loop, **{name:listener.on_prop for name in prop_names})

    # Make sure things are bound correctly
    for name in ev_names:
        sender.trigger_event(name)
        await listener.event_queue_get()
    for name in prop_names:
        val = getattr(sender, name)
        val += 1
        setattr(sender, name, val)
        await listener.prop_queue_get()

    # Unbind instance and recheck
    listener.clear_event_data()
    listener.clear_prop_data()

    sender.unbind(listener)

    await check_events_unbound()

@pytest.mark.asyncio
async def test_multiple_loops(sender_cls, loop_debug):

    class Sender(sender_cls):
        prop_a = Property()
        prop_b = Property()
        _events_ = ['on_test_a', 'on_test_b', 'on_test_c']

    sender = Sender()
    mainloop = asyncio.get_event_loop()
    mainloop.set_debug(loop_debug)

    async def send_event(name, *listener_threads):
        sender.trigger_event(name)
        for t in listener_threads:
            data = await t.listener.event_queue_get()
            assert data['name'] == name
            assert data['loop'] is t.loop
            assert data['loop'] is t.listener.loop

    async def trigger_prop(name, value, *listener_threads):
        setattr(sender, name, value)
        for t in listener_threads:
            data = await t.listener.prop_queue_get()
            assert data['name'] == name
            assert data['value'] == value
            assert data['loop'] is t.loop
            assert data['loop'] is t.listener.loop

    threads = []
    listeners = []
    loops = []
    for i in range(4):
        t = LoopThread(mainloop, sender)
        t.start()
        t.running.wait()
        threads.append(t)
        listeners.append(t.listener)
        loops.append(t.loop)
    assert len(set(loops)) == len(loops)

    for name in Sender._events_:
        print('sending {}'.format(name))
        await send_event(name, *threads)
        print('received {}'.format(name))

    for name in ['prop_a', 'prop_b']:
        for i in range(10):
            print('sending {}={}'.format(name, i))
            await trigger_prop(name, i, *threads)
            print('received {}={}'.format(name, i))

    for t in threads:
        t.stop()

@pytest.mark.asyncio
async def test_event_await(sender_cls, loop_debug):

    class Sender(sender_cls):
        prop_a = Property()
        prop_b = Property()
        _events_ = ['on_test_a', 'on_test_b', 'on_test_c']

    loop = asyncio.get_event_loop()
    loop.set_debug(loop_debug)

    sender = Sender()

    ev_names = sender._Dispatcher__events.keys()
    prop_names = sender._Dispatcher__property_events.keys()

    received_events = asyncio.Queue()
    tasks = []

    async def wait_for_event(name):
        e = sender.get_dispatcher_event(name)
        print('waiting for event "{}"'.format(name))
        args, kwargs = await e
        print('event "{}" received'.format(name))
        await received_events.put([name, args, kwargs])

    for name in ev_names:
        print(name)
        fut = asyncio.ensure_future(wait_for_event(name))
        await asyncio.sleep(.01)

        sender.trigger_event(name)

        await fut
        result = await received_events.get()
        received_events.task_done()
        assert result[0] == name

    for name in prop_names:
        for i in range(10):
            fut = asyncio.ensure_future(wait_for_event(name))
            await asyncio.sleep(.01)
            setattr(sender, name, i)
            result = await received_events.get()
            received_events.task_done()
            await fut
            assert result[0] == name
            instance, value = result[1]
            assert value == i

@pytest.mark.asyncio
async def test_changes_during_emit(sender_cls):

    class Sender(sender_cls):
        _events_ = ['on_test']

    class Listener(object):
        def __init__(self):
            self.event_received = False
            self.queue = asyncio.Queue()
        async def wait_for_event(self):
            r = await self.queue.get()
            self.queue.task_done()
            self.event_received = False
            return r
        async def on_event(self, *args, **kwargs):
            self.event_received = True
            await self.queue.put((args, kwargs))

    class UnbindListener(Listener):
        def __init__(self, loop, sender):
            super().__init__()
            self.loop = loop
            self.sender = sender
            self.new_listeners = []
            self.unbound_listeners = []
        async def on_event(self, *args, **kwargs):
            if kwargs.get('create_listeners'):
                self.new_listeners = []
                for i in range(10):
                    listener = Listener()
                    self.sender.bind_async(loop, on_test=listener.on_event)
                    self.new_listeners.append(listener)
            elif kwargs.get('unbind_listeners'):
                self.unbound_listeners = []
                for listener in self.new_listeners[:]:
                    self.sender.unbind(listener)
                    self.unbound_listeners.append(listener)
                    self.new_listeners.remove(listener)
            elif kwargs.get('defererence_listeners'):
                self.new_listeners.clear()
                self.unbound_listeners.clear()
                await asyncio.sleep(.1)
            await super().on_event(*args, **kwargs)

    loop = asyncio.get_event_loop()
    sender = Sender()

    listener2 = UnbindListener(loop, sender)
    sender.bind_async(loop, on_test=listener2.on_event)

    # Create listeners inside of event emission
    sender.emit('on_test', create_listeners=True)
    await listener2.wait_for_event()

    print('new_listeners: ', len(listener2.new_listeners))

    # The new listeners should not have received the first event
    for listener in listener2.new_listeners:
        with pytest.raises(asyncio.QueueEmpty):
            listener.queue.get_nowait()


    # Unbind the created listeners inside of event emission
    sender.emit('on_test', unbind_listeners=True)
    await listener2.wait_for_event()

    print('unbound_listeners: ', len(listener2.unbound_listeners))
    print('not unbound_listeners: ', len(listener2.new_listeners))
    assert len(listener2.new_listeners) == 0

    # The listeners should have received the "unbind_listeners=True" event
    for listener in listener2.unbound_listeners:
        await listener.wait_for_event()

    # Now fire another event and make sure the unbound_listeners don't receive it
    sender.emit('on_test')
    await listener2.wait_for_event()

    for listener in listener2.unbound_listeners:
        with pytest.raises(asyncio.QueueEmpty):
            listener.queue.get_nowait()

    # Clear previously created listeners and build new ones
    listener2.unbound_listeners.clear()
    sender.emit('on_test', create_listeners=True)
    await listener2.wait_for_event()

    # Dereference them inside of event emission and make sure
    # the weakrefs are removed
    sender.emit('on_test', defererence_listeners=True)
    await listener2.wait_for_event()

    e = sender.get_dispatcher_event('on_test')
    assert len(e.aio_listeners) == 1
