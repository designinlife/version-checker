import os

from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
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

        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=item.tag_pattern, download_urls=item.download_urls, split_mode=item.split_mode)

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get(f'https://api.github.com/repos/{item.repo}/{api_by}',
                                                            params={'per_page': '100'},
                                                            headers=headers,
                                                            is_json=True)

        for v in data_r:
            vname = v['tag_name'] if item.by_release and not item.by_release_name else v['name']
            vhlp.add(vname)

        # Perform actions such as sorting.
        vhlp.done()

        if item.split_mode > 0:
            for k, v in vhlp.versions.items():
                # Output JSON file.
                await assist.create(name=f'{item.name}-{k}',
                                    url=f'https://github.com/{item.repo}',
                                    version=v.latest,
                                    all_versions=v.versions,
                                    download_links=v.download_links)
        else:
            # Output JSON file.
            await assist.create(name=item.name,
                                url=f'https://github.com/{item.repo}',
                                version=vhlp.latest,
                                all_versions=vhlp.versions,
                                download_links=vhlp.download_links)
