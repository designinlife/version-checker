import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from app.commands.jbp import IdeaVersion, Plugin, Plugins, pydantic_to_xml
from app.commands.jbp import cli as jbp_cli
from app.commands.skopeo import cli as skopeo_cli
from app.commands.skopeo import do_skopeo_copy
from app.core.config import AppSetting, AppSettingBase, Configuration


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


class JbpCommandTestCase(unittest.TestCase):
    def test_pydantic_to_xml_omits_empty_until_build(self):
        xml = pydantic_to_xml(
            Plugins(
                plugin=[
                    Plugin(
                        id="demo.plugin",
                        url="https://example.com/demo.zip",
                        version="1.0.0",
                        name="Demo",
                        idea_version=IdeaVersion(since_build="241", until_build=""),
                    )
                ]
            )
        )

        self.assertIn('id="demo.plugin"', xml)
        self.assertIn('since-build="241"', xml)
        self.assertNotIn("until-build", xml)

    def test_jbp_cli_writes_plugin_xml_file(self):
        cfg = Configuration(settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()
        data = [
            {
                "display_name": "Jetbrains Plugin: Demo",
                "latest": "1.0.0",
                "download_urls": ["https://example.com/download.zip#demo.zip"],
                "jbp_extra": {"until": "242.*", "since": "241", "xml_id": "demo.plugin"},
            },
            {"display_name": "Other", "latest": "1.0.0", "download_urls": []},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp).joinpath("nested", "plugins.xml")

            with (
                patch("app.commands.jbp.requests.get", return_value=FakeResponse(data)),
                patch.dict("os.environ", {"DOWNLOAD_URL": "https://mirror.example/"}, clear=False),
            ):
                result = runner.invoke(jbp_cli, ["--output", str(output)], obj=cfg)

            xml = output.read_text(encoding="utf-8")

        self.assertEqual(0, result.exit_code)
        self.assertIn('id="demo.plugin"', xml)
        self.assertIn('url="https://mirror.example/demo.zip"', xml)
        self.assertIn("<name>Demo</name>", xml)


class SkopeoCommandTestCase(unittest.TestCase):
    def test_skopeo_cli_dry_run_generates_latest_tag_commands(self):
        cfg = Configuration(settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()
        data = [
            {
                "name": "docker-demo",
                "repo": "library/demo",
                "tags": [],
                "latest_tags": ["1.0"],
                "suffix": ["-alpine"],
                "fixed_tags": ["latest"],
            }
        ]

        with (
            patch("app.commands.skopeo.requests.get", return_value=FakeResponse(data)),
            patch.dict(
                "os.environ",
                {"PROXY": "http://127.0.0.1:7890", "DOCKER_REGISTRY_HOST": "registry.local", "DOCKER_IO": "docker.example"},
                clear=False,
            ),
        ):
            result = runner.invoke(skopeo_cli, ["--latest", "--dry-run"], obj=cfg)

        self.assertEqual(0, result.exit_code)
        self.assertIn("HTTPS_PROXY=http://127.0.0.1:7890 skopeo copy docker://docker.example/library/demo:1.0", result.output)
        self.assertIn("docker://registry.local/library/demo:1.0-alpine", result.output)
        self.assertIn("docker://registry.local/library/demo:latest", result.output)

    def test_skopeo_cli_dry_run_generates_filtered_tag_commands(self):
        cfg = Configuration(settings=AppSetting(app=AppSettingBase(title="test")))
        runner = CliRunner()
        data = [
            {
                "name": "docker-demo",
                "repo": "library/demo",
                "tags": [
                    {"name": "1.0", "tag_last_pushed": "2026-05-05T00:00:00.000000Z"},
                    {"name": "1.1-debug", "tag_last_pushed": "2026-05-05T00:00:00.000000Z"},
                    {"name": "0.9", "tag_last_pushed": "2026-01-01T00:00:00.000000Z"},
                ],
                "latest_tags": [],
                "suffix": [],
                "fixed_tags": [],
            },
            {
                "name": "docker-other",
                "repo": "library/other",
                "tags": [{"name": "2.0", "tag_last_pushed": "2026-05-05T00:00:00.000000Z"}],
                "latest_tags": [],
                "suffix": [],
                "fixed_tags": [],
            },
        ]

        with (
            patch("app.commands.skopeo.requests.get", return_value=FakeResponse(data)),
            patch.dict("os.environ", {"DOCKER_REGISTRY_HOST": "registry.local", "DOCKER_IO": "docker.example"}, clear=True),
        ):
            result = runner.invoke(
                skopeo_cli,
                ["--repo", "library/demo", "--since", "2026-05-01 00:00:00", "--dry-run", "--disable-skopeo-proxy"],
                obj=cfg,
            )

        self.assertEqual(0, result.exit_code)
        self.assertIn("DT=2026-05-05 skopeo copy docker://docker.example/library/demo:1.0", result.output)
        self.assertIn("docker://registry.local/library/demo:1.0", result.output)
        self.assertNotIn("1.1-debug", result.output)
        self.assertNotIn("0.9", result.output)
        self.assertNotIn("library/other", result.output)

    def test_do_skopeo_copy_skips_manifest_unknown_error(self):
        completed = type("Completed", (), {"returncode": 1, "stderr": b"manifest unknown"})()

        with patch("app.commands.skopeo.subprocess.run", return_value=completed):
            do_skopeo_copy("skopeo copy demo", 1, 1)
