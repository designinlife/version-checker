import json
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core.config import AppSettingSoftItem, AppSettingGitHubItem, AppSettingPHPItem, Configuration, OutputResult
from app.core.version import VersionParser


class Parser(ABC):
    @staticmethod
    @abstractmethod
    def parse(cfg: Configuration, item: AppSettingSoftItem):
        pass

    @staticmethod
    def create(name: str):
        if name == 'gh':
            return GithubParser()
        elif name == 'php':
            return PHPReleasesParser()
        elif name == 'go':
            return GoReleasesParser()
        elif name == 'docker-library':
            return DockerLibraryParser()
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

            github_token = os.environ.get("GITHUB_TOKEN")

            headers = {}

            if github_token:
                headers = {
                    'Accept': 'application/vnd.github+json',
                    'Authorization': f'Bearer {github_token}',
                    'X-GitHub-Api-Version': '2022-11-28',
                }

                logger.debug('Using GITHUB_TOKEN env.')

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f'https://api.github.com/repos/{item.repo}/{api_by}?per_page=100', headers=headers,
                                       proxy=os.environ.get('PROXY')) as resp:
                    logger.debug(f'{resp.url} | STATUS: {resp.status}')

                    data_r = await resp.json()

                    semver_versions = []
                    commit_sha_arr = {}

                    exp_r = re.compile(item.tag_pattern)

                    for v in data_r:
                        m = exp_r.match(v['name'])

                        if m:
                            # if 'suffix' in m.groupdict() and m.group('suffix') is not None:
                            #     ver = '{}.{}.{}{}'.format(m.group('major'), m.group('minor'), m.group('patch'), m.group('suffix'))
                            # else:
                            #     ver = '{}.{}.{}'.format(m.group('major'), m.group('minor'), m.group('patch'))
                            ver = m.group('version')

                            if 'commit' in v:
                                commit_sha_arr[ver] = v['commit']['sha']
                            else:
                                commit_sha_arr[ver] = None

                            semver_versions.append(v['name'])

                    vpsr = VersionParser(item.tag_pattern)

                    if item.category:
                        # 按 <major>.<minor> 规则将版本分类为字典对象, 例如 OpenSSL 的版本划分为: 1.0, 1.1, 3.0, 3.1, 3.2 ...
                        dict_versions = vpsr.semver_split(semver_versions)

                        for m, n in dict_versions.items():
                            latest_version = vpsr.latest(n)
                            download_links = Parser.create_download_links(latest_version, item.download_urls)

                            logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
                            logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                            # 创建输出结果对象并写入 JSON 数据文件。
                            result = OutputResult(name=f'{item.name}-{m}', url=f'https://github.com/{item.repo}', latest=latest_version,
                                                  versions=vpsr.clean(n),
                                                  download_urls=download_links,
                                                  created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                            output_path = Path(cfg.workdir).joinpath('data')

                            if not output_path.is_dir():
                                output_path.mkdir(parents=True, exist_ok=True)

                            async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
                                await f.write(result)

                            logger.info(f'<{item.name}-{m}> data information has been generated.')
                    else:
                        # latest_version = max(semver_versions, key=Version.parse)
                        latest_version = vpsr.latest(semver_versions)
                        download_links = Parser.create_download_links(latest_version, item.download_urls)

                        logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(semver_versions)}')
                        logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                        # 创建输出结果对象并写入 JSON 数据文件。
                        result = OutputResult(name=item.name, url=f'https://github.com/{item.repo}', latest=latest_version,
                                              versions=vpsr.clean(semver_versions),
                                              download_urls=download_links,
                                              created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                        output_path = Path(cfg.workdir).joinpath('data')

                        if not output_path.is_dir():
                            output_path.mkdir(parents=True, exist_ok=True)

                        async with aiofiles.open(output_path.joinpath(f'{item.name}.json'), 'w', encoding='utf-8') as f:
                            await f.write(result)

                        logger.info(f'<{item.name}> data information has been generated.')


class PHPReleasesParser(Parser):
    @staticmethod
    async def parse(cfg: Configuration, item: AppSettingSoftItem):
        if isinstance(item, AppSettingPHPItem):
            semver_versions = []

            timeout = aiohttp.ClientTimeout(total=15)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                for major in item.major:
                    async with session.get(f'https://www.php.net/releases/index.php?json&max=-1&version={major}', proxy=os.environ.get('PROXY')) as resp:
                        logger.debug(f'{resp.url} | STATUS: {resp.status}')

                        data_r = await resp.json()

                        for k, _ in data_r.items():
                            semver_versions.append(k)

            logger.debug(f'PHP: {semver_versions}')

            vpsr = VersionParser(pattern=item.tag_pattern)

            dict_versions = vpsr.semver_split(semver_versions)

            logger.debug(f'PHP Split: {dict_versions}')

            for m, n in dict_versions.items():
                latest_version = vpsr.latest(n)
                download_links = Parser.create_download_links(latest_version, item.download_urls)

                logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
                logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                # 创建输出结果对象并写入 JSON 数据文件。
                result = OutputResult(name=f'{item.name}-{m}', url=f'https://github.com/php/php-src', latest=latest_version,
                                      versions=n,
                                      download_urls=download_links,
                                      created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                output_path = Path(cfg.workdir).joinpath('data')

                if not output_path.is_dir():
                    output_path.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
                    await f.write(result)

                logger.info(f'<{item.name}-{m}> data information has been generated.')


class GoReleasesParser(Parser):
    @staticmethod
    async def parse(cfg: Configuration, item: AppSettingSoftItem):
        if isinstance(item, AppSettingSoftItem):
            semver_versions = []

            timeout = aiohttp.ClientTimeout(total=15)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f'https://go.dev/dl/?mode=json&include=all', proxy=os.environ.get('PROXY')) as resp:
                    logger.debug(f'{resp.url} | STATUS: {resp.status}')

                    data_r = await resp.json()

                    for v in data_r:
                        semver_versions.append(v['version'])

            logger.debug(f'Go: {semver_versions}')

            vpsr = VersionParser(pattern=item.tag_pattern)

            dict_versions = vpsr.semver_split(semver_versions)

            logger.debug(f'Go Split: {dict_versions}')

            for m, n in dict_versions.items():
                latest_version = vpsr.latest(n)
                download_links = Parser.create_download_links(latest_version, item.download_urls)

                logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
                logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                # 创建输出结果对象并写入 JSON 数据文件。
                result = OutputResult(name=f'{item.name}-{m}', url=f'https://go.dev/dl/', latest=latest_version,
                                      versions=n,
                                      download_urls=download_links,
                                      created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                output_path = Path(cfg.workdir).joinpath('data')

                if not output_path.is_dir():
                    output_path.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
                    await f.write(result)

                logger.info(f'<{item.name}-{m}> data information has been generated.')


class DockerLibraryParser(Parser):
    @staticmethod
    async def parse(cfg: Configuration, item: AppSettingSoftItem):
        if isinstance(item, AppSettingSoftItem):
            semver_versions = []

            timeout = aiohttp.ClientTimeout(total=15)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f'https://raw.githubusercontent.com/docker-library/{item.name}/master/versions.json',
                                       proxy=os.environ.get('PROXY')) as resp:
                    logger.debug(f'{resp.url} | STATUS: {resp.status}')

                    data_s = await resp.text()
                    data_r = json.loads(data_s)

                    for _, v in data_r.items():
                        semver_versions.append(v['version'])

            logger.debug(f'docker-library: {semver_versions}')

            vpsr = VersionParser(pattern=item.tag_pattern)

            dict_versions = vpsr.semver_split(semver_versions)

            logger.debug(f'docker-library Split: {dict_versions}')

            for m, n in dict_versions.items():
                latest_version = vpsr.latest(n)
                download_links = Parser.create_download_links(latest_version, item.download_urls)

                logger.debug(f'LATEST: {latest_version} | Versions: {", ".join(n)}')
                logger.debug('DOWNLOADS: {}'.format('\n'.join(download_links)))

                # 创建输出结果对象并写入 JSON 数据文件。
                result = OutputResult(name=f'{item.name}-{m}', url=f'https://github.com/', latest=latest_version,
                                      versions=n,
                                      download_urls=download_links,
                                      created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

                output_path = Path(cfg.workdir).joinpath('data')

                if not output_path.is_dir():
                    output_path.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(output_path.joinpath(f'{item.name}-{m}.json'), 'w', encoding='utf-8') as f:
                    await f.write(result)

                logger.info(f'<{item.name}-{m}> data information has been generated.')
