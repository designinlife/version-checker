from __future__ import annotations

import json
from typing import List, Optional

from pydantic import BaseModel, Field

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class ReleasesIndexItem(BaseModel):
    channel_version: str = Field(..., alias='channel-version')
    latest_release: str = Field(..., alias='latest-release')
    latest_release_date: str = Field(..., alias='latest-release-date')
    security: bool
    latest_runtime: str = Field(..., alias='latest-runtime')
    latest_sdk: str = Field(..., alias='latest-sdk')
    product: str
    release_type: str = Field(..., alias='release-type')
    support_phase: str = Field(..., alias='support-phase')
    eol_date: Optional[str] = Field(..., alias='eol-date')
    releases_json: str = Field(..., alias='releases.json')


class Model(BaseModel):
    schema: str = Field(..., alias='$schema')
    releases_index: List[ReleasesIndexItem] = Field(..., alias='releases-index')


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://raw.githubusercontent.com/dotnet/core/main/release-notes/releases-index.json')

        data_r = json.loads(data_s)
        dotnet_release = Model.model_validate(data_r)
        print(dotnet_release)

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://dart.dev/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
