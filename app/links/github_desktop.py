from typing import List

from app.core.version import Version


class LinkAssembler:
    def __init__(self):
        ...

    @staticmethod
    def assemble(version: Version, download_urls: List[str]) -> List[str]:
        r = []

        for v in download_urls:
            if 'win32' in v:
                r.append(f'{v.format(version=version.semver)}#GitHubDesktopSetup-x64-{version.semver}.exe')
            elif 'darwin' in v:
                r.append(f'{v.format(version=version.semver)}#GitHubDesktop-x64-{version.semver}.zip')

        return r
