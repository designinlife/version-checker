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


class AppSetting(BaseModel):
    app: Optional[AppSettingBase] = None
    softwares: List[ApacheFlumeSoftware | NodeJsSoftware | VirtualBoxSoftware
                    | GoSoftware | PhpSoftware | GithubSoftware
                    | DotNetFxSoftware | DotNetSoftware
                    | SublimeSoftware | XShellSoftware | AndroidStudioSoftware
                    | FlutterSoftware | DartSoftware] = Field(alias='softwares',
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
