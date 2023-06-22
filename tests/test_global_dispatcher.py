import asyncio

import pydispatch
from pydispatch import receiver

import pytest

@pytest.fixture
def dispatcher_cleanup():
    yield
    pydispatch._GLOBAL_DISPATCHER._Dispatcher__events.clear()
    pydispatch.decorators._CACHED_CALLBACKS.cache.clear()

def test_receiver_decorator(dispatcher_cleanup):

    pydispatch.register_event('foo', 'bar')

    results = {'foo':[], 'bar':[], 'foo_bar':[]}
    expected = {'foo':[], 'bar':[], 'foo_bar':[]}

    @receiver('foo')
    def on_foo(*args, **kwargs):
        results['foo'].append((args, kwargs))

    @receiver('bar')
    def on_bar(*args, **kwargs):
        results['bar'].append((args, kwargs))

    @receiver(['foo', 'bar'])
    def on_foo_bar(*args, **kwargs):
        results['foo_bar'].append((args, kwargs))

    for i in range(10):
        pydispatch.emit('foo', i)
        expected['foo'].append(((i,), {}))
        expected['foo_bar'].append(((i,), {}))

    for c in 'abcdef':
        pydispatch.emit('bar', c)
        expected['bar'].append(((c,), {}))
        expected['foo_bar'].append(((c,), {}))

    assert results == expected


def test_receiver_decorator_unregistered(dispatcher_cleanup):
    with pytest.raises(pydispatch.DoesNotExistError):
        @receiver('foo')
        def on_foo(*args, **kwargs):
            pass

def test_receiver_decorator_unregistered_cache(dispatcher_cleanup):
    results = []

    @receiver('foo', cache=True)
    def on_foo(*args, **kwargs):
        results.append((args, kwargs))

    with pytest.raises(pydispatch.DoesNotExistError):
        pydispatch.emit('foo', 47)

    pydispatch.register_event('foo')

    pydispatch.emit('foo', 1)

    assert results == [((1,), {})]


def test_receiver_decorator_unregistered_auto_register(dispatcher_cleanup):
    results = []

    @receiver('foo', auto_register=True)
    def on_foo(*args, **kwargs):
        results.append((args, kwargs))

    pydispatch.emit('foo', 1)

    assert results == [((1,), {})]

def test_receiver_decorator_registered_auto_register(dispatcher_cleanup):

    with pytest.raises(pydispatch.DoesNotExistError):
        pydispatch.get_dispatcher_event('foo')

    pydispatch.register_event('foo')

    assert pydispatch.get_dispatcher_event('foo') is not None

    results = []

    @receiver('foo', auto_register=True)
    def on_foo(*args, **kwargs):
        results.append((args, kwargs))

    pydispatch.emit('foo', 2)

    assert results == [((2,), {})]

def test_receiver_decorator_registered_cache(dispatcher_cleanup):
    with pytest.raises(pydispatch.DoesNotExistError):
        pydispatch.get_dispatcher_event('foo')

    pydispatch.register_event('foo')
    assert pydispatch.get_dispatcher_event('foo') is not None

    results = []

    @receiver('foo', cache=True)
    def on_foo(*args, **kwargs):
        results.append((args, kwargs))

    pydispatch.emit('foo', 3)

    assert results == [((3,), {})]

@pytest.mark.asyncio
async def test_decorator_async_cache(dispatcher_cleanup):
    results = []
    result_ev = asyncio.Event()

    @receiver('foo', cache=True)
    async def on_foo(*args, **kwargs):
        results.append((args, kwargs))
        result_ev.set()

    with pytest.raises(pydispatch.DoesNotExistError):
        pydispatch.emit('foo', 47)

    pydispatch.register_event('foo')

    pydispatch.emit('foo', 1)
    await result_ev.wait()

    assert results == [((1,), {})]


@pytest.mark.asyncio
async def test_decorator_async_auto_register(dispatcher_cleanup):

    results = []
    result_ev = asyncio.Event()

    @receiver('foo', auto_register=True)
    async def on_foo(*args, **kwargs):
        results.append((args, kwargs))
        result_ev.set()

    pydispatch.emit('foo', 1)
    await result_ev.wait()

    assert results == [((1,), {})]
