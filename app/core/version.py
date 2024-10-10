import re
from typing import Optional, List, Mapping, Any

from pydantic import BaseModel


class Version(BaseModel):
    major: int
    minor: Optional[int] = None
    patch: Optional[int] = None
    build: Optional[int] = None
    letter: Optional[str] = None
    version: Optional[str] = None
    year: Optional[str] = None
    month: Optional[str] = None
    day: Optional[str] = None
    other: Optional[str] = None
    raw_data: Optional[Any] = None
    raw_str: Optional[str] = None

    def __repr__(self):
        d = [f'{self.major}']

        if self.minor is not None:
            d.append(f'.{self.minor}')

        if self.patch is not None:
            d.append(f'.{self.patch}')

        if self.build is not None:
            d.append(f'.{self.build}')

        if self.letter is not None:
            d.append(f'{self.letter}')

        # if self.year is not None:
        #     d.append(f'{self.year}')
        # if self.month is not None:
        #     d.append(f'{self.month}')
        # if self.day is not None:
        #     d.append(f'{self.day}')

        return ''.join(d)


class VersionSummary(BaseModel):
    latest: Optional[Version] = None
    versions: List[Version] = ...
    downloads: Optional[List[str]] = None

    def exists(self, version: str) -> bool:
        for v in self.versions:
            if v.version == version:
                return True

        return False

    def __repr__(self):
        return f'Latest: {self.latest}, Versions: {self.versions}, Downloads: {self.downloads}'


class VersionHelper:
    def __init__(self, pattern: str, split: int = 0, download_urls: List[str] = None):
        self.split = split
        self.exp = re.compile(pattern, flags=re.IGNORECASE)
        self._versions: List[Version] = []
        self.download_urls = download_urls

    def append(self, version: str, raw_data: Any = None):
        """追加版本号。

        Args:
            version: 版本号。
            raw_data: 原数据。
        """
        m = self.exp.match(version)

        if m:
            d = m.groupdict()
            v = Version(major=d.get('major'), minor=d.get('minor', None), patch=d.get('patch', None),
                        build=d.get('build', None), letter=d.get('letter', None),
                        version=d.get('version', None), year=d.get('year', None), month=d.get('month', None),
                        day=d.get('day', None), other=d.get('other', None), raw_data=raw_data, raw_str=version)

            self._versions.append(v)

    def add_download_url(self, url: str):
        self.download_urls.append(url)

    # def unique_download_urls(self):
    #     self.download_urls = list(set(self.download_urls))

    def exists(self, version: str) -> bool:
        for v in self._versions:
            if v.version == version:
                return True

        return False

    def raw_exists(self, version: str) -> bool:
        for v in self._versions:
            if v.raw_str == version:
                return True

        return False

    @property
    def is_empty(self) -> bool:
        return len(self._versions) == 0

    @property
    def latest_version(self) -> Version:
        return self.versions[0]

    @property
    def raw_versions(self) -> List[Version]:
        return self._versions

    @property
    def versions(self) -> List[Version]:
        """返回已排序的版本号列表。

        Returns:

        """
        return sorted(self._versions, key=lambda x: (x.major, x.minor, x.patch if x.patch else -1, x.build, x.letter),
                      reverse=True)

    @property
    def split_versions(self) -> Mapping[str, List[Version]]:
        """返回切割后的版本号列表。

        Returns:

        """
        d = dict()

        if self.split == 1:
            for version in self._versions:
                k = f'{version.major}'

                if k not in d:
                    d[k] = []

                d[k].append(version)
        elif self.split == 2:
            for version in self._versions:
                if version.minor is not None:
                    k = f'{version.major}.{version.minor}'

                    if k not in d:
                        d[k] = []

                    d[k].append(version)

        if len(d) > 0:
            for k, v in d.items():
                d[k] = sorted(v, key=lambda x: (x.major, x.minor, x.patch if x.patch else 0, x.build if x.build else 0, x.letter), reverse=True)

        return d

    @property
    def summary(self) -> VersionSummary | Mapping[str, VersionSummary]:
        """返回摘要数据。

        Returns:

        """
        if self.split == 0:
            versions = self.versions  # 引用已排序的版本号数组

            return VersionSummary(latest=versions[0], versions=versions,
                                  downloads=self._format_download_link(versions[0], self.download_urls))
        else:
            d = dict()

            for k, v in self.split_versions.items():
                d[k] = VersionSummary(latest=v[0], versions=v,
                                      downloads=self._format_download_link(v[0], self.download_urls))

            return d

    @staticmethod
    def _format_download_link(latest: Version, download_urls: Optional[List[str]] = None) -> List[str]:
        d = []

        if download_urls:
            for v in download_urls:
                p = latest.model_dump(exclude_none=True)

                d.append(v.format(**p))

        return d
