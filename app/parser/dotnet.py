import asyncio
import json
from asyncio import Semaphore
from typing import Optional, List

import arrow
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import DotNetSoftware
from app.core.version import VersionHelper
from . import Base


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
    eol_date: Optional[str] | None = Field(default=None, alias='eol-date')
    releases_json: str = Field(..., alias='releases.json')


class Model(BaseModel):
    # schema: str = Field(..., alias='$schema')
    releases_index: List[ReleasesIndexItem] = Field(..., alias='releases-index')


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: DotNetSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        async with sem:
            # Make an HTTP request.
            _, status, _, data_s = await self.request('GET',
                                                      'https://raw.githubusercontent.com/dotnet/core/main'
                                                      '/release-notes/releases-index.json',
                                                      is_json=False)

            data_r = json.loads(data_s)
            dotnet_release = Model.model_validate(data_r)

        # Make a batch request.
        tasks = []

        for v in dotnet_release.releases_index:
            if v.release_type in ('lts',):
                # if v.release_type in ('lts',) and v.eol_date is not None and arrow.get(v.eol_date,
                #                                                                        'YYYY-MM-DD') > arrow.now():
                tasks.append(self.request('GET', v.releases_json, is_json=True))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Iterate over a list of versions
        if isinstance(results, list):
            for _, _, _, v in results:
                vhlp = VersionHelper(pattern=soft.pattern, split=0, download_urls=[])

                for v2 in v['releases']:
                    vhlp.append(v2['release-version'])

                    # Runtime download links.
                    if 'runtime' in v2 and v2['runtime']['version'] == v['latest-runtime']:
                        for v3 in v2['runtime']['files']:
                            if 'win-x64.exe' in v3['url'] or 'linux-x64.tar.gz' in v3['url']:
                                vhlp.add_download_url(v3['url'])

                    # SDK download links.
                    if 'sdk' in v2 and v2['sdk']['version'] == v['latest-sdk']:
                        for v3 in v2['sdk']['files']:
                            if 'win-x64.exe' in v3['url'] or 'linux-x64.tar.gz' in v3['url']:
                                vhlp.add_download_url(v3['url'])

                    # Windows Desktop download links.
                    if 'windowsdesktop' in v2 and v2['windowsdesktop']['version'] == v['latest-runtime']:
                        for v3 in v2['windowsdesktop']['files']:
                            if 'win-x64.exe' in v3['url'] or 'linux-x64.tar.gz' in v3['url']:
                                vhlp.add_download_url(v3['url'])

                logger.debug(
                    f'Name: {soft.name}-{v['channel-version']}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

                # Write data to file.
                vlatest = vhlp.versions[0]

                await self.write(soft, vhlp.summary, suffix=f'-{vlatest.major}.{vlatest.minor}')
