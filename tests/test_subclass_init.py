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
