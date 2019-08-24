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


class DEFAULT_PYFILEDIR_ENVS(Enum):

    PYFILEDIR_CANDIDATE_SEP = ("\n", "how pyfiledir join candidates")
    PYFILEDIR_WILDCARD = ("#", "wildcard match charactor for dir or file")
    PYFILEDIR_ADD_TRAILING_SLASH = ("True", "add trailing slash for directory candidate")
    PYFILEDIR_KEEP_LEADING_DOT_SLASH = ("True", "keep leading ./ in path")
    PYFILEDIR_COMPLETE_COMMON_PREFIX = ("True", "complete common prefix of candidates first")
    PYFILEDIR_EXPAND_TIDLE = ("False", "expand =~= to =/home/<user>=")
    PYFILEDIR_IGNORE_CASE = ("False", "completion ignore case")
    PYFILEDIR_USE_UNIHAN_DICT = ("False", "use rich Unihan dict")
    PYFILEDIR_USE_NATURAL_SORT = ("False", "use natural sort, sorting filenames")

    @classmethod
    def items(cls):
        return cls.__members__.items()

    def __str__(self):
        return self.value[0]

    def __hash__(self, other):
        return self.value[0] == other.value[0]

    @property
    def docstring(self):
        return self.value[1]


def get_truthy_env(name):
    return str.lower(get_env(name)) not in ("0", "false", "no", "off")


def get_env(env_name):
    return os.environ.get(env_name) or str(DEFAULT_PYFILEDIR_ENVS[env_name])


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

    if get_truthy_env("PYFILEDIR_USE_UNIHAN_DICT"):
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
            yield alpha == get_env("PYFILEDIR_WILDCARD") and ord(filename[i]) > 127
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
    if get_truthy_env("PYFILEDIR_IGNORE_CASE"):
        return f.lower()
    return f


def do_py_completion(path):
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    basename, selections = rsplit_selection(basename)
    path = os.path.join(dirname, basename)
    expanded_dirname = os.path.expanduser(dirname) or "./"

    if not os.path.exists(expanded_dirname):
        sys.exit(0)

    try:
        files = os.listdir(expanded_dirname)
    except Exception:
        sys.exit(0)

    if get_truthy_env("PYFILEDIR_EXPAND_TIDLE"):
        dirname = os.path.expanduser(dirname)

    ret = []
    for f in files:
        if do_py_match(filename=pre_handler(f), abbrev=basename):
            comp_path = os.path.join(dirname, f)
            ret.append(comp_path)

    keep_dot_slash = get_truthy_env("PYFILEDIR_KEEP_LEADING_DOT_SLASH")
    if not keep_dot_slash:
        ret = [os.path.normpath(p) for p in ret]

    if len(ret) > 1 and get_truthy_env("PYFILEDIR_COMPLETE_COMMON_PREFIX"):
        common_prefix = os.path.commonprefix(ret)
        if len(common_prefix) > len(path):
            ret = [common_prefix]

    if (
            len(ret) == 1
            and os.path.isdir(ret[0])
            and (
                get_truthy_env("PYFILEDIR_ADD_TRAILING_SLASH")
                or same_path(ret[0], path)
            )
    ):
        ret[0] = os.path.join(ret[0], "")  # add trailing slash

    ret = [as_unix_path(p) for p in ret]  # post processing path
    if get_truthy_env("PYFILEDIR_USE_NATURAL_SORT"):
        ret = natural_sort(ret)
    else:
        ret = unicode_sort(ret)
    return get_env("PYFILEDIR_CANDIDATE_SEP").join(ret[selections])
