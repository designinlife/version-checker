import json

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    # Create VersionHelper instance.
    vhlp = VersionHelper(pattern=item.tag_pattern, download_urls=item.download_urls, split_mode=item.split_mode)

    # Make an HTTP request.
    url, http_status_code, _, data_s = await assist.get(f'https://raw.githubusercontent.com/docker-library/{item.name}/master/versions.json')

    data_r = json.loads(data_s)

    for _, v in data_r.items():
        if v and 'version' in v:
            vhlp.add(v['version'])

    # Perform actions such as sorting.
    vhlp.done()

    if item.split_mode > 0:
        for k, v in vhlp.versions.items():
            # Output JSON file.
            await assist.create(name=f'{item.name}-{k}',
                                url=item.url if item.url else 'https://github.com/',
                                version=v.latest,
                                all_versions=v.versions,
                                download_links=v.download_links)
    else:
        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://github.com/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
