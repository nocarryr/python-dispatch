
def test_basic(listener, sender):
    sender.register_event('on_test_a')
    assert 'on_test_a' in sender._Dispatcher__events.keys()

    sender.register_event('on_test_b', 'on_test_c')
    assert len(sender._Dispatcher__events) == 3

    sender.bind(
        on_test_a=listener.on_event,
        on_test_b=listener.on_event,
        on_test_c=listener.on_event,
    )

    names = ['on_test_a', 'on_test_b', 'on_test_c']
    for name in names:
        sender.trigger_event(name)
    assert len(listener.received_events) == 3
    assert listener.received_events == names

def test_cls_events(listener, sender_cls):
    class A(sender_cls):
        _events_ = ['on_test_a']
        def trigger_own_event(self):
            self.trigger_event('on_test_a')

    class B(A):
        _events_ = ['on_test_b']
        def trigger_own_event(self):
            super(B, self).trigger_own_event()
            self.trigger_event('on_test_b')

    a = A()
    b = B()
    a.bind(on_test_a=listener.on_event)
    b.bind(on_test_a=listener.on_event, on_test_b=listener.on_event)

    assert 'on_test_a' in a._Dispatcher__events.keys()
    assert len(a._Dispatcher__events) == 1
    assert len(a._Dispatcher__events['on_test_a'].listeners) ==1

    assert 'on_test_b' in b._Dispatcher__events.keys()
    assert len(b._Dispatcher__events) == 2

    a.trigger_own_event()
    assert listener.received_events == ['on_test_a']
    b.trigger_own_event()
    assert listener.received_events == ['on_test_a', 'on_test_a', 'on_test_b']

def test_unbind(listener, sender):
    names = ['on_test_a', 'on_test_b']
    sender.register_event(*names)
    sender.bind(**{name:listener.on_event for name in names})

    for name in names:
        sender.trigger_event(name)
    assert listener.received_events == names

    listener.received_events = []

    # unbind by method
    sender.unbind(listener.on_event)
    for name in names:
        sender.trigger_event(name)
    assert len(listener.received_events) == 0

    # rebind and make sure events still work
    sender.bind(**{name:listener.on_event for name in names})
    for name in names:
        sender.trigger_event(name)
    assert listener.received_events == names

    listener.received_events = []

    # unbind by instance
    sender.unbind(listener)
    for name in names:
        sender.trigger_event(name)
    assert len(listener.received_events) == 0

def test_removal(sender):
    class Listener(object):
        def __init__(self):
            self.received_events = []
        def on_event(self, *args, **kwargs):
            self.received_events.append(kwargs.get('triggered_event'))
    listener = Listener()

    sender.register_event('on_test')
    sender.bind(on_test=listener.on_event)

    sender.trigger_event('on_test')
    assert len(listener.received_events) == 1

    del listener
    e = sender._Dispatcher__events['on_test']
    l = [m for m in e.listeners]
    assert len(l) == 0
    sender.trigger_event('on_test')
