import unittest

from app.parser import check_requirements
from app.parser.gh import Parser
from app.core.config import GithubSoftware
from app.core.version import VersionHelper


class ParserTestCase(unittest.TestCase):
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
