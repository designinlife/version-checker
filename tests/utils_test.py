import unittest

from app.core.utils import safe_strtobool


class UtilsTestCase(unittest.TestCase):
    def test_safe_strtobool_returns_default_for_invalid_value(self):
        self.assertTrue(safe_strtobool("invalid", default=True))

    def test_safe_strtobool_returns_default_for_missing_value(self):
        self.assertFalse(safe_strtobool(None, default=False))
