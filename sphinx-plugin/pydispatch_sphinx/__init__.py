import typing as tp
from importlib.metadata import version as _get_version

__version__ = _get_version('python-dispatch-sphinx')

from sphinx.application import Sphinx

from . import directives, documenters


def setup(app: Sphinx) -> dict[str, tp.Any]:
    app.setup_extension(directives.__name__)
    app.setup_extension(documenters.__name__)
    return {
        'version':__version__,
        'parallel_read_safe':True,
        'parallel_write_safe':True,
    }
