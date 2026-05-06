import asyncio
import time
from asyncio import Semaphore
from typing import List, Mapping, Optional

import aiofiles
import arrow
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import DockerHubSoftware
from app.core.output import get_output_dir
from app.core.version import VersionHelper, VersionSummary

from . import Base

DOCKER_HUB_RATE_LIMIT_RETRY_BUDGET_SECONDS = 25 * 60
DOCKER_HUB_RATE_LIMIT_MAX_SLEEP_SECONDS = 120


class RepositoryTagItem(BaseModel):
    name: str
    full_size: int
    v2: bool
    tag_last_pushed: str


class RepositoryTags(BaseModel):
    results: List[RepositoryTagItem] = Field(default_factory=list)


class RatelimitHeader(BaseModel):
    rate_limit: Optional[str] = Field(default=None, alias="x-ratelimit-limit")
    rate_remaining: Optional[str] = Field(default=None, alias="x-ratelimit-remaining")
    rate_reset: Optional[str] = Field(default=None, alias="x-ratelimit-reset")


class OutputResult(BaseModel):
    name: str
    repo: str
    tags: List[RepositoryTagItem] = Field(default_factory=list)
    suffix: List[str] = Field(default_factory=list)
    fixed_tags: List[str] = Field(default_factory=list)
    latest_tags: List[str] = Field(default_factory=list)
    created_time: str


class Parser(Base):
    async def sleep(self, seconds: int):
        await asyncio.sleep(seconds)

    def _now(self) -> int:
        return int(time.time())

    def _rate_limit_wait_seconds(self, header: RatelimitHeader, retry_after: Optional[str]) -> int:
        """根据 Docker Hub 限流响应头计算下一次重试前应等待的秒数。"""
        if retry_after:
            try:
                return max(1, int(float(retry_after)))
            except ValueError:
                logger.warning("Invalid Docker Hub Retry-After header. Falling back to X-RateLimit-Reset.")

        if header.rate_reset:
            try:
                return max(1, int(header.rate_reset) - self._now())
            except ValueError:
                logger.warning("Invalid Docker Hub X-RateLimit-Reset header. Using default retry delay.")

        return 60

    async def _wait_for_rate_limit(self, soft: DockerHubSoftware, header: RatelimitHeader, retry_after: Optional[str], waited_seconds: int) -> int:
        wait_seconds = self._rate_limit_wait_seconds(header, retry_after)
        remaining_budget = DOCKER_HUB_RATE_LIMIT_RETRY_BUDGET_SECONDS - waited_seconds

        if wait_seconds > remaining_budget:
            raise RuntimeError(
                f"Docker Hub rate limit retry budget exceeded. "
                f"Repository: {soft.repo}, requested wait: {wait_seconds}s, remaining budget: {remaining_budget}s."
            )

        sleep_seconds = min(wait_seconds, DOCKER_HUB_RATE_LIMIT_MAX_SLEEP_SECONDS)
        logger.warning(
            f"[Docker Hub][{soft.repo}] rate limited. Waiting {sleep_seconds}s before retry. "
            f"({header.rate_remaining}/{header.rate_limit})"
        )
        await self.sleep(sleep_seconds)

        return waited_seconds + sleep_seconds

    async def handle(self, sem: Semaphore, soft: DockerHubSoftware):
        """分页读取 Docker Hub Tag 列表，并保留限流响应头用于输出和日志。"""
        logger.debug(f"Repository: {soft.repo} ({soft.parser})")

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=[])

        repo_parts = soft.repo.split("/", 1)

        current_page = 1
        max_page = soft.max_page

        results: List[RepositoryTagItem] = []
        data_header = RatelimitHeader.model_validate({})
        waited_seconds = 0

        async with sem:
            while True:
                if current_page > max_page:
                    break

                _, status, headers, data_r = await self.request(
                    "GET",
                    f"https://hub.docker.com/v2/namespaces/{repo_parts[0]}/repositories/{repo_parts[1]}/tags",
                    params={"status": "active", "page": f"{current_page}", "page_size": "100"},
                    is_json=True,
                    raise_for_status=False,
                )

                data_header = RatelimitHeader.model_validate(headers)

                if status == 429:
                    waited_seconds = await self._wait_for_rate_limit(soft, data_header, headers.get("Retry-After"), waited_seconds)
                    continue

                if status == 200:
                    data = RepositoryTags.model_validate(data_r)

                    for v in data.results:
                        vhlp.append(v.name)

                    results.extend(data.results)

                    if data_header.rate_remaining == "0" and current_page < max_page:
                        waited_seconds = await self._wait_for_rate_limit(soft, data_header, None, waited_seconds)
                else:
                    raise RuntimeError(f"[Docker Hub][{soft.repo}] HTTP status {status} error.")

                current_page += 1

            await self.write_data(soft, results, data_header, vhlp)

    async def write_data(self, soft: DockerHubSoftware, items: List[RepositoryTagItem], header: RatelimitHeader, vhlp: VersionHelper):
        """写出 Docker Hub 专用 JSON，包含匹配版本、最新标签、可用后缀和限流信息。"""
        output_path = get_output_dir(self.cfg.workdir)

        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        # 只保留能被版本正则识别的 Tag，避免输出无关镜像标签。
        tags = []
        latests = []
        suffix = []

        for v in items:
            if vhlp.exists(v.name):
                tags.append(v)

        version_summary = vhlp.summary

        if isinstance(version_summary, Mapping):
            for k, v in version_summary.items():
                if isinstance(v, VersionSummary):
                    latests.append(v.latest.version)
        elif isinstance(version_summary, VersionSummary):
            latests.append(version_summary.latest.version)

        def is_latest_exists(sfix: str) -> bool:
            """判断某个 Tag 后缀是否仍存在于最新版本对应的标签中。"""
            for vv in latests:
                fv = f"{vv}{sfix}"

                if vhlp.raw_exists(fv):
                    return True

            return False

        # 收集最新版本仍然存在的 Tag 后缀，例如 alpine、slim 等变体。
        for v in vhlp.raw_versions:
            if v.other and v.other not in suffix and is_latest_exists(v.other):
                suffix.append(v.other)

        soft_name = f"docker-{soft.repo.replace('/', '-')}"

        result = OutputResult(
            name=soft_name,
            repo=soft.repo,
            tags=tags,
            latest_tags=latests,
            suffix=suffix,
            fixed_tags=soft.fixed_tags,
            created_time=arrow.now().format("YYYY-MM-DD HH:mm:ss"),
        ).model_dump_json(by_alias=True)

        async with aiofiles.open(output_path.joinpath(f"{soft_name}.json"), "w", encoding="utf-8") as f:
            await f.write(result)

        logger.info(
            f"<\033[1;32m{soft.repo}\033[0m> done. "
            f"({header.rate_remaining}/{header.rate_limit}, {arrow.get(int(header.rate_reset)).format('YYYY-MM-DD HH:mm:ss')})"
        )
