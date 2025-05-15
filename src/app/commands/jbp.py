import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
from xml.dom import minidom

import click
import requests
from click.core import Context
from pydantic import BaseModel, Field
from urllib.parse import urlparse

from app.core.config import Configuration


class JetbrainPluginExtra(BaseModel):
    until: str
    since: str
    xml_id: str


class JetbrainPlugin(BaseModel):
    display_name: str
    latest: str
    download_urls: List[str] = Field(default_factory=list)
    jbp_extra: JetbrainPluginExtra = Field(default=None, alias='jbp_extra')


class IdeaVersion(BaseModel):
    since_build: str
    until_build: str


class Plugin(BaseModel):
    id: str
    url: str
    version: str
    name: str
    idea_version: IdeaVersion


class Plugins(BaseModel):
    plugin: List[Plugin] = Field(default_factory=list)


def pydantic_to_xml(plugins_data: Plugins) -> str:
    root = ET.Element("plugins")

    for plugin_data in plugins_data.plugin:
        plugin_elem = ET.SubElement(root, "plugin")
        plugin_elem.set("id", plugin_data.id)
        plugin_elem.set("url", plugin_data.url)
        plugin_elem.set("version", plugin_data.version)

        name_elem = ET.SubElement(plugin_elem, 'name')
        name_elem.text = plugin_data.name

        idea_version_elem = ET.SubElement(plugin_elem, "idea-version")
        idea_version_elem.set("since-build", plugin_data.idea_version.since_build)
        if plugin_data.idea_version.until_build:
            idea_version_elem.set('until-build', plugin_data.idea_version.until_build)

    rough_string = ET.tostring(root, encoding="utf-8", method="xml", xml_declaration=True)
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ", encoding="utf-8")

    return pretty_xml.decode(encoding='utf-8')


@click.command('jbp', help='Generate Jetbrains Plugin Repository Update xml file.\n\nSupported environment variables:\n\nHTTPS_PROXY, DOWNLOAD_URL')
@click.option('-o', '--output', 'output', help='Output file name.')
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, output: str):
    data_url = 'https://raw.githubusercontent.com/designinlife/version-checker/main/data/all.json'

    r = requests.get(data_url, proxies={'https': os.environ.get('HTTPS_PROXY')}, timeout=10)
    r.raise_for_status()

    data_r = r.json()

    plugins = Plugins()

    for v in data_r:
        if 'jbp_extra' in v and v['jbp_extra'] is not None:
            v_data = JetbrainPlugin(**v)

            plugins.plugin.append(Plugin(id=v_data.jbp_extra.xml_id,
                                         url=f'{os.environ.get('DOWNLOAD_URL', 'https://www.example.com/')}{urlparse(os.path.basename(v_data.download_urls[0])).fragment}',
                                         version=v_data.latest,
                                         name=v_data.display_name.replace('Jetbrains Plugin: ', ''),
                                         idea_version=IdeaVersion(since_build=v_data.jbp_extra.since, until_build=v_data.jbp_extra.until)))

    if output is not None:
        output_p = Path(output)

        output_dir = output_p.parent
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_p, 'w') as f:
            f.write(pydantic_to_xml(plugins))
        return
    else:
        print(pydantic_to_xml(plugins))
