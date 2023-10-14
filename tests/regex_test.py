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


if __name__ == '__main__':
    unittest.main()
