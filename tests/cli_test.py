import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class CliEnvTestCase(unittest.TestCase):
    def test_configuration_accepts_legacy_slient_key(self):
        from app.core.config import Configuration

        cfg = Configuration.model_validate({"slient": True})

        self.assertTrue(cfg.silent)

    def test_cli_import_ignores_non_boolean_debug_value(self):
        sys.modules.pop("app.cli", None)

        with patch.dict(os.environ, {"DEBUG": "release"}, clear=False):
            module = importlib.import_module("app.cli")

        self.assertTrue(hasattr(module, "start"))

    def test_cli_accepts_silent_option(self):
        from click.testing import CliRunner

        from app.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("version-checker.toml").write_text('[app]\ntitle = "test"\n', encoding="utf-8")

            result = runner.invoke(cli, ["--silent", "version"])

        self.assertEqual(0, result.exit_code)

    def test_cli_keeps_slient_option_for_compatibility(self):
        from click.testing import CliRunner

        from app.cli import cli

        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("version-checker.toml").write_text('[app]\ntitle = "test"\n', encoding="utf-8")

            result = runner.invoke(cli, ["--slient", "version"])

        self.assertEqual(0, result.exit_code)
