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
    logger.debug(f'virtualbox parser called.')

    semver_versions = []
    download_links = []

    latest_version = None

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        async with session.get(item.url, proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_s = await resp.text()
            soup = BeautifulSoup(data_s, 'html5lib')

            elements = soup.select('h3.section')
            download_link_ul = soup.select('div#wikipage ul', limit=1)[0]
            download_link_elements = download_link_ul.select('li > a[class=ext-link]')

            exp_ver = re.compile(r'^VirtualBox (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)) platform packages$', flags=re.I)

            for el in elements:
                m = exp_ver.match(el.text.strip())

                if m:
                    latest_version = m.group('version')
                    semver_versions.append(latest_version)
                    break

            if download_link_elements:
                for v in download_link_elements:
                    download_links.append(v.attrs['href'])

    # 创建输出结果对象并写入 JSON 数据文件。
    result = OutputResult(name=f'{item.name}', url=f'https://www.virtualbox.org/wiki/Downloads', latest=latest_version,
                          versions=semver_versions,
                          download_urls=download_links,
                          created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

    output_path = Path(cfg.workdir).joinpath('data')

    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
        await f.write(result)

    logger.info(f'<{item.name}> data information has been generated.')
