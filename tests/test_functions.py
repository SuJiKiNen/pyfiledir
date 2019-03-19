import os

import pytest

from src.pyfiledir import all_ascii, rsplit_selection, same_path


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
