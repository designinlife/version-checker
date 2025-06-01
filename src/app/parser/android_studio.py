from asyncio import Semaphore
from urllib.parse import urljoin

import aiohttp
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
            # _, status, _, data_r = await self.request('GET', 'https://jb.gg/android-studio-releases-list.json', is_json=True)
            data_r = await self._fetch_json('https://jb.gg/android-studio-releases-list.json')

            if isinstance(data_r, dict) and 'content' in data_r:
                for v in data_r['content']['item']:
                    if v['channel'] == 'Release':  # if v['channel'] == 'Release' or v['channel'] == 'Patch':
                        vhlp.append(v['version'])

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)

    @staticmethod
    async def _fetch_json(url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            # 第一次请求，禁用自动重定向以捕获 307
            async with session.get(url, allow_redirects=False) as response:
                if response.status in (301, 302, 307):
                    redirect_url = response.headers.get('Location')
                    if not redirect_url.startswith('http'):
                        redirect_url = urljoin(url, redirect_url)
                    # 请求跳转目标地址并返回 JSON
                    async with session.get(redirect_url) as final_response:
                        return await final_response.json()
                # 如果没有重定向，直接返回 JSON
                return await response.json()
