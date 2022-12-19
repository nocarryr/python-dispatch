
from pathlib import Path
from setuptools.config import read_configuration


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SETUP_CFG = PROJECT_ROOT / 'setup.cfg'

def get_expected_version(config_file: Path = SETUP_CFG) -> str:
    conf_dict = read_configuration(str(config_file))
    return conf_dict['metadata']['version']

EXPECTED_VERSION = get_expected_version()


def test_version():
    import pydispatch
    assert pydispatch.__version__ == EXPECTED_VERSION
