import functools
import re
from collections import defaultdict
from typing import List, Optional, Mapping

from pydantic import BaseModel, Field


def is_numeric(s: Optional[str]):
    if not s:
        return False

    m = re.match(r'^\d+$', s)
    if m:
        return True
    return False


class Version(BaseModel):
    origin: str | None = Field(default=None)
    semver: str | None = Field(default=None)
    groups: dict = Field(default_factory=dict)


class VersionSplitItem(BaseModel):
    latest: str | None = Field(default=None)
    versions: List[Version] = Field(default_factory=list)


class VersionSplitLiteItem(BaseModel):
    latest: str | None = Field(default=None)
    versions: List[str | None] = Field(default_factory=list)
    download_links: List[str] = Field(default_factory=list)


class VersionHelper:
    def __init__(self, name: str, pattern: str, split_mode: int = 0, download_urls: List[str] = None, drop_none: bool = True,
                 use_semver: bool = True, *args, **kwargs):
        self._name: str = name
        self._exp = re.compile(pattern)
        self._split_mode: int = split_mode
        self._download_urls: List[str] = download_urls
        self._all_versions: List[Version] = []
        self._all_split_versions: Mapping[str, VersionSplitItem] = {}
        self._download_links: List[str] = []
        self._drop_none: bool = drop_none
        self._use_semver: bool = use_semver

    def __del__(self):
        self._all_versions = []
        self._split_mode = 0
        self._all_split_versions = {}
        self._download_links = []
        self._exp = None

    def is_match(self, v: str):
        if self._exp.match(v):
            return True
        return False

    def fetch_groups(self, v: str):
        m = self._exp.match(v)

        if m:
            return m.groupdict()

        return None

    @property
    def latest(self):
        """Get the latest SemVer version number.

        Returns:

        """
        if self._split_mode > 0:
            raise ValueError('Calling this property is not allowed in split mode. (Using foreach in split_versions property!)')

        if self._use_semver:
            return self._build_semver(self._all_versions[0])
        else:
            return self._all_versions[0].groups['version']

    @property
    def versions(self):
        """Get a list of all semantic version numbers.

        Returns:

        """
        if self._split_mode > 0:
            r = {}

            for k, v in self._all_split_versions.items():
                versions = []

                for v2 in v.versions:
                    if self._use_semver:
                        versions.append(self._build_semver(v2))
                    else:
                        versions.append(v2.groups['version'])

                download_links = []

                if self._download_urls:
                    download_links = self._build_download_links(v.versions[0], self._download_urls)

                r[k] = VersionSplitLiteItem(latest=versions[0], versions=self._remove_duplicates(versions), download_links=download_links)

            return r
        else:
            r = []

            for v in self._all_versions:
                if self._use_semver:
                    r.append(self._build_semver(v))
                else:
                    r.append(v.groups['version'])

            return self._remove_duplicates(r)

    @property
    def download_links(self) -> List[str]:
        if self._split_mode > 0:
            raise ValueError('Calling this property is not allowed in split mode. (Using foreach in split_versions property!)')

        return self._download_links

    def add_download_url(self, *urls: str):
        for url in urls:
            self._download_urls.append(url)

    def _build_semver(self, version: Version) -> Optional[str]:
        m = self._exp.match(version.origin)
        if m:
            # 剔除第一个 group 项, 因为第一项固定位 <version>
            groups = self._non_as_zero(m.groups()[1:])

            return '.'.join(groups)
        else:
            return None

    def _build_download_links(self, version: Version, download_urls: List[str]) -> List[str]:
        r = []

        for v in download_urls:
            # r.append(v.format(**version.groups))
            r.append(v.format_map(defaultdict(str, **version.groups)))

        return r

    def _remove_duplicates(self, items: List[str]) -> List[str]:
        r: List[str] = []

        for v in items:
            if v not in r:
                r.append(v)

        return r

    def add(self, v: str):
        m = self._exp.match(v)
        if m:
            groupdict = self._non_as_zero(m.groupdict())

            if 'version' not in groupdict:
                raise ValueError('The version variable does not exist in the match pattern.')

            self._all_versions.append(Version(origin=v, semver=m.group('version'), groups=groupdict))

            if self._split_mode > 0:
                if 1 == self._split_mode:  # 依据 <major> 划分
                    if 'major' not in groupdict:
                        raise ValueError('The major variable does not exist in the match pattern.')

                    key = '{}'.format(m.group('major'))
                elif 2 == self._split_mode:  # 依据 <major>.<minor> 划分
                    if 'major' not in groupdict:
                        raise ValueError('The major variable does not exist in the match pattern.')
                    if 'minor' not in groupdict:
                        raise ValueError('The minor variable does not exist in the match pattern.')

                    key = '{}.{}'.format(m.group('major'), m.group('minor'))
                else:
                    raise ValueError(f'Unsupported split mode. (split_mode={self._split_mode})')

                if key not in self._all_split_versions:
                    self._all_split_versions[key] = VersionSplitItem()

                self._all_split_versions[key].versions.append(Version(origin=v, semver=m.group('version'), groups=groupdict))

    def done(self):
        if len(self._all_versions) == 0:
            raise ValueError('The version number list cannot be empty.')

        if self._split_mode > 0:
            for k, v in self._all_split_versions.items():
                self._all_split_versions[k].versions.sort(key=functools.cmp_to_key(self._cmp_semver_version), reverse=True)
                self._all_split_versions[k].latest = self._all_split_versions[k].versions[0].semver
        else:
            self._all_versions.sort(key=functools.cmp_to_key(self._cmp_semver_version), reverse=True)

            if self._download_urls:
                self._download_links = self._build_download_links(self._all_versions[0], self._download_urls)

    def _non_as_zero(self, items: dict | tuple):
        if isinstance(items, dict):
            r = {}

            for k, v in items.items():
                if v is None:
                    if not self._drop_none:
                        r[k] = 0
                else:
                    r[k] = str(v).strip('.')

            return r
        else:
            r = []
            for v in items:
                if v is None:
                    if not self._drop_none:
                        r.append('0')
                else:
                    r.append(str(v).strip('.'))

            return tuple(r)

    def _cmp_semver_version(self, x: Version, y: Version) -> int:
        if x.semver == y.semver:
            return 0

        v1 = None
        v2 = None

        m = self._exp.match(x.origin)
        if m:
            v1 = m.groups()[1:]
            kk = []
            for n in v1:
                if is_numeric(n):
                    kk.append(int(n))
                elif n is None:
                    if not self._drop_none:
                        kk.append(0)
                else:
                    kk.append(n)
            v1 = tuple(kk)

        m = self._exp.match(y.origin)
        if m:
            v2 = m.groups()[1:]
            kk = []
            for n in v2:
                if is_numeric(n):
                    kk.append(int(n))
                elif n is None:
                    if not self._drop_none:
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
