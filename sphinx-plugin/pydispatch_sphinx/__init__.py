import typing as tp
import importlib.metadata

__version__ = importlib.metadata.version('python-dispatch-sphinx')

from sphinx.application import Sphinx

from . import directives
from . import documenters

def setup(app: Sphinx) -> tp.Dict[str, tp.Any]:
    app.setup_extension(directives.__name__)
    app.setup_extension(documenters.__name__)
    return {
        'version':__version__,
        'parallel_read_safe':True,
        'parallel_write_safe':True,
    }
