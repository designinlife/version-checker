from pathlib import Path
from typing import List

from app.core.config import AppSettingSoftItem
from app.core.version import VersionSummary
from . import UrlMakerBase


class UrlMaker(UrlMakerBase):
    def build_links(self, soft: AppSettingSoftItem, version_summary: VersionSummary, urls: List[str]) -> List[str]:
        r = []

        latest = version_summary.latest

        for url in urls:
            if 'amd64' in url and 'rootfs' in url and url.endswith('.tar.zst'):
                r.append(f'{url}#{latest.version}|{Path(url).name}')

        return r
