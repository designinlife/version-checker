import unittest

from app.core.click import ClickStdOption


class ClickStdOptionTestCase(unittest.TestCase):
    def test_hidden_option_has_no_help_record(self):
        option = ClickStdOption(["--secret"], hidden=True)

        self.assertIsNone(option.get_help_record(None))

    def test_required_option_help_record_contains_required_marker(self):
        option = ClickStdOption(["--name", "-n"], help="Name.", required=True)

        opts, help_text = option.get_help_record(None)

        self.assertEqual("-n, --name", opts)
        self.assertEqual("Name. \033[38;5;196m*\033[0m", help_text)

    def test_option_help_record_includes_secondary_options(self):
        option = ClickStdOption(["--debug/--no-debug"], help="Debug mode.")

        opts, help_text = option.get_help_record(None)

        self.assertEqual("--debug / --no-debug", opts)
        self.assertEqual("Debug mode.", help_text)
