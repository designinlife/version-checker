import functools
import re
from typing import List, Optional


def is_numeric(s: Optional[str]):
    if not s:
        return False

    m = re.match(r'^\d+$', s)
    if m:
        return True
    return False


class VersionParser:
    def __init__(self, pattern: str):
        self.exp = re.compile(pattern)

    def latest(self, items: List[str]):
        m = self.exp.match(max(items, key=functools.cmp_to_key(self.cmp_version)))
        if m:
            return m.group('version')

        return None

    def semver_split(self, items: List[str]) -> dict[str, list]:
        r = dict()

        for v in items:
            m = self.exp.match(v)

            if m:
                key = '{}.{}'.format(m.group('major'), m.group('minor'))

                if key not in r:
                    r[key] = []

                # r[key].append(m.group('version'))
                r[key].append(v)

        return r

    def cmp_version(self, x: str, y: str) -> int:
        if x == y:
            return 0

        v1 = None
        v2 = None

        m = self.exp.match(x)
        if m:
            v1 = m.groups()[1:]
            kk = []
            for n in v1:
                if is_numeric(n):
                    kk.append(int(n))
                else:
                    kk.append(n)
            v1 = tuple(kk)

        m = self.exp.match(y)
        if m:
            v2 = m.groups()[1:]
            kk = []
            for n in v2:
                if is_numeric(n):
                    kk.append(int(n))
                else:
                    kk.append(n)
            v2 = tuple(kk)

        if v1 and v2:
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            else:
                return 0
        else:
            return -1