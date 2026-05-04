import unittest

from app.core.version import VersionHelper


class VersionHelperTestCase(unittest.TestCase):
    def test_parse_pattern_sorts_versions_and_formats_download_urls(self):
        helper = VersionHelper(
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
            download_urls=["https://example.com/tool-{version}.zip"],
        )

        helper.append("v1.2.0")
        helper.append("v1.10.0")
        helper.append("invalid")

        summary = helper.summary

        self.assertEqual("1.10.0", summary.latest.version)
        self.assertEqual(["1.10.0", "1.2.0"], [v.version for v in summary.versions])
        self.assertEqual(["https://example.com/tool-1.10.0.zip"], summary.downloads)

    def test_filter_versions_supports_range_conditions(self):
        helper = VersionHelper(
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
            filter_expr=">=1.2.0, <2.0.0",
        )

        helper.append("1.1.9")
        helper.append("1.2.0")
        helper.append("2.0.0")

        self.assertEqual(["1.2.0"], [v.version for v in helper.versions])

    def test_split_versions_groups_by_major(self):
        helper = VersionHelper(
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
            split=1,
        )

        helper.append("1.1.0")
        helper.append("1.2.0")
        helper.append("2.0.0")

        self.assertEqual({"1", "2"}, set(helper.split_versions.keys()))
        self.assertEqual("1.2.0", helper.summary["1"].latest.version)

    def test_summary_raises_clear_error_when_versions_empty(self):
        helper = VersionHelper(pattern=r"^(?P<version>(?P<major>\d+))$")

        with self.assertRaisesRegex(ValueError, "No versions matched"):
            _ = helper.summary

    def test_add_download_url_deduplicates_urls(self):
        helper = VersionHelper(pattern=r"^(?P<version>(?P<major>\d+))$", download_urls=[])

        helper.add_download_url("https://example.com/a.zip")
        helper.add_download_url("https://example.com/a.zip")

        self.assertEqual(["https://example.com/a.zip"], helper.download_urls)

    def test_add_download_url_initializes_default_download_list(self):
        helper = VersionHelper(pattern=r"^(?P<version>(?P<major>\d+))$")

        helper.add_download_url("https://example.com/a.zip")

        self.assertEqual(["https://example.com/a.zip"], helper.download_urls)
