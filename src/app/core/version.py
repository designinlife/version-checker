import re
from typing import Any, List, Mapping, Optional, Tuple

from pydantic import BaseModel


class Version(BaseModel):
    """正则命名组解析后的版本对象，保留原始字符串和解析器附带的原始数据。"""

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
        d = [f"{self.major}"]

        if self.minor is not None:
            d.append(f".{self.minor}")

        if self.patch is not None:
            d.append(f".{self.patch}")

        if self.build is not None:
            d.append(f".{self.build}")

        if self.letter is not None:
            d.append(f"{self.letter}")

        # if self.year is not None:
        #     d.append(f'{self.year}')
        # if self.month is not None:
        #     d.append(f'{self.month}')
        # if self.day is not None:
        #     d.append(f'{self.day}')

        return "".join(d)


class VersionSummary(BaseModel):
    """单个软件或拆分分组的版本摘要。"""

    latest: Optional[Version] = None
    versions: List[Version] = ...
    downloads: Optional[List[str]] = None

    def exists(self, version: str) -> bool:
        """检查摘要版本列表中是否存在指定完整版本号。"""
        for v in self.versions:
            if v.version == version:
                return True

        return False

    def __repr__(self):
        return f"Latest: {self.latest}, Versions: {self.versions}, Downloads: {self.downloads}"


