import json
import re
from html import unescape

import pytest

from conftest import PYDISPATCH_RTD, reset_intersphinx


@pytest.mark.sphinx('rst', testroot='properties')
def test_properties_rst(app, rootdir):
    app.builder.build_all()

    content = (app.outdir / 'index.rst').read_text()

    expected = (rootdir / 'test-properties' / 'output_rst.txt').read_text()

    assert content == expected


@pytest.mark.with_intersphinx(True)
@pytest.mark.sphinx('html', testroot='properties')
def test_properties_html(app, rootdir):
    reset_intersphinx(app)
    app.builder.build_all()

    content = (app.outdir / 'index.html').read_text()
    assert 'id="the_module.TheClass.foo"' in content
    assert 'id="the_module.TheOtherClass.bar"' in content
    assert 'href="#the_module.TheClass.foo"' in content
    for name in ('Property', 'DictProperty', 'ListProperty'):
        assert f'href="{PYDISPATCH_RTD}/reference/properties.html#pydispatch.properties.{name}"' in content
    assert 'Docstring for foo' in content
    assert 'Docstring for bar' in content
    assert 'Docstring for baz' in content
    signature = re.search(
        r'<dt[^>]*id="the_module.TheOtherClass.foo"[^>]*>(.*?)</dt>',
        content, re.DOTALL,
    )
    assert signature is not None
    text = unescape(re.sub(r'<[^>]+>', '', signature.group(1)))
    assert 'Property' in text
    assert 'foo' in text
    assert 'int' in text
    assert '= 0' in text


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

    output_json = (app.outdir / 'output.json').read_text()
    json_lines = [json.loads(line) for line in output_json.splitlines()]
    assert len(json_lines)
    status = [line['status'] for line in json_lines]
    assert set(status) == {'working'}

    output_txt = (app.outdir / 'output.txt').read_text()
    assert not len(output_txt)
