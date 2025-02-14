import importlib
import json
import operator
import os
from abc import ABCMeta, abstractmethod
from asyncio import Semaphore
from pathlib import Path
from typing import Optional, Dict, Tuple, Mapping, List

import aiofiles
import arrow
from loguru import logger

from app.core.config import Configuration, AppSettingSoftItem, OutputResult
from app.core.http import AsyncHttpClient
from app.core.version import VersionSummary
from app.link import UrlMakerBase


def check_requirements(requirement_string: str, major: int, minor: Optional[int] = None) -> bool:
    """
    检查是否满足 requirements 字符串中的条件。

    Args:
        requirement_string: 包含条件的字符串，例如 "major >= 6 && minor < 2"。
        major: major 版本号。
        minor: minor 版本号。

    Returns:
        True 如果满足条件，否则返回 False。
    """
    # 定义运算符映射
    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }

    try:
        # 将 requirement_string 分割成条件
        conditions = requirement_string.split('&&')
        conditions = [c.strip() for c in conditions]  # 清理空格

        # 逐个检查条件
        for condition in conditions:
            parts = condition.split()
            if len(parts) != 3:
                logger.warning(f"Warning: Invalid condition format: {condition}. Skipping.")
                continue

            variable, operator_str, value_str = parts

            # 获取变量值
            if variable == 'major':
                value1 = major
            elif variable == 'minor':
                value1 = minor if isinstance(minor, int) else 0
            else:
                logger.warning(f"Warning: Unknown variable: {variable}. Skipping condition.")
                continue

            # 获取运算符
            op = ops.get(operator_str)
            if op is None:
                logger.warning(f"Warning: Unknown operator: {operator_str}. Skipping condition.")
                continue

            # 获取值
            try:
                value2 = int(value_str)
            except ValueError:
                logger.error(f"Warning: Invalid value: {value_str}. Skipping condition.")
                continue

            # 检查条件是否满足
            if not op(value1, value2):
                return False  # 如果任何一个条件不满足，则返回 False

        # 所有条件都满足，返回 True
        return True
    except Exception as e:
        logger.error(f"Error evaluating requirement: {e}")
        return False


class Base(metaclass=ABCMeta):
    def __init__(self, cfg: Configuration):
        self.cfg = cfg
        self.httpc = AsyncHttpClient(debug=self.cfg.debug)

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
        url, http_status_code, headers, data = await self.httpc.request(method, url, params, data, headers, timeout, is_json)

        return url, http_status_code, headers, data

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
                    if soft.condition and v.latest is not None and not check_requirements(soft.condition, v.latest.major, v.latest.minor):
                        continue

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
