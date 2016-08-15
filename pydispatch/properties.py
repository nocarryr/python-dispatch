
class Property(object):
    def __init__(self, default=None):
        self._name = ''
        self.default = default
        self.__storage = {}
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
    def _del_instance(self, obj):
        del self.__storage[id(obj)]
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
    def _on_change(self, obj, old, value):
        obj.emit(self.name, obj, value, old=old, property=self)
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__, self)
    def __str__(self):
        return self.name

class ListProperty(Property):
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

class DictProperty(Property):
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

class Observable(object):
    def _build_observable(self, item):
        if isinstance(item, list):
            item = ObservableList(item, parent=self)
        elif isinstance(item, dict):
            item = ObservableDict(item, parent=self)
        return item
    def _emit_change(self, **kwargs):
        if not self._init_complete:
            return
        if 'value' not in kwargs:
            kwargs['value'] = self
        p = self.parent_observable
        if p is not None:
            p._emit_change(**kwargs)
            return
        self.property._on_change(self.obj, None, kwargs['value'])

class ObservableList(list, Observable):
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
        self._emit_change()
    def __delitem__(self, key):
        super(ObservableList, self).__delitem__(key)
        self._emit_change()
    def __iadd__(self, other):
        other = self._build_observable(other)
        self.extend(other)
        self._emit_change()
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
        self._emit_change()
    def __delitem__(self, key):
        super(ObservableDict, self).__delitem__(key)
        self._emit_change()
    def update(self, other):
        init = self._init_complete
        self._init_complete = False
        for key, val in other.items():
            self[key] = val
        if init:
            self._init_complete = True
        self._emit_change()
    def clear(self):
        super(ObservableDict, self).clear()
        self._emit_change()
    def pop(self, *args):
        super(ObservableDict, self).pop(*args)
        self._emit_change()
    def setdefault(self, *args):
        super(ObservableDict, self).setdefault(*args)
        self._emit_change()
