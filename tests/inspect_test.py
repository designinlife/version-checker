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

    def test_process_skips_disabled_items_without_importing_parser(self):
        cfg = Configuration()
        cfg.settings = AppSetting(
            softwares=[
                GithubSoftware(
                    name="disabled",
                    repo="owner/disabled",
                    pattern=r"^(?P<version>(?P<major>\d+))$",
                    disabled=True,
                )
            ]
        )

        with patch("importlib.import_module") as import_module:
            result = asyncio.run(process(cfg, worker_num=1))

        import_module.assert_not_called()
        self.assertEqual(["disabled"], [item.name for item in result.skipped])
        self.assertEqual("Software item is disabled.", result.skipped[0].message)

    def test_process_reports_parser_load_failure_as_item_failure(self):
        cfg = Configuration()
        cfg.settings = AppSetting(softwares=[GithubSoftware(name="bad-parser", repo="owner/bad", pattern=r"^(?P<version>(?P<major>\d+))$")])

        with patch("app.commands.inspect.load_parser_class", side_effect=RuntimeError("missing parser")):
            result = asyncio.run(process(cfg, worker_num=1))

        self.assertEqual(["bad-parser"], [item.name for item in result.failed])
        self.assertEqual("RuntimeError", result.failed[0].error_type)
        self.assertEqual("missing parser", result.failed[0].message)

    def test_cli_default_mode_allows_partial_failure(self):
        async def fake_process(_cfg, _worker_num, _filter_name=None):
            return InspectResult(items=[InspectItemResult.failed("bad", "RuntimeError", "boom")])

        @click.command("combine")
        def fake_combine(notify=False):
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
        def fake_combine(notify=False):
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

    def test_cli_ignores_rate_limit_failure_when_not_debug(self):
        async def fake_process(_cfg, _worker_num, _filter_name=None):
            return InspectResult(items=[InspectItemResult.success("ok")])

        async def fake_rate_limit():
            raise RuntimeError("network down")

        @click.command("combine")
        def fake_combine(notify=False):
            pass

        cfg = Configuration(debug=False, settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()

        with (
            patch("app.commands.inspect.process", side_effect=fake_process),
            patch("app.commands.inspect.GithubHelper.show_rate_limit", side_effect=fake_rate_limit),
            patch("app.commands.inspect.cli_combine", fake_combine),
        ):
            result = runner.invoke(inspect_cli, [], obj=cfg)

        self.assertEqual(0, result.exit_code)

    def test_cli_passes_notify_to_combine(self):
        async def fake_process(_cfg, _worker_num, _filter_name=None):
            return InspectResult(items=[InspectItemResult.success("ok")])

        calls = []

        @click.command("combine")
        def fake_combine(notify=False):
            calls.append(notify)

        cfg = Configuration(debug=True, settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()

        with (
            patch("app.commands.inspect.process", side_effect=fake_process),
            patch("app.commands.inspect.cli_combine", fake_combine),
        ):
            result = runner.invoke(inspect_cli, ["--notify"], obj=cfg)

        self.assertEqual(0, result.exit_code)
        self.assertEqual([True], calls)

    def test_cli_rejects_zero_worker(self):
        cfg = Configuration(debug=True, settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()

        result = runner.invoke(inspect_cli, ["--worker", "0"], obj=cfg)

        self.assertNotEqual(0, result.exit_code)
        self.assertIn("Invalid value for '--worker'", result.output)
