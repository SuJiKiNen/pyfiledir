#!/usr/bin/env bash

_pinyin_abbrev_completion() {
    local IFS
    local cur
    IFS=$'\n'
    cur="${COMP_WORDS[COMP_CWORD]}"
    cur=$(eval echo "$cur") # unquote current input
    words=$(pyfiledir "$cur")
    COMPREPLY=( $(compgen -W "$words") )
}

complete -o "filenames" -o "nospace" -o "bashdefault" -o "default" -F _pinyin_abbrev_completion ls cd cat
