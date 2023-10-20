import functools
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


def is_numeric(s: Optional[str]):
    if not s:
        return False

    m = re.match(r'^\d+$', s)
    if m:
        return True
    return False


class Version(BaseModel):
    origin: str = Field(default=None)
    semver: str = Field(default=None)
    groups: dict = Field(default_factory=dict)


class VersionSplitItem(BaseModel):
    latest: str = Field(default=None)
    versions: List[Version] = Field(default_factory=list)


class VersionSplitLiteItem(BaseModel):
    latest: str = Field(default=None)
    versions: List[str] = Field(default_factory=list)
    download_links: List[str] = Field(default_factory=list)


class VersionHelper:
    _versions: List[Version] = []
    _split_versions: Dict[str, VersionSplitItem] = {}
    _download_links: List[str] = []

    def __init__(self, pattern: str, split_mode: int = 0, download_urls: List[str] = None):
        self.exp = re.compile(pattern)
        self.split_mode = split_mode
        self._download_urls = download_urls

    def is_match(self, v: str):
        if self.exp.match(v):
            return True
        return False

    @property
    def latest(self):
        if self.split_mode > 0:
            raise ValueError('Calling this property is not allowed in split mode. (Using foreach in split_versions property!)')

        return self._build_semver(self._versions[0])

    @property
    def versions(self):
        if self.split_mode > 0:
            return self.split_versions
        else:
            r = []

            for v in self._versions:
                r.append(self._build_semver(v))

            return r

    @property
    def download_links(self) -> List[str]:
        if self.split_mode > 0:
            raise ValueError('Calling this property is not allowed in split mode. (Using foreach in split_versions property!)')

        return self._download_links

    @property
    def split_versions(self) -> Dict[str, VersionSplitLiteItem]:
        r = {}

        for k, v in self._split_versions.items():
            versions = []

            for v2 in v.versions:
                versions.append(self._build_semver(v2))

            download_links = []

            if self._download_urls:
                download_links = self._build_download_links(v.versions[0], self._download_urls)

            r[k] = VersionSplitLiteItem(latest=versions[0], versions=versions, download_links=download_links)

        return r

    def _build_semver(self, version: Version) -> Optional[str]:
        m = self.exp.match(version.origin)
        if m:
            # 剔除第一个 group 项, 因为第一项固定位 <version>
            groups = m.groups()[1:]

            return '.'.join(groups)
        else:
            return None

    def _build_download_links(self, version: Version, download_urls: List[str]) -> List[str]:
        r = []

        for v in download_urls:
            r.append(v.format(**version.groups))

        return r

    def add(self, v: str):
        m = self.exp.match(v)
        if m:
            groupdict = m.groupdict()

            if 'version' not in groupdict:
                raise ValueError('The version variable does not exist in the match pattern.')

            self._versions.append(Version(origin=v, semver=m.group('version'), groups=groupdict))

            if self.split_mode > 0:
                if 1 == self.split_mode:  # 依据 <major> 划分
                    if 'major' not in groupdict:
                        raise ValueError('The major variable does not exist in the match pattern.')

                    key = '{}'.format(m.group('major'))
                elif 2 == self.split_mode:  # 依据 <major>.<minor> 划分
                    if 'major' not in groupdict:
                        raise ValueError('The major variable does not exist in the match pattern.')
                    if 'minor' not in groupdict:
                        raise ValueError('The minor variable does not exist in the match pattern.')

                    key = '{}.{}'.format(m.group('major'), m.group('minor'))
                else:
                    raise ValueError(f'Unsupported split mode. (split_mode={self.split_mode})')

                if key not in self._split_versions:
                    self._split_versions[key] = VersionSplitItem()

                self._split_versions[key].versions.append(Version(origin=v, semver=m.group('version'), groups=groupdict))

    def done(self):
        if self.split_mode > 0:
            for k, v in self._split_versions.items():
                self._split_versions[k].versions.sort(key=functools.cmp_to_key(self._cmp_semver_version), reverse=True)
                self._split_versions[k].latest = self._split_versions[k].versions[0].semver
        else:
            self._versions.sort(key=functools.cmp_to_key(self._cmp_semver_version), reverse=True)

            if self._download_urls:
                self._download_links = self._build_download_links(self._versions[0], self._download_urls)

    def _cmp_semver_version(self, x: Version, y: Version) -> int:
        if x.semver == y.semver:
            return 0

        v1 = None
        v2 = None

        m = self.exp.match(x.origin)
        if m:
            v1 = m.groups()[1:]
            kk = []
            for n in v1:
                if is_numeric(n):
                    kk.append(int(n))
                elif n is None:
                    kk.append(0)
                else:
                    kk.append(n)
            v1 = tuple(kk)

        m = self.exp.match(y.origin)
        if m:
            v2 = m.groups()[1:]
            kk = []
            for n in v2:
                if is_numeric(n):
                    kk.append(int(n))
                elif n is None:
                    kk.append(0)
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


class VersionParser:
    def __init__(self, pattern: str):
        self.exp = re.compile(pattern)

    def is_match(self, s: str) -> bool:
        if self.exp.match(s):
            return True
        return False

    def latest(self, items: List[str]):
        m = self.exp.match(max(items, key=functools.cmp_to_key(self.cmp_version)))
        if m:
            return m.group('version').replace('_', '.')

        return None

    def clean(self, items: List[str]) -> List[str]:
        r = []
        for v in items:
            m = self.exp.match(v)
            if m:
                r.append(m.group('version').replace('_', '.'))

        # r.sort(key=functools.cmp_to_key(self.cmp_version), reverse=True)

        return r

    def split(self, items: List[str], only_major: bool = False) -> dict[str, list]:
        r = dict()

        for v in items:
            m = self.exp.match(v)

            if m:
                if only_major:
                    key = m.group('major')
                else:
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
                elif n is None:
                    kk.append(0)
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
                elif n is None:
                    kk.append(0)
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
