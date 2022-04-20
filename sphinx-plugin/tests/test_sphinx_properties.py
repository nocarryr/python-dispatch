import pytest

PYDISPATCH_RTD = 'https://python-dispatch.readthedocs.io/en/latest'

EXTENSIONS = [
    'sphinx.ext.autodoc',
    'sphinx_rst_builder',
    'pydispatch_sphinx',
]

INTERSPHINX_MAPPING = {
    'pydispatch': (PYDISPATCH_RTD, f'{PYDISPATCH_RTD}/objects.inv'),
}

@pytest.fixture(params=[True, False])
def with_napoleon(request):
    exts = set(EXTENSIONS)
    if request.param:
        exts.add('sphinx.ext.napoleon')
    return list(exts)

@pytest.fixture
def app_params(request, app_params, with_napoleon):
    args, kwargs = app_params
    exts = set(with_napoleon)
    marker = request.node.get_closest_marker('with_intersphinx')
    if marker is not None:
        if marker.args and marker.args[0]:
            exts.add('sphinx.ext.intersphinx')
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


@pytest.mark.sphinx('rst', testroot='properties')
def test_properties_rst(app, rootdir):
    app.builder.build_all()

    content = (app.outdir / 'index.rst').read_text()

    expected = (rootdir / 'test-properties' / 'output_rst.txt').read_text()

    assert content == expected

@pytest.mark.sphinx('html', testroot='properties')
def test_properties_html(app, rootdir):
    app.builder.build_all()

    content = (app.outdir / 'index.html').read_text()



@pytest.mark.with_intersphinx(True)
@pytest.mark.sphinx('rst', testroot='properties')
def test_properties_rst_intersphinx(app, rootdir):
    reset_intersphinx(app)

    app.builder.build_all()

    content = (app.outdir / 'index.rst').read_text()

    expected = (rootdir / 'test-properties' / 'output_rst_intersphinx.txt').read_text()
    expected = expected.format(url=PYDISPATCH_RTD.rstrip('/'))

    assert content == expected

@pytest.mark.with_intersphinx(True)
@pytest.mark.sphinx('linkcheck', testroot='properties')
def test_properties_linkcheck(app, rootdir):
    reset_intersphinx(app)

    app.builder.build_all()

    output_txt = (app.outdir / 'output.txt').read_text()
    assert not len(output_txt)
