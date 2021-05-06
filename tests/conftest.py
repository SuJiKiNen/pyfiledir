import os
import sys
from datetime import timedelta

import pytest
from hypothesis import Verbosity, settings

from pyfiledir.py_env import PYFILEDIR_ENVS

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))


def setup_hypothesis():

    settings.register_profile(
        "ci",
        max_examples=100,
        deadline=timedelta(seconds=5),
    )
    settings.register_profile(
        "default",
        max_examples=10,
        verbosity=Verbosity.verbose,
        deadline=timedelta(seconds=2),
    )
    settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))


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
    for env_name, val in PYFILEDIR_ENVS.items():
        monkeysession.setenv(env_name, val)
    monkeysession.setenv("PYFILEDIR_ADD_TRAILING_SLASH", "False")
    monkeysession.setenv("PYFILEDIR_COMPLETE_COMMON_PREFIX", "False")


@pytest.fixture(scope="function")
def test_home_dir(fs, monkeypatch):
    """
    Create test home dir.
    """
    home_dir = "/home/test"
    fs.create_dir(home_dir)
    monkeypatch.setenv("HOME", home_dir)
    # https://docs.python.org/3/whatsnew/3.8.html
    # expanduser() on Windows now prefers the USERPROFILE environment variable
    # and does not use HOME, which is not normally set for regular user accounts.
    # (Contributed by Anthony Sottile in bpo-36264.)
    monkeypatch.setenv("USERPROFILE", home_dir)
    return home_dir


def pytest_addoption(parser):
    parser.addoption(
        "--pyfiledir-debug",
        action="store_true",
        default=False,
        help="enable pyfiledir test debug,verbose output!",
    )


@pytest.fixture
def pyfiledir_debug(request):
    return request.config.getoption("--pyfiledir-debug")
