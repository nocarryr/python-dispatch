import pytest

import sphinx
from sphinx.testing import comparer
from sphinx.testing.path import path

pytest_plugins = 'sphinx.testing.fixtures'

collect_ignore = ['docroots']

def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'with_intersphinx(value): mark test to run with sphinx.ext.intersphinx'
    )

@pytest.fixture(scope='session')
def rootdir():
    return path(__file__).parent.abspath() / 'docroots'

def pytest_assertrepr_compare(op, left, right):
    comparer.pytest_assertrepr_compare(op, left, right)
