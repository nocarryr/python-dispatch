import asyncio
import threading
from _weakref import ref
from _weakrefset import _IterationGuard

from pydispatch.utils import (
    WeakMethodContainer,
    get_method_vars,
    _remove_dead_weakref,
)

class AioEmissionHoldLock(object):
    """Async context manager mixin for :class:`pydispatch.utils.EmissionHoldLock_`

    Supports use in :keyword:`async with` statements
    """
    @property
    def aio_locks(self):
        d = getattr(self, '_aio_locks', None)
        if d is None:
            d = self._aio_locks = {}
        return d
    async def _build_aio_lock(self):
        loop = asyncio.get_event_loop()
        key = id(loop)
        lock = self.aio_locks.get(key)
        if lock is None:
            lock = asyncio.Lock(loop=loop)
            self.aio_locks[key] = lock
        return lock
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
    async def __aenter__(self):
        await self.acquire_async()
        return self
    async def __aexit__(self, *args):
        await self.release_async()

class AioSimpleLock(object):
    """:class:`asyncio.Lock` alternative backed by a :class:`threading.Lock`

    This is a context manager that supports use in both :keyword:`with` and
    :keyword:`async with` context blocks.

    Attributes:
        lock: Instance of :class:`threading.Lock`

    .. versionadded:: 0.1.0
    """
    __slots__ = ('lock')
    def __init__(self):
        self.lock = threading.Lock()
    def acquire(self, blocking=True, timeout=-1):
        """Acquire the :attr:`lock`

        Args:
            blocking (bool): See :meth:`threading.Lock.acquire`
            timeout (float): See :meth:`threading.Lock.acquire`

        Returns:
            bool: :obj:`True` if the lock was acquired, otherwise :obj:`False`

        """
        result = self.lock.acquire(blocking, timeout)
        return result
    def release(self):
        """Release the :attr:`lock`
        """
        self.lock.release()
    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, *args):
        self.release()
    async def acquire_async(self):
        """Acquire the :attr:`lock` asynchronously

        """
        r = self.acquire(blocking=False)
        while not r:
            await asyncio.sleep(.01)
            r = self.acquire(blocking=False)
    async def __aenter__(self):
        await self.acquire_async()
        return self
    async def __aexit__(self, *args):
        self.release()

class WithAioFutures(object):
    """Async context manager to enable :term:`awaitable` event completion

    While this is enabled (using :keyword:`async with`), the specified events
    will create and return a :class:`~asyncio.Future` object that will block
    until all callbacks from event emission have completed.

    .. versionadded:: 0.1.x

    See Also:
        :ref:`awaitable-callback-completion`

    Args:
        instance: The instance of :class:`~pydispatch.dispatch.Dispatcher`
            to enable
        *event_names(str): Name or names of events to enable :term:`awaitable`
            event completion on

    Attributes:
        instance: The :class:`pydispatch.dispatch.Dispatcher` instance given
            during initialization
        event_names(list): The event names given during initialization
        futures(dict): Stores futures created by Events using event names as keys
    """
    def __init__(self, instance, *event_names):
        self.instance = instance
        self.event_names = event_names
        self.futures = {name:[] for name in event_names}
    async def wait(self, *event_names):
        """Wait for any pending callback coroutines to complete

        Event objects store any futures created during emission to the
        :attr:`futures` attribute. This method will wait for their completion.
        This is mostly useful for tracking callback completion for changes to
        :class:`~pydispatch.properties.Property` objects as there would be no
        return value (compared to the :meth:`pydispatch.dispatch.Dispatcher.emit`
        method used for Events).

        See the example for details

        Args:
            *event_names(str): Names of events to wait for. If empty, all events
                given from :attr:`event_names` will be used.

        Note:
            This is meant to be used **instead** of the returned future from
            :meth:`pydispatch.dispatch.Dispatcher.emit`. Using both methods
            is unnecessary and has not been tested::

                # Not recommended
                await emitter.emit('on_event')
                await with_aio_futures.wait()

        """
        if not len(event_names):
            event_names = self.event_names
        for event_name in event_names:
            futures = self.futures[event_name]
            if len(futures):
                await asyncio.wait(futures)
            futures.clear()
    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        loop_id = id(loop)
        for event_name in self.event_names:
            event = self.instance.get_dispatcher_event(event_name)
            if loop_id not in event._return_aio_futures:
                event._return_aio_futures[loop_id] = set()
            event._return_aio_futures[loop_id].add(self)
        return self
    async def __aexit__(self, *args):
        loop = asyncio.get_event_loop()
        loop_id = id(loop)
        for event_name in self.event_names:
            event = self.instance.get_dispatcher_event(event_name)
            event._return_aio_futures.get(loop_id, set()).discard(self)

