import asyncio
import threading
from functools import partial
import time
import pytest

@pytest.mark.asyncio
async def test_aio_event_lock(listener, sender):
    loop = asyncio.get_event_loop()

    sender.register_event('on_test')
    sender.bind(on_test=listener.on_event)

    letters = 'abcdefghijkl'

    sender.emit('on_test', letters[0], emit_count=0)
    assert len(listener.received_event_data) == 1
    listener.received_event_data = []

    async with sender.emission_lock('on_test') as elock:
        assert elock.aio_locks[id(loop)].locked()
        for i in range(len(letters)):
            sender.emit('on_test', letters[i], emit_count=i)
    assert not elock.aio_locks[id(loop)].locked()

    assert len(listener.received_event_data) == 1
    e = listener.received_event_data[0]
    assert e['args'] == (letters[i], )
    assert e['kwargs']['emit_count'] == i

    listener.received_event_data = []

    async def do_emit(i):
        async with sender.emission_lock('on_test') as elock:
            assert elock.aio_locks[id(loop)].locked()
            sender.emit('on_test', i, 'first')
            sender.emit('on_test', i, 'second')
        assert not elock.aio_locks[id(loop)].locked()

    tx_indecies = [i for i in range(8)]
    coros = [asyncio.ensure_future(do_emit(i)) for i in tx_indecies]
    await asyncio.wait(coros)

    assert len(listener.received_event_data) == len(coros)

    rx_indecies = set()
    for edata in listener.received_event_data:
        i, s = edata['args']
        assert i not in rx_indecies
        assert s == 'second'
        rx_indecies.add(i)

    assert rx_indecies == set(tx_indecies)

@pytest.mark.asyncio
async def test_aio_property_lock(listener):
    from pydispatch import Dispatcher, Property
    from pydispatch.properties import ListProperty, DictProperty

    class A(Dispatcher):
        test_prop = Property()
        test_dict = DictProperty()
        test_list = ListProperty()

    loop = asyncio.get_event_loop()
    a = A()
    a.test_list = [-1] * 4
    a.test_dict = {'a':0, 'b':1, 'c':2, 'd':3}
    a.bind(test_prop=listener.on_prop, test_list=listener.on_prop, test_dict=listener.on_prop)

    async with a.emission_lock('test_prop') as elock:
        assert elock.aio_locks[id(loop)].locked()
        for i in range(4):
            a.test_prop = i
    assert not elock.aio_locks[id(loop)].locked()
    assert len(listener.property_events) == 1
    assert listener.property_event_kwargs[0]['property'].name == 'test_prop'
    assert listener.property_events[0] == i

    listener.property_events = []
    listener.property_event_kwargs = []

    async with a.emission_lock('test_list'):
        a.test_prop = 'foo'
        for i in range(4):
            a.test_list = [i] * 4
    assert len(listener.property_events) == 2
    assert listener.property_event_kwargs[0]['property'].name == 'test_prop'
    assert listener.property_events[0] == 'foo'
    assert listener.property_event_kwargs[1]['property'].name == 'test_list'
    assert listener.property_events[1] == [i] * 4

    listener.property_events = []
    listener.property_event_kwargs = []

    async with a.emission_lock('test_dict'):
        a.test_prop = 'bar'
        a.test_list[0] = 'a'
        for i in range(4):
            for key in a.test_dict.keys():
                a.test_dict[key] = i
    assert len(listener.property_events) == 3
    assert listener.property_event_kwargs[0]['property'].name == 'test_prop'
    assert listener.property_events[0] == 'bar'
    assert listener.property_event_kwargs[1]['property'].name == 'test_list'
    assert listener.property_events[1][0] == 'a'
    assert listener.property_event_kwargs[2]['property'].name == 'test_dict'
    assert listener.property_events[2] == {k:i for k in a.test_dict.keys()}

    listener.property_events = []
    listener.property_event_kwargs = []

    async with a.emission_lock('test_prop'):
        async with a.emission_lock('test_list'):
            async with a.emission_lock('test_dict'):
                for i in range(4):
                    a.test_prop = i
                    a.test_list[0] = i
                    a.test_dict[i] = 'foo'
    assert len(listener.property_events) == 3
    assert listener.property_event_kwargs[0]['property'].name == 'test_dict'
    for k in range(4):
        assert listener.property_events[0][k] == 'foo'
    assert listener.property_event_kwargs[1]['property'].name == 'test_list'
    assert listener.property_events[1][0] == i
    assert listener.property_event_kwargs[2]['property'].name == 'test_prop'
    assert listener.property_events[2] == i


    listener.property_event_map.clear()

    async def set_property(prop_name, *values):
        async with a.emission_lock(prop_name):
            for value in values:
                setattr(a, prop_name, value)

    prop_vals = {
        'test_prop':[None, 0, 1, 2],
        'test_list':[[None]*4, [0]*4, [0, 1, 2, 3], ['a', 'b', 'c', 'd']],
        'test_dict':[
            {k:None for k in a.test_dict.keys()},
            {k:0 for k in a.test_dict.keys()},
            {k:v for k, v in zip(a.test_dict.keys(), range(4))},
            {k:v for k, v in zip(a.test_dict.keys(), ['a', 'b', 'c', 'd'])},
        ],
    }

    coros = []
    for prop_name, vals in prop_vals.items():
        coros.append(asyncio.ensure_future(set_property(prop_name, *vals)))
    await asyncio.wait(coros)

    for prop_name, vals in prop_vals.items():
        event_list = listener.property_event_map[prop_name]
        assert len(event_list) == 1
        assert event_list[0]['value'] == vals[-1] == getattr(a, prop_name)

