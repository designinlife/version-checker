import re
import unittest
from app.core.version import VersionParser


class RegexpTestCase(unittest.TestCase):
    def test_version_match(self):
        v1 = 'OpenSSL 1.1.1w'

        exp1 = re.compile(r'^OpenSSL (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?$')
        m = exp1.match(v1)

        self.assertIsInstance(m, re.Match)
        self.assertEqual(m.group('suffix'), 'w')

    def test_version_latest(self):
        ps = VersionParser(pattern=r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?$')

        v1 = ['1.1.1b', '1.1.1a', '1.1.1c', '1.1.1w', '1.1.1v', '1.1.2t', '1.2.0', '1.12.0']

        self.assertEqual(ps.latest(v1), '1.12.0')

        ps = VersionParser(pattern=r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\.(?P<suffix>\d+)$')

        v2 = ['11.0.18.10.1', '11.0.20.9.1', '11.0.18.11.1']

        self.assertEqual(ps.latest(v2), '11.0.20.9.1')

    def test_semver_split(self):
        ps = VersionParser(pattern=r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?$')

        v1 = ['1.1.1b', '1.1.1a', '1.1.1c', '1.1.1w', '1.1.1v', '3.0.1', '3.0.0', '3.0.10', '3.1.2', '3.1.1', '3.1.3', '3.1.4', '3.2.0']

        v2 = ps.semver_split(v1)

        self.assertIsInstance(v2, dict)
        self.assertTrue('3.2' in v2)
        self.assertTrue('3.1' in v2)
        self.assertTrue('3.0' in v2)
        self.assertTrue('1.1' in v2)
        self.assertFalse('1.0' in v2)


if __name__ == '__main__':
    unittest.main()
