#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
import os

inputrc_to_pyfiledir_env_map = {
    "mark-directories": "PYFILEDIR_ADD_TRAILING_SLASH",
    "completion-ignore-case": "PYFILEDIR_IGNORE_CASE",
    "expand-tilde": "PYFILEDIR_EXPAND_TIDLE",
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
    PYFILEDIR_ADD_TRAILING_SLASH = [
        True,
        "add trailing slash for directory candidate",
        bool,
    ]
    PYFILEDIR_KEEP_LEADING_DOT_SLASH = [True, "keep leading ./ in path", bool]
    PYFILEDIR_COMPLETE_COMMON_PREFIX = [
        True,
        "complete common prefix of candidates first",
        bool,
    ]
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
                    if line.startswith("#"):
                        continue
                    elif line.startswith("set"):
                        parts = line.split()
                        if len(parts) < 3:
                            continue
                        if parts[1] in inputrc_to_pyfiledir_env_map.keys():
                            parsed_envs[inputrc_to_pyfiledir_env_map[parts[1]]] = repr(
                                is_truthy(parts[2])
                            )
        except FileNotFoundError:
            pass
        return parsed_envs

    @staticmethod
    def collect_inputrc_envs():
        INPUTRC_ENVS = PYFILEDIR_ENVS.load_env_from_inputrc(
            os.environ.get("INPUTRC") or os.path.expanduser("~/.inputrc"),
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
