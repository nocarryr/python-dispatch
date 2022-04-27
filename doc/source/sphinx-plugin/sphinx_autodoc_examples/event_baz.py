from pydispatch import Dispatcher, Event

class Baz(Dispatcher):
    """Summary line
    """

    _events_ = ['event_a']

    event_a: Event
    """Description of event_a
    """
