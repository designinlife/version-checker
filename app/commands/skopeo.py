import os
from typing import List

import click
import requests
from click.core import Context
from loguru import logger

from app.core.config import Configuration


@click.command('skopeo', help='Generate skopeo copy command script.')
@click.option('-o', '--output', 'output', help='Output file name.', required=True)
@click.option('-r', '--repo', 'repo_name', help='Filter by repo.')
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, output: str, repo_name: str | None):
    logger.debug(f'app cli skopeo called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    http_proxy = os.environ.get('HTTPS_PROXY', None)
    docker_registry_host = os.environ.get('DOCKER_REGISTRY_HOST', 'harbor.stone.cs')

    r = requests.get('https://raw.githubusercontent.com/designinlife/version-checker/main/data/all.json',
                     proxies={'https_proxy': http_proxy},
                     headers={'Content-Type': 'application/json'})
    r.raise_for_status()
    data = r.json()

    if isinstance(data, List):
        with open(output, 'w') as f:
            for v in data:
                if 'tags' in v and v['name'].startswith('docker-'):
                    if not repo_name or repo_name == v['repo']:
                        for v2 in v['tags']:
                            if v2['name'].startswith('sha256') or v2['name'].endswith('-ubi') or v2['name'].endswith('-ent') \
                                    or 'debug' in v2['name'].lower() or 'rc' in v2['name'].lower() or 'beta' in v2['name'].lower() \
                                    or 'alpha' in v2['name'].lower() \
                                    or 'arm' in v2['name'] or 'amd' in v2['name'] or 'windows' in v2['name'] or 'nightly' in v2['name'] \
                                    or 'rootless' in v2['name'] or 'builder' in v2['name']:
                                continue

                            f.write(f'{f'HTTPS_PROXY={http_proxy} ' if http_proxy else ''}'
                                    'skopeo copy '
                                    f'docker://docker.io/{v['repo']}:{v2['name']} '
                                    f'docker://{docker_registry_host}/{v['repo']}:{v2['name']}\n')
