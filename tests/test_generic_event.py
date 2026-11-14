import asyncio
import gc
import weakref

import pytest

from pydispatch import Event


def test_generic_event_callbacks_and_weak_references():
    event: Event[[int]] = Event('value')
    received = []

    class Receiver:
        def callback(self, value):
            received.append(value)
            return False

    receiver = Receiver()
    event.add_listener(receiver.callback)
    assert event(1) is False
    with event.emission_lock:
        assert event(2) is None
        assert received == [1]
    assert received == [1, 2]

    ref = weakref.ref(receiver)
    del receiver
    gc.collect()
    assert ref() is None
    assert event(3) is None


@pytest.mark.asyncio
async def test_generic_event_async_callback_and_waiter():
    event: Event[[int]] = Event('value')
    received = asyncio.Event()
    values = []

    async def callback(value):
        values.append(value)
        received.set()

    event.add_listener(callback, __aio_loop__=asyncio.get_running_loop())
    waiter = asyncio.ensure_future(event)
    async with asyncio.timeout(1):
        while not event.aio_waiters.waiters:
            await asyncio.sleep(0)
    assert event(42) is None
    assert await waiter == ((42,), {})
    await asyncio.wait_for(received.wait(), timeout=1)
    assert values == [42]
