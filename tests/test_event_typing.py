import re
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ('fixture', 'expected_lines'),
    [
        ('event_valid', []),
        ('event_invalid', [11, 12, 13, 14, 15, 16, 27, 28]),
    ],
)
def test_generic_event_mypy(tmp_path, fixture, expected_lines):
    source = Path(__file__).parent / 'typing' / f'{fixture}.py.txt'
    target = tmp_path / f'{fixture}.py'
    target.write_text(source.read_text())
    result = subprocess.run(
        [
            sys.executable, '-m', 'mypy', '--no-incremental',
            '--python-version', '3.11', '--show-error-codes', str(target),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    errors = re.findall(r':(\d+): error: .* \[([^\]]+)\]', result.stdout)
    assert result.stderr == ''
    assert result.returncode == (1 if expected_lines else 0), result.stdout
    assert [int(line) for line, _ in errors] == expected_lines, result.stdout
    assert all(code in {'arg-type', 'call-arg'} for _, code in errors), result.stdout
