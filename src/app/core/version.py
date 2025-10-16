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
    def __init__(self, pattern: str, split: int = 0, download_urls: List[str] = None, filter_expr: str = None):
        self.split = split
        self.exp = re.compile(pattern, flags=re.IGNORECASE)
        self._versions: List[Version] = []
        self.download_urls = download_urls
        self.filter_expr = filter_expr

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
        if self.filter_expr:
            return self.filter_versions(sorted(self._versions, key=lambda x: (x.major, x.minor, x.patch if x.patch else -1, x.build, x.letter),
                                               reverse=True), self.filter_expr)
        else:
            return sorted(self._versions, key=lambda x: (x.major, x.minor, x.patch if x.patch else -1, x.build, x.letter),
                          reverse=True)

    @property
    def split_versions(self) -> Mapping[str, List[Version]]:
        """返回切割后的版本号列表。

        Returns:

        """
        d = dict()

        if self.split == 1:
            for version in self.versions:
                k = f'{version.major}'

                if k not in d:
                    d[k] = []

                d[k].append(version)
        elif self.split == 2:
            for version in self.versions:
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

    @staticmethod
    def filter_versions(versions: List[Version], filter_expr: str) -> List[Version]:
        # Step 1: 解析 filter 表达式，例如 '>= 1.28.0'
        import re

        # 匹配类似 '>= 1.28.0', '<= 2.0.1', '== 1.0.0' 的表达式
        op_version_match = re.match(r'^([<>=]=?|==)\s*(\d+(\.\d+){0,2})$', filter_expr.strip())
        if not op_version_match:
            raise ValueError(f"Invalid filter expression: '{filter_expr}'. Expected format like '>= 1.28.0'")

        op, version_str, _ = op_version_match.groups()
        # 只取第一个三个部分 (major.minor.patch)，忽略更多部分
        version_parts = version_str.split('.')[:3]
        if len(version_parts) < 1:
            raise ValueError(f"Invalid version string in filter: '{version_str}'")

        try:
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            patch = int(version_parts[2]) if len(version_parts) > 2 else 0
        except ValueError:
            raise ValueError(f"Version components must be integers in filter: '{version_str}'")

        # 构造一个用于比较的目标 Version 对象（补全 minor 和 patch 为 0 如果未提供）
        target_version = Version(major=major, minor=minor, patch=patch)

        def version_to_tuple(v: Version) -> tuple:
            # 将 Version 对象转为一个元组，缺失的 minor/patch 当作 0
            major_val = v.major
            minor_val = v.minor if v.minor is not None else 0
            patch_val = v.patch if v.patch is not None else 0
            return major_val, minor_val, patch_val

        def satisfies_condition(ver: Version) -> bool:
            ver_tuple = version_to_tuple(ver)
            target_tuple = version_to_tuple(target_version)

            if op == '>=':
                return ver_tuple >= target_tuple
            elif op == '<=':
                return ver_tuple <= target_tuple
            elif op == '>':
                return ver_tuple > target_tuple
            elif op == '<':
                return ver_tuple < target_tuple
            elif op == '==':
                return ver_tuple == target_tuple
            else:
                raise ValueError(f"Unsupported operator '{op}' in filter expression '{filter_expr}'")

        # 过滤满足条件的版本
        return [ver for ver in versions if satisfies_condition(ver)]
