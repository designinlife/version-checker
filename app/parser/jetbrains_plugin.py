from asyncio import Semaphore
from typing import Optional, List

from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import JetbrainsPluginSoftware
from app.core.version import VersionHelper
from . import Base


class JetbrainPluginInfo(BaseModel):
    id: int
    link: str
    name: str
    approve: bool
    xmlId: str


class JetbrainPluginVersion(BaseModel):
    id: int
    link: str
    version: str
    approve: bool
    listed: bool
    hidden: bool
    recalculate_compatibility_allowed: bool = Field(..., alias='recalculateCompatibilityAllowed')
    cdate: str
    file: str
    since: str
    until: str
    since_until: str = Field(..., alias='sinceUntil')
    channel: Optional[str] = None
    size: int
    downloads: int
    plugin_id: int = Field(..., alias='pluginId')


class JetbrainPluginList(BaseModel):
    versions: List[JetbrainPluginVersion]

    model_config = {
        "arbitrary_types_allowed": True
    }


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: JetbrainsPluginSoftware):
        # logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            # Make an HTTP request.
            _, status, _, data_r = await self.request('GET', f'https://plugins.jetbrains.com/api/plugins/{soft.plugin_id}', is_json=True)

            plugin_info = JetbrainPluginInfo(**data_r)

            soft.display_name = f'Jetbrains Plugin: {plugin_info.name}'
            soft.url = f'https://plugins.jetbrains.com{plugin_info.link}'

            additional = {'data_type': 'jbp', 'xml_id': plugin_info.xmlId}

            _, status, _, data_r = await self.request('GET',
                                                      f'https://plugins.jetbrains.com/api/plugins/{soft.plugin_id}/updates',
                                                      params={
                                                          'channel': '',
                                                          'page': '1',
                                                          'size': soft.size},
                                                      is_json=True)

            if isinstance(data_r, List):
                vlist = JetbrainPluginList(versions=data_r)

                for vitem in vlist.versions:
                    vhlp.append(vitem.version, vitem)

            last_raw_data = vhlp.summary.latest.raw_data

            if isinstance(last_raw_data, JetbrainPluginVersion):
                additional['since'] = last_raw_data.since
                additional['until'] = last_raw_data.until

                vhlp.add_download_url(f'https://downloads.marketplace.jetbrains.com/files/{last_raw_data.file}')

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            # Write data to file.
            await self.write(soft, version_summary=vhlp.summary, storage_dir='jetbrains/plugins', jbp_extra=additional)
