import unittest
from unittest.mock import patch

from app.core.config import Configuration, GithubSoftware
from app.core.version import Version, VersionSummary
from app.link.gradle import UrlMaker as GradleUrlMaker
from app.link.openssl import UrlMaker as OpensslUrlMaker
from app.link.podman_machine_wsl_os import UrlMaker as PodmanMachineWslOsUrlMaker
from app.link.sqlite import UrlMaker as SqliteUrlMaker


class LinkUrlMakerTestCase(unittest.TestCase):
    def test_gradle_url_maker_builds_distribution_links(self):
        maker = GradleUrlMaker(Configuration())
        summary = VersionSummary(latest=Version(major=8, minor=14, version="8.14"), versions=[])

        urls = maker.build_links(GithubSoftware(name="gradle", repo="gradle/gradle", pattern=""), summary, [])

        self.assertEqual(
            [
                "https://services.gradle.org/distributions/gradle-8.14-bin.zip",
                "https://services.gradle.org/distributions/gradle-8.14-all.zip",
                "https://services.gradle.org/distributions/gradle-8.14-src.zip",
                "https://services.gradle.org/distributions/gradle-8.14-docs.zip",
            ],
            urls,
        )

    def test_openssl_url_maker_uses_legacy_source_path_for_1_1(self):
        maker = OpensslUrlMaker(Configuration())
        summary = VersionSummary(
            latest=Version(major=1, minor=1, patch=1, letter="w", version="1.1.1w"),
            versions=[],
        )

        urls = maker.build_links(GithubSoftware(name="openssl", repo="openssl/openssl", pattern=""), summary, [])

        self.assertEqual(["https://www.openssl.org/source/old/1.1.1/openssl-1.1.1w.tar.gz"], urls)

    def test_openssl_url_maker_uses_github_release_path_for_modern_versions(self):
        maker = OpensslUrlMaker(Configuration())
        summary = VersionSummary(latest=Version(major=3, minor=5, patch=0, version="3.5.0"), versions=[])

        urls = maker.build_links(GithubSoftware(name="openssl", repo="openssl/openssl", pattern=""), summary, [])

        self.assertEqual(["https://github.com/openssl/openssl/releases/download/openssl-3.5.0/openssl-3.5.0.tar.gz"], urls)

    def test_podman_machine_wsl_os_url_maker_keeps_only_amd64_rootfs_zst(self):
        maker = PodmanMachineWslOsUrlMaker(Configuration())
        summary = VersionSummary(latest=Version(major=5, minor=0, version="5.0"), versions=[])

        urls = maker.build_links(
            GithubSoftware(name="podman-machine-wsl-os", repo="containers/podman-machine-os", pattern=""),
            summary,
            [
                "https://example.com/podman-amd64-rootfs.tar.zst",
                "https://example.com/podman-arm64-rootfs.tar.zst",
                "https://example.com/podman-amd64-rootfs.tar.gz",
            ],
        )

        self.assertEqual(["https://example.com/podman-amd64-rootfs.tar.zst#5.0|podman-amd64-rootfs.tar.zst"], urls)

    def test_sqlite_url_maker_builds_year_scoped_downloads(self):
        maker = SqliteUrlMaker(Configuration())
        summary = VersionSummary(latest=Version(major=3, minor=50, patch=2, version="3.50.2"), versions=[])

        with patch("app.link.sqlite.arrow.now") as now:
            now.return_value.format.return_value = "2026"
            urls = maker.build_links(GithubSoftware(name="sqlite", repo="sqlite/sqlite", pattern=""), summary, [])

        self.assertEqual(
            [
                "https://www.sqlite.org/2026/sqlite-amalgamation-3500200.zip",
                "https://www.sqlite.org/2026/sqlite-autoconf-3500200.tar.gz",
                "https://www.sqlite.org/2026/sqlite-doc-3500200.zip",
                "https://www.sqlite.org/2026/sqlite-tools-linux-x64-3500200.zip",
                "https://www.sqlite.org/2026/sqlite-dll-win-x64-3500200.zip",
                "https://www.sqlite.org/2026/sqlite-tools-win-x64-3500200.zip",
            ],
            urls,
        )
