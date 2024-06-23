import json
from pathlib import Path

import click
from click.core import Context
from loguru import logger

from app.core.config import Configuration


@click.command('combine', help='Merge JSON data into a file.')
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration):
    logger.debug(f'app cli combine called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    # Merge the output JSON data files into all.json.
    p = Path(cfg.workdir).joinpath('data')

    data = []

    for file in p.glob('*.json'):
        if file.name != 'all.json':
            with open(file, 'r', encoding='utf-8') as f:
                data.append(json.loads(f.read()))

    data_w = sorted(data, key=lambda x: x['name'])

    with open(p.joinpath('all.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(data_w, ensure_ascii=True, separators=(',', ':')))

    logger.info('The all.json file has been generated.')
