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


@pytest.mark.parametrize("dirs,files,typed,excepted", [
    (["subdir1", "subdir2"], ["file1", "file2"], "~/", unicode_sort(["subdir1", "subdir2", "file1", "file2"])),
    (["subdir1", "subdir2"], [], "~/", unicode_sort(["subdir1", "subdir2"])),
    ([], ["file1", "file2"], "~/", unicode_sort(["file1", "file2"])),
])
def test_empty_basename_match_all_files_or_dirs_in_directory(dirs, files, typed, excepted, fs):
    home_dir = '/home/test'
    os.environ['HOME'] = home_dir
    for d in dirs:
        fs.create_dir(os.path.join(home_dir, d))
    for f in files:
        fs.create_file(os.path.join(home_dir, f))
    excepted = [os.path.join("~/", f) for f in excepted]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize("dirs,typed,excepted", [
    (
        ["/1024", "/1025"],
        "/1",
        ["/1024", "/1025"],
    ),
    (
        ["/个人图片", "/个人信息"],
        "/个" + "1",
        [unicode_sort(["/个人图片", "/个人信息"])[0]],
    ),
])
def test_number_selection(dirs, typed, excepted, fs):
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize("dirs,typed,excepted", [
    (
        ["第{}组".format(i) for i in range(1, 9)],
        "d1",
        ["第1组"],
    ),
    (
        ["第{}组".format(i) for i in range(1, 9)],
        "第1",
        ["第1组"],
    ),
    (
        ["第{}组".format(i) for i in range(1, 20)],
        "第11",
        ["第10组"],
    ),
])
def test_number_selection_start_from_one(dirs, typed, excepted, fs):
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


def test_solo_completion_do_completion_again_add_forward_slash(fs):
    fs.create_dir("/test")
    assert do_py_completion("/test") == "/test/"
    assert do_py_completion(do_py_completion("/te")) == "/test/"
