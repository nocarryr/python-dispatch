import asyncio

from pydispatch.utils import WeakMethodContainer, get_method_vars

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

class AioWeakMethodContainer(WeakMethodContainer):
    def __init__(self):
        super().__init__()
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
    def __call__(self, *args, **kwargs):
        for loop, m in self.iter_methods():
            asyncio.run_coroutine_threadsafe(m(*args, **kwargs), loop=loop)
    def __delitem__(self, key):
        if key in self.event_loop_map:
            del self.event_loop_map[key]
        return super().__delitem__(key)
