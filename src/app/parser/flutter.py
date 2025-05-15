from asyncio import Semaphore

from loguru import logger

from app.core.config import FlutterSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: FlutterSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET', 'https://storage.googleapis.com/'
                                                             'flutter_infra_release/releases/releases_windows.json',
                                                      is_json=True)

            if isinstance(data_r, dict) and 'releases' in data_r:
                for v in data_r['releases']:
                    if v['channel'] == 'stable':
                        vhlp.append(v['version'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
