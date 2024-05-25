from typing import Optional, List, Literal

from pydantic import BaseModel, Field


class AppSettingBase(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None


class AppSettingSoftItem(BaseModel):
    name: str = ...
    url: Optional[str] = None
    pattern: Optional[str] = Field(default=None)
    split: int = Field(default=0)
    disabled: bool = Field(default=False)
    download_dynamic: bool = Field(default=False, description='动态生成下载地址')
    download_urls: List[str] = Field(default_factory=list)


class GithubSoftware(AppSettingSoftItem):
    parser: Literal['gh'] = Field(default='gh')
    repo: str
    release: bool = Field(default=False)
    assets: bool = Field(default=False)
    max_page: int = Field(default=1)


class GitlabSoftware(AppSettingSoftItem):
    parser: Literal['gitlab']
    id: int
    release: bool = Field(default=False)
    by_tag_name: bool = Field(default=False)
    host: str = Field(default='gitlab.com')


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


class SourceForgeSoftware(AppSettingSoftItem):
    parser: Literal['sf']
    project: str


class AlmaLinuxSoftware(AppSettingSoftItem):
    parser: Literal['almalinux']


class RockyLinuxSoftware(AppSettingSoftItem):
    parser: Literal['rockylinux']


class AppSetting(BaseModel):
    app: Optional[AppSettingBase] = None
    softwares: List[ApacheFlumeSoftware | NodeJsSoftware | VirtualBoxSoftware
                    | GoSoftware | PhpSoftware | GithubSoftware | GithubDesktopSoftware | GitlabSoftware
                    | DotNetFxSoftware | DotNetSoftware | ChromeSoftware | JetbrainsSoftware | FirefoxSoftware
                    | SublimeSoftware | XShellSoftware | AndroidStudioSoftware | SourceForgeSoftware
                    | FlutterSoftware | DartSoftware
                    | AlmaLinuxSoftware | RockyLinuxSoftware] = Field(alias='softwares',
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
    latest: str | None = Field(default=None)
    versions: List[str | None] = Field(default_factory=list)
    download_urls: List[str] = Field(default_factory=list)
    created_time: str
