import pytest

from pyfiledir.__version__ import __version__
from pyfiledir.py_cli import _envs_action, _help_action, _version_action
from pyfiledir.py_core import PYFILEDIR_ENVS


@pytest.mark.parametrize(
    "args", [
        *_version_action.option_strings,
    ],
)
def test_version(script_runner, args):
    ret = script_runner.run('pyfiledir', args)
    assert ret.success
    assert __version__ in ret.stdout
    assert "python" in ret.stdout.lower()
    assert ret.stderr == ''


@pytest.mark.parametrize(
    "args", [
        "",
        *_help_action.option_strings,
    ],
)
def test_help(script_runner, args):
    ret = script_runner.run('pyfiledir', args)
    assert ret.success
    assert ret.stderr == ''


@pytest.mark.parametrize(
    "args", [
        *_envs_action.option_strings,
    ],
)
def test_envs(script_runner, args):
    ret = script_runner.run('pyfiledir', args)
    assert ret.success
    assert ret.stderr == ''
    for env in PYFILEDIR_ENVS:
        assert env.name in ret.stdout
