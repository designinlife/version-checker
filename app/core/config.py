from typing import Optional, List

from pydantic import BaseModel, Field


class AppSettingBase(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None


class AppSettingSoftItem(BaseModel):
    name: str = Field()
    code: Optional[str] = Field(default=None)
    repo: Optional[str] = Field(default=None)
    download_urls: List[str] = Field(default_factory=list)
    dynamic_links: bool = Field(default=False)
    parser: Optional[str] = Field(default='gh')
    split_mode: int = Field(default=0)
    tag_pattern: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    major: List[int] = Field(default_factory=list)
    by_release: bool = Field(default=False)
    by_release_name: bool = Field(default=False)
    by_tag: Optional[str] = Field(default=None)
    disabled: bool = Field(default=False)


class AppSetting(BaseModel):
    app: Optional[AppSettingBase] = None
    softwares: List[AppSettingSoftItem] = Field(alias='softwares', default_factory=list)


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
