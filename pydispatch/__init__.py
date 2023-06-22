import sys
import warnings
try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

try:
    __version__ = importlib_metadata.version('python-dispatch')
except: # pragma: no cover
    __version__ = 'unknown'

if sys.version_info < (3, 6): # pragma: no cover
    warnings.warn('You are using `python-dispatch` with a deprecated Python version. '
                  'After version 0.1.x, `python-dispatch` will only support Python 3.6 or greater.',
                  UserWarning)

from pydispatch.dispatch import *
from pydispatch.dispatch import _GLOBAL_DISPATCHER
from pydispatch.properties import *
from pydispatch import decorators
from pydispatch.decorators import *


def register_event(*names):
    """Register event (or events) on the :ref:`global-dispatcher`

    .. seealso:: :meth:`.Dispatcher.register_event`
    .. versionadded:: 0.2.2
    """
    _GLOBAL_DISPATCHER.register_event(*names)
    decorators._post_register_hook(*names)

def bind(**kwargs):
    """Subscribe callbacks to events on the :ref:`global-dispatcher`

    .. seealso:: :meth:`.Dispatcher.bind`
    .. versionadded:: 0.2.2
    """
    _GLOBAL_DISPATCHER.bind(**kwargs)

def unbind(*args):
    """Unbind callbacks from events on the :ref:`global-dispatcher`

    .. seealso:: :meth:`.Dispatcher.unbind`
    .. versionadded:: 0.2.2
    """
    _GLOBAL_DISPATCHER.unbind(*args)

def bind_async(loop, **kwargs):
    """Bind async callbacks to events on the :ref:`global-dispatcher`

    .. seealso:: :meth:`.Dispatcher.bind_async`
    .. versionadded:: 0.2.2
    """
    _GLOBAL_DISPATCHER.bind_async(loop, **kwargs)

def emit(name, *args, **kwargs):
    """Dispatch the event with the given *name* on the :ref:`global-dispatcher`

    .. seealso:: :meth:`.Dispatcher.emit`
    .. versionadded:: 0.2.2
    """
    return _GLOBAL_DISPATCHER.emit(name, *args, **kwargs)

def get_dispatcher_event(name):
    """Retrieve the :class:`~.dispatch.Event` object by the given name
    from the :ref:`global-dispatcher`

    .. seealso:: :meth:`.Dispatcher.get_dispatcher_event`
    .. versionadded:: 0.2.2
    """
    return _GLOBAL_DISPATCHER.get_dispatcher_event(name)
