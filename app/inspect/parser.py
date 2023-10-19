import importlib
import re
from typing import List

from app.core.config import AppSettingSoftItem
from app.parser import Assistant


class Parser:
    @staticmethod
    async def create(name: str, assistant: Assistant, item: AppSettingSoftItem):
        module = importlib.import_module('app.parser.%s' % name.replace('-', '_'))
        await module.parse(assistant, item)

    @staticmethod
    def create_download_links(version: str, links: List[str], pattern: str = None) -> List[str]:
        r = []

        if pattern:
            exp = re.compile(pattern)
        else:
            exp = re.compile(r'^(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<patch>\d+))?(.*)$')

        m = exp.match(version)

        if m:
            grpdict = m.groupdict()

            if 'version' not in grpdict:
                grpdict['version'] = version

            for v in links:
                # r.append(v.format(version=version, major=m.group('major'), minor=m.group('minor')))
                r.append(v.format(**grpdict))
        else:
            for v in links:
                r.append(v.format(version=version))

        return r
