"""Properties

:class:`Property` objects can be defined on subclasses of
:class:`~pydispatch.Dispatcher` to create instance attributes that act as events
when their values change::

    from pydispatch import Dispatcher, Property

    class Foo(Dispatcher):
        name = Property()
        value = Property()
    def __str__(self):
        return self.__class__.__name__

    class Listener(object):
        def on_foo_name(self, instance, value, **kwargs):
            print("{}'s name is {}".format(instance, value))
        def on_foo_value(self, instance, value, **kwargs):
            print('{} = {}'.format(instance, value))

    foo_obj = Foo()
    listener_obj = Listener()

    foo_obj.bind(name=listener_obj.on_foo_name, value=listener_obj.on_foo_value)

    foo_obj.name = 'bar'
    # Foo's name is bar

    foo_obj.value = 42
    # Foo = 42

Type checking is not enforced, so values can be any valid python type.
Values are however checked for equality to avoid dispatching events for no
reason. If custom objects are used as values, they must be able to support
equality checking. In most cases, this will be handled automatically.
"""

import sys
import weakref

from pydispatch.utils import InformativeWVDict

PY2 = sys.version_info < (3,)

class Property(object):
    """Defined on the class level to create an observable attribute

    Args:
        default (Optional): If supplied, this will be the default value of the
            Property for all instances of the class. Otherwise ``None``

    Attributes:
        name (str): The name of the Property as defined in the class definition.
            This will match the attribute name for the :class:`Dispatcher` instance.

    """
    def __init__(self, default=None):
        self._name = ''
        self.default = default
        self.__storage = {}
        self.__weakrefs = InformativeWVDict(del_callback=self._on_weakref_fin)
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        if self._name != '':
            return
        self._name = value
    def _add_instance(self, obj, default=None):
        if default is None:
            default = self.default
        self.__storage[id(obj)] = self.default
        self.__weakrefs[id(obj)] = obj
    def _del_instance(self, obj):
        del self.__storage[id(obj)]
    def _on_weakref_fin(self, obj_id):
        del self.__storage[obj_id]
    def __get__(self, obj, objcls=None):
        if obj is None:
            return self
        obj_id = id(obj)
        if obj_id not in self.__storage:
            self._add_instance(obj)
        return self.__storage[obj_id]
    def __set__(self, obj, value):
        obj_id = id(obj)
        if obj_id not in self.__storage:
            self._add_instance(obj)
        current = self.__storage[obj_id]
        if current == value:
            return
        self.__storage[obj_id] = value
        self._on_change(obj, current, value)
    def _on_change(self, obj, old, value, **kwargs):
        """Called internally to emit changes from the instance object

        The keyword arguments here will be passed to callbacks through the
        instance object's :meth:`~Dispatcher.emit` method.

        Keyword Args:
            property: The :class:`Property` instance. This is useful if multiple
                properties are bound to the same callback. The attribute name
            keys (optional): If the :class:`Property` is a container type
                (:class:`ListProperty` or :class:`DictProperty`), the changes
                may be found here.
                This is not implemented for nested containers and will only be
                available for operations that do not alter the size of the
                container.

        """
        kwargs['property'] = self
        obj.emit(self.name, obj, value, old=old, **kwargs)
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__, self)
    def __str__(self):
        return self.name

class ListProperty(Property):
    """Property with a ``list`` type value

    Changes to the contents of the list are able to be observed through
    :class:`ObservableList`.
    """
    def __init__(self, default=None):
        if default is None:
            default = []
        super(ListProperty, self).__init__(default)
    def _add_instance(self, obj):
        default = self.default[:]
        default = ObservableList(default, obj=obj, property=self)
        super(ListProperty, self)._add_instance(obj, default)
    def __set__(self, obj, value):
        value = ObservableList(value, obj=obj, property=self)
        super(ListProperty, self).__set__(obj, value)
    def __get__(self, obj, objcls=None):
        if obj is None:
            return self
        value = super(ListProperty, self).__get__(obj, objcls)
        if not isinstance(value, ObservableList):
            value = ObservableList(value, obj=obj, property=self)
            self._Property__storage[id(obj)] = value
        return value

