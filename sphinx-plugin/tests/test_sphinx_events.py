import json
import pytest

from conftest import PYDISPATCH_RTD, reset_intersphinx


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
