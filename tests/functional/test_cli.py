import pytest

from pyfiledir.__version__ import __version__
from pyfiledir.py_cli import (
    _HUMAN_READBLE_ENVS_HEADER,
    _help_action,
    _version_action,
    _where_action,
)
from pyfiledir.py_env import PYFILEDIR_ENVS


@pytest.mark.parametrize(
    "arg",
    [
        *_version_action.option_strings,
    ],
)
def test_version(script_runner, arg):
    ret = script_runner.run("pyfiledir", arg)
    assert ret.success
    assert __version__ in ret.stdout
    for name in ["python", "pyfiledir", "unihan"]:
        assert name in ret.stdout.lower()
    assert ret.stderr == ""


@pytest.mark.parametrize(
    "arg",
    [
        "",
        *_help_action.option_strings,
    ],
)
def test_help(script_runner, arg):
    ret = script_runner.run("pyfiledir", arg)
    assert ret.success
    assert ret.stderr == ""


@pytest.mark.parametrize(
    "args,special_expected_strs",
    [
        (("-e",), _HUMAN_READBLE_ENVS_HEADER),
        (("-e", "bash"), ""),
    ],
)
def test_print_envs(script_runner, args, special_expected_strs):
    ret = script_runner.run("pyfiledir", *args)
    assert ret.success
    assert ret.stderr == ""
    for expepted_str in special_expected_strs:
        assert expepted_str in ret.stdout
    for env in PYFILEDIR_ENVS:
        assert env.name in ret.stdout


@pytest.mark.parametrize(
    "arg",
    [
        *_where_action.option_strings,
    ],
)
def test_where(script_runner, arg):
    ret = script_runner.run("pyfiledir", arg)
    assert ret.success
    assert ret.stderr == ""
    assert ret.stdout.strip().endswith("pyfiledir")
