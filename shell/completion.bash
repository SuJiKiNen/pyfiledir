_pinyin_abbrev_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    words=$(pyfiledir $cur)
    COMPREPLY=( $(compgen -W "$words") )
}

complete -o "nospace" -o "bashdefault" -o "default" -F _pinyin_abbrev_completion ls cd cat
