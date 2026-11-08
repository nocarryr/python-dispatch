import shutil
import subprocess
import sys
from pathlib import Path


def test_html_build_renders_readme_and_markdown(tmp_path):
    root = Path(__file__).resolve().parents[1]
    project = tmp_path / 'project'
    source = project / 'doc' / 'source'
    source.mkdir(parents=True)
    for name in ('conf.py', 'index.rst'):
        shutil.copy(root / 'doc' / 'source' / name, source / name)
    shutil.copy(root / 'README.md', project / 'README.md')

    with (source / 'conf.py').open('a') as config:
        config.write('\nintersphinx_mapping = {}\nhtml_static_path = []\n')
    with (source / 'index.rst').open('a') as index:
        index.write('\n.. toctree::\n\n   markdown-test\n')
    for name in ('overview', 'reference/index', 'sphinx-plugin/index'):
        path = source / f'{name}.rst'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'{name}\n{"=" * len(name)}\n')
    (source / 'markdown-test.md').write_text(
        '# Markdown test\n\nThis is **bold** Markdown.\n'
    )

    output = tmp_path / 'html'
    result = subprocess.run(
        [
            sys.executable, '-m', 'sphinx', '-b', 'html', '-W',
            '--keep-going', str(source), str(output),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    index = (output / 'index.html').read_text()
    assert 'Lightweight event handling for Python' in index
    assert 'I got data:' in index
    assert '<table ' in index
    assert 'href="https://github.com/nocarryr/python-dispatch/blob/master/CONTRIBUTING.md"' in index
    assert 'href="https://github.com/nocarryr/python-dispatch/blob/master/LICENSE.txt"' in index
    assert 'href="https://github.com/nocarryr/python-dispatch"' in index
    assert '<strong>bold</strong>' in (output / 'markdown-test.html').read_text()
