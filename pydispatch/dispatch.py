import types

from pydispatch.utils import WeakMethodContainer
from pydispatch.properties import Property


class Event(object):
    __slots__ = ('name', 'listeners')
    def __init__(self, name):
        self.name = name
        self.listeners = WeakMethodContainer()
    def add_listener(self, callback):
        self.listeners.add_method(callback)
    def remove_listener(self, obj):
        if isinstance(obj, types.MethodType):
            self.listeners.del_method(obj)
        else:
            self.listeners.del_instance(obj)
    def __call__(self, *args, **kwargs):
        for m in self.listeners.iter_methods():
            r = m(*args, **kwargs)
            if r is False:
                return r
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__, self)
    def __str__(self):
        return self.name

class Dispatcher(object):
    def __new__(cls, *args, **kwargs):
        def iter_bases(_cls):
            if _cls is object:
                raise StopIteration
            yield _cls
            for b in _cls.__bases__:
                for _cls_ in iter_bases(b):
                    yield _cls_
        props = {}
        events = set()
        for _cls in iter_bases(cls):
            for attr in dir(_cls):
                prop = getattr(_cls, attr)
                if attr not in props and isinstance(prop, Property):
                    props[attr] = prop
                    prop.name = attr
                _events = getattr(_cls, '_events_', [])
                events |= set(_events)
        cls._PROPERTIES_ = props
        cls._EVENTS_ = events
        obj = super(Dispatcher, cls).__new__(cls)
        obj._Dispatcher__init_events()
        return obj
    def __init_events(self):
        if hasattr(self, '_Dispatcher__events'):
            return
        self.__events = {}
        for name in self._EVENTS_:
            self.__events[name] = Event(name)
        self.__property_events = {}
        for name, prop in self._PROPERTIES_.items():
            self.__property_events[name] = Event(name)
            prop._add_instance(self)
    def register_event(self, *names):
        for name in names:
            if name in self.__events:
                continue
            self.__events[name] = Event(name)
    def bind(self, **kwargs):
        props = self.__property_events
        events = self.__events
        for name, cb in kwargs.items():
            if name in props:
                e = props[name]
            else:
                e = events[name]
            e.add_listener(cb)
    def unbind(self, *args):
        props = self.__property_events.values()
        events = self.__events.values()
        for arg in args:
            for prop in props:
                prop.remove_listener(arg)
            for e in events:
                e.remove_listener(arg)
    def emit(self, name, *args, **kwargs):
        e = self.__property_events.get(name)
        if e is None:
            e = self.__events[name]
        return e(*args, **kwargs)
