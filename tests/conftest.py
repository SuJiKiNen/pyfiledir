import os
import sys
from datetime import timedelta

import pytest
from hypothesis import Verbosity, settings

from pyfiledir.py_core import DEFAULT_PYFILEDIR_ENVS

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))


def setup_hypothesis():

    settings.register_profile(
        "ci",
        max_examples=1000,
        deadline=timedelta(seconds=5),
    )
    settings.register_profile(
        "default",
        max_examples=10,
        verbosity=Verbosity.verbose,
        deadline=timedelta(seconds=2),
    )
    settings.load_profile(os.getenv('HYPOTHESIS_PROFILE', 'default'))


setup_hypothesis()


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
