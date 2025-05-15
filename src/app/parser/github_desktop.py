from asyncio import Semaphore
from typing import List

from loguru import logger

from app.core.config import GithubDesktopSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: GithubDesktopSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET',
                                                      'https://central.github.com/deployments'
                                                      '/desktop/desktop/changelog.json',
                                                      is_json=True)

            if isinstance(data_r, List):
                for v in data_r:
                    vhlp.append(v['version'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
