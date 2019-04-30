import os

import pytest
from src.pyfiledir import (
    all_ascii,
    get_truthy_env,
    rsplit_selection,
    same_path,
)


@pytest.mark.parametrize("path,excepted", [
    ("/test1", ("/test1", slice(None, None, 1))),
    ("/测试1", ("/测试", slice(0, 1, 1))),
])
def test_rsplit_selection(path, excepted):
    assert rsplit_selection(path) == excepted


@pytest.mark.parametrize("path,excepted", [
    ("/test1", True),
    ("/测试1", False),
])
def test_isascii(path, excepted):
    assert all_ascii(path) == excepted


def test_same_path(fs):
    os.environ['HOME'] = '/home/test'
    home_dir = '/home/test'
    assert same_path(home_dir, "~/")


@pytest.mark.parametrize("env_val,excepted", [
    ("1", True),
    ("0", False),
    ("yes", True),
    ("no", False),
    ("true", True),
    ("false", False),
    ("True", True),
    ("False", False),
    ("on", True),
    ("off", False),
])
def test_get_truthy_env(env_val, excepted):
    key = 'PYFILEDIR_ADD_TRAILING_SLASH'
    os.environ[key] = env_val
    assert get_truthy_env(key) == excepted
