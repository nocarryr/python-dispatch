
def test_properties(listener):
    from pydispatch import Dispatcher, Property
    class A(Dispatcher):
        test_prop = Property('default')
        name = Property('')
        something = Property()
        def __init__(self, name):
            self.name = name
            self.something = 'stuff'

    a = A('foo')
    assert a.something == 'stuff'
    assert a.name == 'foo'
    a.bind(test_prop=listener.on_prop)

    assert 'test_prop' in a._Dispatcher__property_events
    assert len(a._Dispatcher__property_events['test_prop'].listeners) == 1

    assert a.test_prop == 'default'
    a.test_prop = 'a'
    a.test_prop = 'a'
    a.test_prop = 'b'
    assert listener.property_events == ['a', 'b']

def test_container_properties(listener):
    from pydispatch import Dispatcher, ListProperty, DictProperty

    class A(Dispatcher):
        test_dict = DictProperty({'defaultkey':'defaultval'})
        test_list = ListProperty(['defaultitem'])

    a = A()
    a.bind(test_dict=listener.on_prop, test_list=listener.on_prop)

    assert a.test_dict['defaultkey'] == 'defaultval'
    assert a.test_list[0] == 'defaultitem'

    a.test_dict = {'changed':True}
    a.test_list = ['changed']

    assert a.test_dict['changed'] is True and len(a.test_dict) == 1
    assert a.test_list[0] == 'changed' and len(a.test_list) == 1

    assert listener.property_events == [{'changed':True}, ['changed']]

    listener.property_events = []
    listener.property_event_kwargs = []
    a.test_dict['nested_dict'] = {'foo':'bar'}
    a.test_dict['nested_dict']['foo'] = 'baz'
    a.test_dict['nested_dict']['nested_list'] = [0]
    a.test_dict['nested_dict']['nested_list'].append(1)

    assert len(listener.property_events) == 4
    assert a.test_dict['nested_dict']['nested_list'] == [0, 1]
    assert 'nested_dict' in listener.property_event_kwargs[0]['keys']

    listener.property_events = []

    a.test_list.append({'nested_dict':{'foo':'bar'}})
    d = a.test_list[-1]
    d['nested_dict']['foo'] = 'baz'

    assert len(listener.property_events) == 2
    assert a.test_list[-1] == {'nested_dict':{'foo':'baz'}}

    listener.property_events = []
    del a.test_list[:]
    assert len(listener.property_events) == 1
    assert len(a.test_list) == 0

    if hasattr(list, 'clear'):
        listener.property_events = []
        a.test_list.append(42)
        a.test_list.clear()
        a.test_list.append(True)
        assert len(listener.property_events) == 3

def test_list_property_ops(listener):
    from pydispatch import Dispatcher, ListProperty

    class A(Dispatcher):
        test_list = ListProperty()

    a = A()
    a.bind(test_list=listener.on_prop)

    # Test slicing
    listener.property_events = []
    a.test_list[1:4] = ['a', 'b', 'c', 'd']
    assert len(listener.property_events) == 1
    assert a.test_list == ['a', 'b', 'c', 'd']

    # Test __setitem__
    listener.property_events = []
    listener.property_event_kwargs = []
    a.test_list[0] = 'z'
    assert len(listener.property_events) == 1
    assert a.test_list == ['z', 'b', 'c', 'd']
    assert listener.property_event_kwargs[0]['keys'] == [0]

    # Test __delitem__
    listener.property_events = []
    del a.test_list[0]
    assert len(listener.property_events) == 1
    assert a.test_list == ['b', 'c', 'd']

    # Test remove
    listener.property_events = []
    a.test_list = ['a', 'b', 'c', 'd']
    a.test_list.remove('d')
    assert len(listener.property_events) == 2
    assert a.test_list == ['a', 'b', 'c']

    # Test __iadd__
    listener.property_events = []
    a.test_list = ['a', 'b', 'c', 'd']
    a.test_list += ['e', 'f', 'g']
    assert a.test_list == ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    assert len(listener.property_events) == 2

