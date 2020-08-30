import os
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
    def __init__(self, sources_dir):
        scripts_dir = os.path.join(sources_dir, "shell")
        script_file = os.path.join(scripts_dir, 'readline_completion.bash')
        bin_path = os.path.join(sources_dir, "bin")
        bash_startup = "env -i LANG=en_US.UTF-8 PATH=/usr/bin/:/bin:{} bash --noprofile --rcfile".format(bin_path)
        cmd = "{} {}".format(bash_startup, script_file)
        self.p = pexpect.spawn(
            cmd,
            encoding='utf-8',
        )

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
def bash(sources_dir):
    return Bash(sources_dir)
