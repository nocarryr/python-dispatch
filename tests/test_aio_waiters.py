import asyncio

import pytest

from pydispatch.aioutils import AioEventWaiter, AioEventWaiters


@pytest.mark.asyncio
async def test_waiter_initial_state_and_event_arguments():
    loop = asyncio.get_running_loop()
    waiter = AioEventWaiter(loop)
    assert waiter.loop is loop
    assert waiter.args == []
    assert waiter.kwargs == {}

    marker = object()
    waiter.trigger(marker, 2, key=marker)
    args, kwargs = await waiter
    assert args == (marker, 2)
    assert kwargs == {'key': marker}
    assert args[0] is marker
    assert kwargs['key'] is marker


@pytest.mark.asyncio
async def test_waiter_can_be_woken_without_trigger():
    waiter = AioEventWaiter(asyncio.get_running_loop())
    waiter.aio_event.set()
    assert await waiter == ([], {})


@pytest.mark.asyncio
async def test_waiters_notify_all_and_clear():
    waiters = AioEventWaiters()
    first = await waiters.add_waiter()
    second = await waiters.add_waiter()

    waiters('value', key=42)

    assert await first == (('value',), {'key': 42})
    assert await second == (('value',), {'key': 42})
    assert waiters.waiters == set()


@pytest.mark.asyncio
async def test_waiters_can_be_awaited_directly():
    registered = asyncio.Event()

    class NotifyingWaiters(AioEventWaiters):
        async def add_waiter(self):
            waiter = await super().add_waiter()
            registered.set()
            return waiter

    waiters = NotifyingWaiters()
    task = asyncio.ensure_future(waiters)
    await asyncio.wait_for(registered.wait(), timeout=1)
    assert len(waiters.waiters) == 1

    waiters('ready', count=2)

    assert await task == (('ready',), {'count': 2})
    assert waiters.waiters == set()
