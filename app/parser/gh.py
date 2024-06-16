import os
import time
from asyncio import Semaphore
from datetime import timedelta
from typing import Optional, List

import arrow
from loguru import logger
from pydantic import BaseModel

from app.core.config import GithubSoftware
from app.core.version import VersionHelper
from . import Base


class GithubRateLimitRate(BaseModel):
    limit: int
    remaining: int
    reset: int
    used: int
    resource: Optional[str]


class GithubRateLimit(BaseModel):
    rate: GithubRateLimitRate


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: GithubSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser}, Release: {soft.release})')

        # Due to Github API current limit, you need to check whether the data update has expired!
        expired, last_update_time = self.is_expired(soft)
        if not expired:
            logger.warning(f'[{soft.name}] The last update time is: {last_update_time}, it has not been more than 6 hours, no need to update!')
            return

        api_by = 'releases' if soft.release else 'tags'

        github_token = os.environ.get("GITHUB_TOKEN")

        headers = {}

        if github_token:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {github_token}',
                'X-GitHub-Api-Version': '2022-11-28',
            }

            logger.debug('Using GITHUB_TOKEN env.')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        gns = soft.repo

        async with sem:
            for page in range(0, soft.max_page):
                # Make an HTTP request.
                url, http_status_code, _, data_r = await self.request('GET',
                                                                      f'https://api.github.com/repos/{gns}/{api_by}',
                                                                      params={'per_page': '100', 'page': str(page + 1)},
                                                                      headers=headers,
                                                                      is_json=True)

                for v in data_r:
                    if soft.release:
                        if v['draft'] is False and v['prerelease'] is False:
                            if soft.assets:
                                vhlp.append(v['tag_name'], raw_data={'tag_name': v['tag_name'], 'assets': v['assets']})
                            else:
                                vhlp.append(v['tag_name'])
                    else:
                        vhlp.append(v['name'])

            # Do you want to download the assets attachment?
            if soft.release and soft.assets:
                rdata = vhlp.latest_version.raw_data

                if isinstance(rdata['assets'], List):
                    for v in rdata['assets']:
                        vhlp.add_download_url(v['browser_download_url'])

        logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

        if soft.split > 0:
            logger.debug(f'Split Versions: {vhlp.split_versions}')

        # Write data to file.
        await self.write(soft, vhlp.summary)

    async def github_ratelimit(self):
        """Print GitHub ratelimit data.

        """
        github_token = os.environ.get("GITHUB_TOKEN")

        headers = {}

        if github_token:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {github_token}',
                'X-GitHub-Api-Version': '2022-11-28',
            }

        _, status, _, data_r = await self.request('GET', 'https://api.github.com/rate_limit', headers=headers,
                                                  timeout=15, is_json=True)

        dm = GithubRateLimit.model_validate(data_r, strict=False)

        logger.info(
            f'Rate Limit | CPU: {os.cpu_count()} '
            f'| Remaining: \033[1;32m{dm.rate.remaining}\033[0m/\033[1;33m{dm.rate.limit}\033[0m'
            f',\033[1;34m{timedelta(seconds=dm.rate.reset - int(time.time()))}\033[0m '
            f'| Current Time: {arrow.now("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss ZZ")} '
            f'| Reset: {arrow.get(dm.rate.reset).to("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss ZZ")}')
