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
    _GLOBAL_DISPATCHER.register_event(*names)
    decorators._post_register_hook(*names)

register_event.__doc__ = Dispatcher.register_event.__doc__

def bind(**kwargs):
    _GLOBAL_DISPATCHER.bind(**kwargs)
bind.__doc__ = Dispatcher.bind.__doc__

def unbind(*args):
    _GLOBAL_DISPATCHER.unbind(*args)
unbind.__doc__ = Dispatcher.unbind.__doc__

def bind_async(loop, **kwargs):
    _GLOBAL_DISPATCHER.bind_async(loop, **kwargs)
bind_async.__doc__ = Dispatcher.bind_async.__doc__

def emit(name, *args, **kwargs):
    return _GLOBAL_DISPATCHER.emit(name, *args, **kwargs)
emit.__doc__ = Dispatcher.emit.__doc__

def get_dispatcher_event(name):
    return _GLOBAL_DISPATCHER.get_dispatcher_event(name)
get_dispatcher_event.__doc__ = Dispatcher.get_dispatcher_event.__doc__
