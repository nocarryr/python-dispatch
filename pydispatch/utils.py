import sys
import weakref
import types

PY2 = sys.version_info.major == 2
if not PY2:
    basestring = str

def get_method_vars(m):
    if PY2:
        f = m.im_func
        obj = m.im_self
    else:
        f = m.__func__
        obj = m.__self__
    return f, obj

class WeakMethodContainer(weakref.WeakValueDictionary):
    def keys(self):
        if PY2:
            return self.iterkeys()
        return super(WeakMethodContainer, self).keys()
    def add_method(self, m):
        if isinstance(m, types.FunctionType):
            self['function', id(m)] = m
        else:
            f, obj = get_method_vars(m)
            wrkey = (f, id(obj))
            self[wrkey] = obj
    def del_method(self, m):
        if isinstance(m, types.FunctionType):
            wrkey = ('function', id(m))
        else:
            f, obj = get_method_vars(m)
            wrkey = (f, id(obj))
        if wrkey in self:
            del self[wrkey]
    def del_instance(self, obj):
        to_remove = set()
        for wrkey, _obj in self.iter_instances():
            if obj is _obj:
                to_remove.add(wrkey)
        for wrkey in to_remove:
            del self[wrkey]
    def iter_instances(self):
        for wrkey in set(self.keys()):
            obj = self.get(wrkey)
            if obj is None:
                continue
            yield wrkey, obj
    def iter_methods(self):
        for wrkey, obj in self.iter_instances():
            f, obj_id = wrkey
            if f == 'function':
                yield self[wrkey]
            else:
                yield getattr(obj, f.__name__)

class InformativeDict(dict):
    def __delitem__(self, key):
        super(InformativeDict, self).__delitem__(key)
        self.del_callback(key)

class InformativeWVDict(weakref.WeakValueDictionary):
    def __init__(self, **kwargs):
        self.del_callback = kwargs.get('del_callback')
        weakref.WeakValueDictionary.__init__(self)
        self.data = InformativeDict()
        self.data.del_callback = self._data_del_callback
    def _data_del_callback(self, key):
        self.del_callback(key)