@pytest.mark.asyncio
async def test_aio_lock_concurrency(listener, sender):

    letters = 'abcdefghijkl'

    class EmitterThread(threading.Thread):
        def __init__(self):
            super().__init__()
            self.running = threading.Event()
            self.stopped = threading.Event()
            self.rx_queue = asyncio.Queue()
        def run(self):
            loop = self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.msg_queue = asyncio.Queue()
            self.running.set()
            loop.run_until_complete(self.run_loop())
            self.stopped.set()
        async def stop(self):
            self.running.clear()
            result = await self.send_msg(None)
            self.stopped.wait()
        async def send_msg(self, msg):
            fut = asyncio.run_coroutine_threadsafe(self.msg_queue.put(msg), loop=self.loop)
            await asyncio.wrap_future(fut)
            result = await self.rx_queue.get()
            self.rx_queue.task_done()
            return result
        async def run_loop(self):
            while self.running.is_set():
                msg = await self.msg_queue.get()
                self.msg_queue.task_done()
                if msg is None:
                    self.running.clear()
                    break
                if msg == 'acquire':
                    await self.acquire()
                    self.rx_queue.put_nowait(msg)
                elif msg == 'release':
                    await self.release()
                    self.rx_queue.put_nowait(msg)
                elif isinstance(msg, dict):
                    args = msg.get('args', [])
                    kwargs = msg.get('kwargs', {})
                    if msg.get('action') == 'emit':
                        await self.do_emit(*args, **kwargs)
                        self.rx_queue.put_nowait(msg)
            self.rx_queue.put_nowait('exit')
        async def acquire(self):
            lock = sender.emission_lock('on_test')
            await lock.acquire_async()
        async def release(self):
            lock = sender.emission_lock('on_test')
            await lock.release_async()
        async def do_emit(self, *args, **kwargs):
            sender.emit('on_test', *args, **kwargs)

    loop = asyncio.get_event_loop()
    sender.register_event('on_test')
    sender.bind(on_test=listener.on_event)
    emission_lock = sender.emission_lock('on_test')

    t = EmitterThread()
    t.start()
    t.running.wait()

    async with emission_lock:
        assert emission_lock.held
        assert len(emission_lock.aio_locks) == 1
        assert id(loop) in emission_lock.aio_locks
        assert emission_lock.aio_locks[id(loop)].locked()

        await t.send_msg('acquire')
        assert emission_lock.held
        assert len(emission_lock.aio_locks) == 2
        assert id(t.loop) in emission_lock.aio_locks
        assert emission_lock.aio_locks[id(t.loop)].locked()

        sender.emit('on_test', letters[0], emit_count=0)

        assert len(listener.received_event_data) == 0

    await t.send_msg('release')
    assert len(listener.received_event_data) == 1

    async with emission_lock:
        assert emission_lock.held
        sender.emit('on_test', False)
        assert len(listener.received_event_data) == 1

        await t.send_msg(dict(action='emit', args=[letters[1]], kwargs={'emit_count':1}))
        assert emission_lock.held
        assert len(listener.received_event_data) == 1

    assert len(listener.received_event_data) == 2
    edata = listener.received_event_data[1]
    assert edata['args'][0] is not False
    assert edata['args'][0] == letters[1]
    assert edata['kwargs']['emit_count'] == 1

    await t.stop()
    t.join()

@pytest.mark.asyncio
async def test_aio_simple_lock():
    from pydispatch.aioutils import AioSimpleLock

    loop = asyncio.get_event_loop()

    async def timed_acquire_async(lock, timeout=1):
        start_ts = loop.time()
        await asyncio.sleep(timeout)
        await lock.acquire_async()
        end_ts = loop.time()
        return end_ts - start_ts

    def timed_acquire_sync(lock, timeout=1):
        start_ts = time.time()
        time.sleep(timeout)
        lock.acquire()
        end_ts = time.time()
        return end_ts - start_ts

    async def timed_release_async(lock, timeout=1):
        await asyncio.sleep(timeout)
        lock.release()

    def timed_release_sync(lock, timeout=1):
        time.sleep(timeout)
        lock.release()

    lock = AioSimpleLock()

    timeout = .5

    start_ts = loop.time()
    await lock.acquire_async()
    fut = asyncio.ensure_future(timed_release_async(lock, timeout))
    await lock.acquire_async()
    end_ts = loop.time()
    assert end_ts - start_ts >= timeout
    assert fut.done()
    lock.release()

    fut = asyncio.ensure_future(timed_acquire_async(lock, .1))
    async with lock:
        await asyncio.sleep(timeout)
    elapsed = await fut
    assert elapsed >= timeout
    lock.release()

    start_ts = loop.time()
    await lock.acquire_async()
    fut = loop.run_in_executor(None, partial(timed_release_sync, lock, timeout))
    await lock.acquire_async()
    end_ts = loop.time()
    assert end_ts - start_ts >= timeout
    lock.release()
    await fut

    async with lock:
        fut = loop.run_in_executor(None, partial(timed_acquire_sync, lock, .1))
        await asyncio.sleep(timeout)
    elapsed = await fut
    assert elapsed >= timeout
