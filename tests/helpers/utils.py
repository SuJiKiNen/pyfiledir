#!/usr/bin/env python

from hypothesis import strategies as st

from pyfiledir.py_core import GB2312EncodeingRange

_st_num = int.from_bytes(GB2312EncodeingRange.min_codepoint, byteorder="big")
_ed_num = int.from_bytes(GB2312EncodeingRange.max_codepoint, byteorder="big")


def chinese_character():
    num = st.integers(min_value=_st_num, max_value=_ed_num)

    def num_to_char(num):
        char_bytes = num.to_bytes(length=2, byteorder="big")
        try:
            return char_bytes.decode("GB18030")
        except UnicodeDecodeError:
            return ""
    return st.builds(num_to_char, num)


def file_sequence(perm, str1, str2, total_files):
    """
    https://en.wikipedia.org/wiki/File_sequence
    """
    assert len(perm) == 3

    def add_bracket(s):
        return "{{{0}}}".format(s)
    filename_pattern = "".join(map(add_bracket, perm))
    seq = [
        filename_pattern.format(i, str1, str2)
        for i in range(total_files)
    ]
    return seq


def file_sequence_strategy():
    return st.builds(
        file_sequence,
        perm=st.permutations([0, 1, 2]),
        str1=st.text(chinese_character()),
        str2=st.text(chinese_character()),
        total_files=st.integers(min_value=1, max_value=1000),
    )
