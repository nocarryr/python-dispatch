import os
import sys

sys.path.insert(0, os.path.abspath('.'))

extensions = [
    'sphinx.ext.autodoc',
    'pydispatch_sphinx',
    'sphinxcontrib.restbuilder',
]

source_suffix = '.rst'
exclude_patterns = ['_build']

autodoc_member_order = 'bysource'
