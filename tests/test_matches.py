import os

from src.pyfiledir import do_py_completion


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


def test_empty_basename_match_all_files_in_directory(fs):
    home_dir = '/home/test'
    os.environ['HOME'] = home_dir
    fs.create_dir(home_dir)
    fs.create_dir(os.path.join(home_dir, "subdir1"))
    fs.create_dir(os.path.join(home_dir, "subdir2"))
    assert do_py_completion("~/") == " ".join(["~/subdir1", "~/subdir2"])
