from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get('https://storage.googleapis.com/flutter_infra_release/releases/releases_windows.json',
                                                            is_json=True)

        if isinstance(data_r, dict) and 'releases' in data_r:
            for v in data_r['releases']:
                if v['channel'] == 'stable':
                    vhlp.add(v['version'])

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://flutter.dev/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
