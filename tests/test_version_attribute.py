
import sys
from pathlib import Path
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SETUP_CFG = PROJECT_ROOT / 'pyproject.toml'

def get_expected_version(config_file: Path = SETUP_CFG) -> str:
    with config_file.open('rb') as f:
        config_dict = tomllib.load(f)
    return config_dict['project']['version']


EXPECTED_VERSION = get_expected_version()


def test_version():
    import pydispatch
    assert pydispatch.__version__ == EXPECTED_VERSION
