from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        if item.code == 'workstation':
            await Parser.vmware_workstation(assist, item)
        elif item.code == 'esxi':
            await Parser.vmware_esxi(assist, item)
        elif item.code == 'vsphere':
            await Parser.vmware_vsphere(assist, item)
        else:
            raise ValueError(f'Invalid product code. ({item.code})')

    @staticmethod
    async def vmware_workstation(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^VMware Workstation (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)) Pro for Windows$')

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get('https://www.virten.net/repo/vTracker.json', is_json=True)

        cache_links = {}

        for v in data_r['data']['vTracker']:
            grp = vhlp.fetch_groups(v['product'])

            if grp:
                vhlp.add(v['product'])

                if grp['version'] not in cache_links:
                    cache_links[grp['version']] = v['downloadLink']

        # Perform actions such as sorting.
        vhlp.done()

        download_links = []

        if vhlp.latest in cache_links:
            download_links.append(cache_links[vhlp.latest])

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.vmware.com/products/workstation-pro.html',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=download_links)

    @staticmethod
    async def vmware_esxi(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^VMware ESXi (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))(?:.*)$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get('https://www.virten.net/repo/vTracker.json', is_json=True)

        for v in data_r['data']['vTracker']:
            vhlp.add(v['product'])

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.vmware.com/products/vsphere.html',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)

    @staticmethod
    async def vmware_vsphere(assist: Assistant, item: AppSettingSoftItem):
        # Create VersionHelper instance.
        vhlp = VersionHelper(name=item.name, pattern=r'^VMware vSphere Hypervisor \(ESXi\) (?P<version>(?P<major>\d+)\.(?P<minor>\d)[a-zA-Z](?P<patch>\d+))$',
                             download_urls=item.download_urls)

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get('https://www.virten.net/repo/vTracker.json', is_json=True)

        for v in data_r['data']['vTracker']:
            vhlp.add(v['product'])

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.vmware.com/products/vsphere.html',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
