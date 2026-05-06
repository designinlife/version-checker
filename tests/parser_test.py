import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from app.core.config import Configuration, GithubSoftware
from app.core.version import VersionHelper
from app.parser import Base, check_requirements
from app.parser.gh import Parser


class ParserTestCase(unittest.TestCase):
    def _fake_parser(self, workdir: str | None = None):
        class FakeParser(Base):
            async def handle(self, _sem, _soft):
                raise NotImplementedError

        parser = FakeParser.__new__(FakeParser)
        parser.cfg = Configuration(workdir=workdir)
        return parser

    def test_cache_ttl_hours_uses_env_value(self):
        from app.parser import get_cache_ttl_hours

        with patch.dict(os.environ, {"VERSION_CHECKER_CACHE_TTL_HOURS": "3"}, clear=True):
            self.assertEqual(3, get_cache_ttl_hours())

    def test_cache_ttl_hours_falls_back_to_default(self):
        from app.parser import get_cache_ttl_hours

        with patch.dict(os.environ, {"VERSION_CHECKER_CACHE_TTL_HOURS": "bad"}, clear=True):
            self.assertEqual(1, get_cache_ttl_hours())

    def test_check_requirements_supports_major_and_minor(self):
        self.assertTrue(check_requirements("major >= 6 && minor < 5", major=6, minor=4))
        self.assertFalse(check_requirements("major >= 6 && minor < 5", major=6, minor=5))

    def test_github_asset_pattern_matching(self):
        parser = Parser.__new__(Parser)

        self.assertTrue(parser._check_assets_allowed([r".*windows.*x86_64.*\.zip$"], "tool-windows-x86_64.zip"))
        self.assertFalse(parser._check_assets_allowed([r".*windows.*x86_64.*\.zip$"], "tool-linux-x86_64.tar.gz"))

    def test_github_latest_assets_are_appended_once(self):
        parser = Parser.__new__(Parser)
        soft = GithubSoftware(
            name="demo",
            repo="owner/demo",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
            release=True,
            assets=True,
        )
        helper = VersionHelper(pattern=soft.pattern, download_urls=[])

        helper.append(
            "v1.0.0",
            raw_data={
                "assets": [
                    {"browser_download_url": "https://example.com/old.zip"},
                ]
            },
        )
        helper.append(
            "v2.0.0",
            raw_data={
                "assets": [
                    {"browser_download_url": "https://example.com/new.zip"},
                    {"browser_download_url": "https://example.com/new.zip"},
                ]
            },
        )

        parser._append_latest_assets(soft, helper)

        self.assertEqual(["https://example.com/new.zip"], helper.download_urls)

    def test_dynamic_download_urls_fall_back_when_link_maker_contract_invalid(self):
        parser = self._fake_parser()
        soft = GithubSoftware(
            name="demo",
            repo="owner/demo",
            pattern=r"^v(?P<version>(?P<major>\d+))$",
            download_dynamic=True,
        )
        summary = VersionHelper(pattern=soft.pattern, download_urls=["https://example.com/{version}.zip"])
        summary.append("v1")
        version_summary = summary.summary

        class InvalidUrlMaker:
            def __init__(self, _cfg):
                pass

        with patch("app.parser.importlib.import_module") as import_module:
            import_module.return_value.UrlMaker = InvalidUrlMaker
            urls = parser._build_download_urls(soft, version_summary, ["https://example.com/1.zip"])

        self.assertEqual(["https://example.com/1.zip"], urls)

    def test_base_write_outputs_split_summaries_and_skips_failed_condition(self):
        with tempfile.TemporaryDirectory() as tmp:
            parser = self._fake_parser(workdir=tmp)
            soft = GithubSoftware(
                name="demo",
                repo="owner/demo",
                url="https://example.com/demo",
                display_name="Demo",
                pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+))$",
                condition="major >= 2",
            )
            helper = VersionHelper(pattern=soft.pattern, split=1)
            helper.append("1.0")
            helper.append("2.0")

            asyncio.run(parser.write(soft, helper.summary, storage_dir="tools"))

            output_dir = os.path.join(tmp, "data")
            skipped_path = os.path.join(output_dir, "demo-1.json")
            written_path = os.path.join(output_dir, "demo-2.json")
            data = json.loads(open(written_path, encoding="utf-8").read())

        self.assertFalse(os.path.exists(skipped_path))
        self.assertEqual("demo-2", data["name"])
        self.assertEqual("Demo", data["display_name"])
        self.assertEqual("2.0", data["latest"])
        self.assertEqual("tools", data["storage_dir"])

    def test_base_is_expired_reads_default_and_split_output_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = os.path.join(tmp, "data")
            os.makedirs(output_dir)
            created_time = "2026-05-06 08:00:00"
            with open(os.path.join(output_dir, "demo.json"), "w", encoding="utf-8") as f:
                json.dump({"created_time": created_time}, f)
            with open(os.path.join(output_dir, "split-2.json"), "w", encoding="utf-8") as f:
                json.dump({"created_time": created_time}, f)

            parser = self._fake_parser(workdir=tmp)
            soft = GithubSoftware(name="demo", repo="owner/demo", pattern=r"^(?P<version>(?P<major>\d+))$")
            split_soft = GithubSoftware(name="split", repo="owner/split", pattern=r"^(?P<version>(?P<major>\d+))$", split=1)

            with (
                patch("app.parser.arrow.now") as now,
                patch.dict(os.environ, {"VERSION_CHECKER_CACHE_TTL_HOURS": "2"}, clear=False),
            ):
                now.return_value.shift.return_value = now.return_value
                now.return_value.__ge__.return_value = False
                is_expired, last_update = parser.is_expired(soft)
                split_is_expired, split_last_update = parser.is_expired(split_soft)

        self.assertFalse(is_expired)
        self.assertEqual(created_time, last_update)
        self.assertFalse(split_is_expired)
        self.assertEqual(created_time, split_last_update)

    def test_base_wrap_handle_converts_exceptions_to_failed_result(self):
        class FailingParser(Base):
            async def handle(self, _sem, _soft):
                raise RuntimeError("boom")

        parser = FailingParser(Configuration())
        soft = GithubSoftware(name="demo", repo="owner/demo", pattern=r"^(?P<version>(?P<major>\d+))$")

        result = asyncio.run(parser.wrap_handle(asyncio.Semaphore(1), soft))

        self.assertEqual("demo", result.name)
        self.assertEqual("RuntimeError", result.error_type)
        self.assertEqual("boom", result.message)
