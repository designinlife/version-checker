from __future__ import annotations

import asyncio
import json
import os
from typing import List, Optional

import aiohttp
import arrow
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
    # schema: str = Field(..., alias='$schema')
    releases_index: List[ReleasesIndexItem] = Field(..., alias='releases-index')


class Parser:
    @staticmethod
    async def get(session: aiohttp.ClientSession, url: str):
        async with session.get(url, proxy=os.environ.get('PROXY')) as response:
            return await response.json()

    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Make an HTTP request.
        url, http_status_code, _, data_s = await assist.get('https://raw.githubusercontent.com/dotnet/core/main/release-notes/releases-index.json')

        data_r = json.loads(data_s)
        dotnet_release = Model.model_validate(data_r)

        # Make a batch request.
        tasks = []

        async with aiohttp.ClientSession() as session:
            for v in dotnet_release.releases_index:
                if v.release_type in ('lts', 'sts') and v.eol_date is not None and arrow.get(v.eol_date, 'YYYY-MM-DD') > arrow.now():
                    tasks.append(Parser.get(session, v.releases_json))

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Iterate over a list of versions
        if isinstance(results, list):
            for v in results:
                download_links = []

                # Create VersionHelper instance.
                vhlp = VersionHelper(name=item.name, pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$',
                                     download_urls=item.download_urls)

                for v2 in v['releases']:
                    vhlp.add(v2['release-version'])

                    # Runtime download links.
                    if v2['runtime']['version'] == v['latest-runtime']:
                        for v3 in v2['runtime']['files']:
                            download_links.append(v3['url'])
                    # SDK download links.
                    if v2['sdk']['version'] == v['latest-sdk']:
                        for v3 in v2['sdk']['files']:
                            download_links.append(v3['url'])
                    # Windows Desktop download links.
                    if v2['windowsdesktop']['version'] == v['latest-runtime']:
                        for v3 in v2['sdk']['files']:
                            download_links.append(v3['url'])

                # Perform actions such as sorting.
                vhlp.done()

                # Output JSON file.
                await assist.create(name=f'{item.name}-{v["channel-version"]}',
                                    url=item.url if item.url else 'https://dotnet.microsoft.com/',
                                    version=vhlp.latest,
                                    all_versions=vhlp.versions,
                                    download_links=download_links)