def test_dict_property_ops(listener):
    from pydispatch import Dispatcher, DictProperty

    class A(Dispatcher):
        test_dict = DictProperty({'a':1, 'b':2, 'c':3, 'd':4})

    a = A()
    a.bind(test_dict=listener.on_prop)

    v = a.test_dict.pop('a')
    assert len(listener.property_events) == 1
    assert 'a' not in a.test_dict

    listener.property_events = []
    del a.test_dict['b']
    assert len(listener.property_events) == 1
    assert 'b' not in a.test_dict

    listener.property_events = []
    listener.property_event_kwargs = []
    a.test_dict.update({'c':3, 'e':5, 'f':6, 'g':7})
    assert len(listener.property_events) == 1
    assert a.test_dict == {'c':3, 'd':4, 'e':5, 'f':6, 'g':7}
    assert sorted(listener.property_event_kwargs[0]['keys']) == ['e', 'f', 'g']

    listener.property_events = []
    a.test_dict.clear()
    assert len(listener.property_events) == 1
    assert len(a.test_dict) == 0

    listener.property_events = []
    a.test_dict.setdefault('foo', 'bar')
    assert len(listener.property_events) == 1
    assert a.test_dict['foo'] == 'bar'

def test_empty_defaults(listener):
    from pydispatch import Dispatcher, ListProperty, DictProperty
    from pydispatch.properties import ObservableList, ObservableDict

    class A(Dispatcher):
        test_dict = DictProperty()
        test_list = ListProperty()

    a = A()
    a.bind(test_dict=listener.on_prop, test_list=listener.on_prop)

    assert isinstance(a.test_dict, ObservableDict)
    assert isinstance(a.test_list, ObservableList)

    a.test_dict['foo'] = 'bar'
    a.test_list.append('baz')

    assert isinstance(a.test_dict, ObservableDict)
    assert isinstance(a.test_list, ObservableList)

    assert len(listener.property_events) == 2

def test_unbind(listener):
    from pydispatch import Dispatcher, Property
    class A(Dispatcher):
        test_prop = Property()
    a = A()
    a.bind(test_prop=listener.on_prop)

    a.test_prop = 1
    assert len(listener.property_events) == 1

    listener.property_events = []

    # unbind by method
    a.unbind(listener.on_prop)
    a.test_prop = 2
    assert len(listener.property_events) == 0

    # rebind and make sure events still work
    a.bind(test_prop=listener.on_prop)
    a.test_prop = 3
    assert len(listener.property_events) == 1

    listener.property_events = []

    # unbind by instance
    a.unbind(listener)
    a.test_prop = 4
    assert len(listener.property_events) == 0

def test_removal():
    from pydispatch import Dispatcher, Property

    class Listener(object):
        def __init__(self):
            self.property_events = []
        def on_prop(self, obj, value, **kwargs):
            self.property_events.append(value)

    class A(Dispatcher):
        test_prop = Property()

    listener = Listener()
    a = A()

    a.bind(test_prop=listener.on_prop)
    a.test_prop = 1
    assert len(listener.property_events) == 1

    del listener

    e = a._Dispatcher__property_events['test_prop']
    l = [m for m in e.listeners]
    assert len(l) == 0

    prop = A._PROPERTIES_['test_prop']
    del a
    assert len(prop._Property__weakrefs) == 0
    assert len(prop._Property__storage) == 0

def test_self_binding():
    from pydispatch import Dispatcher, Property, ListProperty, DictProperty

    class A(Dispatcher):
        test_prop = Property()
        test_dict = DictProperty()
        test_list = ListProperty()
        def __init__(self):
            self.received = []
            self.bind(
                test_prop=self.on_test_prop,
                test_dict=self.on_test_dict,
                test_list=self.on_test_list,
            )
        def on_test_prop(self, *args, **kwargs):
            self.received.append('test_prop')
        def on_test_dict(self, *args, **kwargs):
            self.received.append('test_dict')
        def on_test_list(self, *args, **kwargs):
            self.received.append('test_list')

    a = A()

    a.test_prop = 'foo'
    a.test_dict['foo'] = 'bar'
    a.test_list.append('baz')

    assert a.received == ['test_prop', 'test_dict', 'test_list']

