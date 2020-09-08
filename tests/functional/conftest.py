import os
import sys
from distutils import dir_util

import pexpect
from pytest import fixture


@fixture(scope="session")
def sources_dir(tmpdir_factory):
    """
    copy pyfiledir sources tree to
    a temporary diretory/src
    """
    sources_dir = tmpdir_factory.mktemp('src')
    origin_sources_dir = os.path.join(os.getcwd())
    dir_util.copy_tree(origin_sources_dir, str(sources_dir))
    return sources_dir


class Bash():
    def __init__(self, sources_dir, debug=False):
        scripts_dir = sources_dir.join("shell")
        completion_file = scripts_dir.join('readline_completion.bash')
        key_binding_file = scripts_dir.join('readline_key_binding.bash')
        script_file = scripts_dir.join('test_readline_bashrc.bash')
        bash_startup = "\n".join(
            [
                "#!/usr/bin/env bash",
                "source {}".format(completion_file),
                "source {}".format(key_binding_file),
                "export PS1='\\u@\\h:\\w\\$' ",
                "unset PROMPT_COMMAND",
            ],
        )
        with script_file.open("w") as f:
            f.write(bash_startup)
        bin_path = sources_dir.join("bin")
        self.cmd = (
            "env -i "
            "LANG=en_US.UTF-8 "
            "PATH=/usr/bin/:/bin:{} "
            "bash --noprofile --rcfile {} -i"
        ).format(bin_path, script_file)
        if debug:
            self.cmd += " -x"

        self.p = pexpect.spawn(
            self.cmd,
            encoding='utf-8',
        )

        if debug:
            self.p.logfile = sys.stdout

    def cd(self, diretory):
        self.p.sendline('cd {}'.format(diretory))

    def complete_at_point(self):
        """send alt + /"""
        self.p.send('\x1b/')

    def type(self, chars):
        self.p.send(chars)

    def expect(self, expcetd):
        self.p.expect(expcetd, timeout=1)


@fixture(scope="function")
def bash(sources_dir, pyfiledir_debug):
    return Bash(sources_dir, pyfiledir_debug)
