import re
from typing import Optional, List, Tuple, Mapping, Any

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
        if not filter_expr.strip():
            return versions  # 如果没有 filter，返回全部

        # Step 1: 拆分多个条件，例如 ">=1.28.0, <2.0.0" -> ['>=1.28.0', '<2.0.0']
        sub_conditions = [cond.strip() for cond in filter_expr.split(',') if cond.strip()]

        # Step 2: 解析每一个子条件，得到 (operator, (major, minor, patch))
        parsed_conditions = []
        for cond in sub_conditions:
            import re
            # 匹配操作符（>=, <=, >, <, ==）以及版本号（如 1.28.0, 1.0, 2 等）
            match = re.match(r'^([<>=]=?|==)\s+(\d+(\.\d+){0,2})$', cond)
            if not match:
                raise ValueError(f"Invalid filter condition: '{cond}'. Expected format like '>=1.28.0' or '<2.0.0'")

            op, version_str, _ = match.groups()
            version_parts = version_str.split('.')[:3]  # 最多取 major.minor.patch
            if not version_parts:
                raise ValueError(f"Invalid version in condition: '{version_str}'")

            try:
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                patch = int(version_parts[2]) if len(version_parts) > 2 else 0
            except ValueError:
                raise ValueError(f"Version numbers must be integers in condition: '{version_str}'")

            target = Version(major=major, minor=minor, patch=patch)
            parsed_conditions.append((op, target))

        # Step 3: 定义一个函数，将 Version 转为可比较的三元组 (major, minor, patch)，缺失字段补 0
        def version_to_tuple(v: Version) -> Tuple[int, int, int]:
            _major = v.major
            _minor = v.minor if v.minor is not None else 0
            _patch = v.patch if v.patch is not None else 0
            return _major, _minor, _patch

        # Step 4: 定义一个函数，判断单个 Version 是否满足单个条件 (op, target)
        def matches_condition(_ver: Version, _op: str, _target: Version) -> bool:
            ver_tuple = version_to_tuple(_ver)
            target_tuple = version_to_tuple(_target)

            if _op == '>':
                return ver_tuple > target_tuple
            elif _op == '<':
                return ver_tuple < target_tuple
            elif _op == '>=':
                return ver_tuple >= target_tuple
            elif _op == '<=':
                return ver_tuple <= target_tuple
            elif _op == '==':
                return ver_tuple == target_tuple
            else:
                raise ValueError(f"Unsupported operator '{_op}' in condition")

        # Step 5: 过滤：保留所有满足全部条件的版本
        result = []
        for ver in versions:
            try:
                # 检查该版本是否满足所有子条件
                all_match = all(
                    matches_condition(ver, op, target)
                    for op, target in parsed_conditions
                )
                if all_match:
                    result.append(ver)
            except Exception as e:
                # 如果出现意外错误（比如版本字段为 None 但未处理），可根据需求决定是否跳过或报错
                raise ValueError(f"Error evaluating version {ver}: {e}")

        return result
