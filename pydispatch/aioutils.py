import asyncio

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
