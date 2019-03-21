#!/usr/bin/env bash

_pinyin_abbrev_completion() {
    # use printf to handle space,parentheses etc in filename properly
    # see https://stackoverflow.com/questions/1146098/properly-handling-spaces-and-quotes-in-bash-completion
    local IFS
    local cur
    IFS=$'\n'
    cur="${COMP_WORDS[COMP_CWORD]}"
    words=$(pyfiledir "$cur")
    words=($(compgen -W "${words[*]}"))
    if [[ "${#words[*]}" -eq 0 ]]; then
        COMPREPLY=()
    else
        COMPREPLY=($(printf '%q\n' "${words[@]}"))
    fi
}

complete -o "nospace" -o "bashdefault" -o "default" -F _pinyin_abbrev_completion ls cd cat
