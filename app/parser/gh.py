import os
from asyncio import Semaphore
from typing import List

from loguru import logger

from app.core.config import GithubSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: GithubSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser}, Release: {soft.release})')

        # Due to GitHub API current limit, you need to check whether the data update has expired!
        expired, last_update_time = self.is_expired(soft)
        if not expired:
            logger.info(f'[{soft.name}] SKIPPED: The last update time is: {last_update_time}, it has not been more than 6 hours, no need to update!')
            return

        if soft.latest:
            soft.release = True
            soft.max_page = 1

        api_by = 'releases' if soft.release else 'tags'

        if soft.latest:
            api_by = 'releases/latest'

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
                params = None

                if not soft.latest:
                    params = {'per_page': '100', 'page': str(page + 1)}

                # Make an HTTP request.
                url, http_status_code, _, data_r = await self.request('GET',
                                                                      f'https://api.github.com/repos/{gns}/{api_by}',
                                                                      params=params,
                                                                      headers=headers,
                                                                      is_json=True)

                if soft.latest:
                    if data_r['draft'] is False and data_r['prerelease'] is False:
                        if soft.assets:
                            vhlp.append(data_r['tag_name'], raw_data={'tag_name': data_r['tag_name'], 'assets': data_r['assets']})
                        else:
                            vhlp.append(data_r['tag_name'])

                        if soft.assets:
                            rdata = vhlp.latest_version.raw_data

                            if isinstance(rdata['assets'], List):
                                for v in rdata['assets']:
                                    vhlp.add_download_url(v['browser_download_url'])
                else:
                    for v in data_r:
                        if soft.release:
                            if v['draft'] is False and v['prerelease'] is False:
                                if soft.assets:
                                    vhlp.append(v['tag_name'], raw_data={'tag_name': v['tag_name'], 'assets': v['assets']})
                                else:
                                    vhlp.append(v['tag_name'])
                        else:
                            vhlp.append(v['name'])

                    # Do you want to download the assets' attachment?
                    if soft.release and soft.assets:
                        rdata = vhlp.latest_version.raw_data

                        if isinstance(rdata['assets'], List):
                            for v in rdata['assets']:
                                vhlp.add_download_url(v['browser_download_url'])

        if vhlp.is_empty:
            logger.warning(f'[{soft.name}] versions is empty.')
            return

        logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

        if soft.split > 0:
            logger.debug(f'Split Versions: {vhlp.split_versions}')

        # Write data to file.
        await self.write(soft, vhlp.summary)
