import os

import aiohttp
from loguru import logger

from app.core.config import AppSettingSoftItem
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    github_token = os.environ.get("GITHUB_TOKEN")

    headers = {}

    if github_token:
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {github_token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

        logger.debug('Using GITHUB_TOKEN env.')

    download_links = []

    if item.by_tag:
        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get(f'https://api.github.com/repos/{item.repo}/releases/tags/{item.by_tag}',
                                                            headers=headers,
                                                            is_json=True)

        for v2 in data_r['assets']:
            download_links.append(v2['browser_download_url'])

        # Output JSON file.
        await assist.create(name=item.name,
                            url=f'https://github.com/{item.repo}/releases/tag/{item.by_tag}',
                            version=data_r['name'],
                            all_versions=[data_r['name']],
                            download_links=download_links)
    else:
        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get(f'https://api.github.com/repos/{item.repo}/releases',
                                                            params={'per_page': '100'},
                                                            headers=headers,
                                                            is_json=True)

        if len(data_r) > 0:
            data = data_r[0]

            download_links = []

            for v2 in data['assets']:
                download_links.append(v2['browser_download_url'])

            # Output JSON file.
            await assist.create(name=item.name,
                                url=f'https://github.com/{item.repo}',
                                version=data['name'],
                                all_versions=[data['name']],
                                download_links=download_links)
