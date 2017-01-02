import pytest


@pytest.fixture
def listener():
    class Listener(object):
        def __init__(self):
            self.received_events = []
            self.received_event_data = []
            self.property_events = []
            self.property_event_kwargs = []
        def on_event(self, *args, **kwargs):
            self.received_event_data.append({'args':args, 'kwargs':kwargs})
            name = kwargs.get('triggered_event')
            if name is not None:
                self.received_events.append(name)
        def on_prop(self, obj, value, **kwargs):
            self.property_events.append(value)
            self.property_event_kwargs.append(kwargs)

    return Listener()


@pytest.fixture
def sender_cls():
    from pydispatch import Dispatcher
    class Sender(Dispatcher):
        def trigger_event(self, name, *args, **kwargs):
            kwargs['triggered_event'] = name
            self.emit(name, *args, **kwargs)
    return Sender

@pytest.fixture
def sender(sender_cls):
    return sender_cls()
