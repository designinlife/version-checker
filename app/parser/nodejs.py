from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    # Create VersionHelper instance.
    vhlp = VersionHelper(pattern=item.tag_pattern, download_urls=item.download_urls)

    # Make an HTTP request.
    url, http_status_code, _, data_r = await assist.get('https://nodejs.org/download/release/index.json', is_json=True)

    for v in data_r:
        if 'lts' in v and v['lts'] is not False:
            vhlp.add(v['version'])

    # Perform actions such as sorting.
    vhlp.done()

    latest_version = vhlp.latest
    download_links = vhlp.download_links
    all_versions = vhlp.versions

    # Output JSON file.
    await assist.create(name=item.name,
                        url='https://nodejs.org/',
                        version=latest_version,
                        all_versions=all_versions,
                        download_links=download_links)
