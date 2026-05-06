import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from app.core.config import ChromeSoftware, Configuration, DartSoftware, DockerHubSoftware, GitLsRemoteSoftware, GoSoftware, NodeJsSoftware
from app.parser.chrome import Parser as ChromeParser
from app.parser.dart import Parser as DartParser
from app.parser.docker_hub import Parser as DockerHubParser
from app.parser.docker_hub import RatelimitHeader, RepositoryTagItem
from app.parser.git_ls_remote import Parser as GitLsRemoteParser
from app.parser.go import Parser as GoParser
from app.parser.nodejs import Parser as NodeJsParser


class ParserOfflineTestCase(unittest.TestCase):
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
