import os
import sys

sys.path.insert(0, os.path.abspath('.'))

extensions = [
    'sphinx.ext.autodoc',
    'pydispatch_sphinx',
    'sphinx_rst_builder',
]

source_suffix = '.rst'

autodoc_member_order = 'bysource'
