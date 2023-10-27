from __future__ import annotations

import json
import uuid
from typing import List

from pydantic import BaseModel
from loguru import logger

from app.core.config import AppSettingSoftItem
from app.core.version import VersionHelper
from . import Assistant


class Daystart(BaseModel):
    elapsed_seconds: int
    elapsed_days: int


class UrlItem(BaseModel):
    codebase: str


class Urls(BaseModel):
    url: List[UrlItem]


class PackageItem(BaseModel):
    hash_sha256: str
    size: int
    name: str
    fp: str
    required: bool
    hash: str


class Packages(BaseModel):
    package: List[PackageItem]


class Manifest(BaseModel):
    arguments: str
    version: str
    packages: Packages


class Updatecheck(BaseModel):
    status: str
    urls: Urls
    manifest: Manifest


class AppItem(BaseModel):
    appid: str
    cohort: str
    status: str
    cohortname: str
    updatecheck: Updatecheck


class Response(BaseModel):
    server: str
    protocol: str
    daystart: Daystart
    app: List[AppItem]


class Model(BaseModel):
    response: Response


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
        # See <https://chromium.googlesource.com/chromium/src.git/+/master/docs/updater/protocol_3_1.md>

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

        # Stable supplement.
        url, http_status_code, _, data_s = await assist.post('https://update.googleapis.com/service/update2/json', json={
            'request': {
                'domainjoined': False,
                'hw': {
                    'avx': True,
                    'physmemory': 32,
                    'sse': True,
                    'sse2': True,
                    'sse3': True,
                    'sse41': True,
                    'sse42': True,
                    'ssse3': True
                },
                'ismachine': True,
                'nacl_arch': 'x86-64',
                'os': {
                    'arch': 'x86_64',
                    'platform': 'Windows',
                    'version': '10.0.19045.3570'
                },
                'protocol': '3.1',
                'requestid': f'{str(uuid.uuid1())}',
                'sessionid': f'{str(uuid.uuid1())}',
                'app': [{
                    'appid': '{8A69D345-D564-463C-AFF1-A69D9E530F96}',
                    'release_channel': 'stable',
                    'brand': 'GCEB',
                    'lang': '',
                    'updatecheck': {},
                    'version': '5.0.375',
                    'installsource': 'ondemand',
                }]
            }
        }, headers={'Content-Type': 'application/json', 'X-Goog-Update-Interactivity': 'fg'}, is_json=False)

        data = Model.model_validate(json.loads(data_s[4:]))

        logger.info(f'Protocol: {data.response.protocol} Stable Version: {data.response.app[0].updatecheck.manifest.version}')

        vhlp.add(data.response.app[0].updatecheck.manifest.version)

        # Perform actions such as sorting.
        vhlp.done()

        # Output JSON file.
        await assist.create(name=item.name,
                            url=item.url if item.url else 'https://www.google.com/chrome/',
                            version=vhlp.latest,
                            all_versions=vhlp.versions,
                            download_links=vhlp.download_links)
