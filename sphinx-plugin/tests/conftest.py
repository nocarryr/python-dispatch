import pytest

import sphinx
from sphinx.testing import comparer
from sphinx.testing.path import path

pytest_plugins = 'sphinx.testing.fixtures'

PYDISPATCH_RTD = 'https://python-dispatch.readthedocs.io/en/latest'

EXTENSIONS = [
    'sphinx.ext.autodoc',
    'sphinx_rst_builder',
    'pydispatch_sphinx',
]

INTERSPHINX_MAPPING = {
    'pydispatch': (PYDISPATCH_RTD, f'{PYDISPATCH_RTD}/objects.inv'),
}

collect_ignore = ['docroots']

def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'with_intersphinx(value): mark test to run with sphinx.ext.intersphinx'
    )

@pytest.fixture(params=[True, False])
def with_napoleon(request):
    exts = set(EXTENSIONS)
    if request.param:
        exts.add('sphinx.ext.napoleon')
    return list(exts)

@pytest.fixture
def app_params(request, app_params):
    args, kwargs = app_params
    exts = set(EXTENSIONS)
    marker = request.node.get_closest_marker('with_intersphinx')
    if marker is not None:
        if marker.args and marker.args[0]:
            exts.add('sphinx.ext.intersphinx')
    if exts != set(EXTENSIONS):
        kwargs['confoverrides'] = {'extensions':list(exts)}
    return args, kwargs

def reset_intersphinx(app):
    from sphinx.ext.intersphinx import (
        load_mappings,
        normalize_intersphinx_mapping,
    )
    app.config.intersphinx_mapping = INTERSPHINX_MAPPING.copy()
    app.config.intersphinx_cache_limit = 0
    app.config.intersphinx_disabled_reftypes = []
    assert app.config.intersphinx_mapping == INTERSPHINX_MAPPING.copy()
    normalize_intersphinx_mapping(app, app.config)
    load_mappings(app)

@pytest.fixture
def app(app):
    yield app


@pytest.fixture(scope='session')
def rootdir():
    return path(__file__).parent.abspath() / 'docroots'

def pytest_assertrepr_compare(op, left, right):
    comparer.pytest_assertrepr_compare(op, left, right)
