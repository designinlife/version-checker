import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from app.core.config import (
    AlmaLinuxSoftware,
    ApacheFlumeSoftware,
    ChromeSoftware,
    CodebergSoftware,
    Configuration,
    DartSoftware,
    DockerHubSoftware,
    DotNetFxSoftware,
    FirefoxSoftware,
    FlutterSoftware,
    GiteaSoftware,
    GithubSoftware,
    GitlabSoftware,
    GitLsRemoteSoftware,
    GoSoftware,
    HAProxySoftware,
    JetbrainsPluginSoftware,
    JetbrainsSoftware,
    NodeJsSoftware,
    PhpSoftware,
    RockyLinuxSoftware,
    SourceForgeSoftware,
    VirtualBoxSoftware,
)
from app.parser.almalinux import Parser as AlmaLinuxParser
from app.parser.apache_flume import Parser as ApacheFlumeParser
from app.parser.chrome import Parser as ChromeParser
from app.parser.codeberg import Parser as CodebergParser
from app.parser.dart import Parser as DartParser
from app.parser.docker_hub import Parser as DockerHubParser
from app.parser.docker_hub import RatelimitHeader, RepositoryTagItem
from app.parser.dotnetfx import Parser as DotNetFxParser
from app.parser.firefox import Parser as FirefoxParser
from app.parser.flutter import Parser as FlutterParser
from app.parser.gh import Parser as GithubParser
from app.parser.git_ls_remote import Parser as GitLsRemoteParser
from app.parser.gitea import Parser as GiteaParser
from app.parser.gitlab import Parser as GitlabParser
from app.parser.go import Parser as GoParser
from app.parser.haproxy import Parser as HAProxyParser
from app.parser.jetbrains import Parser as JetbrainsParser
from app.parser.jetbrains_plugin import Parser as JetbrainsPluginParser
from app.parser.nodejs import Parser as NodeJsParser
from app.parser.php import Parser as PhpParser
from app.parser.rockylinux import Parser as RockyLinuxParser
from app.parser.sf import Parser as SourceForgeParser
from app.parser.virtualbox import Parser as VirtualBoxParser


