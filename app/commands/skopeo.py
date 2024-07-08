import os
import subprocess
from typing import List

import arrow
import click
import requests
from click.core import Context
from loguru import logger

from app.core.config import Configuration


@click.command('skopeo', help='Generate skopeo copy command script.')
@click.option('-o', '--output', 'output', help='Output file name.')
@click.option('-r', '--repo', 'repo_name', help='Filter by repo.')
@click.option('--since', 'since_time', help='Filter by tag pushed time. (Format: YYYY-MM-DD HH:mm:ss)')
@click.option('--latest', 'is_latest_only', help='Only latest version?', is_flag=True)
@click.option('--dry-run', 'is_dry_run', help='Do you want to debug and run? (Only print commands to the console)', is_flag=True)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, output: str, repo_name: str | None, since_time: str | None, is_latest_only: bool, is_dry_run: bool):
    logger.debug(f'app cli skopeo called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    http_proxy = os.environ.get('HTTPS_PROXY', None)
    docker_registry_host = os.environ.get('DOCKER_REGISTRY_HOST', 'harbor.stone.cs')

    r = requests.get('https://raw.githubusercontent.com/designinlife/version-checker/main/data/all.json',
                     proxies={'https_proxy': http_proxy},
                     headers={'Content-Type': 'application/json'})
    r.raise_for_status()
    data = r.json()

    cmds = []

    if isinstance(data, List):
        for v in data:
            if 'tags' in v and v['name'].startswith('docker-'):
                if is_latest_only:
                    for v2 in v['latest']:
                        cmds.append(f'{f'HTTPS_PROXY={http_proxy} ' if http_proxy else ''}skopeo copy '
                                    f'docker://docker.io/{v['repo']}:{v2} '
                                    f'docker://{docker_registry_host}/{v['repo']}:{v2}')

                        for v3 in v['suffix']:
                            cmds.append(f'{f'HTTPS_PROXY={http_proxy} ' if http_proxy else ''}'
                                        f'skopeo copy docker://docker.io/{v['repo']}:{v2}{v3} docker://{docker_registry_host}/{v['repo']}:{v2}{v3}')
                else:
                    if not repo_name or repo_name == v['repo']:
                        for v2 in v['tags']:
                            if v2['name'].startswith('sha256') or v2['name'].endswith('-ubi') or v2['name'].endswith('-ent') \
                                    or 'debug' in v2['name'].lower() or 'rc' in v2['name'].lower() or 'beta' in v2['name'].lower() \
                                    or 'alpha' in v2['name'].lower() \
                                    or 'arm' in v2['name'] or 'amd' in v2['name'] or 'windows' in v2['name'] or 'nightly' in v2['name'] \
                                    or 'rootless' in v2['name'] or 'builder' in v2['name']:
                                continue

                            # 按 Tag 推送时间过滤
                            tag_pushed_time = arrow.get(v2['tag_last_pushed'], tzinfo='UTC').to(tz='Asia/Shanghai')

                            if since_time and tag_pushed_time < arrow.get(since_time, 'YYYY-MM-DD HH:mm:ss', tzinfo='Asia/Shanghai'):
                                continue

                            cmds.append(f'{f'HTTPS_PROXY={http_proxy} ' if http_proxy else ''}'
                                        f'DT={tag_pushed_time.format('YYYY-MM-DD')} '
                                        'skopeo copy '
                                        f'docker://docker.io/{v['repo']}:{v2['name']} '
                                        f'docker://{docker_registry_host}/{v['repo']}:{v2['name']}\n')

    if cmds:
        if is_dry_run:
            print('\n'.join(cmds))
        elif output:
            with open(output, 'w') as f:
                f.write('#!/bin/bash\n\n')
                f.write('set -x\n\n')
                f.write('\n'.join(cmds))

            logger.info(f'Output file: {output}')
        else:
            for cmd in cmds:
                subprocess.run(cmd, shell=True)
