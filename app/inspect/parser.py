import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import aiofiles
import aiohttp
import arrow
from loguru import logger
from semver import Version

from app.core.config import AppSettingSoftItem, AppSettingGitHubItem, AppSettingPHPItem, Configuration, OutputResult


class Parser(ABC):
    @staticmethod
    @abstractmethod
    def parse(cfg: Configuration, item: AppSettingSoftItem):
        pass

    @staticmethod
    def create(name: str):
        if name == 'GithubParser':
            return GithubParser()
        elif name == 'PHPReleasesParser':
            return PHPReleasesParser()
        else:
            return None

    @staticmethod
    def create_download_links(version: str, links: List[str]) -> List[str]:
        r = []

        for v in links:
            r.append(v.format(version=version))

        return r


class GithubParser(Parser):
    @staticmethod
    async def parse(cfg: Configuration, item: AppSettingSoftItem):
        if isinstance(item, AppSettingGitHubItem):
            # Sleep for the "sleep_for" seconds.
            # await asyncio.sleep(3)
            timeout = aiohttp.ClientTimeout(total=15)
            api_by = 'releases' if item.by_release else 'tags'

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f'https://api.github.com/repos/{item.repo}/{api_by}', proxy=os.environ.get('PROXY')) as resp:
                    logger.debug(f'{resp.url} | STATUS: {resp.status}')

                    data_r = await resp.json()

                    semver_versions = []
                    commit_sha_arr = {}

                    exp_r = re.compile(item.tag_pattern)

                    for v in data_r:
                        m = exp_r.match(v['name'])

                        if m:
                            ver = '{}.{}.{}'.format(m.group('major'), m.group('minor'), m.group('patch'))

                            commit_sha_arr[ver] = v['commit']['sha']
                            semver_versions.append(ver)

                    latest_version = max(semver_versions, key=Version.parse)
                    download_links = Parser.create_download_links(latest_version, item.download_urls)

                    logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
                    logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                    # 创建输出结果对象并写入 JSON 数据文件。
                    result = OutputResult(name=item.name, url=f'https://github.com/{item.repo}', latest=latest_version,
                                          versions=semver_versions, commit_sha=commit_sha_arr[latest_version],
                                          download_urls=download_links,
                                          created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                    output_path = Path(cfg.workdir).joinpath('data')

                    if not output_path.is_dir():
                        output_path.mkdir(parents=True, exist_ok=True)

                    async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
                        await f.write(result)

                    # logger.info(f'<{item.name}> data information has been generated.')


class PHPReleasesParser(Parser):
    @staticmethod
    async def parse(cfg: Configuration, item: AppSettingSoftItem):
        if isinstance(item, AppSettingPHPItem):
            timeout = aiohttp.ClientTimeout(total=15)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                for major in item.major:
                    async with session.get(f'https://www.php.net/releases/index.php?json&max=-1&version={major}', proxy=os.environ.get('PROXY')) as resp:
                        logger.debug(f'{resp.url} | STATUS: {resp.status}')

                        data_r = await resp.json()

                        semver_versions = []

                        for k, _ in data_r.items():
                            semver_versions.append(k)

                        latest_version = max(semver_versions, key=Version.parse)
                        download_links = Parser.create_download_links(latest_version, item.download_urls)

                        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
                        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                        # 创建输出结果对象并写入 JSON 数据文件。
                        result = OutputResult(name=item.name, url='https://github.com/php/php-src', latest=latest_version,
                                              versions=semver_versions,
                                              download_urls=download_links,
                                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                        output_path = Path(cfg.workdir).joinpath('data')

                        if not output_path.is_dir():
                            output_path.mkdir(parents=True, exist_ok=True)

                        async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
                            await f.write(result)

                        # logger.info(f'<{item.name}> data information has been generated.')
