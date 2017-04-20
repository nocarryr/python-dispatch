import asyncio
import pytest

@pytest.mark.asyncio
async def test_aio_event_lock(listener, sender):
    sender.register_event('on_test')
    sender.bind(on_test=listener.on_event)

    letters = 'abcdefghijkl'

    sender.emit('on_test', letters[0], emit_count=0)
    assert len(listener.received_event_data) == 1
    listener.received_event_data = []

    async with sender.emission_lock('on_test') as elock:
        assert elock.aio_lock.locked()
        for i in range(len(letters)):
            sender.emit('on_test', letters[i], emit_count=i)
    assert not elock.aio_lock.locked()

    assert len(listener.received_event_data) == 1
    e = listener.received_event_data[0]
    assert e['args'] == (letters[i], )
    assert e['kwargs']['emit_count'] == i

    listener.received_event_data = []

    async def do_emit(i):
        async with sender.emission_lock('on_test') as elock:
            assert elock.aio_lock.locked()
            sender.emit('on_test', i, 'first')
            sender.emit('on_test', i, 'second')
        assert not elock.aio_lock.locked()

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

    a = A()
    a.test_list = [-1] * 4
    a.test_dict = {'a':0, 'b':1, 'c':2, 'd':3}
    a.bind(test_prop=listener.on_prop, test_list=listener.on_prop, test_dict=listener.on_prop)

    async with a.emission_lock('test_prop') as elock:
        assert elock.aio_lock.locked()
        for i in range(4):
            a.test_prop = i
    assert not elock.aio_lock.locked()
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
