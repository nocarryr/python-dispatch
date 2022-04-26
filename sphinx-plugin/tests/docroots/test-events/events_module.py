from pydispatch import Dispatcher, Event

class TheClass(Dispatcher):
    """Docstring for TheClass

    Look at :event:`on_foo`, :attr:`on_bar` and
    :obj:`on_baz`
    """
    _events_ = ['on_foo', 'on_bar', 'on_baz']

    a_normal_attribute: str
    """Documentation for a_normal_attribute"""

    on_foo: Event
    """Documentation for on_foo event"""

    on_bar: Event
    """Documentation for on_bar event"""

    def on_baz(self, name: str, value: int, **kwargs):
        """Documentation for on_baz event
        """
        pass

class TheSubClass(TheClass):
    """Docstring for TheSubClass

    Look at :event:`on_spam` and :event:`on_eggs`
    """
    _events_ = ['on_spam', 'on_eggs']

    on_spam: Event
    """Documentation for on_spam event"""

    def on_eggs(self, scrambled: bool, **kwargs):
        """Documentation for on_eggs event"""
        pass

    def a_normal_method(self, value: int) -> int:
        """Documentation for a_normal_method
        """
        return value + 1

class TheOverridingSubClass(TheSubClass):
    """Docstring for TheOverridingSubClass

    I override docstrings for :event:`on_foo` and :event:`on_eggs`
    """

    def on_foo(self, state: bool, **kwargs):
        """Overriden documentation for :event:`TheClass.on_foo` event"""
        pass

    def on_eggs(self, over_easy: bool, **kwargs):
        """Overriden documentation for :event:`TheSubClass.on_eggs` event"""
        pass

class NonDispatcherClass:
    """Docstring for NonDispatcherClass
    """

    def __init__(self, *args, **kwargs):
        pass

    on_foo: Event
    """I should not be recognized by this extension"""

    def on_bar(self):
        """I should not be recognized by this extension"""
