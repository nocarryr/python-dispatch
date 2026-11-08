import sys
from pathlib import Path

import pytest

pytest_plugins = 'sphinx.testing.fixtures'

PYDISPATCH_RTD = 'https://python-dispatch.readthedocs.io/en/latest'

EXTENSIONS = [
    'sphinx.ext.autodoc',
    'sphinxcontrib.restbuilder',
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
    return request.param

@pytest.fixture
def app_params(request, app_params, with_napoleon):
    args, kwargs = app_params
    # Sphinx autodoc updates class annotations during a build.
    for name in ('events_module', 'the_module'):
        sys.modules.pop(name, None)
    exts = list(EXTENSIONS)
    if with_napoleon:
        exts.append('sphinx.ext.napoleon')
    marker = request.node.get_closest_marker('with_intersphinx')
    if marker is not None and marker.args and marker.args[0]:
        exts.append('sphinx.ext.intersphinx')
    kwargs.setdefault('confoverrides', {})['extensions'] = exts
    return args, kwargs

def reset_intersphinx(app):
    from sphinx.ext.intersphinx import (
        load_mappings,
        validate_intersphinx_mapping,
    )
    app.config.intersphinx_mapping = INTERSPHINX_MAPPING.copy()
    app.config.intersphinx_cache_limit = 0
    app.config.intersphinx_disabled_reftypes = []
    assert app.config.intersphinx_mapping == INTERSPHINX_MAPPING.copy()
    validate_intersphinx_mapping(app, app.config)
    load_mappings(app)

@pytest.fixture
def app(app):
    yield app


@pytest.fixture(scope='session')
def rootdir():
    return Path(__file__).resolve().parent / 'docroots'
