"""
:class:`Property` objects can be defined on subclasses of
:class:`~pydispatch.dispatch.Dispatcher` to create instance attributes that act
as events when their values change

.. doctest:: properties_module

    >>> from pydispatch import Dispatcher, Property

    >>> class Foo(Dispatcher):
    ...     name = Property()
    ...     value = Property()
    ...     def __str__(self):
    ...         return self.__class__.__name__

    >>> class Listener(object):
    ...     def on_foo_name(self, instance, value, **kwargs):
    ...         print("{}'s name is {}".format(instance, value))
    ...     def on_foo_value(self, instance, value, **kwargs):
    ...         print('{} = {}'.format(instance, value))

    >>> foo_obj = Foo()
    >>> listener_obj = Listener()
    >>> foo_obj.bind(name=listener_obj.on_foo_name, value=listener_obj.on_foo_value)

    >>> foo_obj.name = 'bar'
    Foo's name is bar
    >>> foo_obj.value = 42
    Foo = 42

Type checking is not enforced, so values can be any valid python type.
Values are however checked for equality to avoid dispatching events for no
reason. If custom objects are used as values, they must be able to support
equality checking. In most cases, this will be handled automatically.
"""

import weakref
import numbers
from fractions import Fraction
from typing import Optional, Tuple

from pydispatch.utils import InformativeWVDict


__all__ = [
    'Property', 'StringProperty', 'BoolProperty', 'IntProperty', 'FloatProperty',
    'ComplexProperty', 'FractionProperty', 'ListProperty', 'DictProperty',
]

NumberOrNone = Optional[numbers.Number]

class ValidationError(ValueError):
    def __init__(self, prop, value, obj=None):
        self.prop = prop
        self.obj = obj
        self.value = value
    def __str__(self):
        return f'Value "{self.value!r}" not valid for {self.prop!r}'

class NoneNotAllowedError(ValidationError):
    def __str__(self):
        return f'"None" not allowed for {self.prop!r}'

class InvalidTypeError(ValidationError):
    def __str__(self):
        value_type = type(self.value)
        return f'Type "{value_type.__name__}" not valid for {self.prop!r}'

class OutOfRangeError(ValidationError):
    def __str__(self):
        vmin, vmax = self.prop.get_range(self.obj)
        range_str = f'{vmin} <= value <= {vmax}'
        return f'Value {self.value} must be in range "{range_str}" for {self.prop!r}'

