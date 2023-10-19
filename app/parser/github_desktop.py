import os
from pathlib import Path

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core.config import AppSettingSoftItem, Configuration, OutputResult


async def parse(cfg: Configuration, item: AppSettingSoftItem):
    semver_versions = []
    download_links = []

    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get('https://central.github.com/deployments/desktop/desktop/changelog.json', proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_r = await resp.json()
            latest_version = data_r[0]['version']
            semver_versions.append(latest_version)
            download_links.append('https://central.github.com/deployments/desktop/desktop/latest/win32')
            download_links.append('https://central.github.com/deployments/desktop/desktop/latest/darwin')

    if semver_versions and download_links:
        # 创建输出结果对象并写入 JSON 数据文件。
        result = OutputResult(name=f'{item.name}', url=item.url, latest=latest_version,
                              versions=semver_versions,
                              download_urls=download_links,
                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

        output_path = Path(cfg.workdir).joinpath('data')

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
            await f.write(result)

        logger.info(f'<{item.name}> data information has been generated.')
