import sys
import warnings
import pkg_resources

try:
    __version__ = pkg_resources.require('python-dispatch')[0].version
except: # pragma: no cover
    __version__ = 'unknown'

if sys.version_info < (3, 6): # pragma: no cover
    warnings.warn('You are using `python-dispatch` with a deprecated Python version. '
                  'After version 0.1.x, `python-dispatch` will only support Python 3.6 or greater.',
                  UserWarning)

from pydispatch.dispatch import Dispatcher, Event
from pydispatch.properties import *
