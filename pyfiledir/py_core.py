#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bisect
import locale
import os
import sys
from collections import OrderedDict, namedtuple
from enum import Enum
from functools import lru_cache

if __package__ is None or __package__ == '':
    from py_polyphone import PY_POLYPHONE
else:
    from pyfiledir.py_polyphone import PY_POLYPHONE

for cn_char, pys in PY_POLYPHONE.items():
    PY_POLYPHONE[cn_char] = [py[0] for py in pys]

EncodingRange = namedtuple('EncodingRange', 'encoding min_codepoint max_codepoint')
GB2312EncodeingRange = EncodingRange(
    encoding="gb2312",
    min_codepoint=b"\xb0\xa1",
    max_codepoint=b"\xd7\xf9",
)

inputrc_to_pyfiledir_env_map = {
    "mark-directories": 'PYFILEDIR_ADD_TRAILING_SLASH',
    "completion-ignore-case": 'PYFILEDIR_IGNORE_CASE',
    "expand-tilde": 'PYFILEDIR_EXPAND_TIDLE',
}


def is_truthy(value):
    return value not in ("0", "false", "no", "off")


def get_truthy_env(name):
    return is_truthy(str.lower(get_env(name)))


def get_env(env_name):
    return os.environ.get(env_name) or str(PYFILEDIR_ENVS[env_name])


class PYFILEDIR_ENVS(Enum):

    PYFILEDIR_CANDIDATE_SEP = ["\n", "how pyfiledir join candidates", str]
    PYFILEDIR_WILDCARD = [",", "wildcard match charactor for dir or file", str]
    PYFILEDIR_ADD_TRAILING_SLASH = [True, "add trailing slash for directory candidate", bool]
    PYFILEDIR_KEEP_LEADING_DOT_SLASH = [True, "keep leading ./ in path", bool]
    PYFILEDIR_COMPLETE_COMMON_PREFIX = [True, "complete common prefix of candidates first", bool]
    PYFILEDIR_EXPAND_TIDLE = [False, "expand =~= to =/home/<user>=", bool]
    PYFILEDIR_IGNORE_CASE = [True, "completion ignore case", bool]
    PYFILEDIR_USE_UNIHAN_DICT = [True, "use rich Unihan dict", bool]
    PYFILEDIR_USE_NATURAL_SORT = [False, "use natural sort, sorting filenames", bool]

    @classmethod
    def items(cls):
        return cls.__members__.items()

    def __str__(self):
        return str(self.value[0])

    def __hash__(self, other):
        return self.value[0] == other.value[0]

    def __eq__(self, other):
        return self.value[0] == other

    def __bool__(self):
        return self.value[0]

    @property
    def docstring(self):
        return self.value[1]

    @staticmethod
    def update(*args, **kwargs):
        for k, v in kwargs.items():
            PYFILEDIR_ENVS[k].value[0] = v

    def load_env_from_inputrc(filename=None):
        parsed_envs = {}
        try:
            with open(filename, "r") as f:
                for line in f:
                    # handle inputrc if statement?
                    if line.startswith('#'):
                        continue
                    elif line.startswith('set'):
                        parts = line.split()
                        if len(parts) < 3:
                            continue
                        if parts[1] in inputrc_to_pyfiledir_env_map.keys():
                            parsed_envs[
                                inputrc_to_pyfiledir_env_map[parts[1]]
                            ] = repr(is_truthy(parts[2]))
        except FileNotFoundError:
            pass
        return parsed_envs

    @staticmethod
    def collect_inputrc_envs():
        INPUTRC_ENVS = PYFILEDIR_ENVS.load_env_from_inputrc(
            os.environ.get('INPUTRC')
            or os.path.expanduser('~/.inputrc'),
        )
        PYFILEDIR_ENVS.update(**INPUTRC_ENVS)

    @staticmethod
    def collect_environ_envs():
        ENVIRON_ENVS = PYFILEDIR_ENVS.load_envs_from_environ()
        PYFILEDIR_ENVS.update(**ENVIRON_ENVS)

    @staticmethod
    def load_envs_from_environ():
        envs_from_environ = {}
        for env_name, val in PYFILEDIR_ENVS.items():
            if val.value[2] == bool:
                envs_from_environ[env_name] = get_truthy_env(env_name)
            if val.value[2] == str:
                envs_from_environ[env_name] = get_env(env_name)
        return envs_from_environ

    @staticmethod
    def collect_envs():
        PYFILEDIR_ENVS.collect_inputrc_envs()
        PYFILEDIR_ENVS.collect_environ_envs()


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)


def rsplit_selection(filename):
    sel = None
    if (
            filename
            and len(filename) > 1
            and not all_ascii(filename)
            and filename[-1] in char_range('1', '9')
    ):
        sel = int(filename[-1])
        return filename[:-1], slice(sel-1, sel, 1)
    else:
        return filename, slice(None, None, 1)


def all_ascii(string):
    try:
        string.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def unicode_sort(dirs=[]):
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        # TODO: add warning logger here
        pass
    return sorted(dirs, key=locale.strxfrm)


def try_cast_int(s):
    try:
        return int(s)
    except ValueError:
        return s


def natural_sort_key(s):
    import re
    num_list = re.findall(r'\d+', s)
    num_list = map(try_cast_int, num_list)
    return tuple(num_list)


def natural_sort(l):
    return sorted(l, key=natural_sort_key)


