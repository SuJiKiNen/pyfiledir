#!/usr/bin/env python

import locale
import os
import sys
from functools import lru_cache

SEP = "\n"

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
def get_py(s):
    try:
        char = s.encode("GB18030")
    except Exception:
        return s
    if char < b"\xb0\xa1":
        return s
    if char > b"\xd7\xf9":
        return "?"
    if char < b"\xb0\xc5":
        return "a"
    if char < b"\xb2\xc1":
        return "b"
    if char < b"\xb4\xee":
        return "c"
    if char < b"\xb6\xea":
        return "d"
    if char < b"\xb7\xa2":
        return "e"
    if char < b"\xb8\xc1":
        return "f"
    if char < b"\xb9\xfe":
        return "g"
    if char < b"\xbb\xf7":
        return "h"
    if char < b"\xbf\xa6":
        return "j"
    if char < b"\xc0\xac":
        return "k"
    if char < b"\xc2\xe8":
        return "l"
    if char < b"\xc4\xc3":
        return "m"
    if char < b"\xc5\xb6":
        return "n"
    if char < b"\xc5\xbe":
        return "o"
    if char < b"\xc6\xda":
        return "p"
    if char < b"\xc8\xbb":
        return "q"
    if char < b"\xc8\xf6":
        return "r"
    if char < b"\xcb\xfa":
        return "s"
    if char < b"\xcd\xda":
        return "t"
    if char < b"\xce\xf4":
        return "w"
    if char < b"\xd1\xb9":
        return "x"
    if char < b"\xd4\xd1":
        return "y"
    if char < b"\xd7\xfa":
        return "z"
    return s


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
    return SEP.join(ret[pieces])


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        print(do_py_completion(path=sys.argv[1]), end="")
