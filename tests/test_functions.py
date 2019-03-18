import pytest
from src.pyfiledir import isascii, rsplit_selection


@pytest.mark.parametrize("path,excepted", [
    ("/test1", ("/test1", slice(None, None, 1))),
    ("/测试1", ("/测试", slice(1, 2, 1))),
])
def test_rsplit_selection(path, excepted):
    assert rsplit_selection(path) == excepted


@pytest.mark.parametrize("path,excepted", [
    ("/test1", True),
    ("/测试1", False),
])
def test_isascii(path, excepted):
    assert isascii(path) == excepted
