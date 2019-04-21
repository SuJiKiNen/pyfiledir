from src.pyfiledir import get_py, get_py2

st = b"\xb0\xa0"
ed = b"\xd7\xfb"

assert ed > st

st_num = int.from_bytes(st, byteorder="big")
ed_num = int.from_bytes(ed, byteorder="big")

assert ed_num > st_num


def test_new_py2_identity_to_py():
    for num in range(st_num, ed_num):
        bytes = num.to_bytes(length=2, byteorder="big")
        try:
            char = bytes.decode("GB18030")
            assert get_py(char) == get_py2(char)
        except UnicodeDecodeError:
            pass
