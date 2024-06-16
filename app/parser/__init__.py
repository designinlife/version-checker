import importlib
import json
import os
from abc import ABCMeta, abstractmethod
from asyncio import Semaphore
from pathlib import Path
from typing import Optional, Dict, Tuple, Mapping, List

import aiofiles
import aiohttp
import arrow
from loguru import logger

from app.core import DEFAULT_USERAGENT
from app.core.config import Configuration, AppSettingSoftItem, OutputResult
from app.core.version import VersionSummary
from app.link import UrlMakerBase


class Base(metaclass=ABCMeta):
    def __init__(self, cfg: Configuration):
        self.cfg = cfg

    @abstractmethod
    async def handle(self, sem: Semaphore, soft: AppSettingSoftItem):
        ...

    async def wrap_handle(self, sem: Semaphore, soft: AppSettingSoftItem):
        try:
            await self.handle(sem, soft)
        except Exception as e:
            logger.error(f'[{soft.name}] error found.')
            logger.exception(e)

    async def request(self, method: str, url: str,
                      params: Optional[Dict[str, str]] = None,
                      data: Optional[dict] = None,
                      headers: Optional[Dict[str, str]] = None,
                      timeout: float = 15,
                      is_json: bool = False):
        """
        Send an HTTP request.

        Args:
            method:
            url:
            params:
            data:
            headers:
            timeout:
            is_json:

        Returns:

        """
        hdr = {'User-Agent': DEFAULT_USERAGENT}

        if headers:
            hdr.update(headers)

        if self.cfg.debug:
            # logger.debug(f'URL: {url}, PARAMS: {params}, HEADERS: {headers}, TIMEOUT: {timeout},
            # JSON RESULT: {is_json}')
            logger.debug(f'URL: {url}, PARAMS: {params}, TIMEOUT: {timeout}, JSON RESULT: {is_json}')

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(method=method, url=url,
                                       params=params,
                                       json=data,
                                       headers=hdr,
                                       proxy=os.environ.get('PROXY')) as resp:
                if 200 <= resp.status < 300:
                    # for k, v in resp.headers.items():
                    #     if 'ratelimit' in k.lower():
                    #         logger.debug(f'Response Header: {k}={v}')

                    if is_json:
                        return resp.url, resp.status, resp.headers, await resp.json()
                    else:
                        return resp.url, resp.status, resp.headers, await resp.text()
                else:
                    raise ValueError(f'HTTP status code exception. ({resp.status} | {url})')

    def _build_download_urls(self, soft: AppSettingSoftItem, version_summary: VersionSummary,
                             download_urls: List[str]) -> List[str]:
        if soft.download_dynamic:
            # Dynamically create an UrlMaker instance.
            module = importlib.import_module('app.link.%s' % soft.name.replace('-', '_'))
            cls = getattr(module, 'UrlMaker')
            cls_o = cls(self.cfg)

            if isinstance(cls_o, UrlMakerBase):
                return cls_o.build_links(soft=soft, version_summary=version_summary, urls=download_urls)
        else:
            return download_urls

    def is_expired(self, soft: AppSettingSoftItem) -> Tuple[bool, str]:
        """检查数据是否过期。

        Args:
            soft:

        Returns:

        """
        output_subdir = os.environ.get('OUTPUT_DATA_DIR', 'data')
        output_path = Path(self.cfg.workdir).joinpath(output_subdir)

        file = None

        if soft.split == 0:
            file = output_path.joinpath(f'{soft.name}.json')
        else:
            files = output_path.glob(f'{soft.name}-*.json', case_sensitive=True)
            for cf in files:
                file = cf
                break

        if file and file.is_file():
            with open(file, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())

                # Data will be considered expired if it has been updated for more than 6 hours!
                if arrow.now().shift(hours=-6) >= arrow.get(data['created_time']):
                    return True, data['created_time']
                else:
                    return False, data['created_time']

        return True, '2000-01-01 00:00:00'

    async def write(self, soft: AppSettingSoftItem, version_summary: VersionSummary | Mapping[str, VersionSummary],
                    suffix: str = ''):
        output_subdir = os.environ.get('OUTPUT_DATA_DIR', 'data')
        output_path = Path(self.cfg.workdir).joinpath(output_subdir)

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        if isinstance(version_summary, Mapping):
            for k, v in version_summary.items():
                if isinstance(v, VersionSummary):
                    result = OutputResult(name=f'{soft.name}-{k}', url=f'{soft.url}', latest=repr(v.latest),
                                          versions=[repr(x) for x in v.versions],
                                          download_urls=self._build_download_urls(soft, v, v.downloads),
                                          created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(
                        by_alias=True)

                    async with aiofiles.open(output_path.joinpath(f'{soft.name}-{k}.json'), 'w', encoding='utf-8') as f:
                        await f.write(result)

                    logger.info(f'<\033[1;32m{soft.name}-{k}\033[0m> done.')
        else:
            result = OutputResult(name=f'{soft.name}{suffix}', url=f'{soft.url}', latest=repr(version_summary.latest),
                                  versions=[repr(x) for x in version_summary.versions],
                                  download_urls=self._build_download_urls(soft, version_summary,
                                                                          version_summary.downloads),
                                  created_time=arrow.now().format('YYYY-MM-DD HH:mm:ss')).model_dump_json(by_alias=True)

            async with aiofiles.open(output_path.joinpath(f'{soft.name}{suffix}.json'), 'w', encoding='utf-8') as f:
                await f.write(result)

            logger.info(f'<\033[1;32m{soft.name}{suffix}\033[0m> done.')
