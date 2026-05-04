import re
import unittest


class RegexpTestCase(unittest.TestCase):
    def test_github_semver_tag_pattern(self):
        exp = re.compile(r"^v(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$")

        match = exp.match("v1.2.3")

        self.assertIsNotNone(match)
        self.assertEqual({"version": "1.2.3", "major": "1", "minor": "2", "patch": "3"}, match.groupdict())
