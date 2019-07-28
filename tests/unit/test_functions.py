import os

import pytest

from pyfiledir.__main__ import main
from pyfiledir.py_core import (
    all_ascii,
    do_py_completion,
    get_py,
    get_truthy_env,
    rsplit_selection,
    same_path,
)


@pytest.mark.parametrize(
    "path,excepted", [
        ("/test1", ("/test1", slice(None, None, 1))),
        ("/测试1", ("/测试", slice(0, 1, 1))),
    ],
)
def test_rsplit_selection(path, excepted):
    assert rsplit_selection(path) == excepted


@pytest.mark.parametrize(
    "path,excepted", [
        ("/test1", True),
        ("/测试1", False),
    ],
)
def test_isascii(path, excepted):
    assert all_ascii(path) == excepted


def test_same_path(fs, test_home_dir):
    assert same_path(test_home_dir, "~/")


@pytest.mark.parametrize(
    "char, excepted",
    ([
        ("a", "a"),
        ("1", "1"),
        ("好", "h"),
        ("あ", "あ"),  # b'\xa4\xa2'
    ]),
)
def test_get_py(char, excepted):
    assert excepted in get_py(char)


@pytest.mark.parametrize(
    "env_val,excepted", [
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
    ],
)
def test_get_truthy_env(env_val, excepted):
    key = 'PYFILEDIR_ADD_TRAILING_SLASH'
    os.environ[key] = env_val
    assert get_truthy_env(key) == excepted


def test_do_py_completion_on_not_exists_path():
    with pytest.raises(SystemExit):
        do_py_completion("/not_exists_path/file")


@pytest.mark.parametrize(
    "files,typed", [
        (["abc"], "abc"),
        (["arise", "are"], "a"),
    ],
)
def test_main_function(fs, test_home_dir, files, typed, capsys):
    os.chdir(test_home_dir)
    [fs.create_file(f) for f in files]
    main(["pyfiledir", typed])
    out, err = capsys.readouterr()
    assert any(f in out for f in files)
