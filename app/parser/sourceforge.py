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
        async with session.get(f'https://sourceforge.net/projects/{item.name}/best_release.json', proxy=os.environ.get('PROXY')) as resp:
            logger.debug(f'{resp.url} | STATUS: {resp.status}')

            data_r = await resp.json()

            try:
                filename_parts = f"{data_r['release']['filename']}".split('/')

                latest_version = filename_parts[1]
                semver_versions.append(latest_version)
                download_links.append(data_r['release']['url'])
            except Exception as exc:
                logger.exception('[Parser::sourceforge][{}] {}'.format(item.name, exc))

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
