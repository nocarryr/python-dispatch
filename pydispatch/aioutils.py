import asyncio
import threading
from _weakref import ref

from pydispatch.utils import (
    WeakMethodContainer,
    get_method_vars,
    _remove_dead_weakref,
)

class AioEmissionHoldLock(object):
    @property
    def aio_lock(self):
        l = getattr(self, '_aio_lock', None)
        if l is None:
            l = self._aio_lock = asyncio.Lock()
        return l
    async def __aenter__(self):
        await self.aio_lock.acquire()
        self.acquire()
        return self
    async def __aexit__(self, *args):
        self.aio_lock.release()
        self.release()

class AioSimpleLock(object):
    __slots__ = ('lock')
    def __init__(self):
        self.lock = threading.Lock()
    def acquire(self, blocking=True, timeout=-1):
        result = self.lock.acquire(blocking, timeout)
        return result
    def release(self):
        self.lock.release()
    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, *args):
        self.release()
    async def acquire_async(self):
        r = self.acquire(blocking=False)
        while not r:
            await asyncio.sleep(.01)
            r = self.acquire(blocking=False)
    async def __aenter__(self):
        await self.acquire_async()
        return self
    async def __aexit__(self, *args):
        self.release()

class AioEventWaiter(object):
    __slots__ = ('loop', 'aio_event', 'args', 'kwargs')
    def __init__(self, loop):
        self.loop = loop
        self.aio_event = asyncio.Event(loop=loop)
        self.args = []
        self.kwargs = {}
    def trigger(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.aio_event.set()
    async def wait(self):
        await self.aio_event.wait()
        return self.args, self.kwargs
    def __await__(self):
        return self.wait()

class AioEventWaiters(object):
    __slots__ = ('waiters', 'lock')
    def __init__(self):
        self.waiters = set()
        self.lock = AioSimpleLock()
    async def add_waiter(self):
        loop = asyncio.get_event_loop()
        async with self.lock:
            waiter = AioEventWaiter(loop)
            self.waiters.add(waiter)
        return waiter
    async def wait(self):
        waiter = await self.add_waiter()
        return await waiter
    def __await__(self):
        return self.wait()
    def __call__(self, *args, **kwargs):
        with self.lock:
            for waiter in self.waiters:
                waiter.trigger(*args, **kwargs)
            self.waiters.clear()


class AioWeakMethodContainer(WeakMethodContainer):
    def __init__(self):
        super().__init__()
        def remove(wr, selfref=ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(wr.key)
                else:
                    # Atomic removal is necessary since this function
                    # can be called asynchronously by the GC
                    _remove_dead_weakref(self.data, wr.key)
                    self._on_weakref_fin(wr.key)
        self._remove = remove
        self.event_loop_map = {}
    def add_method(self, loop, callback):
        f, obj = get_method_vars(callback)
        wrkey = (f, id(obj))
        self[wrkey] = obj
        self.event_loop_map[wrkey] = loop
    def iter_methods(self):
        for wrkey, obj in self.iter_instances():
            f, obj_id = wrkey
            loop = self.event_loop_map[wrkey]
            m = getattr(obj, f.__name__)
            yield loop, m
    def _on_weakref_fin(self, key):
        if key in self.event_loop_map:
            del self.event_loop_map[key]
    def __call__(self, *args, **kwargs):
        for loop, m in self.iter_methods():
            asyncio.run_coroutine_threadsafe(m(*args, **kwargs), loop=loop)
    def __delitem__(self, key):
        if key in self.event_loop_map:
            del self.event_loop_map[key]
        return super().__delitem__(key)
