from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=item.tag_pattern, download_urls=item.download_urls, split_mode=2)

        # Make an HTTP request.
        for major in item.major:
            url, http_status_code, _, data_r = await assist.get(f'https://www.php.net/releases/index.php?json&max=-1&version={major}', is_json=True)

            for k, _ in data_r.items():
                vhlp.add(k)

        # Perform actions such as sorting.
        vhlp.done()

        for k, v in vhlp.versions.items():
            # Output JSON file.
            await assist.create(name=f'{item.name}-{k}',
                                url='https://www.php.net/',
                                version=v.latest,
                                all_versions=v.versions,
                                download_links=v.download_links)
