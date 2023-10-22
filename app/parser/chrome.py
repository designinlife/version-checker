from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # See <https://www.chromium.org/getting-involved/download-chromium/#downloading-old-builds-of-chrome-chromium>
        # See <https://developer.chrome.com/docs/versionhistory/>
        # See <https://github.com/Bugazelle/chromium-all-old-stable-versions/blob/master/src/chromium.py>
        # See <https://serpapi.com/>
        # See <https://cloud.google.com/storage/docs/json_api/v1/objects/list>
        # See <https://omahaproxy.appspot.com/all.json?channel=stable>
        # See <https://chromium.cypress.io/>

        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\.(?P<fix>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get(
            'https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/stable/versions/all/releases',
            is_json=True)

        if isinstance(data_r, dict) and 'releases' in data_r:
            for v in data_r['releases']:
                vhlp.add(v['version'])

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.google.com/chrome/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
