import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.commands.combine import combine_data
from app.core.config import Configuration
from app.core.output import get_output_dir


class OutputDirTestCase(unittest.TestCase):
    def test_get_output_dir_uses_default_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            self.assertEqual(Path(tmp).joinpath("data"), get_output_dir(tmp))

    def test_get_output_dir_uses_output_data_dir_env(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OUTPUT_DATA_DIR": "out"}, clear=True):
            self.assertEqual(Path(tmp).joinpath("out"), get_output_dir(tmp))


class CombineOutputDirTestCase(unittest.TestCase):
    def test_combine_uses_output_data_dir_env(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OUTPUT_DATA_DIR": "out"}, clear=True):
            out_dir = Path(tmp).joinpath("out")
            out_dir.mkdir()
            out_dir.joinpath("demo.json").write_text(
                json.dumps(
                    {
                        "name": "demo",
                        "url": "https://example.com",
                        "latest": "1.0.0",
                        "versions": ["1.0.0"],
                        "created_time": "2026-01-01 00:00:00",
                    }
                ),
                encoding="utf-8",
            )

            cfg = Configuration(workdir=tmp)
            combine_data(cfg)

            self.assertTrue(out_dir.joinpath("all.json").is_file())
