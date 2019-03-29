#!/usr/bin/env bash

_pinyin_abbrev_completion() {
    # use printf to handle space,parentheses etc in filename properly
    # see https://stackoverflow.com/questions/1146098/properly-handling-spaces-and-quotes-in-bash-completion
    local IFS
    local cur
    local length
    local words
    IFS=$'\n'
    cur="${COMP_WORDS[COMP_CWORD]}"
    cur=$(eval echo "$cur") # unquote current input
    if command -v dos2unix >/dev/null 2>&1; then
        words=$(pyfiledir "$cur" | dos2unix)
    else
        words=$(pyfiledir "$cur")
    fi
    words=($(compgen -W "${words[*]}"))
    length="${#words[@]}"
    if [[ "$length" -eq 1 ]]; then
        COMPREPLY=($(printf '%q'"$IFS" "${words[@]}"))
    elif [[ "$length" -eq 0 ]]; then
        COMPREPLY=()
    else
        COMPREPLY=($(printf '%s'"$IFS" "${words[@]}"))
    fi
}

complete -o "nospace" -o "bashdefault" -o "default" -F _pinyin_abbrev_completion ls cd cat
