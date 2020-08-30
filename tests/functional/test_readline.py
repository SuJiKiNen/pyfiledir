import pytest


@pytest.mark.parametrize(
    "dirs,typed,expected",
    (
        (["test"], "t", "test/"),
        (["测试", "test"], "c", "测试/"),
    ),
)
def test_readline(bash, tmpdir, dirs, typed, expected):
    for d in dirs:
        tmpdir.mkdir(d)
    bash.cd(tmpdir)
    bash.type(typed)
    bash.complete_at_point()
    bash.expect(expected)
