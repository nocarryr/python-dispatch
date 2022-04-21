from pydispatch import Dispatcher, Event

class TheClass(Dispatcher):
    """Docstring for TheClass

    Look at :event:`on_foo`, :attr:`on_bar` and
    :obj:`on_baz`
    """
    _events_ = ['on_foo', 'on_bar', 'on_baz']

    on_foo: Event
    """Documentation for on_foo event"""

    on_bar: Event
    """Documentation for on_bar event"""

    def on_baz(self, name: str, value: int, **kwargs):
        """Documentation for on_baz event
        """
        pass
