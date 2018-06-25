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
        self.received_event_queue = asyncio.Queue(loop=mainloop)
        self.property_events = []
        self.property_event_kwargs = []
        self.property_event_map = {}
        self.property_event_loops = []
        self.property_queue = asyncio.Queue(loop=mainloop)
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

class LoopThread(threading.Thread):
    def __init__(self, mainloop, sender):
        super().__init__()
        self.mainloop = mainloop
        self.sender = sender
        self.running = threading.Event()
        self.stopped = threading.Event()
    def run(self):
        loop = self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        listener = AsyncListener(loop, self.mainloop)
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
    async def get_event_queue(self):
        item = await self.listener.received_event_queue.get()
        self.listener.received_event_queue.task_done()
        return item
    async def get_prop_queue(self):
        item = await self.listener.property_queue.get()
        self.listener.property_queue.task_done()
        return item
    def stop(self):
        self.running.clear()
        self.stopped.wait()


@pytest.mark.asyncio
async def test_aio_listeners(sender_cls):

    class Sender(sender_cls):
        prop_a = Property()
        prop_b = Property()
        _events_ = ['on_test_a', 'on_test_b', 'on_test_c']

    sender = Sender()
    mainloop = asyncio.get_event_loop()

    async def send_event(name, *listener_threads):
        sender.trigger_event(name)
        for t in listener_threads:
            data = await t.get_event_queue()
            assert data['name'] == name
            assert data['loop'] is t.loop
            assert data['loop'] is t.listener.loop

    async def trigger_prop(name, value, *listener_threads):
        setattr(sender, name, value)
        for t in listener_threads:
            data = await t.get_prop_queue()
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
