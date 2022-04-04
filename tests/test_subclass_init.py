import math
import time
import warnings

def test_dispatcher_construction():
    from pydispatch import Dispatcher, Property

    class A(Dispatcher):
        foo = Property()
        bar = Property()
        baz = Property()
        _events_ = [
            'on_stuff', 'on_more_stuff',
        ]
    class B(A):
        a = Property()
        b = Property()
        c = Property()
        _events_ = [
            'on_even_more_stuff', 'on_one_more_thing'
        ]

    with warnings.catch_warnings(record=True) as w_list:
        warnings.simplefilter("always")
        a = A()
        b = B()
        for w in w_list:
            # Check for PEP-0479 (StopIteration) issues
            assert not issubclass(w.category, DeprecationWarning)
            assert not issubclass(w.category, PendingDeprecationWarning)
        assert len(w_list) == 0

    a_prop_names = {'foo', 'bar', 'baz'}
    a_event_names = {'on_stuff', 'on_more_stuff'}
    assert a_prop_names == set(a._Dispatcher__property_events.keys())
    assert a_event_names == set(a._Dispatcher__events.keys())

    b_prop_names = {'a', 'b', 'c'}
    b_prop_names |= a_prop_names
    b_event_names = {'on_even_more_stuff', 'on_one_more_thing'}
    b_event_names |= a_event_names

    assert b_prop_names == set(b._Dispatcher__property_events.keys())
    assert b_event_names == set(b._Dispatcher__events.keys())


def test_new_class_creation():
    from pydispatch import Dispatcher
    from pydispatch.properties import Property, DictProperty

    class A(Dispatcher):
        prop_a = Property()
        _events_ = ['a_event']
    a_props = {'prop_a':A.prop_a}

    class B(A):
        prop_b = Property()
        _events_ = ['b_event']
    b_props = {'prop_a':A.prop_a, 'prop_b':B.prop_b}

    class C(B):
        prop_a = DictProperty()             # Override A.prop_a
        prop_c = Property()
        _events_ = ['a_event', 'c_event']   # Redefine 'a_event'
    c_props = {'prop_a':C.prop_a, 'prop_b':B.prop_b, 'prop_c':C.prop_c}

    assert A._PROPERTIES_ == a_props
    assert A._EVENTS_ == {'a_event'}
    assert B._PROPERTIES_ == b_props
    assert B._EVENTS_ == {'a_event', 'b_event'}
    assert C._PROPERTIES_ == c_props
    assert C._EVENTS_ == {'a_event', 'b_event', 'c_event'}

    assert C.prop_a is not A.prop_a
    assert C.prop_b is B.prop_b
    assert B.prop_a is A.prop_a

    a, b, c = A(), B(), C()

    for attr in ['prop_b', 'prop_c']:
        assert not hasattr(a, attr)
    assert not hasattr(b, 'prop_c')

    a.prop_a = 'aa'
    assert b.prop_a is None
    assert c.prop_a == {}
    b.prop_a = 'ba'
    b.prop_b = 'bb'
    assert a.prop_a != b.prop_a
    assert c.prop_a == {}
    assert c.prop_b is c.prop_b is None
    c.prop_a = {'ca':1}
    c.prop_b = 'cb'
    c.prop_c = 'cc'
    assert a.prop_a != b.prop_a != c.prop_a
    assert b.prop_b != c.prop_b
