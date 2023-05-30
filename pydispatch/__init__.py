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
from pydispatch.properties import *
