
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
    from pydispatch import Dispatcher
    from pydispatch.properties import ListProperty, DictProperty
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

    a.test_dict['nested_dict'] = {'foo':'bar'}
    a.test_dict['nested_dict']['foo'] = 'baz'
    a.test_dict['nested_dict']['nested_list'] = [0]
    a.test_dict['nested_dict']['nested_list'].append(1)

    assert len(listener.property_events) == 4
    assert a.test_dict['nested_dict']['nested_list'] == [0, 1]

    listener.property_events = []

    a.test_list.append({'nested_dict':{'foo':'bar'}})
    d = a.test_list[-1]
    d['nested_dict']['foo'] = 'baz'

    assert len(listener.property_events) == 2
    assert a.test_list[-1] == {'nested_dict':{'foo':'baz'}}

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
