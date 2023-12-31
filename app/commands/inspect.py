from typing import Optional

import click
from click.core import Context
from loguru import logger

from app.core.click import ClickStdOption
from app.core.config import Configuration
from app.inspect import InspectRunner


@click.command('inspect', help='Batch check the latest release version number of the software.')
@click.option('--filter-name', '-i', 'filter_name', help='Filter name.', cls=ClickStdOption)
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration, filter_name: Optional[str] = None):
    logger.debug(f'app cli inspect called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    ir = InspectRunner(ctx, cfg)
    ir.start(filter_name)
