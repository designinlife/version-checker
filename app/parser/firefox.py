import re

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^(?P<version>(?P<major>\d{3})\.(?P<minor>\d+)\.(?P<patch>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get('https://product-details.mozilla.org/1.0/firefox.json', is_json=True)

        if 'releases' in data_r and isinstance(data_r['releases'], dict):
            ver_filter = re.compile(r'^(?P<major>\d+)\.(?P<minor>\d+)(?P<patch>[a-z\d]*)$')

            for _, v in data_r['releases'].items():
                if v['category'] != 'dev':
                    m = ver_filter.match(v['version'])

                    if m:
                        grps = m.groupdict()

                        vhlp.add(f'{grps["major"]}.{grps["minor"]}.{v["build_number"]}')

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.mozilla.org/en-US/firefox/new/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
