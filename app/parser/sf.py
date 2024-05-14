from asyncio import Semaphore
from pathlib import Path
from typing import Mapping

from loguru import logger
from pydantic import BaseModel

from app.core.config import SourceForgeSoftware
from app.core.version import VersionHelper
from . import Base


class SFPlatformRelease(BaseModel):
    filename: str


class SourceForgeBestRelease(BaseModel):
    platform_releases: Mapping[str, SFPlatformRelease]


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: SourceForgeSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET',
                                                      f'https://sourceforge.net/'
                                                      f'projects/{soft.project}/best_release.json',
                                                      is_json=True)

            sf = SourceForgeBestRelease.model_validate(data_r)
            win = sf.platform_releases.get('windows')

            if win:
                vhlp.append(Path(win.filename).name)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
