#!/usr/bin/env bash
if [ -n "$BASH_VERSION" ]; then
    bind -x '"\e/":pyfiledir-filename-completions'
fi
