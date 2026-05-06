import importlib
import json
import operator
import os
from abc import ABCMeta, abstractmethod
from asyncio import Semaphore
from typing import Dict, List, Mapping, Optional, Tuple

import aiofiles
import arrow
from loguru import logger

from app.core.config import AppSettingSoftItem, Configuration, OutputResult
from app.core.http import AsyncHttpClient
from app.core.inspect_result import InspectItemResult
from app.core.output import get_output_dir
from app.core.version import VersionSummary
from app.link import UrlMakerBase


def get_cache_ttl_hours() -> int:
    """读取运行数据缓存有效期；非法或过小配置统一回退为 1 小时。"""
    raw_value = os.environ.get("VERSION_CHECKER_CACHE_TTL_HOURS", "1")
    try:
        ttl_hours = int(raw_value)
    except ValueError:
        logger.warning("Invalid VERSION_CHECKER_CACHE_TTL_HOURS value. Using default cache TTL.")
        return 1

    if ttl_hours < 1:
        logger.warning("VERSION_CHECKER_CACHE_TTL_HOURS must be greater than or equal to 1. Using default cache TTL.")
        return 1

    return ttl_hours


def check_requirements(requirement_string: str, major: int, minor: Optional[int] = None) -> bool:
    """检查版本号是否满足 `major >= 6 && minor < 2` 这类条件表达式。"""
    ops = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le, "==": operator.eq, "!=": operator.ne}

    try:
        conditions = requirement_string.split("&&")
        conditions = [c.strip() for c in conditions]

        for condition in conditions:
            parts = condition.split()
            if len(parts) != 3:
                logger.warning(f"Warning: Invalid condition format: {condition}. Skipping.")
                continue

            variable, operator_str, value_str = parts

            if variable == "major":
                value1 = major
            elif variable == "minor":
                value1 = minor if isinstance(minor, int) else 0
            else:
                logger.warning(f"Warning: Unknown variable: {variable}. Skipping condition.")
                continue

            op = ops.get(operator_str)
            if op is None:
                logger.warning(f"Warning: Unknown operator: {operator_str}. Skipping condition.")
                continue

            try:
                value2 = int(value_str)
            except ValueError:
                logger.error(f"Warning: Invalid value: {value_str}. Skipping condition.")
                continue

            if not op(value1, value2):
                return False

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
        """解析器入口方法，子类负责抓取远端版本并调用 `write()` 写出结果。"""
        ...

    async def wrap_handle(self, sem: Semaphore, soft: AppSettingSoftItem):
        """包装单个软件条目的解析流程，把异常转换为结构化检测结果。"""
        try:
            await self.handle(sem, soft)
            return InspectItemResult.success(soft.name)
        except Exception as e:
            logger.error(f"[{soft.name}] error found.")
            logger.exception(e)
            return InspectItemResult.failed(soft.name, type(e).__name__, str(e))

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, str]] = None,
        data: Optional[dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 15,
        is_json: bool = False,
    ):
        """通过解析器共享的 HTTP 客户端发送请求，保持 parser 子类的网络调用入口一致。"""
        url, http_status_code, headers, data = await self.httpc.request(method, url, params, data, headers, timeout, is_json)

        return url, http_status_code, headers, data

    def _build_download_urls(self, soft: AppSettingSoftItem, version_summary: VersionSummary, download_urls: List[str]) -> List[str]:
        """根据配置决定直接使用下载模板，还是委托 `app.link` 动态生成下载地址。"""
        if soft.download_dynamic:
            # 动态下载地址模块按软件名称约定加载，例如 `sqlite` -> `app.link.sqlite.UrlMaker`。
            module = importlib.import_module("app.link.%s" % soft.name.replace("-", "_"))
            cls = getattr(module, "UrlMaker")
            cls_o = cls(self.cfg)

            if isinstance(cls_o, UrlMakerBase):
                return cls_o.build_links(soft=soft, version_summary=version_summary, urls=download_urls)
        else:
            return download_urls

    def is_expired(self, soft: AppSettingSoftItem) -> Tuple[bool, str]:
        """检查软件输出文件是否超过缓存有效期，返回是否过期和上次更新时间。"""
        output_path = get_output_dir(self.cfg.workdir)

        file = None

        if soft.split == 0:
            file = output_path.joinpath(f"{soft.name}.json")
        else:
            files = output_path.glob(f"{soft.name}-*.json", case_sensitive=True)
            for cf in files:
                file = cf
                break

        if file and file.is_file():
            with open(file, "r", encoding="utf-8") as f:
                data = json.loads(f.read())

                ttl_hours = get_cache_ttl_hours()
                if arrow.now().shift(hours=-ttl_hours) >= arrow.get(data["created_time"]):
                    return True, data["created_time"]
                else:
                    return False, data["created_time"]

        return True, "2000-01-01 00:00:00"

    async def write(
        self,
        soft: AppSettingSoftItem,
        version_summary: VersionSummary | Mapping[str, VersionSummary],
        suffix: str = "",
        storage_dir: Optional[str] = None,
        **kwargs,
    ):
        """把版本摘要写入软件 JSON 文件；split 场景会按主版本或次版本拆分多个文件。"""
        output_path = get_output_dir(self.cfg.workdir)

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        if isinstance(version_summary, Mapping):
            for k, v in version_summary.items():
                if isinstance(v, VersionSummary):
                    if soft.condition and v.latest is not None and not check_requirements(soft.condition, v.latest.major, v.latest.minor):
                        continue

                    result = OutputResult(
                        name=f"{soft.name}-{k}",
                        url=f"{soft.url}",
                        display_name=soft.display_name,
                        latest=repr(v.latest),
                        versions=[repr(x) for x in v.versions],
                        storage_dir=storage_dir,
                        download_urls=self._build_download_urls(soft, v, v.downloads),
                        created_time=arrow.now().format("YYYY-MM-DD HH:mm:ss"),
                        **kwargs,
                    ).model_dump_json(by_alias=True, exclude_none=True)

                    async with aiofiles.open(output_path.joinpath(f"{soft.name}-{k}.json"), "w", encoding="utf-8") as f:
                        await f.write(result)

                    logger.info(f"<\033[1;32m{soft.name}-{k}\033[0m> done.")
        else:
            result = OutputResult(
                name=f"{soft.name}{suffix}",
                url=f"{soft.url}",
                display_name=soft.display_name,
                latest=repr(version_summary.latest),
                versions=[repr(x) for x in version_summary.versions],
                storage_dir=storage_dir,
                download_urls=self._build_download_urls(soft, version_summary, version_summary.downloads),
                created_time=arrow.now().format("YYYY-MM-DD HH:mm:ss"),
                **kwargs,
            ).model_dump_json(by_alias=True, exclude_none=True)

            async with aiofiles.open(output_path.joinpath(f"{soft.name}{suffix}.json"), "w", encoding="utf-8") as f:
                await f.write(result)

            logger.info(f"<\033[1;32m{soft.name}{suffix}\033[0m> done.")
