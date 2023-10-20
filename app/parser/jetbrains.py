from app.core.config import AppSettingSoftItem
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get('https://data.services.jetbrains.com/products/releases',
                                                            params={'code': item.code, 'latest': 'true', 'type': 'release'},
                                                            is_json=True)

        if item.code in data_r and len(data_r[item.code]) > 0:
            latest = data_r[item.code][0]['version']
            versions = [latest]
            download_links = []

            for k, v in data_r[item.code][0]['downloads'].items():
                if k in ('linux', 'windows', 'mac'):
                    download_links.append(v['link'].replace('https://download.jetbrains.com/', 'https://download-cf.jetbrains.com/'))

            # Output JSON file.
            await assist.create(name=item.name,
                                url=item.url if item.url else 'https://www.jetbrains.com/',
                                version=latest,
                                all_versions=versions,
                                download_links=download_links)
