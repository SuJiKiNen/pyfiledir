#!/usr/bin/env python

"""
Completing Chinese directories or filenames by acronym of Pinyin.
"""

import argparse

if __package__ is None or __package__ == '':
    from py_core import PYFILEDIR_ENVS, do_py_completion
else:
    from pyfiledir.py_core import PYFILEDIR_ENVS, do_py_completion

parser = argparse.ArgumentParser(
    prog="pyfiledir",
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    add_help=False,
)

_acronym_action = parser.add_argument(
    "acronym",
    help="acronym of Pinyin",
    nargs='?',
    default="",
)

_help_action = parser.add_argument(
    '-h',
    '--help',
    action='help', default=argparse.SUPPRESS,
    help='Show this help message and exit.',
)

_envs_action = parser.add_argument(
    "-e",
    "--envs",
    nargs='?',
    const="human",
    dest="output_env_type",
    help="print available environment variables.",
)

_version_action = parser.add_argument(
    '-v',
    '-V',
    '--version',
    action='store_true',
    help='print pyfiledir version.',
)

_where_action = parser.add_argument(
    "-w",
    "--where",
    action='store_true',
    help="print where pyfiledir is.",
)


def parse_args(argv):
    return parser.parse_args(argv)


def process_print_bash_export_envs(args):
    PYFILEDIR_ENVS.collect_envs()
    for env_name, info in PYFILEDIR_ENVS.__members__.items():
        cur_value = repr(info.value[0])
        print(
            "{}={}".format(
                env_name,
                cur_value,
            ),
        )


_HUMAN_READBLE_ENVS_HEADER = ("ENV_NAME", "TYPE", "CURRENT_VALUE")


def process_print_envs(args):
    PYFILEDIR_ENVS.collect_envs()
    max_env_name_len = 0
    max_env_type_len = 0
    max_env_value_len = 0
    for env_name, info in PYFILEDIR_ENVS.__members__.items():
        default_value = repr(info.value[0])
        env_type = info.value[2].__name__
        max_env_name_len = max(max_env_name_len, len(env_name))
        max_env_type_len = max(max_env_type_len, len(env_type))
        max_env_value_len = max(max_env_value_len, len(default_value))

    PADDING = 2
    row_format = (
        "{:<" + str(max_env_name_len + PADDING) + "}" +
        "{:^" + str(max_env_type_len + PADDING) + "}" +
        "{:^" + str(max_env_value_len + PADDING) + "}"
    )

    print(row_format.format(*_HUMAN_READBLE_ENVS_HEADER))
    for env_name, info in PYFILEDIR_ENVS.__members__.items():
        cur_value = repr(info.value[0])
        env_type = info.value[2].__name__
        print(
            row_format.format(
                env_name,
                env_type,
                cur_value,
            ),
        )
    print()
    print('You can ues bash "pyfiledir -e bash" to view a simple version.')


def process_print_versions(args):
    import platform
    import sys
    from __version__ import __version__
    from __unihan import __unihan_version__, __unihan_data_file_url__
    print(
        "{:<9} {:<10} from ({})".format(
            platform.python_implementation(),
            platform.python_version(),
            sys.executable,
        ),
    )
    print(
        "{:<9} {:<10} from ({})".format(
            "pyfiledir",
            __version__,
            sys.argv[0],
        ),
    )
    print(
        "{:<9} {:<10} from ({})".format(
            "Unihan",
            __unihan_version__,
            __unihan_data_file_url__,
        ),
    )


def process_print_where(args):
    import sys
    print(sys.argv[0])


def process_args(args):

    if args.output_env_type:
        if args.output_env_type == "human":
            process_print_envs(args)
        elif args.output_env_type == "bash":
            process_print_bash_export_envs(args)
    elif args.version:
        process_print_versions(args)
    elif args.acronym:
        print(do_py_completion(path=args.acronym), end="")
    elif args.where:
        process_print_where(args)
    else:
        parser.print_help()
