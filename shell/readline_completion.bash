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

function pyfiledir-filename-completions {

    local PY_EXEC
    if command -v python3 >/dev/null 2>&1; then
        PY_EXEC=python3
    elif  command -v python >/dev/null 2>&1; then
        if [[ $(python -V) =~ "Python 3" ]]; then
            PY_EXEC=python
        fi
    fi

    if [ -z $PY_EXEC ]; then
        printf "%s\n" "error: cannot find python3"
        exit 2
    fi
    # need recalculate READLINE_POINT,which count in bytes
    # while in bash substring count in characters
    # https://lists.gnu.org/archive/html/bug-bash/2018-04/msg00040.html
    local OLD_READLINE_POINT=$READLINE_POINT
    READLINE_POINT=$($PY_EXEC -c "print(len('$READLINE_LINE'.encode('utf8')[0:int('$READLINE_POINT')].decode('utf8')))")
    local BEFORE="${READLINE_LINE:0:${READLINE_POINT}}"
    local AFTER="${READLINE_LINE:${READLINE_POINT}}"
    local COMP_WORD

    cur="${BEFORE##* }" # get last word of input before readline point
    if [ -z "$cur" ]; then
        return 0
    fi
    cur=$(eval printf '%s' "$cur") # unquote current input

    local IFS=$'\n'
    local words=()
    local common_prefix
    mapfile -t words < <(pyfiledir "$cur")

    if [ ${#words[*]} -gt 1 ]; then
        for (( _i=0 ; _i<${#words[*]} ; _i++ )); do
            word=${words[$_i]}
            printf "%-12s " "$word"
        done | sort | fmt -w $((COLUMNS-8)) | column -tx
        common_prefix=$(printf '%s ' "${words[*]}" | $PY_EXEC -c "import sys, os; sys.stdout.write(os.path.commonprefix(sys.stdin.readlines()))")
        if [ -n "$common_prefix" ]; then
            COMP_WORD=$(printf "%q" $common_prefix)
            BEFORE=${BEFORE/%$cur/$COMP_WORD}
            READLINE_LINE=${BEFORE}${AFTER}
            READLINE_POINT=$($PY_EXEC -c "print(len('${BEFORE}'.encode('utf8')))")
        fi
    elif [ ${#words[*]} -eq 1 ]; then
        COMP_WORD=$(printf "%q" ${words[0]})
        BEFORE=${BEFORE/%$cur/$COMP_WORD} # replace last word
        READLINE_LINE=${BEFORE}${AFTER}
        READLINE_POINT=$($PY_EXEC -c "print(len('${BEFORE}'.encode('utf8')))")
    else
        # restore orgin READLINE_POINT
        READLINE_POINT=${OLD_READLINE_POINT}
    fi
}
