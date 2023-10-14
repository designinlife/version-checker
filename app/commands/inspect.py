import click
from click.core import Context
from loguru import logger

from app.core.config import Configuration
from app.inspect import InspectRunner


@click.command('inspect', help='Batch check the latest release version number of the software.')
@click.pass_obj
@click.pass_context
def cli(ctx: Context, cfg: Configuration):
    logger.info(f'app cli inspect called. (Working directory: {cfg.workdir} | Title: {cfg.settings.app.title})')

    ir = InspectRunner(ctx, cfg)
    ir.start()
