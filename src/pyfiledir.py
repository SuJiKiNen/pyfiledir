#!/usr/bin/env python

import bisect
import locale
import os
import sys
from collections import OrderedDict
from functools import lru_cache

PYFILEDIR_CANDIDATE_SEP = "\n"
PYFILEDIR_WILDCARD = '#'

POLYPHONE_TABLE = {
    '把': ['ba', 'pa'],
    '便': ['bian', 'pian'],
    '不': ['bu', 'fou'],
    '参': ['cen', 'shen'],
    '藏': ['cang', 'zang'],
    '曾': ['ceng', 'zeng'],
    '查': ['cha', 'zha'],
    '柴': ['chai', 'zhai'],
    '嘲': ['chao', 'zhao'],
    '朝': ['chao', 'zhao'],
    '车': ['che', 'ju'],
    '乘': ['cheng', 'sheng'],
    '逞': ['cheng', 'ying'],
    '仇': ['chou', 'qiu'],
    '臭': ['chou', 'xiu'],
    '雏': ['chu', 'ju'],
    '畜': ['xu', 'chu'],
    '传': ['chuan', 'zhuan'],
    '串': ['chuan', 'guan'],
    '茨': ['ci', 'zi'],
    '歹': ['dai', 'e'],
    '呆': ['dai', 'bao'],
    '单': ['chan', 'dan'],
    '奠': ['dian', 'zheng'],
    '调': ['diao', 'tiao'],
    '侗': ['dong', 'tong'],
    '逗': ['dou', 'zhu'],
    '兑': ['dui', 'rui'],
    '恶': ['e', 'wu'],
    '繁': ['fan', 'po'],
    '番': ['fan', 'pan'],
    '冯': ['feng', 'ping'],
    '拂': ['fu', 'bi'],
    '革': ['ge', 'ji'],
    '给': ['gei', 'ji'],
    '雇': ['gu', 'hu'],
    '筴': ['ce', 'jia'],
    '龟': ['gui', 'jun'],
    '蛤': ['ha', 'ge'],
    '会': ['hui', 'kuai'],
    '祭': ['ji', 'zhai'],
    '己': ['ji', 'qi'],
    '稽': ['ji', 'qi'],
    '挟': ['xie', 'jia'],
    '降': ['jiang', 'xiang'],
    '剿': ['chao', 'jiao'],
    '解': ['jie', 'xie'],
    '颈': ['jing', 'geng'],
    '咎': ['jiu', 'gao'],
    '句': ['jv', 'gou'],
    '卷': ['juan', 'quan'],
    '楷': ['kai', 'jie'],
    '扛': ['kang', 'gang'],
    '姥': ['mu', 'lao'],
    '乐': ['le', 'yue'],
    '率': ['lv', 'shuai'],
    '泌': ['mi', 'bi'],
    '淖': ['nao', 'zhuo', 'chuo'],
    '宁': ['ning', 'zhu'],
    '弄': ['nong', 'long'],
    '女': ['nv', 'ru'],
    '耙': ['pa', 'ba'],
    '旁': ['pang', 'bang'],
    '捧': ['peng', 'feng'],
    '屏': ['ping', 'bing'],
    '魄': ['po', 'bo'],
    '葡': ['pu', 'bei'],
    '脯': ['fu', 'pu'],
    '曝': ['pu', 'bao'],
    '埔': ['pu', 'bu'],
    '奇': ['qi', 'ji'],
    '契': ['qi', 'xie'],
    '栖': ['qi', 'xi'],
    '洽': ['qia', 'he'],
    '区': ['qu', 'ou'],
    '圈': ['quan', 'juan'],
    '炔': ['gui', 'que'],
    '厦': ['xia', 'sha'],
    '刹': ['cha', 'sha'],
    '栅': ['zha', 'shan'],
    '裳': ['chang', 'shang'],
    '折': ['zhe', 'she'],
    '盛': ['cheng', 'sheng'],
    '石': ['shi', 'dan'],
    '适': ['shi', 'kuo'],
    '失': ['shi', 'yi'],
    '湿': ['shi', 'xi'],
    '属': ['zhu', 'shu'],
    '衰': ['shuai', 'cui'],
    '说': ['shuo', 'yue', 'shui'],
    '伺': ['ci', 'si'],
    '台': ['tai', 'yi'],
    '倘': ['chang', 'tang'],
    '提': ['ti', 'di'],
    '湍': ['tuan', 'zhuan'],
    '屯': ['tun', 'zhun'],
    '驮': ['duo', 'tuo'],
    '味': ['wei', 'mei'],
    '尉': ['wei', 'yu'],
    '蔚': ['wei', 'yu'],
    '挝': ['wo', 'zhua'],
    '涡': ['wo', 'guo'],
    '系': ['xi', 'ji'],
    '吓': ['xia', 'he'],
    '咸': ['xian', 'jian'],
    '巷': ['xiang', 'hang'],
    '兄': ['xiong', 'kuang'],
    '宿': ['su', 'xiu'],
    '削': ['xiao', 'shao'],
    '噎': ['ye', 'sha'],
    '涌': ['yong', 'chong'],
    '俞': ['yu', 'chou'],
    '予': ['yu', 'zhu'],
    '择': ['ze', 'yi'],
    '轧': ['zha', 'ga', 'ya'],
    '喳': ['cha', 'zha'],
    '翟': ['zhai', 'di'],
    '粘': ['zhan', 'nian'],
    '重': ['chong', 'zhong', 'chong'],
    '种': ['zhong', 'chong'],
    '粥': ['zhou', 'yu'],
    '拽': ['zhuai', 'ye'],
    '幢': ['chuang', 'zhuang'],
    '椎': ['chui', 'zhui'],
    '兹': ['ci', 'zi'],
    '卒': ['zu', 'cu'],
}