def test_emission_lock(listener):
    from pydispatch import Dispatcher, Property, ListProperty, DictProperty

    class A(Dispatcher):
        test_prop = Property()
        test_dict = DictProperty()
        test_list = ListProperty()

    a = A()
    a.bind(test_prop=listener.on_prop, test_list=listener.on_prop, test_dict=listener.on_prop)

    letters = 'abcdefghijkl'

    a.test_prop = 'foo'
    a.test_list = [-1] * 4
    a.test_dict = {'a':0, 'b':1, 'c':2, 'd':3}

    assert len(listener.property_events) == 3
    listener.property_events = []
    listener.property_event_kwargs = []

    with a.emission_lock('test_prop'):
        for i in range(4):
            a.test_prop = i
    assert len(listener.property_events) == 1
    assert listener.property_event_kwargs[0]['property'].name == 'test_prop'
    assert listener.property_events[0] == i

    listener.property_events = []
    listener.property_event_kwargs = []

    with a.emission_lock('test_list'):
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

    with a.emission_lock('test_dict'):
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

    with a.emission_lock('test_prop'):
        with a.emission_lock('test_list'):
            with a.emission_lock('test_dict'):
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

def test_copy_on_change(listener):
    from pydispatch import Dispatcher, ListProperty, DictProperty

    class A(Dispatcher):
        test_dict = DictProperty(copy_on_change=True)
        test_list = ListProperty(copy_on_change=True)
        no_cp_dict = DictProperty()
        no_cp_list = ListProperty()

    a = A()
    a.bind(
        test_dict=listener.on_prop, test_list=listener.on_prop,
        no_cp_dict=listener.on_prop, no_cp_list=listener.on_prop,
    )

    a.test_dict['foo'] = 'bar'
    assert listener.property_event_kwargs[0]['old'] == {}

    a.test_dict['foo'] = None
    assert listener.property_event_kwargs[1]['old'] == {'foo':'bar'}

    a.test_dict['nested_dict'] = {'a':1}
    assert listener.property_event_kwargs[2]['old'] == {'foo':None}

    a.test_dict['nested_dict']['b'] = 2
    assert listener.property_event_kwargs[3]['old'] == {'foo':None, 'nested_dict':{'a':1}}

    a.test_dict['nested_list'] = ['a', 'b']
    assert listener.property_event_kwargs[4]['old'] == {
        'foo':None, 'nested_dict':{'a':1, 'b':2}
    }

    a.test_dict['nested_list'].append('c')
    assert listener.property_event_kwargs[5]['old'] == {
        'foo':None, 'nested_dict':{'a':1, 'b':2}, 'nested_list':['a', 'b']
    }

    listener.property_event_kwargs = []

    a.test_list.append('a')
    assert listener.property_event_kwargs[0]['old'] == []

    a.test_list.extend(['b', 'c'])
    assert listener.property_event_kwargs[1]['old'] == ['a']

    a.test_list[0] = {}
    assert listener.property_event_kwargs[2]['old'] == ['a', 'b', 'c']

    a.test_list[0]['foo'] = 'bar'
    assert listener.property_event_kwargs[3]['old'] == [{}, 'b', 'c']

    a.test_list[1] = [0]
    assert listener.property_event_kwargs[4]['old'] == [{'foo':'bar'}, 'b', 'c']

    a.test_list[1].append(1)
    assert listener.property_event_kwargs[5]['old'] == [{'foo':'bar'}, [0], 'c']

    listener.property_event_kwargs = []

    a.no_cp_dict['foo'] = 'bar'
    assert listener.property_event_kwargs[0]['old'] == None

    a.no_cp_dict['nested_dict'] = {}
    assert listener.property_event_kwargs[1]['old'] == None

    a.no_cp_dict['nested_dict']['a'] = 1
    assert listener.property_event_kwargs[2]['old'] == None

    a.no_cp_dict['nested_list'] = []
    assert listener.property_event_kwargs[3]['old'] == None

    a.no_cp_dict['nested_list'].append(1)
    assert listener.property_event_kwargs[4]['old'] == None

    listener.property_event_kwargs = []

    a.no_cp_list.append('a')
    assert listener.property_event_kwargs[0]['old'] == None

    a.no_cp_list.extend(['b', 'c'])
    assert listener.property_event_kwargs[1]['old'] == None

    a.no_cp_list[0] = {}
    assert listener.property_event_kwargs[2]['old'] == None

    a.no_cp_list[0]['foo'] = 'bar'
    assert listener.property_event_kwargs[3]['old'] == None

    a.no_cp_list[1] = []
    assert listener.property_event_kwargs[4]['old'] == None

    a.no_cp_list[1].append(1)
    assert listener.property_event_kwargs[5]['old'] == None
