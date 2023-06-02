import weakref
from weakref import ref, _remove_dead_weakref
from _weakref import ref
import types
import asyncio

def get_method_vars(m):
    f = m.__func__
    obj = m.__self__
    return f, obj

def isfunction(m):
    return isinstance(m, types.FunctionType)

def iscoroutinefunction(obj):
    return asyncio.iscoroutinefunction(obj)

class WeakMethodContainer(weakref.WeakValueDictionary):
    """Container to store weak references to callbacks

    Instance methods are stored using the underlying :term:`function` object
    and the instance id (using :func:`id(obj) <id>`) as the key (a two-tuple)
    and the object itself as the value. This ensures proper weak referencing.

    Functions are stored using the string "function" and the id of the function
    as the key (a two-tuple).
    """
    def add_method(self, m, **kwargs):
        """Add an instance method or function

        Args:
            m: The instance method or function to store
        """
        if isfunction(m):
            self['function', id(m)] = m
        else:
            f, obj = get_method_vars(m)
            wrkey = (f, id(obj))
            self[wrkey] = obj
    def del_method(self, m):
        """Remove an instance method or function if it exists

        Args:
            m: The instance method or function to remove
        """
        if isfunction(m):
            wrkey = ('function', id(m))
        else:
            f, obj = get_method_vars(m)
            wrkey = (f, id(obj))
        if wrkey in self:
            del self[wrkey]
    def del_instance(self, obj):
        """Remove any stored instance methods that belong to an object

        Args:
            obj: The instance object to remove
        """
        to_remove = set()
        for wrkey, _obj in self.iter_instances():
            if obj is _obj:
                to_remove.add(wrkey)
        for wrkey in to_remove:
            del self[wrkey]
    def iter_instances(self):
        """Iterate over the stored objects

        Yields:
            wrkey: The two-tuple key used to store the object
            obj: The instance or function object
        """
        for wrkey in set(self.keys()):
            obj = self.get(wrkey)
            if obj is None:
                continue
            yield wrkey, obj
    def iter_methods(self):
        """Iterate over stored functions and instance methods

        Yields:
            Instance methods or function objects
        """
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
    """A WeakValueDictionary providing a callback for deletion

    Keyword Arguments:
        del_callback: A callback function that will be called when an item is
            either deleted or dereferenced. It will be called with the key as
            the only argument.
    """
    def __init__(self, **kwargs):
        self.del_callback = kwargs.get('del_callback')
        weakref.WeakValueDictionary.__init__(self)
        def remove(wr, selfref=ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(wr.key)
                else:
                    # Atomic removal is necessary since this function
                    # can be called asynchronously by the GC
                    _remove_dead_weakref(self.data, wr.key)
                    self._data_del_callback(wr.key)
        self._remove = remove
        self.data = InformativeDict()
        self.data.del_callback = self._data_del_callback
    def _data_del_callback(self, key):
        self.del_callback(key)

class EmissionHoldLock:
    """Context manager used for :meth:`pydispatch.dispatch.Dispatcher.emission_lock`

    Supports use as a :term:`context manager` used in :keyword:`with` statements
    and an :term:`asynchronous context manager` when used in
    :keyword:`async with` statements.

    Args:
        event_instance: The :class:`~pydispatch.dispatch.Event` instance
            associated with the lock

    Attributes:
        event_instance: The :class:`~pydispatch.dispatch.Event` instance
            associated with the lock
        last_event: The positional and keyword arguments from the event's last
            emission as a two-tuple. If no events were triggered while the lock
            was held, :obj:`None`.
        held (bool): The internal state of the lock
    """
    def __init__(self, event_instance):
        self.event_instance = event_instance
        self.last_event = None
        self.held = False
    @property
    def aio_locks(self):
        d = getattr(self, '_aio_locks', None)
        if d is None:
            d = self._aio_locks = {}
        return d

    def acquire(self):
        if self.held:
            return
        self.held = True
        self.last_event = None
    def release(self):
        if not self.held:
            return
        if self.last_event is not None:
            args, kwargs = self.last_event
            self.last_event = None
            self.held = False
            self.event_instance(*args, **kwargs)

    async def acquire_async(self):
        self.acquire()
        lock = await self._build_aio_lock()
        if not lock.locked():
            await lock.acquire()
    async def release_async(self):
        lock = await self._build_aio_lock()
        if lock.locked:
            lock.release()
        self.release()

    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, *args):
        self.release()

    async def __aenter__(self):
        await self.acquire_async()
        return self
    async def __aexit__(self, *args):
        await self.release_async()

    async def _build_aio_lock(self):
        loop = asyncio.get_event_loop()
        key = id(loop)
        lock = self.aio_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self.aio_locks[key] = lock
        return lock
