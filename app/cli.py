#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tomllib
from pathlib import Path

import click
from dotenv import load_dotenv
from loguru import logger

from app import __version__
from app.commands.combine import cli as cli_combine
from app.commands.inspect import cli as cli_inspect
from app.core.click import ClickStdOption
from app.core.config import Configuration, AppSetting
from app.core.utils import strtobool

logger.remove()
logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level='ERROR', backtrace=True,
           diagnose=False)

# The following code adds a filter so that the STDOUT pipe does not print exception information!
if strtobool(os.environ.get('DEBUG', 'false')):
    logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               filter=lambda record: record["level"].no < 40, level='DEBUG')

    load_dotenv('.env.dev')

    logger.info('Mode: Debug')
else:
    logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               filter=lambda record: record["level"].no < 40, level='INFO')

    load_dotenv()

    logger.info('Mode: Production')


@click.group(context_settings={'max_content_width': 120}, help='\x1b[38;5;121mPython CLI Tools %s\x1b[0m' % __version__)
@click.option('-c', 'config_file', help='Configuration file name.', type=click.Path(), default='version-checker.toml',
              cls=ClickStdOption)
@click.option('--slient', 'slient', help='Turn on silent mode?', is_flag=True)
@click.option('--debug', 'debug', help='Turn on debug mode?', is_flag=True)
@click.option('--log', 'log', help='Specifies the log file path.', cls=ClickStdOption)
@click.option('--disable-log-time', 'disable_log_time', help='Block log time.', is_flag=True)
@click.option('-v', 'verbose', help='Log display level. (-v,-vv,-vvv)', count=True, default=0)
@click.pass_context
def cli(ctx, **kwargs):
    cfg = Configuration.model_validate(kwargs)

    cfg.workdir = os.getcwd()

    ctx.obj = cfg

    # 解析配置文件
    if not cfg.config_file:
        logger.critical('No configuration file specified.')

    if not Path(cfg.config_file).is_file():
        logger.critical('Configuration file does not exist.')

    logger.debug('Configuration file loaded: %s' % cfg.config_file)

    with open(cfg.config_file, 'r', encoding='utf-8') as f:
        cfg_dict = tomllib.loads(f.read())
        ctx.obj.settings = AppSetting.model_validate(cfg_dict)

        logger.debug(ctx.obj.settings.model_dump_json())


@cli.command('version', help='Print versions.')
def app_version():
    print('version-checker v%s' % (__version__,))


# noinspection PyTypeChecker
cli.add_command(cli_combine)
# noinspection PyTypeChecker
cli.add_command(cli_inspect)


def start():
    cli()


if __name__ == '__main__':
    cli()
