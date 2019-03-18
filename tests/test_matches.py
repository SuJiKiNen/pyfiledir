import os

import pytest
from src.pyfiledir import SEP, do_py_completion, unicode_sort


def test_completion_not_expand_tilde(fs):
    os.environ['HOME'] = '/home/test'
    home_dir = '/home/test'
    fs.create_dir(home_dir)

    target_dir = "~/测试目录"
    target_dir_expanded = os.path.expanduser(target_dir)
    target_file = os.path.join(target_dir_expanded, "file")
    fs.create_dir(target_dir_expanded)
    fs.create_file(target_file)
    assert do_py_completion("~/c") == target_dir


def test_completion_keep_leading_dot_slash(fs):
    os.environ['HOME'] = '/home/test'
    home_dir = '/home/test'
    fs.create_dir(os.path.join(home_dir, "subdir1"))
    fs.create_dir(os.path.join(home_dir, "subdir2"))
    os.chdir(home_dir)
    assert do_py_completion("./") == SEP.join(["./subdir1", "./subdir2"])


def test_complete_implicit_current_directory(fs):
    os.environ['HOME'] = '/home/test'
    home_dir = '/home/test'
    fs.create_dir(home_dir)
    os.chdir("/home")
    assert do_py_completion("t") == SEP.join(["test"])


def test_empty_basename_match_all_files_in_directory(fs):
    home_dir = '/home/test'
    os.environ['HOME'] = home_dir
    fs.create_dir(home_dir)
    fs.create_dir(os.path.join(home_dir, "subdir1"))
    fs.create_dir(os.path.join(home_dir, "subdir2"))
    assert do_py_completion("~/") == SEP.join(["~/subdir1", "~/subdir2"])


@pytest.mark.parametrize("dirs,typed,output", [
    (
        ["/1024", "/1025"],
        "/1",
        ["/1024", "/1025"],
    ),
    (
        ["/个人图片", "/个人信息"],
        "/个" + "1",
        [unicode_sort(["/个人图片", "/个人信息"])[1]],
    ),
])
def test_number_selection(dirs, typed, output, fs):
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(output)
