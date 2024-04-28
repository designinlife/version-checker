from app.core.config import AppSettingSoftItem
from . import Assistant


class Parser:
    @staticmethod
    async def parse(assist: Assistant, item: AppSettingSoftItem):
        all_versions = []
        download_links = []

        # Make an HTTP request.
        url, http_status_code, _, data_r = await assist.get(
            'https://central.github.com/deployments/desktop/desktop/changelog.json', is_json=True)

        latest_version = data_r[0]['version']
        all_versions.append(latest_version)

        download_links.append(
            f'https://central.github.com/deployments/desktop/desktop/latest/win32#GitHubDesktopSetup-x64-{latest_version}.exe')
        download_links.append(
            f'https://central.github.com/deployments/desktop/desktop/latest/darwin#GitHubDesktop-x64-{latest_version}.zip')

        if all_versions and download_links:
            # Output JSON file.
            await assist.create(name=item.name,
                                url='https://desktop.github.com/',
                                version=latest_version,
                                all_versions=all_versions,
                                download_links=download_links)
