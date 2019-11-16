import os
import random
from unittest.mock import patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pyfakefs.fake_filesystem_unittest import Patcher

from pyfiledir import py_core
from pyfiledir.__main__ import main
from utils import file_sequence_strategy


@pytest.mark.parametrize(
    "path,excepted", [
        ("test1", ("test1", slice(None, None, 1))),
        ("测试1", ("测试", slice(0, 1, 1))),
        ("0", ("0", slice(None, None, 1))),
        ("test", ("test", slice(None, None, 1))),
        ("测试", ("测试", slice(None, None, 1))),
    ],
)
def test_rsplit_selection(path, excepted):
    assert py_core.rsplit_selection(path) == excepted


@pytest.mark.parametrize(
    "path,excepted", [
        ("/test1", True),
        ("/测试1", False),
    ],
)
def test_isascii(path, excepted):
    assert py_core.all_ascii(path) == excepted


def test_same_path(fs, test_home_dir):
    assert py_core.same_path(test_home_dir, "~/")


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
    assert excepted in py_core.get_py(char)


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
    assert py_core.get_truthy_env(key) == excepted


def test_do_py_completion_on_not_exists_path():
    with pytest.raises(SystemExit):
        py_core.do_py_completion("/not_exists_path/file")


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


@given(
    file_seqs=file_sequence_strategy(),
)
@settings(max_examples=32)
def test_natural_sort(file_seqs):
    shuffled_file_seqs = random.sample(file_seqs, len(file_seqs))
    assert file_seqs == py_core.natural_sort(shuffled_file_seqs)


@given(
    inputrc_envs=st.dictionaries(
        st.sampled_from(
            list(py_core.inputrc_to_pyfiledir_env_map.keys()),
        ),
        st.booleans().map(lambda x: (x, "on") if x else (x, "off")),
    ),
)
def test_load_env_from_from_inputrc_file(inputrc_envs):

    with Patcher(
            modules_to_reload=[
                py_core,
            ],
    ) as patcher:
        file_path = '/.inputrc'
        contents = "\n".join(
            ("set {} {}".format(key, inputrc_envs[key][1]) for key in inputrc_envs)
        )
        patcher.fs.create_file(file_path, contents=contents)
        ret = py_core.PYFILEDIR_ENVS.load_env_from_inputrc(file_path)
        for key in inputrc_envs:
            pyfiledir_env_name = py_core.inputrc_to_pyfiledir_env_map[key]
            assert ret[pyfiledir_env_name] == str(inputrc_envs[key][0])

        # check PYFILEDIR_ENVS setup successfully according inputrc file
        with patch.dict(
                os.environ,
                {
                    'INPUTRC': file_path,
                },
        ):
            py_core.PYFILEDIR_ENVS.collect_inputrc_envs()
            for key in inputrc_envs:
                pyfiledir_env_name = py_core.inputrc_to_pyfiledir_env_map[key]
                assert str(py_core.PYFILEDIR_ENVS[pyfiledir_env_name]) == str(inputrc_envs[key][0])
