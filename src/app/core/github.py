import os
import time
from datetime import timedelta
from typing import Optional

import arrow
from loguru import logger
from pydantic import BaseModel, Field

from app.core.http import AsyncHttpClient


class GithubRateLimitRate(BaseModel):
    limit: int
    remaining: int
    reset: int
    used: int
    resource: Optional[str] = Field(default=None)


class GithubRateLimit(BaseModel):
    rate: GithubRateLimitRate


class GithubHelper:
    @staticmethod
    async def show_rate_limit():
        github_token = os.environ.get("GITHUB_TOKEN")

        headers = {}

        if github_token:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {github_token}',
                'X-GitHub-Api-Version': '2022-11-28',
            }

        httpc = AsyncHttpClient()

        _, status, _, data_r = await httpc.request('GET', 'https://api.github.com/rate_limit', headers=headers,
                                                   timeout=15, is_json=True)

        dm = GithubRateLimit.model_validate(data_r, strict=False)

        logger.info(
            f'Rate Limit | CPU: {os.cpu_count()} '
            f'| Remaining: \033[1;32m{dm.rate.remaining}\033[0m/\033[1;33m{dm.rate.limit}\033[0m'
            f',\033[1;34m{timedelta(seconds=dm.rate.reset - int(time.time()))}\033[0m '
            f'| Current Time: {arrow.now("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss ZZ")} '
            f'| Reset: {arrow.get(dm.rate.reset).to("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss ZZ")}')