for cn_char, pys in POLYPHONE_TABLE.items():
    POLYPHONE_TABLE[cn_char] = [py[0] for py in pys]


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)


def rsplit_selection(path):
    sel = None
    if (
            path
            and not all_ascii(path)
            and path[-1] in char_range('1', '9')
    ):
        sel = int(path[-1])
        return path[:-1], slice(sel-1, sel, 1)
    else:
        return path, slice(None, None, 1)


def all_ascii(path):
    try:
        path.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def unicode_sort(dirs=[]):
    locale.setlocale(locale.LC_ALL, "")
    return sorted(dirs, key=locale.strxfrm)


@lru_cache(maxsize=1024)
def get_py(char):
    try:
        char_bytes = char.encode("GB18030")
    except Exception:
        return char

    if char_bytes < b"\xb0\xa1" or char_bytes > b"\xd7\xf9":
        return char
    table = OrderedDict([
        ("a", b"\xb0\xc4"),
        ("b", b"\xb2\xc0"),
        ("c", b"\xb4\xed"),
        ("d", b"\xb6\xe9"),
        ("e", b"\xb7\xa1"),
        ("f", b"\xb8\xc0"),
        ("g", b"\xb9\xfd"),
        ("h", b"\xbb\xf6"),
        ("j", b"\xbf\xa5"),
        ("k", b"\xc0\xab"),
        ("l", b"\xc2\xe7"),
        ("m", b"\xc4\xc2"),
        ("n", b"\xc5\xb5"),
        ("o", b"\xc5\xbd"),
        ("p", b"\xc6\xd9"),
        ("q", b"\xc8\xba"),
        ("r", b"\xc8\xf5"),
        ("s", b"\xcb\xf9"),
        ("t", b"\xcd\xd9"),
        ("w", b"\xce\xf3"),
        ("x", b"\xd1\xb8"),
        ("y", b"\xd4\xd0"),
        ("z", b"\xd7\xf9"),
    ])
    keys = list(table.keys())
    values = list(table.values())
    ix = bisect.bisect_left(values, char_bytes)
    return keys[ix]


@lru_cache(maxsize=1024)
def do_polyphone_match(cn_char, alpha):
    return (
        cn_char in POLYPHONE_TABLE.keys()
        and alpha in POLYPHONE_TABLE[cn_char]
    )


@lru_cache(maxsize=1024)
def do_py_match(filename, abbrev):
    if len(filename) < len(abbrev):
        return False

    for i, char in enumerate(abbrev):
        def match():
            yield char == PYFILEDIR_WILDCARD and ord(filename[i]) > 127
            yield filename[i] == char
            yield get_py(filename[i]) == char
            yield do_polyphone_match(cn_char=filename[i], alpha=char)
        if not any(match()):
            return False
    return True


def same_path(path1, path2):
    path1 = os.path.expanduser(path1)
    path1 = os.path.normpath(path1)
    path2 = os.path.expanduser(path2)
    path2 = os.path.normpath(path2)
    return path1 == path2


def as_unix_path(path):
    return path.replace(os.path.sep, "/")


def do_py_completion(path):

    path, pieces = rsplit_selection(path)
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    expanded_dirname = os.path.expanduser(dirname) or "./"

    if not os.path.exists(expanded_dirname):
        sys.exit(0)

    try:
        files = os.listdir(expanded_dirname)
    except Exception:
        sys.exit(0)

    ret = []
    for f in files:
        if do_py_match(filename=f, abbrev=basename):
            comp_path = os.path.join(dirname, f)
            ret.append(comp_path)

    if len(ret) == 1 and os.path.isdir(ret[0]) and same_path(ret[0], path):
        ret[0] = os.path.join(ret[0], "")  # add trailing slash

    ret = [as_unix_path(p) for p in ret]  # post processing path
    ret = unicode_sort(ret)
    return PYFILEDIR_CANDIDATE_SEP.join(ret[pieces])


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        print(do_py_completion(path=sys.argv[1]), end="")