class ParserOfflineTestCase(unittest.TestCase):
    def test_github_parser_reads_tag_api_versions(self):
        parser = GithubParser.__new__(GithubParser)
        parser.is_expired = lambda _soft: (True, "2000-01-01 00:00:00")
        parser.request = AsyncMock(
            return_value=(
                "https://api.github.com/repos/owner/demo/tags",
                200,
                {},
                [{"name": "v1.0.0"}, {"name": "v2.0.0"}],
            )
        )
        parser.write = AsyncMock()
        soft = GithubSoftware(
            name="demo",
            parser="gh",
            repo="owner/demo",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["2.0.0", "1.0.0"], [v.version for v in summary.versions])
        parser.request.assert_awaited_once()

    def test_github_parser_reads_latest_release_assets(self):
        parser = GithubParser.__new__(GithubParser)
        parser.is_expired = lambda _soft: (True, "2000-01-01 00:00:00")
        parser.request = AsyncMock(
            return_value=(
                "https://api.github.com/repos/owner/demo/releases/latest",
                200,
                {},
                {
                    "draft": False,
                    "prerelease": False,
                    "tag_name": "v3.0.0",
                    "assets": [
                        {"browser_download_url": "https://example.com/demo-windows-x64.zip"},
                        {"browser_download_url": "https://example.com/demo-linux-x64.tar.gz"},
                    ],
                },
            )
        )
        parser.write = AsyncMock()
        soft = GithubSoftware(
            name="demo",
            parser="gh",
            repo="owner/demo",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
            latest=True,
            assets=True,
            assets_patterns=[r".*windows.*\.zip$"],
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual("3.0.0", summary.latest.version)
        self.assertEqual(["https://example.com/demo-windows-x64.zip"], summary.downloads)

    def test_github_parser_skips_when_cache_is_valid(self):
        parser = GithubParser.__new__(GithubParser)
        parser.is_expired = lambda _soft: (False, "2026-05-06 08:00:00")
        parser.request = AsyncMock()
        parser.write = AsyncMock()
        soft = GithubSoftware(
            name="demo",
            parser="gh",
            repo="owner/demo",
            pattern=r"^v(?P<version>(?P<major>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        parser.request.assert_not_awaited()
        parser.write.assert_not_awaited()

    def test_nodejs_parser_keeps_lts_versions_only(self):
        parser = NodeJsParser.__new__(NodeJsParser)
        parser.request = AsyncMock(
            return_value=(
                "https://nodejs.org/download/release/index.json",
                200,
                {},
                [
                    {"version": "v22.1.0", "lts": False},
                    {"version": "v20.19.0", "lts": "Iron"},
                ],
            )
        )
        parser.write = AsyncMock()
        soft = NodeJsSoftware(name="nodejs", parser="nodejs", pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["20.19.0"], [v.version for v in summary.versions])

    def test_chrome_parser_keeps_stable_windows_versions(self):
        parser = ChromeParser.__new__(ChromeParser)
        parser.request = AsyncMock(
            return_value=(
                "https://chromiumdash.appspot.com/fetch_releases",
                200,
                {},
                [
                    {"channel": "Stable", "platform": "Windows", "version": "125.0.1"},
                    {"channel": "Beta", "platform": "Windows", "version": "126.0.1"},
                    {"channel": "Stable", "platform": "Linux", "version": "125.0.2"},
                ],
            )
        )
        parser.write = AsyncMock()
        soft = ChromeSoftware(name="chrome", parser="chrome", pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["125.0.1"], [v.version for v in summary.versions])

    def test_dart_parser_reads_stable_release_prefixes(self):
        parser = DartParser.__new__(DartParser)
        parser.request = AsyncMock(
            return_value=(
                "https://storage.googleapis.com/storage/v1/b/dart-archive/o",
                200,
                {},
                {"prefixes": ["channels/stable/release/3.8.1/", "channels/beta/release/4.0.0/"]},
            )
        )
        parser.write = AsyncMock()
        soft = DartSoftware(name="dart", parser="dart", pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["3.8.1"], [v.version for v in summary.versions])

    def test_go_parser_keeps_stable_versions_only(self):
        parser = GoParser.__new__(GoParser)
        parser.request = AsyncMock(
            return_value=(
                "https://go.dev/dl/?mode=json&include=all",
                200,
                {},
                [
                    {"version": "go1.24.4", "stable": True, "files": []},
                    {"version": "go1.25rc1", "stable": False, "files": []},
                ],
            )
        )
        parser.write = AsyncMock()
        soft = GoSoftware(name="go", parser="go", pattern=r"^go(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["1.24.4"], [v.version for v in summary.versions])

    def test_firefox_parser_keeps_major_firefox_releases(self):
        parser = FirefoxParser.__new__(FirefoxParser)
        parser.request = AsyncMock(
            return_value=(
                "https://product-details.mozilla.org/1.0/firefox.json",
                200,
                {},
                {
                    "releases": {
                        "firefox-126": {"product": "firefox", "category": "major", "version": "126.0"},
                        "firefox-126b": {"product": "firefox", "category": "dev", "version": "126.0b1"},
                        "thunderbird-115": {"product": "thunderbird", "category": "major", "version": "115.0"},
                    }
                },
            )
        )
        parser.write = AsyncMock()
        soft = FirefoxSoftware(name="firefox", parser="firefox", pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["126.0"], [v.version for v in summary.versions])

    def test_flutter_parser_keeps_stable_releases(self):
        parser = FlutterParser.__new__(FlutterParser)
        parser.request = AsyncMock(
            return_value=(
                "https://storage.googleapis.com/flutter_infra_release/releases/releases_windows.json",
                200,
                {},
                {"releases": [{"channel": "stable", "version": "3.32.0"}, {"channel": "beta", "version": "3.33.0"}]},
            )
        )
        parser.write = AsyncMock()
        soft = FlutterSoftware(name="flutter", parser="flutter", pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["3.32.0"], [v.version for v in summary.versions])

    def test_php_parser_collects_versions_for_configured_majors(self):
        parser = PhpParser.__new__(PhpParser)
        parser.request = AsyncMock(
            side_effect=[
                ("https://www.php.net/releases/index.php?json&max=-1&version=8", 200, {}, {"8.4.8": {}, "8.3.22": {}}),
                ("https://www.php.net/releases/index.php?json&max=-1&version=7", 200, {}, {"7.4.33": {}}),
            ]
        )
        parser.write = AsyncMock()
        soft = PhpSoftware(
            name="php",
            parser="php",
            major=[8, 7],
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["8.4.8", "8.3.22", "7.4.33"], [v.version for v in summary.versions])

    def test_sourceforge_parser_uses_windows_best_release_filename(self):
        parser = SourceForgeParser.__new__(SourceForgeParser)
        parser.request = AsyncMock(
            return_value=(
                "https://sourceforge.net/projects/demo/best_release.json",
                200,
                {},
                {"platform_releases": {"windows": {"filename": "/project/demo/demo-2.0.0-win.zip"}}},
            )
        )
        parser.write = AsyncMock()
        soft = SourceForgeSoftware(
            name="demo",
            parser="sf",
            project="demo",
            pattern=r"^demo-(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))-win\.zip$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual("2.0.0", summary.latest.version)

    def test_jetbrains_plugin_parser_adds_download_and_jbp_metadata(self):
        parser = JetbrainsPluginParser.__new__(JetbrainsPluginParser)
        parser.request = AsyncMock(
            side_effect=[
                (
                    "https://plugins.jetbrains.com/api/plugins/123",
                    200,
                    {},
                    {"id": 123, "link": "/plugin/123-demo", "name": "Demo", "approve": True, "xmlId": "demo.plugin"},
                ),
                (
                    "https://plugins.jetbrains.com/api/plugins/123/updates",
                    200,
                    {},
                    [
                        {
                            "id": 1,
                            "link": "/plugin/download",
                            "version": "2.0.0",
                            "approve": True,
                            "listed": True,
                            "hidden": False,
                            "recalculateCompatibilityAllowed": False,
                            "cdate": "2026-05-06",
                            "file": "plugin/demo.zip",
                            "since": "241",
                            "until": "242.*",
                            "sinceUntil": "241-242.*",
                            "size": 10,
                            "downloads": 1,
                            "pluginId": 123,
                        }
                    ],
                ),
            ]
        )
        parser.write = AsyncMock()
        soft = JetbrainsPluginSoftware(
            name="demo-plugin",
            parser="jetbrains-plugin",
            plugin_id=123,
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        _, kwargs = parser.write.await_args
        summary = kwargs["version_summary"]
        self.assertEqual("Jetbrains Plugin: Demo", soft.display_name)
        self.assertEqual("https://plugins.jetbrains.com/plugin/123-demo", soft.url)
        self.assertEqual(["https://downloads.marketplace.jetbrains.com/files/plugin/demo.zip#123-demo.zip"], summary.downloads)
        self.assertEqual({"xml_id": "demo.plugin", "since": "241", "until": "242.*"}, kwargs["jbp_extra"])
        self.assertEqual("jetbrains/plugins", kwargs["storage_dir"])

    def test_git_ls_remote_parser_extracts_tag_versions(self):
        parser = GitLsRemoteParser.__new__(GitLsRemoteParser)
        parser.run_command = AsyncMock(
            return_value={
                "returncode": 0,
                "stdout": "abc\trefs/tags/v1.2.0\nabc\trefs/tags/v1.2.0^{}\nabc\trefs/tags/not-a-version\n",
                "stderr": "",
            }
        )
        parser.write = AsyncMock()
        soft = GitLsRemoteSoftware(
            name="demo",
            parser="git-ls-remote",
            url="https://example.com/repo.git",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["1.2.0"], [v.version for v in summary.versions])

    def test_git_ls_remote_parser_does_not_write_when_command_fails(self):
        parser = GitLsRemoteParser.__new__(GitLsRemoteParser)
        parser.run_command = AsyncMock(return_value={"returncode": 1, "stdout": "", "stderr": "fatal"})
        parser.write = AsyncMock()
        soft = GitLsRemoteSoftware(
            name="demo",
            parser="git-ls-remote",
            url="https://example.com/repo.git",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        parser.write.assert_not_awaited()

    def test_docker_hub_write_data_outputs_matching_tags_and_suffixes(self):
        from app.core.version import VersionHelper

        with tempfile.TemporaryDirectory() as tmp:
            parser = DockerHubParser.__new__(DockerHubParser)
            parser.cfg = Configuration(workdir=tmp)
            soft = DockerHubSoftware(
                parser="docker-hub",
                repo="library/demo",
                pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+))(?P<other>-.+)?$",
                fixed_tags=["latest"],
            )
            helper = VersionHelper(pattern=soft.pattern, split=0, download_urls=[])
            for tag in ("1.0", "1.0-alpine", "debug"):
                helper.append(tag)

            asyncio.run(
                parser.write_data(
                    soft,
                    [
                        RepositoryTagItem(name="1.0", full_size=1, v2=True, tag_last_pushed="2026-05-05T00:00:00Z"),
                        RepositoryTagItem(name="1.0-alpine", full_size=1, v2=True, tag_last_pushed="2026-05-05T00:00:00Z"),
                        RepositoryTagItem(name="debug", full_size=1, v2=True, tag_last_pushed="2026-05-05T00:00:00Z"),
                    ],
                    RatelimitHeader.model_validate(
                        {"x-ratelimit-limit": "100", "x-ratelimit-remaining": "99", "x-ratelimit-reset": "1777939200"}
                    ),
                    helper,
                )
            )

            data = json.loads(Path(tmp).joinpath("data", "docker-library-demo.json").read_text(encoding="utf-8"))

        self.assertEqual("docker-library-demo", data["name"])
        self.assertEqual(["1.0"], [item["name"] for item in data["tags"]])
        self.assertEqual(["1.0"], data["latest_tags"])
        self.assertEqual(["-alpine"], data["suffix"])
        self.assertEqual(["latest"], data["fixed_tags"])

    def test_gitea_parser_reads_tag_names(self):
        parser = GiteaParser.__new__(GiteaParser)
        parser.request = AsyncMock(
            return_value=("https://gitea.example/api/v1/repos/o/r/tags", 200, {}, [{"name": "v1.0.0"}, {"name": "v2.0.0"}])
        )
        parser.write = AsyncMock()
        soft = GiteaSoftware(
            name="demo",
            parser="gitea",
            host="gitea.example",
            owner="o",
            repo="r",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["2.0.0", "1.0.0"], [v.version for v in summary.versions])

    def test_gitlab_parser_reads_release_tag_names(self):
        parser = GitlabParser.__new__(GitlabParser)
        parser.request = AsyncMock(return_value=("https://gitlab.example/api/v4/projects/1/releases", 200, {}, [{"tag_name": "v3.1.0"}]))
        parser.write = AsyncMock()
        soft = GitlabSoftware(
            name="demo",
            parser="gitlab",
            host="gitlab.example",
            id=1,
            release=True,
            by_tag_name=True,
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["3.1.0"], [v.version for v in summary.versions])

    def test_codeberg_parser_reads_rss_titles(self):
        parser = CodebergParser.__new__(CodebergParser)
        rss = """<?xml version="1.0"?><rss><channel><item><title>v1.2.0</title></item><item><title>v2.0.0</title></item></channel></rss>"""
        parser.request = AsyncMock(return_value=("https://codeberg.org/o/r/tags.rss", 200, {}, rss))
        parser.write = AsyncMock()
        soft = CodebergSoftware(
            name="demo",
            parser="codeberg",
            repo="o/r",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["2.0.0", "1.2.0"], [v.version for v in summary.versions])

    def test_jetbrains_parser_collects_versions_and_downloads(self):
        parser = JetbrainsParser.__new__(JetbrainsParser)
        parser.request = AsyncMock(
            return_value=(
                "https://data.services.jetbrains.com/products/releases",
                200,
                {},
                {
                    "IIU": [
                        {
                            "version": "2026.1",
                            "majorVersion": "2026.1",
                            "downloads": {
                                "windows": {"link": "https://download.jetbrains.com/idea/ideaIU-2026.1.exe"},
                                "linux": {"link": "https://download.jetbrains.com/idea/ideaIU-2026.1.tar.gz"},
                            },
                        }
                    ]
                },
            )
        )
        parser.write = AsyncMock()
        soft = JetbrainsSoftware(
            name="idea",
            parser="jetbrains",
            code=["IIU"],
            os=["windows"],
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["2026.1"], [v.version for v in summary.versions])
        self.assertEqual(["https://download-cdn.jetbrains.com/idea/ideaIU-2026.1.exe#2026.1|ideaIU-2026.1.exe"], summary.downloads)

    def test_virtualbox_parser_collects_latest_download_links(self):
        parser = VirtualBoxParser.__new__(VirtualBoxParser)
        parser.request = AsyncMock(
            side_effect=[
                (
                    "https://download.virtualbox.org/virtualbox/",
                    200,
                    {},
                    "<html><body><pre>"
                    "<a href='7.0.20/'>7.0.20/</a>"
                    "<a href='7.1.8/'>7.1.8/</a>"
                    "<a href='README.txt'>README</a>"
                    "</pre></body></html>",
                ),
                (
                    "https://download.virtualbox.org/virtualbox/7.1.8/",
                    200,
                    {},
                    "<html><body><pre>"
                    "<a href='VirtualBox-7.1.8-Win.exe'>exe</a>"
                    "<a href='Oracle_VM_VirtualBox_Extension_Pack-7.1.8.vbox-extpack'>ext</a>"
                    "<a href='SHA256SUMS'>sum</a>"
                    "</pre></body></html>",
                ),
            ]
        )
        parser.write = AsyncMock()
        soft = VirtualBoxSoftware(
            name="virtualbox",
            parser="virtualbox",
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual("7.1.8", summary.latest.version)
        self.assertEqual(
            [
                "https://download.virtualbox.org/virtualbox/7.1.8/VirtualBox-7.1.8-Win.exe",
                "https://download.virtualbox.org/virtualbox/7.1.8/Oracle_VM_VirtualBox_Extension_Pack-7.1.8.vbox-extpack",
            ],
            summary.downloads,
        )

    def test_dotnetfx_parser_collects_supported_versions_and_downloads(self):
        parser = DotNetFxParser.__new__(DotNetFxParser)
        table_html = """
        <html><body><div id="supported-versions-table"><div><table><tbody>
        <tr><td>4.8.1</td></tr><tr><td>4.8</td></tr>
        </tbody></table></div></div></body></html>
        """
        thanks_html = """
        <html><body><div class="main-container"><div class="swim-container"><div><div><p>
        <a href="https://go.microsoft.com/fwlink/?linkid=123">download</a>
        </p></div></div></div></div></body></html>
        """
        parser.request = AsyncMock(
            side_effect=[
                ("https://dotnet.microsoft.com/en-us/download/dotnet-framework", 200, {}, table_html),
                ("https://dotnet.microsoft.com/thank-you/1", 200, {}, thanks_html),
                ("https://dotnet.microsoft.com/thank-you/2", 200, {}, ""),
                ("https://dotnet.microsoft.com/thank-you/3", 200, {}, ""),
                ("https://dotnet.microsoft.com/thank-you/4", 200, {}, ""),
            ]
        )
        parser.write = AsyncMock()
        soft = DotNetFxSoftware(
            name="dotnetfx",
            parser="dotnetfx",
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<patch>\d+))?)$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["4.8.1", "4.8"], [v.version for v in summary.versions])
        self.assertEqual(["https://go.microsoft.com/fwlink/?linkid=123"], summary.downloads)

    def test_haproxy_parser_collects_successful_tag_pages(self):
        parser = HAProxyParser.__new__(HAProxyParser)
        parser.request = AsyncMock(
            side_effect=[
                ("https://git.haproxy.org/git/haproxy-3.0.git/refs/tags/", 200, {}, "<pre><a>v3.0.1</a><a>v3.0.0</a></pre>"),
                ("https://git.haproxy.org/git/haproxy-2.9.git/refs/tags/", 404, {}, ""),
                ("https://git.haproxy.org/git/haproxy-2.8.git/refs/tags/", 200, {}, "<pre><a>v2.8.15</a></pre>"),
                ("https://git.haproxy.org/git/haproxy-2.6.git/refs/tags/", 404, {}, ""),
                ("https://git.haproxy.org/git/haproxy-2.4.git/refs/tags/", 404, {}, ""),
                ("https://git.haproxy.org/git/haproxy-2.2.git/refs/tags/", 404, {}, ""),
            ]
        )
        parser.write = AsyncMock()
        soft = HAProxySoftware(
            name="haproxy",
            parser="haproxy",
            pattern=r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["3.0.1", "3.0.0", "2.8.15"], [v.version for v in summary.versions])

    def test_apache_flume_parser_reads_latest_and_archived_versions(self):
        parser = ApacheFlumeParser.__new__(ApacheFlumeParser)
        html = """
        <html><body><div id="releases">
        <span></span><span></span><p><a href="1.11.0.html">latest</a></p><span></span><span></span>
        <div><ul><li><a href="1.10.1.html">old</a></li><li><a href="1.9.0.html">older</a></li></ul></div>
        </div></body></html>
        """
        parser.request = AsyncMock(return_value=("https://flume.apache.org/releases/index.html", 200, {}, html))
        parser.write = AsyncMock()
        soft = ApacheFlumeSoftware(
            name="apache-flume",
            parser="apache-flume",
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["1.11.0", "1.10.1", "1.9.0"], [v.version for v in summary.versions])

    def test_rockylinux_parser_reads_rows_with_release_dates(self):
        parser = RockyLinuxParser.__new__(RockyLinuxParser)
        html = """
        <html><body><div class="tabbed-block"><table><tbody>
        <tr><td>9.5</td><td></td><td>2026-05-01</td></tr>
        <tr><td>8.10</td><td></td><td></td></tr>
        </tbody></table></div></body></html>
        """
        parser.request = AsyncMock(return_value=("https://wiki.rockylinux.org/rocky/version/", 200, {}, html))
        parser.write = AsyncMock()
        soft = RockyLinuxSoftware(name="rocky", parser="rockylinux", pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["9.5"], [v.version for v in summary.versions])

    def test_almalinux_parser_reads_release_rows_for_all_supported_majors(self):
        parser = AlmaLinuxParser.__new__(AlmaLinuxParser)
        table = """
        <table><tbody>
        <tr><td><a>10.0</a></td><td></td><td></td><td>2026-05-01</td></tr>
        <tr><td><a>10.0-beta</a></td><td></td><td></td><td></td></tr>
        </tbody></table>
        """
        html = f"""
        <html><body>
        <h2 id="almalinux-os-10">10</h2>{table}
        <h2 id="almalinux-os-9">9</h2>{table.replace("10.0", "9.6")}
        <h2 id="almalinux-os-8">8</h2>{table.replace("10.0", "8.10")}
        </body></html>
        """
        parser.request = AsyncMock(return_value=("https://wiki.almalinux.org/release-notes/", 200, {}, html))
        parser.write = AsyncMock()
        soft = AlmaLinuxSoftware(name="alma", parser="almalinux", pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+))$")

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        summary = parser.write.await_args.args[1]
        self.assertEqual(["10.0", "9.6", "8.10"], [v.version for v in summary.versions])
