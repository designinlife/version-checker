from asyncio import Semaphore
from pathlib import Path
from typing import Mapping

from loguru import logger

from app.core.config import JetbrainsSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: JetbrainsSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        # jb_cfgs = {'AC': 'AppCode', 'CL': 'CLion', 'RSU': 'ReSharper Ultimate', 'DG': 'DataGrip',
        #            'GO': 'Goland', 'IIU': 'IntelliJ IDEA', 'PS': 'PhpStorm', 'PCP': 'PyCharm', 'RD': 'Rider',
        #            'RM': 'RubyMine', 'WS': 'WebStorm', 'FL': 'Fleet', 'RR': 'RustRover', 'DS': 'DataSpell',
        #            'QA': 'Aqua',
        #            'TC': 'TeamCity', 'WRS': 'Writerside'}

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET',
                                                      'https://data.services.jetbrains.com/products/releases',
                                                      params={
                                                          'code': ','.join(soft.code),
                                                          'latest': 'true', 'type': 'release'},
                                                      is_json=True)

            if isinstance(data_r, Mapping):
                for code, vitem in data_r.items():
                    if len(vitem) > 0:
                        for v2 in vitem:
                            vhlp.append(v2['version'])

                            for os, v3 in v2['downloads'].items():
                                if os in soft.os:
                                    vhlp.add_download_url(
                                        f'{v3['link']}#{v2['majorVersion']}|{Path(v3['link']).name}'.replace(
                                            '://download.jetbrains.com/',
                                            '://download-cdn.jetbrains.com/'))

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)
