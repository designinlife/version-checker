from asyncio import Semaphore

from loguru import logger

from app.core.config import AndroidStudioSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: AndroidStudioSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        # See <https://plugins.jetbrains.com/docs/intellij/android-studio-releases-list.html>

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET', 'https://jb.gg/android-studio-releases-list.json',
                                                      is_json=True)

            if isinstance(data_r, dict) and 'content' in data_r:
                for v in data_r['content']['item']:
                    if v['channel'] == 'Release':
                        vhlp.append(v['version'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