@lru_cache(maxsize=1024)
def get_py(char, _encoding="GB2312"):
    """
    There are 3,755 Level 1 Chinese characters, ranging from 0xB0A1 to 0xD7F9 in GB2312 codes.
    """

    if PYFILEDIR_ENVS.PYFILEDIR_USE_UNIHAN_DICT:
        from pyfiledir.py_dict import PY_DICT
        if char in PY_DICT.keys():
            return [pinyin[0] for pinyin in PY_DICT[char]]
        else:
            return [char]

    try:
        char_bytes = char.encode(_encoding)
    except Exception:
        return char

    if not (b"\xb0\xa1" <= char_bytes <= b"\xd7\xf9"):
        return char
    table = OrderedDict([
        ("a", b"\xb0\xc4"),
        ("b", b"\xb2\xc0"),
        ("c", b"\xb4\xed"),
        ("d", b"\xb6\xe9"),
        ("e", b"\xb7\xa1"),
        ("f", b"\xb8\xc0"),
        ("g", b"\xb9\xfd"),
        ("h", b"\xbb\xf6"),
        ("j", b"\xbf\xa5"),
        ("k", b"\xc0\xab"),
        ("l", b"\xc2\xe7"),
        ("m", b"\xc4\xc2"),
        ("n", b"\xc5\xb5"),
        ("o", b"\xc5\xbd"),
        ("p", b"\xc6\xd9"),
        ("q", b"\xc8\xba"),
        ("r", b"\xc8\xf5"),
        ("s", b"\xcb\xf9"),
        ("t", b"\xcd\xd9"),
        ("w", b"\xce\xf3"),
        ("x", b"\xd1\xb8"),
        ("y", b"\xd4\xd0"),
        ("z", b"\xd7\xf9"),
    ])
    keys = list(table.keys())
    values = list(table.values())
    ix = bisect.bisect_left(values, char_bytes)
    return [keys[ix]]


@lru_cache(maxsize=1024)
def do_polyphone_match(cn_char, alpha):
    return (
        cn_char in PY_POLYPHONE.keys()
        and alpha in PY_POLYPHONE[cn_char]
    )


@lru_cache(maxsize=1024)
def do_py_match(filename, abbrev):
    if len(filename) < len(abbrev):
        return False

    for i, alpha in enumerate(abbrev):
        def match():
            yield alpha == PYFILEDIR_ENVS.PYFILEDIR_WILDCARD and not all_ascii(filename[i])
            yield filename[i] == alpha
            yield alpha in get_py(filename[i])
            yield do_polyphone_match(cn_char=filename[i], alpha=alpha)
        if not any(match()):
            return False
    return True


def same_path(path1, path2):
    path1 = os.path.expanduser(path1)
    path1 = os.path.normpath(path1)
    path2 = os.path.expanduser(path2)
    path2 = os.path.normpath(path2)
    return path1 == path2


def as_unix_path(path):
    return path.replace(os.path.sep, "/")


def pre_handler(f):
    if PYFILEDIR_ENVS.PYFILEDIR_IGNORE_CASE:
        return f.lower()
    return f


def do_py_completion(path):
    PYFILEDIR_ENVS.collect_envs()
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    basename, selection = rsplit_selection(basename)
    path = os.path.join(dirname, basename)
    expanded_dirname = os.path.expanduser(dirname) or "./"

    if not os.path.exists(expanded_dirname):
        sys.exit(0)

    try:
        files = os.listdir(expanded_dirname)
    except Exception:
        sys.exit(0)

    if PYFILEDIR_ENVS.PYFILEDIR_EXPAND_TIDLE:
        dirname = os.path.expanduser(dirname)

    ret = []
    for f in files:
        if do_py_match(filename=pre_handler(f), abbrev=basename):
            comp_path = os.path.join(dirname, f)
            ret.append(comp_path)

    keep_dot_slash = PYFILEDIR_ENVS.PYFILEDIR_KEEP_LEADING_DOT_SLASH
    if not keep_dot_slash:
        ret = [os.path.normpath(p) for p in ret]

    should_add_slash = True
    if len(ret) > 1 and PYFILEDIR_ENVS.PYFILEDIR_COMPLETE_COMMON_PREFIX:
        common_prefix = os.path.commonprefix(ret)
        """
        if common_prefix is a prefix of others,then it shouldn't
        add forward slash eg. /docker, /docker-pg-replication/
        /do[tab] -> /docker
        when input has number selection,this rule not applied
        eg. /测试 /测试目录
        /测1[tab] -> /测试/
        """
        if selection == slice(None, None, 1):
            for p in ret:
                if len(p) > len(common_prefix) and p.startswith(common_prefix):
                    should_add_slash = False
                    break
        if len(common_prefix) > len(path):
            ret = [common_prefix]

    if PYFILEDIR_ENVS.PYFILEDIR_USE_NATURAL_SORT:
        ret = natural_sort(ret)
    else:
        ret = unicode_sort(ret)

    ret = ret[selection]

    if (
            len(ret) == 1
            and os.path.isdir(ret[0])
            and (
                PYFILEDIR_ENVS.PYFILEDIR_ADD_TRAILING_SLASH
                or same_path(ret[0], path)
            )
            and should_add_slash
    ):
        ret[0] = os.path.join(ret[0], "")  # add trailing slash

    ret = [as_unix_path(p) for p in ret]  # post processing path

    return str(PYFILEDIR_ENVS.PYFILEDIR_CANDIDATE_SEP).join(ret)
