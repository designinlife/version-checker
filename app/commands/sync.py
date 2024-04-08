from typing import Optional

import click
from click.core import Context
from loguru import logger

from app.core.click import ClickStdOption
from app.core.config import Configuration


@click.command('sync', help='Synchronize software to local directory.')
@click.option('--filter-name', '-i', 'filter_name', help='Filter name.', cls=ClickStdOption)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, filter_name: Optional[str] = None):
    logger.info(f'app cli sync called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')
