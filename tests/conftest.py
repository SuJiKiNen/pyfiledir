import pytest
from pyfiledir.pyfiledir import DEFAULT_PYFILEDIR_ENVS


@pytest.fixture(scope="session")
def monkeysession(request):
    """
    Monkeypatch for session socpe.
    see https://github.com/pytest-dev/pytest/issues/363
    """
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def set_pyfiledir_default_envs(monkeysession):
    """
    Default environment for running tests.
    """
    for env_name, val in DEFAULT_PYFILEDIR_ENVS.items():
        monkeysession.setenv(env_name, val)
    monkeysession.setenv("PYFILEDIR_ADD_TRAILING_SLASH", "False")
    monkeysession.setenv("PYFILEDIR_COMPLETE_COMMON_PREFIX", "False")


@pytest.fixture(scope="function")
def test_home_dir(fs, monkeypatch):
    """
    Create test home dir.
    """
    home_dir = '/home/test'
    fs.create_dir(home_dir)
    monkeypatch.setenv('HOME', home_dir)
    return home_dir
