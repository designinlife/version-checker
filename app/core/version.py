import functools
import re
from typing import List


class VersionParser:
    _suffix: bool = False

    def __init__(self, pattern: str):
        self.exp = re.compile(pattern)

        if '{suffix}' in pattern:
            self._suffix = True

    def latest(self, items: List[str]):
        items.sort(key=functools.cmp_to_key(self.cmp_version))

        return items[0]

    def cmp_version(self, x: str, y: str) -> int:
        if x == y:
            return 0

        m = self.exp.match(x)
        if m:
            if self._suffix:
                v1 = (int(m.group('major')), int(m.group('minor')), int(m.group('patch')), m.group('suffix'))
            else:
                v1 = (int(m.group('major')), int(m.group('minor')), int(m.group('patch')), m.group('suffix'))
        else:
            if self._suffix:
                v1 = (0, 0, 0, None)
            else:
                v1 = (0, 0, 0)

        m = self.exp.match(y)
        if m:
            if self._suffix:
                v2 = (int(m.group('major')), int(m.group('minor')), int(m.group('patch')), m.group('suffix'))
            else:
                v2 = (int(m.group('major')), int(m.group('minor')), int(m.group('patch')), m.group('suffix'))
        else:
            if self._suffix:
                v2 = (0, 0, 0, None)
            else:
                v2 = (0, 0, 0)

        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
