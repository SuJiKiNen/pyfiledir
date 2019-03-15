#!/usr/bin/env python

import locale
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

SEP = " "


def _is_zsh():
    return 'zsh' in os.environ['SHELL']


def _expanduser(path):
    return path


def _rstrip_selection(path):
    num = None
    if len(path) > 1 and path[-1] >= '0' and path[-1] <= '9':
        num = int(path[-1])
    return path[:-1], num


def isascii(path):
    try:
        path.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def unicode_sort(dirs=[]):
    locale.setlocale(locale.LC_ALL, "")
    return sorted(dirs, key=locale.strxfrm)


@lru_cache(maxsize=1024)
def get_py(s):
    try:
        char = s.encode("GB18030")
    except Exception:
        return s
    if char < b"\xb0\xa1":
        return s
    if char > b"\xd7\xf9":
        return "?"
    if char < b"\xb0\xc5":
        return "a"
    if char < b"\xb2\xc1":
        return "b"
    if char < b"\xb4\xee":
        return "c"
    if char < b"\xb6\xea":
        return "d"
    if char < b"\xb7\xa2":
        return "e"
    if char < b"\xb8\xc1":
        return "f"
    if char < b"\xb9\xfe":
        return "g"
    if char < b"\xbb\xf7":
        return "h"
    if char < b"\xbf\xa6":
        return "j"
    if char < b"\xc0\xac":
        return "k"
    if char < b"\xc2\xe8":
        return "l"
    if char < b"\xc4\xc3":
        return "m"
    if char < b"\xc5\xb6":
        return "n"
    if char < b"\xc5\xbe":
        return "o"
    if char < b"\xc6\xda":
        return "p"
    if char < b"\xc8\xbb":
        return "q"
    if char < b"\xc8\xf6":
        return "r"
    if char < b"\xcb\xfa":
        return "s"
    if char < b"\xcd\xda":
        return "t"
    if char < b"\xce\xf4":
        return "w"
    if char < b"\xd1\xb9":
        return "x"
    if char < b"\xd4\xd1":
        return "y"
    if char < b"\xd7\xfa":
        return "z"
    return s


@lru_cache(maxsize=1024)
def do_py_match(filename, abbrev):
    if len(filename) < len(abbrev):
        return False

    for i, char in enumerate(abbrev):
        if not (filename[i] == char or get_py(filename[i]) == char):
            return False
    return True


def do_unescape_path(path):
    ret = subprocess.run(
        [
            'echo',
            '-e',  # enable interpretation of backslash escapes
            '-n',  # do not output the trailing newline
            path
        ],
        stdout=subprocess.PIPE
    )
    return ret.stdout.decode('utf-8')


def do_escape_path(path):
    ret = subprocess.run(
        [
            'printf',
            '%q',
            path
        ],
        stdout=subprocess.PIPE
    )
    return ret.stdout.decode("utf-8")


def do_py_completion(path):
    os_view_path = os.path.expanduser(path)
    os_view_dirname = os.path.dirname(os_view_path)
    if not os_view_dirname:
        os_view_dirname = "./"

    if not os.path.exists(os_view_dirname):
        sys.exit(0)

    try:
        files = os.listdir(os_view_dirname)
    except Exception:
        sys.exit(0)

    py_view_path = _expanduser(path)
    if not isascii(py_view_path):
        py_view_path, sel = _rstrip_selection(py_view_path)
    else:
        sel = None

    py_view_basename = os.path.basename(py_view_path)
    py_view_dirname = os.path.dirname(py_view_path)

    ret = []
    for f in files:
        if do_py_match(filename=f, abbrev=py_view_basename):
            comp_path = os.path.join(py_view_dirname, f)
            comp_path = Path(comp_path).as_posix()
            ret.append(comp_path)

    if sel:
        ret = unicode_sort(ret)
        return SEP.join(ret[sel:sel+1])
    else:
        return SEP.join(ret)


if __name__ == '__main__':
    if _is_zsh():
        sys.exit(0)
    if len(sys.argv) >= 2:
        print(do_py_completion(path=sys.argv[1]))