class DictProperty(Property):
    """Property with a ``dict`` type value

    Changes to the contents of the dict are able to be observed through
    :class:`ObservableDict`.
    """
    def __init__(self, default=None):
        if default is None:
            default = {}
        super(DictProperty, self).__init__(default)
    def _add_instance(self, obj):
        default = self.default.copy()
        default = ObservableDict(default, obj=obj, property=self)
        super(DictProperty, self)._add_instance(obj, default)
    def __set__(self, obj, value):
        value = ObservableDict(value, obj=obj, property=self)
        super(DictProperty, self).__set__(obj, value)
    def __get__(self, obj, objcls=None):
        if obj is None:
            return self
        value = super(DictProperty, self).__get__(obj, objcls)
        if not isinstance(value, ObservableDict):
            value = ObservableDict(value, obj=obj, property=self)
            self._Property__storage[id(obj)] = value
        return value

class Observable(object):
    """Used by container subclasses to emit changes and build other observables

    When an item is added to an observable container (a subclass of Observable)
    it is type-checked and, if possible replaced by an observable version of it.

    In other words, if a ``dict`` is added to a :class:`ObservableDict`, it is
    copied and replaced by another :class:`ObservableDict`. This allows nested
    containers to be observed and their changes to be tracked.
    """
    def _build_observable(self, item):
        if isinstance(item, list):
            item = ObservableList(item, parent=self)
        elif isinstance(item, dict):
            item = ObservableDict(item, parent=self)
        return item
    def _emit_change(self, **kwargs):
        if not self._init_complete:
            return
        p = self.parent_observable
        if p is not None:
            p._emit_change()
            return
        self.property._on_change(self.obj, None, self, **kwargs)

class ObservableList(list, Observable):
    """A ``list`` object that tracks changes to its contents
    """
    def __init__(self, initlist=None, **kwargs):
        self._init_complete = False
        super(ObservableList, self).__init__()
        self.property = kwargs.get('property')
        self.obj = kwargs.get('obj')
        self.parent_observable = kwargs.get('parent')
        if initlist is not None:
            self.extend(initlist)
        self._init_complete = True
    def __setitem__(self, key, item):
        item = self._build_observable(item)
        super(ObservableList, self).__setitem__(key, item)
        self._emit_change(keys=[key])
    def __delitem__(self, key):
        super(ObservableList, self).__delitem__(key)
        self._emit_change()
    if PY2:
        def __setslice__(self, *args):
            super(ObservableList, self).__setslice__(*args)
            self._emit_change()
        def __delslice__(self, *args):
            super(ObservableList, self).__delslice__(*args)
            self._emit_change()
    if hasattr(list, 'clear'):
        def clear(self):
            super(ObservableList, self).clear()
            self._emit_change()
    def __iadd__(self, other):
        other = self._build_observable(other)
        self.extend(other)
        return self
    def append(self, item):
        item = self._build_observable(item)
        super(ObservableList, self).append(item)
        self._emit_change()
    def extend(self, other):
        init = self._init_complete
        self._init_complete = False
        for item in other:
            self.append(item)
        if init:
            self._init_complete = True
        self._emit_change()
    def remove(self, *args):
        super(ObservableList, self).remove(*args)
        self._emit_change()

class ObservableDict(dict, Observable):
    """A ``dict`` object that tracks changes to its contents
    """
    def __init__(self, initdict=None, **kwargs):
        self._init_complete = False
        super(ObservableDict, self).__init__()
        self.property = kwargs.get('property')
        self.obj = kwargs.get('obj')
        self.parent_observable = kwargs.get('parent')
        if initdict is not None:
            self.update(initdict)
        self._init_complete = True
    def __setitem__(self, key, item):
        item = self._build_observable(item)
        super(ObservableDict, self).__setitem__(key, item)
        self._emit_change(keys=[key])
    def __delitem__(self, key):
        super(ObservableDict, self).__delitem__(key)
        self._emit_change()
    def update(self, other):
        init = self._init_complete
        self._init_complete = False
        keys = set(other.keys()) - set(self.keys())
        for key, val in other.items():
            if key not in keys and self[key] == val:
                continue
            self[key] = val
            keys.add(key)
        if init:
            self._init_complete = True
        self._emit_change(keys=list(keys))
    def clear(self):
        super(ObservableDict, self).clear()
        self._emit_change()
    def pop(self, *args):
        super(ObservableDict, self).pop(*args)
        self._emit_change()
    def setdefault(self, *args):
        super(ObservableDict, self).setdefault(*args)
        self._emit_change()
