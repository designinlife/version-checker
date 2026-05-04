import unittest

from app.parser import check_requirements
from app.parser.gh import Parser


class ParserTestCase(unittest.TestCase):
    def test_check_requirements_supports_major_and_minor(self):
        self.assertTrue(check_requirements("major >= 6 && minor < 5", major=6, minor=4))
        self.assertFalse(check_requirements("major >= 6 && minor < 5", major=6, minor=5))

    def test_github_asset_pattern_matching(self):
        parser = Parser.__new__(Parser)

        self.assertTrue(parser._check_assets_allowed([r".*windows.*x86_64.*\.zip$"], "tool-windows-x86_64.zip"))
        self.assertFalse(parser._check_assets_allowed([r".*windows.*x86_64.*\.zip$"], "tool-linux-x86_64.tar.gz"))
