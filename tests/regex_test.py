import re
import unittest

from app.core.version import VersionParser, VersionHelper


class RegexpTestCase(unittest.TestCase):
    def test_version_match(self):
        v1 = 'OpenSSL 1.1.1w'

        exp1 = re.compile(r'^OpenSSL (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?$')
        m = exp1.match(v1)

        self.assertIsInstance(m, re.Match)
        self.assertEqual(m.group('suffix'), 'w')

    def test_version_latest(self):
        ps = VersionParser(pattern=r'^OpenSSL (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?)$')

        v1 = ['OpenSSL 1.1.1b', 'OpenSSL 1.1.1a', 'OpenSSL 1.1.1c', 'OpenSSL 1.1.1w', 'OpenSSL 1.1.1v', 'OpenSSL 1.1.2t', 'OpenSSL 1.2.0', 'OpenSSL 1.12.0']

        self.assertEqual(ps.latest(v1), '1.12.0')

        ps = VersionParser(pattern=r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\.(\d+)\.(\d+))$')

        v2 = ['11.0.18.10.1', '11.0.20.9.1', '11.0.18.11.1']

        self.assertEqual(ps.latest(v2), '11.0.20.9.1')

    def test_semver_split(self):
        ps = VersionParser(pattern=r'^OpenSSL (?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?)$')

        v1 = ['OpenSSL 1.1.1b', 'OpenSSL 1.1.1a', 'OpenSSL 1.1.1c', 'OpenSSL 1.1.1w', 'OpenSSL 1.1.1v', 'OpenSSL 3.0.1', 'OpenSSL 3.0.0', 'OpenSSL 3.0.10',
              'OpenSSL 3.1.2', 'OpenSSL 3.1.1', 'OpenSSL 3.1.3', 'OpenSSL 3.1.4', 'OpenSSL 3.2.0']

        v2 = ps.split(v1)

        self.assertIsInstance(v2, dict)
        self.assertTrue('3.2' in v2)
        self.assertTrue('3.1' in v2)
        self.assertTrue('3.0' in v2)
        self.assertTrue('1.1' in v2)
        self.assertFalse('1.0' in v2)

    def test_version_helper_curl(self):
        helper = VersionHelper(pattern=r'^curl-(?P<version>(?P<major>\d+)_(?P<minor>\d+)_(?P<patch>\d+))$', split_mode=0)
        helper.add('v7_0_2beta')
        helper.add('tiny-curl-7_72_0')
        helper.add('curl-8_4_0')
        helper.add('curl-7_81_0')
        helper.add('curl-8_0_1')
        helper.add('curl-8_1_0')
        helper.add('curl-8_1_1')
        helper.add('curl-7_86_0')
        helper.add('curl-8_0_0')

        helper.sort()

        print(helper.latest, helper.versions)


if __name__ == '__main__':
    unittest.main()
