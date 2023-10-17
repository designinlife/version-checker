import os
import re
from pathlib import Path

import aiofiles
import aiohttp
import arrow
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import AppSettingSoftItem, Configuration, OutputResult
from app.core.version import VersionParser
from app.inspect.parser import Parser


async def parse(cfg: Configuration, item: AppSettingSoftItem):
    semver_versions = []

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(item.url, proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_s = await resp.text()
            soup = BeautifulSoup(data_s, 'html.parser')

            all_elements = soup.select('body > div.md-container > main > div > div.md-sidebar.md-sidebar--secondary > div > div > nav > ul > li > a')

            exp = re.compile(r'^Ruby (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<patch>\d+)?)$')

            for v in all_elements:
                m = exp.match(v.text.strip())

                if m:
                    semver_versions.append(m.group('version'))

    logger.debug(f'Ruby: {semver_versions}')

    vpsr = VersionParser(pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<patch>\d+)?)$')

    latest_version = vpsr.latest(semver_versions)
    download_links = Parser.create_download_links(latest_version, item.download_urls)

    logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
    logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

    # 创建输出结果对象并写入 JSON 数据文件。
    result = OutputResult(name=f'{item.name}', url=f'https://www.ruby-lang.org/en/downloads/', latest=latest_version,
                          versions=semver_versions,
                          download_urls=download_links,
                          created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

    output_path = Path(cfg.workdir).joinpath('data')

    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
        await f.write(result)

    logger.info(f'<{item.name}> data information has been generated.')
