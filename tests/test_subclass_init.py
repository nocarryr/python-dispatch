import sys
import math
import time
import warnings
import pytest

VERSION_INFO = (sys.version_info.major, sys.version_info.minor)

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

@pytest.mark.skipif(
    VERSION_INFO >= (3, 6),
    reason='Python >= 3.6 uses __init_subclass__',
)
def test_subclass_new_timing():
    from pydispatch import Dispatcher, Property

    timings = {}

    for skip_initialized in [False, True]:
        print('skip_initialized: ', skip_initialized)
        Dispatcher._Dispatcher__skip_initialized = skip_initialized
        Dispatcher._Dispatcher__initialized_subclasses.clear()

        class A(Dispatcher):
            foo = Property()
            bar = Property()
            baz = Property()
            _events_ = [
                'on_stuff', 'on_more_stuff',
            ]
            def __init__(self, *args, **kwargs):
                self.foo = 1
                self.bar = 2
                self.baz = 3
        class B(A):
            a = Property()
            b = Property()
            c = Property()
            _events_ = [
                'on_even_more_stuff', 'on_one_more_thing'
            ]
            def __init__(self, *args, **kwargs):
                super(B, self).__init__(*args, **kwargs)
                self.a = 1
                self.b = 2
                self.c = 3

        times = []
        start_ts = time.time()

        for i in range(40000):
            before_init = time.time()
            obj = B()
            post_init = time.time()
            times.append(post_init - before_init)

        total_time = post_init - start_ts
        min_time = min(times)
        max_time = max(times)
        avg_time = math.fsum(times) / len(times)
        print('total_time={}, avg={}, min={}, max={}'.format(
            total_time, avg_time, min_time, max_time))

        timings[skip_initialized] = {'total':total_time, 'avg':avg_time}

    assert (timings[True]['avg'] < timings[False]['avg'] or
                timings[True]['total'] < timings[False]['total'])

@pytest.mark.skipif(
    VERSION_INFO < (3, 6),
    reason='__init_subclass__ not available in Python < 3.6',
)
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
    assert not len(a._Dispatcher__initialized_subclasses)
    assert not len(b._Dispatcher__initialized_subclasses)
    assert not len(c._Dispatcher__initialized_subclasses)

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
