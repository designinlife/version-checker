from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


async def parse(assist: Assistant, item: AppSettingSoftItem):
    # Create VersionHelper instance.
    vhlp = VersionHelper(pattern=item.tag_pattern, download_urls=item.download_urls, split_mode=item.split_mode)

    ns, name = item.repo.split('/')

    # Make an HTTP request.
    url, http_status_code, _, data_r = await assist.get(f'https://hub.docker.com/v2/namespaces/{ns}/repositories/{name}/tags',
                                                        params={'page_size': '100'},
                                                        is_json=True)

    if 'results' in data_r and isinstance(data_r['results'], list):
        for v in data_r['results']:
            vhlp.add(v['name'])

        # Perform actions such as sorting.
        vhlp.done()

        if item.split_mode > 0:
            for k, v in vhlp.versions.items():
                # Output JSON file.
                await assist.create(name=f'{item.name}-{k}',
                                    url=item.url if item.url else 'https://hub.docker.com/',
                                    version=v.latest,
                                    all_versions=v.versions,
                                    download_links=v.download_links)
        else:
            # Output JSON file.
            await assist.create(name=item.name,
                                url=item.url if item.url else 'https://hub.docker.com/',
                                version=vhlp.latest,
                                all_versions=vhlp.versions,
                                download_links=vhlp.download_links)
