#!/usr/bin/env bash
_pyfiledir_setup_pythonpath(){
    _PYFILEDIR_PATH="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" || return; pwd -P )"
    PYTHONPATH=$PYTHONPATH:$_PYFILEDIR_PATH
    export PYTHONPATH
    unset _PYFILEDIR_PATH
}
_pyfiledir_setup_pythonpath

_pyfiledir_completion() {
    # use printf to handle space,parentheses etc in filename properly
    # see https://stackoverflow.com/questions/1146098/properly-handling-spaces-and-quotes-in-bash-completion
    local IFS
    local cur
    local length
    local words
    IFS=$'\n'
    cur="${COMP_WORDS[COMP_CWORD]}"
    cur=$(eval printf '%s' "$cur") # unquote current input
    if [ "$OSTYPE" = "*msys*" ] && command -v dos2unix >/dev/null 2>&1; then
        words=$(pyfiledir "$cur" | dos2unix)
    else
        words=$(pyfiledir "$cur")
    fi
    words=($(compgen -W "${words[*]}"))

    if [ "$OSTYPE" = "*msys*" ] && command -v cygpath > /dev/null 2>&1; then
        # convert Windows style path to Unix One
        # like D:\ => /d/
        for ix in "${!words[@]}"; do
            words[$ix]=$(cygpath -u "${words[$ix]}")
        done
    fi

    length="${#words[@]}"
    if [[ "$length" -eq 0 ]]; then
        COMPREPLY=()
    else
        COMPREPLY=($(printf '%q'"$IFS" "${words[@]}"))
    fi
}

if [[ -n "$BASH_VERSION" ]]; then
    complete -o "nospace" -o "bashdefault" -o "default" -F _pyfiledir_completion ls cd cat
fi
