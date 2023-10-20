from app.core.config import AppSettingSoftItem
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        all_versions = []
        download_links = []

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get(f'https://sourceforge.net/projects/{item.name}/best_release.json', is_json=True)

        filename_parts = f"{data_r['release']['filename']}".split('/')

        latest_version = filename_parts[1]
        all_versions.append(latest_version)
        download_links.append(data_r['release']['url'])

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else f'https://sourceforge.net/projects/{item.name}/',
                            version=latest_version,
                            all_versions=all_versions,
                            download_links=download_links)