class AioEventWaiter(object):
    """Stores necessary information for a single "waiter"

    Used by :class:`AioEventWaiters` to handle :keyword:`awaiting <await>`
    an :class:`~pydispatch.dispatch.Event` on a specific
    :class:`event loop <asyncio.BaseEventLoop>`

    Attributes:
        loop: The :class:`EventLoop <asyncio.BaseEventLoop>` instance
        aio_event: An :class:`asyncio.Event` used to track event emission
        args (list): The positional arguments attached to the event
        kwargs (dict): The keyword arguments attached to the event

    .. versionadded:: 0.1.0
    """
    __slots__ = ('loop', 'aio_event', 'args', 'kwargs', '_complete_event')
    def __init__(self, loop):
        self.loop = loop
        self.aio_event = asyncio.Event(loop=loop)
        self.args = []
        self.kwargs = {}
        self._complete_event = asyncio.Event(loop=loop)
    def trigger(self, *args, **kwargs):
        """Called on event emission and notifies the :meth:`wait` method

        Called by :class:`AioEventWaiters` when the
        :class:`~pydispatch.dispatch.Event` instance is dispatched.

        Positional and keyword arguments are stored as instance attributes for
        use in the :meth:`wait` method and :attr:`aio_event` is set.

        Returns:
            If within the context of :class:`WithAioFutures`, a wrapped
            `asyncio.Future` that will block until the :keyword:`await`
            operation has completed. Otherwise :obj:`None`.

        .. versionchanged:: 0.1.x

            The `asyncio.Future` return value was added
        """
        return_aio_futures = kwargs.get('__return_aio_futures__', False)
        self.args = args
        self.kwargs = kwargs
        fut = None
        if return_aio_futures:
            fut = asyncio.wrap_future(asyncio.run_coroutine_threadsafe(
                self._wait_for_completion(), loop=self.loop,
            ))

        self.aio_event.set()
        return fut
    async def wait(self):
        """Waits for event emission and returns the event parameters

        Returns:
            args (list): Positional arguments attached to the event
            kwargs (dict): Keyword arguments attached to the event

        """
        await self.aio_event.wait()
        return self.args, self.kwargs
    async def _wait_for_completion(self):
        await self._complete_event.wait()
    def _on_await_task_complete(self):
        self._complete_event.set()
    def __await__(self):
        task = asyncio.ensure_future(self.wait())
        task.add_done_callback(self._on_await_task_complete)
        return task.__await__()

class AioEventWaiters(object):
    """Container used to manage :keyword:`await` use with events

    Used by :class:`pydispatch.dispatch.Event` when it is
    :keyword:`awaited <await>`

    Attributes:
        waiters (set): Instances of :class:`AioEventWaiter` currently "awaiting"
            the event
        lock (AioSimpleLock): A sync/async lock to guard modification to the
            :attr:`waiters` container during event emission

    .. versionadded:: 0.1.0
    """
    __slots__ = ('waiters', 'lock')
    def __init__(self):
        self.waiters = set()
        self.lock = AioSimpleLock()
    async def add_waiter(self):
        """Add a :class:`AioEventWaiter` to the :attr:`waiters` container

        The event loop to use for :attr:`AioEventWaiter.loop` is found in the
        current context using :func:`asyncio.get_event_loop`

        Returns:
            waiter: The created :class:`AioEventWaiter` instance

        """
        loop = asyncio.get_event_loop()
        async with self.lock:
            waiter = AioEventWaiter(loop)
            self.waiters.add(waiter)
        return waiter
    async def wait(self):
        """Creates a :class:`waiter <AioEventWaiter>` and "awaits" its result

        This method is used by :class:`pydispatch.dispatch.Event` instances when
        they are "awaited" and is the primary functionality of
        :class:`AioEventWaiters` and :class:`AioEventWaiter`.

        Returns:
            args (list): Positional arguments attached to the event
            kwargs (dict): Keyword arguments attached to the event

        """
        waiter = await self.add_waiter()
        return await waiter
    def __await__(self):
        task = asyncio.ensure_future(self.wait())
        return task.__await__()
    def __call__(self, *args, **kwargs):
        """Triggers any stored :class:`waiters <AioEventWaiter>`

        Calls :meth:`AioEventWaiter.trigger` method on all instances stored in
        :attr:`waiters`. After completion, the :attr:`waiters` are removed.

        Args:
            *args: Positional arguments to pass to :meth:`AioEventWaiter.trigger`
            **kwargs: Keyword arguments to pass to :meth:`AioEventWaiter.trigger`

        Returns:
            If within the context of :class:`WithAioFutures`, a wrapped
            `asyncio.Future` that will block until the :keyword:`await`
            operation has completed. Otherwise :obj:`None`.

        .. versionchanged:: 0.1.x

            The `asyncio.Future` return value was added
        """
        return_aio_futures = kwargs.get('__return_aio_futures__', False)
        tasks = []
        with self.lock:
            for waiter in self.waiters:
                tasks.append(waiter.trigger(*args, **kwargs))
            self.waiters.clear()
        if return_aio_futures:
            if len(tasks):
                return asyncio.gather(*tasks)
            else:
                return asyncio.sleep(0)

