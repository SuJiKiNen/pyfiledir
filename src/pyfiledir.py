#!/usr/bin/env python

import locale
import os
import subprocess
import sys
from functools import lru_cache

SEP = " "


def _is_zsh():
    return 'zsh' in os.environ['SHELL']


def rsplit_selection(path):
    sel = None
    if path and not isascii(path) and path[-1].isdigit():
        sel = int(path[-1])
        return path[:-1], slice(sel, sel+1, 1)
    else:
        return path, slice(None, None, 1)


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

    path, pieces = rsplit_selection(path)
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    expanded_dirname = os.path.expanduser(dirname) or "./"

    if not os.path.exists(expanded_dirname):
        sys.exit(0)

    try:
        files = os.listdir(expanded_dirname)
    except Exception:
        sys.exit(0)

    ret = []
    for f in files:
        if do_py_match(filename=f, abbrev=basename):
            comp_path = os.path.join(dirname, f)
            ret.append(comp_path)

    ret = unicode_sort(ret)
    return SEP.join(ret[pieces])


if __name__ == '__main__':
    if _is_zsh():
        sys.exit(0)
    if len(sys.argv) >= 2:
        print(do_py_completion(path=sys.argv[1]))
