import asyncio
import unittest
from unittest.mock import patch

import click
from click.testing import CliRunner

from app.commands.inspect import cli as inspect_cli
from app.commands.inspect import process
from app.core.config import AppSetting, AppSettingBase, Configuration, GithubSoftware
from app.core.inspect_result import InspectItemResult, InspectResult
from app.parser import Base as BaseParser


class InspectProcessTestCase(unittest.TestCase):
    def test_process_keeps_running_after_item_failure(self):
        cfg = Configuration()
        cfg.settings = AppSetting(
            softwares=[
                GithubSoftware(name="bad", repo="owner/bad", pattern=r"^(?P<version>(?P<major>\d+))$"),
                GithubSoftware(name="good", repo="owner/good", pattern=r"^(?P<version>(?P<major>\d+))$"),
            ]
        )

        calls = []

        class FakeParser(BaseParser):
            def __init__(self, _cfg):
                self.cfg = _cfg

            async def wrap_handle(self, _sem, soft):
                calls.append(soft.name)
                if soft.name == "bad":
                    from app.core.inspect_result import InspectItemResult

                    return InspectItemResult.failed("bad", "RuntimeError", "boom")

                from app.core.inspect_result import InspectItemResult

                return InspectItemResult.success("good")

            async def handle(self, _sem, _soft):
                raise NotImplementedError

        with patch("importlib.import_module") as import_module:
            import_module.return_value.Parser = FakeParser
            result = asyncio.run(process(cfg, worker_num=2))

        self.assertEqual(["bad", "good"], calls)
        self.assertEqual(["bad"], [item.name for item in result.failed])
        self.assertEqual(["good"], [item.name for item in result.success])

    def test_cli_default_mode_allows_partial_failure(self):
        async def fake_process(_cfg, _worker_num, _filter_name=None):
            return InspectResult(items=[InspectItemResult.failed("bad", "RuntimeError", "boom")])

        @click.command("combine")
        def fake_combine():
            pass

        cfg = Configuration(debug=True, settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()

        with (
            patch("app.commands.inspect.process", side_effect=fake_process),
            patch("app.commands.inspect.cli_combine", fake_combine),
        ):
            result = runner.invoke(inspect_cli, [], obj=cfg)

        self.assertEqual(0, result.exit_code)

    def test_cli_strict_mode_fails_on_partial_failure(self):
        async def fake_process(_cfg, _worker_num, _filter_name=None):
            return InspectResult(items=[InspectItemResult.failed("bad", "RuntimeError", "boom")])

        @click.command("combine")
        def fake_combine():
            pass

        cfg = Configuration(debug=True, settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()

        with (
            patch("app.commands.inspect.process", side_effect=fake_process),
            patch("app.commands.inspect.cli_combine", fake_combine),
        ):
            result = runner.invoke(inspect_cli, ["--strict"], obj=cfg)

        self.assertNotEqual(0, result.exit_code)
        self.assertIn("Inspect completed with failed item(s).", result.output)
