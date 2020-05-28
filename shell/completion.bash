#!/usr/bin/env bash
_pyfiledir_setup_pythonpath(){
    _PYFILEDIR_PATH="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" || return; pwd -P )"
    if [ "$OSTYPE" = "msys" ]; then
        PYTHONPATH=${PYTHONPATH:+${PYTHONPATH};}$_PYFILEDIR_PATH
    else
        #----------|-if PYTHONPATH not empty add leading colon |
        PYTHONPATH=${PYTHONPATH:+${PYTHONPATH}:}$_PYFILEDIR_PATH
    fi
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
    if [ -z "$cur" ]; then
        return 0
    fi

    if [ "$OSTYPE" = "msys" ] && command -v dos2unix >/dev/null 2>&1; then
        words=$(pyfiledir "$cur" | dos2unix)
    else
        words=$(pyfiledir "$cur")
    fi
    words=($(compgen -W "${words[*]}"))

    if [ "$OSTYPE" = "msys" ] && command -v cygpath > /dev/null 2>&1; then
        # convert Windows style path to Unix One
        # like D:\ => /d/
        for ix in "${!words[@]}"; do
            words[$ix]=$(cygpath -u "${words[$ix]}")
        done
    fi

    length="${#words[@]}"
    if [ "$length" -eq 0 ]; then
        COMPREPLY=()
    else
        COMPREPLY=($(printf '%q'"$IFS" "${words[@]}"))
    fi
}

if [ -z "$PYFILEDIR_BASH_COMPLETE_OPTIONS" ]; then
    PYFILEDIR_BASH_COMPLETE_OPTIONS="-o nospace -o bashdefault -o default -F _pyfiledir_completion"
fi

if [ -z "$PYFILEDIR_BASH_COMPLETION_COMMANDS" ]; then
    PYFILEDIR_BASH_COMPLETION_COMMANDS="cat cd cp emacs ln ls mkdir mv rm rmdir vi vim wc"
fi

if [ -n "$BASH_VERSION" ]; then
    complete $PYFILEDIR_BASH_COMPLETE_OPTIONS $PYFILEDIR_BASH_COMPLETION_COMMANDS
fi
