import importlib
import os
import sys
import unittest
from unittest.mock import patch


class CliEnvTestCase(unittest.TestCase):
    def test_cli_import_ignores_non_boolean_debug_value(self):
        sys.modules.pop("app.cli", None)

        with patch.dict(os.environ, {"DEBUG": "release"}, clear=False):
            module = importlib.import_module("app.cli")

        self.assertTrue(hasattr(module, "start"))
