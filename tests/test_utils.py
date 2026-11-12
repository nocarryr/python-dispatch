import asyncio
import gc

import pytest

from pydispatch.aioutils import AioWeakMethodContainer
from pydispatch.utils import InformativeWVDict, WeakMethodContainer, isfunction


class WeakValue:
    pass


def test_weak_method_container_accepts_callback_keyword_and_extra_kwargs():
    def callback():
        pass

    container = WeakMethodContainer()
    container.add_method(callback=callback, extra=True)

    assert list(container.iter_methods()) == [callback]
    container.del_method(callback=callback)
    assert list(container.iter_methods()) == []


def test_isfunction_accepts_obj_keyword():
    def callback():
        pass

    assert isfunction(obj=callback)
    assert not isfunction(obj=object())


@pytest.mark.asyncio
@pytest.mark.parametrize('use_keywords', [False, True])
async def test_aio_weak_method_container_adds_functions_and_bound_methods(use_keywords):
    class Listener:
        async def callback(self):
            pass

    async def callback():
        pass

    loop = asyncio.get_running_loop()
    listener = Listener()
    container = AioWeakMethodContainer()
    for method in (callback, listener.callback):
        if use_keywords:
            container.add_method(callback=method, loop=loop, extra=True)
        else:
            container.add_method(method, loop, extra=True)

    assert set(container.iter_methods()) == {
        (loop, callback),
        (loop, listener.callback),
    }

    container.del_method(callback=listener.callback)
    assert list(container.iter_methods()) == [(loop, callback)]


@pytest.mark.asyncio
@pytest.mark.parametrize('loop_kwargs', [{}, {'loop': None}])
async def test_aio_weak_method_container_requires_loop(loop_kwargs):
    async def callback():
        pass

    container = AioWeakMethodContainer()
    with pytest.raises(TypeError, match='loop'):
        container.add_method(callback, **loop_kwargs)
    assert len(container) == 0
    assert container.event_loop_map == {}


def test_informative_weak_dict_notifies_on_explicit_deletion():
    deleted = []
    values = InformativeWVDict(del_callback=deleted.append)
    value = WeakValue()
    values['key'] = value

    del values['key']

    assert deleted == ['key']
    assert 'key' not in values


def test_informative_weak_dict_notifies_when_value_is_collected():
    deleted = []
    values = InformativeWVDict(del_callback=deleted.append)
    value = WeakValue()
    values['key'] = value

    del value
    gc.collect()

    assert deleted == ['key']
    assert 'key' not in values


def test_informative_weak_dict_without_callback_still_raises_on_deletion():
    values = InformativeWVDict()
    value = WeakValue()
    values['key'] = value

    with pytest.raises(TypeError):
        del values['key']

    assert 'key' not in values
