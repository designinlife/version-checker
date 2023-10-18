import os
import sys
import unittest

from loguru import logger

from app.core.config import Configuration


class MyTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

        logger.remove()
        logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level='ERROR')
        logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level='DEBUG')

        kwargs = {'config_file': 'version-checker.toml', 'slient': False, 'debug': False, 'disable_log_time': False, 'verbose': 0}

        self.cfg = Configuration.model_validate(kwargs)
        self.cfg.workdir = os.getcwd()