class AioWeakMethodContainer(WeakMethodContainer):
    """Storage for coroutine functions as weak references

    .. versionadded:: 0.1.0
    """
    def __init__(self):
        super().__init__()
        def remove(wr, selfref=ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(wr.key)
                else:
                    # Atomic removal is necessary since this function
                    # can be called asynchronously by the GC
                    _remove_dead_weakref(self.data, wr.key)
                    self._on_weakref_fin(wr.key)
        self._remove = remove
        self.event_loop_map = {}
    def add_method(self, loop, callback):
        """Add a coroutine function

        Args:
            loop: The :class:`event loop <asyncio.BaseEventLoop>` instance
                on which to schedule callbacks
            callback: The :term:`coroutine function` to add
        """
        f, obj = get_method_vars(callback)
        wrkey = (f, id(obj))
        self[wrkey] = obj
        self.event_loop_map[wrkey] = loop
    def iter_instances(self):
        """Iterate over the stored objects

        .. seealso:: :meth:`pydispatch.utils.WeakMethodContainer.iter_instances`
        """
        with _IterationGuard(self):
            yield from super().iter_instances()
    def iter_methods(self):
        """Iterate over stored coroutine functions

        Yields:
            Stored :term:`coroutine function` objects

        .. seealso:: :meth:`pydispatch.utils.WeakMethodContainer.iter_instances`
        """
        for wrkey, obj in self.iter_instances():
            f, obj_id = wrkey
            loop = self.event_loop_map[wrkey]
            m = getattr(obj, f.__name__)
            yield loop, m
    def _on_weakref_fin(self, key):
        if key in self.event_loop_map:
            del self.event_loop_map[key]
    def submit_coroutine(self, coro, loop):
        """Schedule and await a coroutine on the specified loop

        The coroutine is wrapped and scheduled using
        :func:`asyncio.run_coroutine_threadsafe`. While the coroutine is
        "awaited", the result is not available as method returns immediately.

        Args:
            coro: The :term:`coroutine` to schedule
            loop: The :class:`event loop <asyncio.BaseEventLoop>` on which to
                schedule the coroutine

        Note:
            This method is used internally by :meth:`__call__` and is not meant
            to be called directly.

        Returns:
            The :class:`concurrent.futures.Future` object created by
            :func:`asyncio.run_coroutine_threadsafe`

        .. versionchanged:: 0.1.x

            The `concurrent.futures.Future` return value was added
        """
        async def _do_call(_coro):
            with _IterationGuard(self):
                await _coro
        return asyncio.run_coroutine_threadsafe(_do_call(coro), loop=loop)
    def __call__(self, *args, **kwargs):
        """Triggers all stored callbacks (coroutines)

        Args:
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks

        Returns:
            If within the context of :class:`WithAioFutures`, a wrapped
            `asyncio.Future` that will block until the :keyword:`await`
            operation has completed. Otherwise :obj:`None`.

        .. versionchanged:: 0.1.x

            The `asyncio.Future` return value was added
        """
        return_aio_futures = kwargs.get('__return_aio_futures__', False)
        tasks = []
        for loop, m in self.iter_methods():
            coro = m(*args, **kwargs)
            fut = self.submit_coroutine(coro, loop)
            tasks.append(asyncio.wrap_future(fut))
        if return_aio_futures:
            if len(tasks):
                return asyncio.gather(*tasks)
            else:
                return asyncio.sleep(0)
    def __delitem__(self, key):
        if key in self.event_loop_map:
            del self.event_loop_map[key]
        return super().__delitem__(key)
