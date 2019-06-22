import os
from unittest.mock import patch

import pytest
from src.pyfiledir import (
    as_unix_path,
    do_polyphone_match,
    do_py_completion,
    get_env,
    unicode_sort,
)


def test_completion_default_behavior_not_expand_tilde(fs, test_home_dir):

    target_dir = "~/测试目录"
    target_dir_expanded = os.path.expanduser(target_dir)
    target_file = os.path.join(target_dir_expanded, "file")
    fs.create_dir(target_dir_expanded)
    fs.create_file(target_file)
    assert do_py_completion("~/c") == target_dir


@patch.dict(
    os.environ,
    {
        "PYFILEDIR_EXPAND_TIDLE": "on",
    },
)
def test_completion_expand_tidle(fs, test_home_dir):
    target_dir = "~/测试目录"
    target_dir_expanded = os.path.expanduser(target_dir)
    target_file = os.path.join(target_dir_expanded, "file")
    fs.create_dir(target_dir_expanded)
    fs.create_file(target_file)
    assert do_py_completion("~/c") == target_dir_expanded


def test_completion_keep_leading_dot_slash(fs, test_home_dir):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    fs.create_dir(os.path.join(test_home_dir, "subdir1"))
    fs.create_dir(os.path.join(test_home_dir, "subdir2"))
    os.chdir(test_home_dir)
    assert do_py_completion("./") == SEP.join(["./subdir1", "./subdir2"])


def test_complete_implicit_current_directory(fs, test_home_dir):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    os.chdir("/home")
    assert do_py_completion("t") == SEP.join(["test"])


@pytest.mark.parametrize(
    "dirs,files,typed,excepted", [
        (["subdir1", "subdir2"], ["file1", "file2"], "~/", unicode_sort(["subdir1", "subdir2", "file1", "file2"])),
        (["subdir1", "subdir2"], [], "~/", unicode_sort(["subdir1", "subdir2"])),
        ([], ["file1", "file2"], "~/", unicode_sort(["file1", "file2"])),
    ],
)
def test_empty_basename_match_all_files_or_dirs_in_directory(dirs, files, typed, excepted, fs, test_home_dir):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    for d in dirs:
        fs.create_dir(os.path.join(test_home_dir, d))
    for f in files:
        fs.create_file(os.path.join(test_home_dir, f))
    excepted = [as_unix_path(os.path.join("~/", f)) for f in excepted]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize(
    "dirs,typed,excepted", [
        (
            ["/1024", "/1025"],
            "/1",
            ["/1024", "/1025"],
        ),
        (
            ["/2021_12_28", "/2023_10_15", "/2025_04_12"],
            "/2023",
            ["/2023_10_15"],
        ),
        (
            ["/个人图片", "/个人信息"],
            "/个" + "1",
            [unicode_sort(["/个人图片", "/个人信息"])[0]],
        ),
    ],
)
def test_number_selection(dirs, typed, excepted, fs):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize(
    "dirs,typed,excepted", [
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
    ],
)
def test_number_selection_start_from_one(dirs, typed, excepted, fs):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


def test_solo_completion_on_dirs_do_completion_again_add_forward_slash(fs):
    fs.create_dir("/test_dir")
    assert do_py_completion("/test_dir") == "/test_dir/"
    assert do_py_completion(do_py_completion("/te")) == "/test_dir/"


def test_solo_completion_on_files_do_completion_again_not_add_forward_slash(fs):
    fs.create_file("/test_file")
    assert do_py_completion("/test_file") == "/test_file"
    assert do_py_completion(do_py_completion("/te")) == "/test_file"


@pytest.mark.parametrize(
    "cn_char,alpha", [
        ("重", "c"),
        ("重", "z"),
        ("乐", "l"),
        ("乐", "y"),
    ],
)
def test_do_polyphone_match(cn_char, alpha):
    assert do_polyphone_match(cn_char, alpha)


@pytest.mark.parametrize(
    "dirs,typed,excepted", [
        (["/乐趣"], "/lq", ["/乐趣"]),
        (["/音乐"], "/yy", ["/音乐"]),
        (["/重要"], "/zy", ["/重要"]),
        (["/重复"], "/cf", ["/重复"]),
    ],
)
def test_polyphone_completion_mtach(dirs, typed, excepted, fs):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize(
    "dirs,typed,excepted", [
        (["/芙蓉", "/fr"], "/##", ["/芙蓉"]),
        (["/目录"], "/##", ["/目录"]),
    ],
)
def test_number_sign_is_unicode_wildcard(dirs, typed, excepted, fs):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize(
    "dirs,typed,excepted", [
        (["/test1", "/test2"], "/te", ["/test"]),
        (["/学习java", "/学习javascript"], "/x", ["/学习java"]),
        (
            [
                "/学习java",
                "/学习javascript",
                "/xx",
            ],
            "/x",
            unicode_sort(["/学习java", "/学习javascript", "/xx"]),
        ),
    ],
)
@patch.dict(
    os.environ,
    {
        "PYFILEDIR_COMPLETE_COMMON_PREFIX": "1",
    },
)
def test_complete_common_prefix_first(dirs, typed, excepted, fs):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)


@pytest.mark.parametrize(
    "dirs,typed,excepted", [
        (["/Test1", "/TEST2"], "/te", unicode_sort(["/Test1", "/TEST2"])),
    ],
)
@patch.dict(
    os.environ,
    {
        "PYFILEDIR_COMPLETE_COMMON_PREFIX": "off",
        "PYFILEDIR_IGNORE_CASE": "yes",
    },
)
def test_candidates_ignore_case(dirs, typed, excepted, fs):
    SEP = get_env("PYFILEDIR_CANDIDATE_SEP")
    [fs.create_dir(d) for d in dirs]
    assert do_py_completion(typed) == SEP.join(excepted)