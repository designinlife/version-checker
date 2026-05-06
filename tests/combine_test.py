import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from app.commands.combine import cli as combine_cli
from app.core.config import AppSetting, AppSettingBase, Configuration


def write_demo_data(tmp: str):
    data_dir = Path(tmp).joinpath("data")
    data_dir.mkdir()
    data_dir.joinpath("demo.json").write_text(
        json.dumps(
            {
                "name": "demo",
                "url": "https://example.com",
                "latest": "1.0.0",
                "versions": ["1.0.0"],
                "created_time": "2026-01-01 00:00:00",
            }
        ),
        encoding="utf-8",
    )
    data_dir.joinpath("all.json").write_text(
        json.dumps(
            [
                {
                    "name": "demo",
                    "url": "https://example.com",
                    "latest": "0.9.0",
                    "versions": ["0.9.0"],
                    "created_time": "2026-01-01 00:00:00",
                }
            ]
        ),
        encoding="utf-8",
    )


class CombineCliTestCase(unittest.TestCase):
    def test_combine_does_not_send_email_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_demo_data(tmp)

            cfg = Configuration(workdir=tmp, settings=AppSetting(app=AppSettingBase(title="test")))
            runner = CliRunner()

            with patch("app.commands.combine.send_mail") as send_mail:
                result = runner.invoke(combine_cli, [], obj=cfg)

        self.assertEqual(0, result.exit_code)
        send_mail.assert_not_called()

    def test_combine_notify_missing_template_does_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_demo_data(tmp)

            cfg = Configuration(workdir=tmp, settings=AppSetting(app=AppSettingBase(title="test")))
            runner = CliRunner()

            result = runner.invoke(combine_cli, ["--notify"], obj=cfg)

        self.assertEqual(0, result.exit_code)