class Property(object):
    """Defined on the class level to create an observable attribute

    Args:
        default (Optional): If supplied, this will be the default value of the
            Property for all instances of the class. Otherwise :obj:`None`
        allownone (bool, optional): If False, prevents assigning :obj:`None`
            to the Property. Default is True (where *None* is allowed)

    Attributes:
        name (str): The name of the Property as defined in the class definition.
            This will match the attribute name for the
            :class:`~pydispatch.dispatch.Dispatcher` instance.

    """
    def __init__(self, default=None, allownone=True):
        self._name = ''
        self.default = default
        self.allownone = allownone
        self.__storage = {}
        self.__weakrefs = InformativeWVDict(del_callback=self._on_weakref_fin)
    @property
    def name(self):
        return self._name
    def __set_name__(self, owner, name):
        self._name = name
    def _add_instance(self, obj, default=None):
        if default is None:
            default = self.default
        self.__storage[id(obj)] = self.default
        self.__weakrefs[id(obj)] = obj
    def _del_instance(self, obj):
        del self.__storage[id(obj)]
    def _on_weakref_fin(self, obj_id):
        if obj_id in self.__storage:
            del self.__storage[obj_id]
    def __get__(self, obj, objcls=None):
        if obj is None:
            return self
        obj_id = id(obj)
        if obj_id not in self.__storage:
            self._add_instance(obj)
        return self.__storage[obj_id]
    def __set__(self, obj, value):
        if value is None and not self.allownone:
            raise NoneNotAllowedError(self, value)
        obj_id = id(obj)
        if obj_id not in self.__storage:
            self._add_instance(obj)
        current = self.__storage[obj_id]
        if value is not None:
            value = self._validate_value(obj, value)
        if current == value:
            return
        self.__storage[obj_id] = value
        self._on_change(obj, current, value)
    def _validate_value(self, obj, value):
        return value
    def _on_change(self, obj, old, value, **kwargs):
        """Called internally to emit changes from the instance object

        The keyword arguments here will be passed to callbacks through the
        instance object's :meth:`~pydispatch.dispatch.Dispatcher.emit` method.

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

class StringProperty(Property):
    """A Property allowing only string values
    """
    def _validate_value(self, obj, value):
        if not isinstance(value, str):
            raise InvalidTypeError(self, value)
        return value

class BoolProperty(Property):
    """A Property allowing :class:`bool` values
    """
    def __init__(self, default=False, allownone=False):
        super().__init__(default, allownone)

    def _validate_value(self, obj, value):
        if type(value) is not bool:
            raise InvalidTypeError(self, value)
        return value

class NumericProperty(Property):
    """A Property for numeric values

    Keyword Arguments:
        min (numbers.Number, optional): The minimum value allowed for the
            Property. If not provided (or *None*) there is no minimum value.
        max (numbers.Number, optional): The maximum value allowed for the
            Property. If not provided (or *None*) there is no maximum value.

    Note:
        This is a base class for concrete number types such as
        :class:`IntProperty` and :class:`FloatProperty` providing common
        functionality for type checking and range validation.

    """
    _value_type_abc = numbers.Number
    _value_type_concrete = None

    min: NumberOrNone
    """If set, the minimum value allowed for the Property. This can be overridden
    per instance using the :meth:`set_min` and :meth:`set_range` methods.
    """

    max: NumberOrNone
    """If set, the maximum value allowed for the Property. This can be overridden
    per instance using the :meth:`set_min` and :meth:`set_range` methods.
    """

    def __init__(self, default=0, allownone=False, **kwargs):
        super().__init__(default, allownone)
        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        self.__range_storage = {}

    def _on_weakref_fin(self, obj_id):
        super()._on_weakref_fin(obj_id)
        if obj_id in self.__range_storage:
            del self.__range_storage[obj_id]

    def get_range(self, obj) -> Tuple[NumberOrNone, NumberOrNone]:
        """Get the effective :attr:`min` and :attr:`max` values for a specific
        *obj* instance
        """
        obj_id = id(obj)
        r = self.__range_storage.get(obj_id)
        if r is not None:
            return r
        return (self.min, self.max)

    def set_range(self, obj, vmin: NumberOrNone, vmax: NumberOrNone):
        """Set the value range for a specific *obj* instance. This overrides the
        :attr:`min` and :attr:`max` value defined in the class definition
        """
        obj_id = id(obj)
        self.__range_storage[obj_id] = (vmin, vmax)

    def set_min(self, obj, vmin: NumberOrNone):
        """Set the minimum value for a specific *obj* instance. This overrides
        the :attr:`min` value defined in the class definition
        """
        obj_id = id(obj)
        r = self.__range_storage.get(obj_id)
        if r is not None:
            _, vmax = r
        else:
            vmax = self.max
        self.__range_storage[obj_id] = (vmin, vmax)

    def set_max(self, obj, vmax: NumberOrNone):
        """Set the minimum value for a specific *obj* instance. This overrides
        the :attr:`min` value defined in the class definition
        """
        obj_id = id(obj)
        r = self.__range_storage.get(obj_id)
        if r is not None:
            vmin, _ = r
        else:
            vmin = self.min
        self.__range_storage[obj_id] = (vmin, vmax)

    def _validate_value(self, obj, value):
        if isinstance(value, bool):
            raise InvalidTypeError(self, value)
        value = self._coerce_value(obj, value)
        vmin, vmax = self.get_range(obj)
        if vmin is not None and value < vmin:
            raise OutOfRangeError(self, value, obj)
        elif vmax is not None and value > vmax:
            raise OutOfRangeError(self, value, obj)
        return value

    def _coerce_value(self, obj, value):
        t_abc, t_concrete = self._value_type_abc, self._value_type_concrete
        if t_abc is not None and not isinstance(value, t_abc):
            raise InvalidTypeError(self, value)
        if t_concrete is not None:
            if isinstance(value, t_concrete):
                return value
            try:
                value = t_concrete(value)
            except (ValueError, TypeError):
                raise InvalidTypeError(self, value)
        return value

class IntProperty(NumericProperty):
    """Property for :class:`int` types
    """
    _value_type_abc = numbers.Integral
    _value_type_concrete = int

class FloatProperty(NumericProperty):
    """Property for :class:`float` types
    """
    _value_type_abc = numbers.Real
    _value_type_concrete = float

class ComplexProperty(NumericProperty):
    """Property for :class:`complex` types
    """
    _value_type_abc = numbers.Complex
    _value_type_concrete = complex

class FractionProperty(NumericProperty):
    """Property for :class:`fraction.Fraction` types
    """
    _value_type_abc = numbers.Rational
    _value_type_concrete = Fraction

class ListProperty(Property):
    """Property with a :class:`list` type value

    Args:
        default (Optional): If supplied, this will be the default value of the
            Property for all instances of the class. Otherwise :obj:`None`
        copy_on_change (bool, optional): If :obj:`True`, the list will be copied
            when contents are modified. This can be useful for observing the
            original state of the list from within callbacks. The copied
            (original) state will be available from the keyword argument 'old'.
            The default is :obj:`False` (for performance and memory reasons).

    Changes to the contents of the list are able to be observed through
    :class:`ObservableList`.
    """
    def __init__(self, default=None, copy_on_change=False):
        if default is None:
            default = []
        self.copy_on_change = copy_on_change
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
    """Property with a :class:`dict` type value

    Args:
        default (Optional): If supplied, this will be the default value of the
            Property for all instances of the class. Otherwise :obj:`None`
        copy_on_change (bool, optional): If :obj:`True`, the dict will be copied
            when contents are modified. This can be useful for observing the
            original state of the dict from within callbacks. The copied
            (original) state will be available from the keyword argument 'old'.
            The default is :obj:`False` (for performance and memory reasons).

    Changes to the contents of the dict are able to be observed through
    :class:`ObservableDict`.
    """
    def __init__(self, default=None, copy_on_change=False):
        if default is None:
            default = {}
        self.copy_on_change = copy_on_change
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
    """Mixin used by :class:`ObservableList` and :class:`ObservableDict`
    to emit changes and build other observables

    When an item is added to an observable container (a subclass of Observable)
    it is type-checked and, if possible replaced by an observable version of it.

    In other words, if a dict is added to a :class:`ObservableDict`, it is
    copied and replaced by another :class:`ObservableDict`. This allows nested
    containers to be observed and their changes to be tracked.
    """
    def _build_observable(self, item):
        if isinstance(item, list):
            item = ObservableList(item, parent=self)
        elif isinstance(item, dict):
            item = ObservableDict(item, parent=self)
        return item
    def _get_copy_or_none(self):
        p = self.parent_observable
        if p is not None:
            return p._get_copy_or_none()
        if not self.copy_on_change:
            return None
        return self._deepcopy()
    def _deepcopy(self):
        o = self.copy()
        if isinstance(self, list):
            item_iter = enumerate(self)
        elif isinstance(self, dict):
            item_iter = self.items()
        for key, item in item_iter:
            if isinstance(item, Observable):
                o[key] = item._deepcopy()
        return o
    def _emit_change(self, **kwargs):
        if not self._init_complete:
            return
        old = kwargs.pop('old')
        p = self.parent_observable
        if p is not None:
            p._emit_change(old=old)
            return
        self.property._on_change(self.obj, old, self, **kwargs)

class ObservableList(list, Observable):
    """A :class:`list` subclass that tracks changes to its contents

    Note:
        This class is for internal use and not intended to be used directly
    """
    def __init__(self, initlist=None, **kwargs):
        self._init_complete = False
        super(ObservableList, self).__init__()
        self.property = kwargs.get('property')
        self.obj = kwargs.get('obj')
        self.parent_observable = kwargs.get('parent')
        if self.property is not None:
            self.copy_on_change = self.property.copy_on_change
        else:
            self.copy_on_change = False
        if initlist is not None:
            self.extend(initlist)
        self._init_complete = True
    def __setitem__(self, key, item):
        old = self._get_copy_or_none()
        item = self._build_observable(item)
        super(ObservableList, self).__setitem__(key, item)
        self._emit_change(keys=[key], old=old)
    def __delitem__(self, key):
        old = self._get_copy_or_none()
        super(ObservableList, self).__delitem__(key)
        self._emit_change(old=old)
    def clear(self):
        old = self._get_copy_or_none()
        super(ObservableList, self).clear()
        self._emit_change(old=old)
    def __iadd__(self, other):
        other = self._build_observable(other)
        self.extend(other)
        return self
    def append(self, item):
        old = self._get_copy_or_none()
        item = self._build_observable(item)
        super(ObservableList, self).append(item)
        self._emit_change(old=old)
    def extend(self, other):
        old = self._get_copy_or_none()
        init = self._init_complete
        self._init_complete = False
        for item in other:
            self.append(item)
        if init:
            self._init_complete = True
        self._emit_change(old=old)
    def remove(self, *args):
        old = self._get_copy_or_none()
        super(ObservableList, self).remove(*args)
        self._emit_change(old=old)

class ObservableDict(dict, Observable):
    """A :class:`dict` subclass that tracks changes to its contents

    Note:
        This class is for internal use and not intended to be used directly
    """
    def __init__(self, initdict=None, **kwargs):
        self._init_complete = False
        super(ObservableDict, self).__init__()
        self.property = kwargs.get('property')
        self.obj = kwargs.get('obj')
        self.parent_observable = kwargs.get('parent')
        if self.property is not None:
            self.copy_on_change = self.property.copy_on_change
        else:
            self.copy_on_change = False
        if initdict is not None:
            self.update(initdict)
        self._init_complete = True
    def __setitem__(self, key, item):
        old = self._get_copy_or_none()
        item = self._build_observable(item)
        super(ObservableDict, self).__setitem__(key, item)
        self._emit_change(keys=[key], old=old)
    def __delitem__(self, key):
        old = self._get_copy_or_none()
        super(ObservableDict, self).__delitem__(key)
        self._emit_change(old=old)
    def update(self, other):
        old = self._get_copy_or_none()
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
        self._emit_change(keys=list(keys), old=old)
    def clear(self):
        old = self._get_copy_or_none()
        super(ObservableDict, self).clear()
        self._emit_change(old=old)
    def pop(self, *args):
        old = self._get_copy_or_none()
        super(ObservableDict, self).pop(*args)
        self._emit_change(old=old)
    def setdefault(self, *args):
        old = self._get_copy_or_none()
        super(ObservableDict, self).setdefault(*args)
        self._emit_change(old=old)
