import json
import re
from html import unescape

import pytest
from conftest import PYDISPATCH_RTD, reset_intersphinx


def test_generic_event_documenter_recognizes_dispatcher_subclasses():
    from types import SimpleNamespace

    from pydispatch_sphinx.documenters import DispatcherEventAttributeDocumenter
    from sphinx.ext.autodoc import INSTANCEATTR

    from pydispatch import Dispatcher, Event

    class Sender(Dispatcher):
        on_foo: Event[[int]]

    class Other:
        on_foo: Event[[int]]

    documenter = DispatcherEventAttributeDocumenter
    assert documenter.can_document_member(
        INSTANCEATTR, 'on_foo', True, SimpleNamespace(object=Sender),
    )
    assert not documenter.can_document_member(
        INSTANCEATTR, 'on_foo', True, SimpleNamespace(object=Other),
    )


@pytest.mark.sphinx('rst', testroot='events')
def test_events_rst(app, rootdir):
    app.builder.build_all()

    content = (app.outdir / 'index.rst').read_text()

    expected = (rootdir / 'test-events' / 'output_rst.txt').read_text()

    assert content == expected


@pytest.mark.with_intersphinx(True)
@pytest.mark.sphinx('html', testroot='events')
def test_events_html(app, rootdir):
    reset_intersphinx(app)

    app.builder.build_all()

    content = (app.outdir / 'index.html').read_text()
    assert 'id="events_module.TheClass.on_foo"' in content
    assert 'id="events_module.TheClass.on_baz"' in content
    assert 'id="events_module.TheOverridingSubClass.on_foo"' in content
    assert 'href="#events_module.TheClass.on_foo"' in content
    assert f'href="{PYDISPATCH_RTD}/reference/dispatch.html#pydispatch.dispatch.Event"' in content
    assert 'Documentation for on_baz event' in content
    assert '<dl class="py event">' in content
    assert '<dl class="py attribute">' in content
    signature = re.search(
        r'<dt[^>]*id="events_module.TheClass.on_baz"[^>]*>(.*?)</dt>',
        content, re.DOTALL,
    )
    assert signature is not None
    text = unescape(re.sub(r'<[^>]+>', '', signature.group(1)))
    assert 'Event' in text
    assert 'on_baz' in text
    assert 'name: str' in text
    assert 'value: int' in text
    non_dispatcher = content.split('id="events_module.NonDispatcherClass"', 1)[1]
    assert '<dl class="py event">' not in non_dispatcher


@pytest.mark.with_intersphinx(True)
@pytest.mark.sphinx('rst', testroot='events')
def test_events_intersphinx(app, rootdir):
    reset_intersphinx(app)

    app.builder.build_all()

    content = (app.outdir / 'index.rst').read_text()

    expected = (rootdir / 'test-events' / 'output_rst_intersphinx.txt').read_text()
    expected = expected.format(url=PYDISPATCH_RTD.rstrip('/'))

    assert content == expected

@pytest.mark.with_intersphinx(True)
@pytest.mark.sphinx('linkcheck', testroot='events')
def test_events_linkcheck(app, rootdir):
    reset_intersphinx(app)

    app.builder.build_all()

    output_json = (app.outdir / 'output.json').read_text()
    json_lines = [json.loads(line) for line in output_json.splitlines()]
    assert len(json_lines)
    status = [line['status'] for line in json_lines]
    assert set(status) == {'working'}

    output_txt = (app.outdir / 'output.txt').read_text()
    assert not len(output_txt)
