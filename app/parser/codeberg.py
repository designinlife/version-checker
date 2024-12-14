from asyncio import Semaphore
from typing import List

from loguru import logger

from app.core.config import CodebergSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: CodebergSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            if soft.release:
                api_url = f'https://codeberg.org/api/v1/repos/{soft.repo}/releases'
            else:
                api_url = f'https://codeberg.org/api/v1/repos/{soft.repo}/tags'

            _, status, _, data_r = await self.request('GET', api_url, is_json=True)

            if isinstance(data_r, List):
                for v in data_r:
                    if soft.release:
                        vhlp.append(v['tag_name'])
                    else:
                        vhlp.append(v['name'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