class VersionHelper:
    """负责把远端版本字符串解析为 Version、排序、过滤并生成下载地址。"""

    def __init__(self, pattern: str, split: int = 0, download_urls: List[str] = None, filter_expr: str = None):
        self.split = split
        self.exp = re.compile(pattern, flags=re.IGNORECASE)
        self._versions: List[Version] = []
        self.download_urls = download_urls or []
        self.filter_expr = filter_expr

    def append(self, version: str, raw_data: Any = None):
        """按配置正则解析并追加版本；不匹配的字符串会被静默忽略。"""
        m = self.exp.match(version)

        if m:
            d = m.groupdict()
            v = Version(
                major=d.get("major"),
                minor=d.get("minor", None),
                patch=d.get("patch", None),
                build=d.get("build", None),
                letter=d.get("letter", None),
                version=d.get("version", None),
                year=d.get("year", None),
                month=d.get("month", None),
                day=d.get("day", None),
                other=d.get("other", None),
                raw_data=raw_data,
                raw_str=version,
            )

            self._versions.append(v)

    def add_download_url(self, url: str):
        """追加下载地址并保持列表去重。"""
        if url not in self.download_urls:
            self.download_urls.append(url)

    def exists(self, version: str) -> bool:
        """检查原始解析列表中是否存在指定完整版本号。"""
        for v in self._versions:
            if v.version == version:
                return True

        return False

    def raw_exists(self, version: str) -> bool:
        """检查原始解析列表中是否存在指定远端原始版本字符串。"""
        for v in self._versions:
            if v.raw_str == version:
                return True

        return False

    @property
    def is_empty(self) -> bool:
        """返回是否尚未解析到任何版本。"""
        return len(self._versions) == 0

    @property
    def latest_version(self) -> Version:
        """返回排序和过滤后的第一个版本。"""
        return self.versions[0]

    @property
    def raw_versions(self) -> List[Version]:
        """返回未排序、未过滤的原始解析结果。"""
        return self._versions

    @property
    def versions(self) -> List[Version]:
        """返回按数字版本倒序排列、并按 filter 表达式过滤后的版本列表。"""
        if self.filter_expr:
            return self.filter_versions(sorted(self._versions, key=self._sort_key, reverse=True), self.filter_expr)
        else:
            return sorted(self._versions, key=self._sort_key, reverse=True)

    @staticmethod
    def _sort_key(version: Version) -> tuple[int, int, int, int, str]:
        """把可选版本段规整为稳定排序键，缺失数字段低于显式数字段。"""
        return (
            version.major,
            version.minor if version.minor is not None else -1,
            version.patch if version.patch is not None else -1,
            version.build if version.build is not None else -1,
            version.letter or "",
        )

    @property
    def split_versions(self) -> Mapping[str, List[Version]]:
        """按 split 配置把版本列表拆为主版本或主次版本分组。"""
        d = dict()

        if self.split == 1:
            for version in self.versions:
                k = f"{version.major}"

                if k not in d:
                    d[k] = []

                d[k].append(version)
        elif self.split == 2:
            for version in self.versions:
                if version.minor is not None:
                    k = f"{version.major}.{version.minor}"

                    if k not in d:
                        d[k] = []

                    d[k].append(version)

        if len(d) > 0:
            for k, v in d.items():
                d[k] = sorted(v, key=self._sort_key, reverse=True)

        return d

    @property
    def summary(self) -> VersionSummary | Mapping[str, VersionSummary]:
        """生成写出 JSON 所需的摘要数据；拆分模式会返回分组到摘要的映射。"""
        if self.split == 0:
            versions = self.versions  # 引用已排序的版本号数组

            if not versions:
                raise ValueError("No versions matched the configured pattern.")

            return VersionSummary(
                latest=versions[0], versions=versions, downloads=self._format_download_link(versions[0], self.download_urls)
            )
        else:
            d = dict()
            split_versions = self.split_versions

            if not split_versions:
                raise ValueError("No versions matched the configured pattern.")

            for k, v in split_versions.items():
                d[k] = VersionSummary(latest=v[0], versions=v, downloads=self._format_download_link(v[0], self.download_urls))

            return d

    @staticmethod
    def _format_download_link(latest: Version, download_urls: Optional[List[str]] = None) -> List[str]:
        """使用 latest 的非空字段格式化下载地址模板，例如 `{version}`、`{major}`。"""
        d = []

        if download_urls:
            for v in download_urls:
                p = latest.model_dump(exclude_none=True)

                d.append(v.format(**p))

        return d

    @staticmethod
    def filter_versions(versions: List[Version], filter_expr: str) -> List[Version]:
        """按逗号分隔的范围表达式过滤版本，支持 >、>=、<、<=、==。

        表达式中的版本最多比较 major/minor/patch 三段；缺失段按 0 处理。
        """
        if not filter_expr.strip():
            return versions

        sub_conditions = [cond.strip() for cond in filter_expr.split(",") if cond.strip()]

        parsed_conditions = []
        for cond in sub_conditions:
            import re

            match = re.match(r"^([<>=]=?|==)\s*(\d+(\.\d+){0,2})$", cond)
            if not match:
                raise ValueError(f"Invalid filter condition: '{cond}'. Expected format like '>=1.28.0' or '<2.0.0'")

            op, version_str, _ = match.groups()
            version_parts = version_str.split(".")[:3]
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

        def version_to_tuple(v: Version) -> Tuple[int, int, int]:
            """把版本对象规整为三段数字元组，便于范围比较。"""
            _major = v.major
            _minor = v.minor if v.minor is not None else 0
            _patch = v.patch if v.patch is not None else 0
            return _major, _minor, _patch

        def matches_condition(_ver: Version, _op: str, _target: Version) -> bool:
            """判断单个版本是否满足一个已解析的比较条件。"""
            ver_tuple = version_to_tuple(_ver)
            target_tuple = version_to_tuple(_target)

            if _op == ">":
                return ver_tuple > target_tuple
            elif _op == "<":
                return ver_tuple < target_tuple
            elif _op == ">=":
                return ver_tuple >= target_tuple
            elif _op == "<=":
                return ver_tuple <= target_tuple
            elif _op == "==":
                return ver_tuple == target_tuple
            else:
                raise ValueError(f"Unsupported operator '{_op}' in condition")

        result = []
        for ver in versions:
            try:
                all_match = all(matches_condition(ver, op, target) for op, target in parsed_conditions)
                if all_match:
                    result.append(ver)
            except Exception as e:
                raise ValueError(f"Error evaluating version {ver}: {e}")

        return result
