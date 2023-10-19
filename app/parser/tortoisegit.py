import os
import re
from pathlib import Path

import aiofiles
import aiohttp
import arrow
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import AppSettingSoftItem, Configuration, OutputResult


async def parse(cfg: Configuration, item: AppSettingSoftItem):
    semver_versions = []
    download_links = []

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get('https://tortoisegit.org/download/', proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_s = await resp.text()
            soup = BeautifulSoup(data_s, 'html5lib')

            latest_element = soup.select_one('div[class="wrap_content contentpage"] > p:nth-of-type(1)')
            latest_exp = re.compile(r'^The current stable version is: (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(\.(?P<suffix>\d+))?)$')
            m = latest_exp.match(latest_element.text)
            if m:
                latest_version = m.group('version')
                semver_versions.append(latest_version)

                ver_split = latest_version.split('.')
                ver_split_len = len(ver_split)

                if ver_split_len > 3:
                    download_links.append(f'https://download.tortoisegit.org/tgit/{latest_version}/TortoiseGit-{latest_version}-32bit.msi')
                    download_links.append(f'https://download.tortoisegit.org/tgit/{latest_version}/TortoiseGit-{latest_version}-64bit.msi')
                    download_links.append(f'https://download.tortoisegit.org/tgit/{latest_version}/TortoiseGit-{latest_version}-arm64.msi')
                elif ver_split_len == 3:
                    download_links.append(f'https://download.tortoisegit.org/tgit/{latest_version}.0/TortoiseGit-{latest_version}.0-32bit.msi')
                    download_links.append(f'https://download.tortoisegit.org/tgit/{latest_version}.0/TortoiseGit-{latest_version}.0-64bit.msi')
                    download_links.append(f'https://download.tortoisegit.org/tgit/{latest_version}.0/TortoiseGit-{latest_version}.0-arm64.msi')
                else:
                    raise ValueError(f'TORTOISEGIT VERSION NUMBER IS NOT STANDARDIZED. ({latest_version})')

    if semver_versions and download_links:
        # 创建输出结果对象并写入 JSON 数据文件。
        result = OutputResult(name=f'{item.name}', url=item.url if item.url else f'https://sourceforge.net/projects/{item.name}/', latest=latest_version,
                              versions=semver_versions,
                              download_urls=download_links,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        output_path = Path(cfg.workdir).joinpath('data')

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<{item.name}> data information has been generated.')
