#!/usr/bin/env sh
# -*- coding: utf-8 -*-

# A trick than run as shell script,find sutiable python version
# and execute current script as Pyhton script
# '''something''' seen as comment in Python
''':'  # equal a empty quoted string and a quoted colon(no-op)
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$0" "$@"
fi

if command -v python >/dev/null 2>&1; then
    # eg. python -V ->  Python 3.6.5
    py_version=$(python -V | cut -d ' ' -f2 | cut -d '.' -f1)
    if [ "${py_version}" -eq 3 ]; then
        exec python "$0" "$@"
    fi
fi
>&2 printf "%s" "error: cannot find python3"
# https://www.tldp.org/LDP/abs/html/exitcodes.html
# exitcode 2: Missing keyword or command, or permission problem
exit 2
':'''
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_DIR = os.path.expanduser(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "pyfiledir"))

if __package__ is None or __package__ == '':
    # executed directly
    from py_core import do_py_completion
else:
    # imported as a package
    from pyfiledir.py_core import do_py_completion


def main(argv):
    if len(argv) >= 2:
        print(do_py_completion(path=argv[1]), end="")


if __name__ == '__main__':
    sys.exit(main(sys.argv))

# Local Variables:
# mode: python
# End:
