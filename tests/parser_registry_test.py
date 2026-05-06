import tomllib
import unittest
from pathlib import Path

from app.core.config import AppSetting
from app.parser import Base
from app.parser.registry import load_parser_class, validate_parser_contracts


class ParserRegistryTestCase(unittest.TestCase):
    def test_all_configured_parsers_are_loadable(self):
        cfg_dict = tomllib.loads(Path("version-checker.toml").read_text(encoding="utf-8"))
        settings = AppSetting.model_validate(cfg_dict)

        errors = validate_parser_contracts(settings.softwares)

        self.assertEqual([], errors)

    def test_load_parser_class_returns_base_subclass(self):
        parser_class = load_parser_class("gh")

        self.assertTrue(issubclass(parser_class, Base))
