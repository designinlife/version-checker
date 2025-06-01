from typing import Optional, List, Literal, Any

from pydantic import BaseModel, Field, ConfigDict


class AppSettingBase(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None


class AppSettingSoftItem(BaseModel):
    name: str = ...
    display_name: Optional[str] = None
    url: Optional[str] = None
    pattern: Optional[str] = Field(default=None)
    split: int = Field(default=0)
    disabled: bool = Field(default=False)
    download_dynamic: bool = Field(default=False, description='动态生成下载地址')
    download_urls: List[str] = Field(default_factory=list)
    condition: Optional[str] = None  # 条件表达式: major >= 6 && minor < 5 或 major >= 6


class GithubSoftware(AppSettingSoftItem):
    parser: Literal['gh'] = Field(default='gh')
    repo: str
    release: bool = Field(default=False)  # 当设置为 True 时, 按 /releases API 获取数据。否则，按 /tags API 获取。
    latest: bool = Field(default=False)  # 仅获取最新版本 (API: /releases/latest)
    assets: bool = Field(default=False)
    assets_patterns: List[str] = Field(default_factory=list)
    max_page: int = Field(default=1)
    page_size: int = Field(default=100)


class GitlabSoftware(AppSettingSoftItem):
    parser: Literal['gitlab']
    id: int
    release: bool = Field(default=False)
    by_tag_name: bool = Field(default=False)
    host: str = Field(default='gitlab.com')


class CodebergSoftware(AppSettingSoftItem):
    parser: Literal['codeberg']
    repo: str
    host: str = Field(default='codeberg.org')
    release: bool = Field(default=False)
    latest: bool = Field(default=False)
    assets: bool = Field(default=False)
    assets_patterns: List[str] = Field(default_factory=list)
    max_page: int = Field(default=1)


class GoSoftware(AppSettingSoftItem):
    parser: Literal['go']


class PhpSoftware(AppSettingSoftItem):
    parser: Literal['php']
    major: List[int]


class ApacheFlumeSoftware(AppSettingSoftItem):
    parser: Literal['apache-flume']


class NodeJsSoftware(AppSettingSoftItem):
    parser: Literal['nodejs']


class VirtualBoxSoftware(AppSettingSoftItem):
    parser: Literal['virtualbox']


class IndexSoftware(AppSettingSoftItem):
    parser: Literal['index']


class DotNetSoftware(AppSettingSoftItem):
    parser: Literal['dotnet']


class DotNetFxSoftware(AppSettingSoftItem):
    parser: Literal['dotnetfx']


class SublimeSoftware(AppSettingSoftItem):
    parser: Literal['sublime']


class XShellSoftware(AppSettingSoftItem):
    parser: Literal['xshell']


class FlutterSoftware(AppSettingSoftItem):
    parser: Literal['flutter']


class DartSoftware(AppSettingSoftItem):
    parser: Literal['dart']


class AndroidStudioSoftware(AppSettingSoftItem):
    parser: Literal['android-studio']


class FirefoxSoftware(AppSettingSoftItem):
    parser: Literal['firefox']


class ChromeSoftware(AppSettingSoftItem):
    parser: Literal['chrome']


class GithubDesktopSoftware(AppSettingSoftItem):
    parser: Literal['github-desktop']


class JetbrainsSoftware(AppSettingSoftItem):
    parser: Literal['jetbrains']
    code: List[str] = Field(default_factory=list)
    os: List[str] = Field(default_factory=list)


class JetbrainsPluginSoftware(AppSettingSoftItem):
    parser: Literal['jetbrains-plugin']
    plugin_id: int
    size: int = 5


class SourceForgeSoftware(AppSettingSoftItem):
    parser: Literal['sf']
    project: str


class AlmaLinuxSoftware(AppSettingSoftItem):
    parser: Literal['almalinux']


class RockyLinuxSoftware(AppSettingSoftItem):
    parser: Literal['rockylinux']


class NavicatSoftware(AppSettingSoftItem):
    parser: Literal['navicat']


class HAProxySoftware(AppSettingSoftItem):
    parser: Literal['haproxy']


class DockerHubSoftware(AppSettingSoftItem):
    parser: Literal['docker-hub']
    name: Optional[str] = None
    repo: str = ...
    fixed_tags: List[str] = Field(default_factory=list)
    max_page: int = Field(default=1)

    def model_post_init(self, __context: Any) -> None:
        if self.name is None:
            self.name = self.repo


class AppSetting(BaseModel):
    app: Optional[AppSettingBase] = None
    softwares: List[ApacheFlumeSoftware | NodeJsSoftware | VirtualBoxSoftware
                    | GoSoftware | PhpSoftware | GithubSoftware | GithubDesktopSoftware | GitlabSoftware | CodebergSoftware
                    | DotNetFxSoftware | DotNetSoftware | ChromeSoftware | JetbrainsSoftware | JetbrainsPluginSoftware | FirefoxSoftware
                    | SublimeSoftware | XShellSoftware | AndroidStudioSoftware | SourceForgeSoftware
                    | FlutterSoftware | DartSoftware | NavicatSoftware | HAProxySoftware | DockerHubSoftware
                    | AlmaLinuxSoftware | RockyLinuxSoftware | IndexSoftware] = Field(alias='softwares',
                                                                                      default_factory=list)


class Configuration(BaseModel):
    # model_config = ConfigDict(from_attributes=True)

    config_file: Optional[str] = Field(default=None)
    slient: bool = Field(default=False)
    debug: bool = Field(default=False)
    log: Optional[str] = Field(default=None)
    disable_log_time: bool = Field(default=False)
    verbose: int = Field(default=0)
    workdir: Optional[str] = Field(default=None)
    settings: AppSetting = Field(default_factory=AppSetting)


class OutputResult(BaseModel):
    name: str
    url: str
    display_name: Optional[str] = None
    latest: str | None = Field(default=None)
    versions: List[str | None] = Field(default_factory=list)
    storage_dir: Optional[str] = None
    download_urls: List[str] = Field(default_factory=list)
    created_time: str
    jbp_extra: dict | None = Field(default=None, alias='jbp_extra')
