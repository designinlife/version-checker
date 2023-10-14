import re
import unittest


class RegexpTestCase(unittest.TestCase):
    def test_version_match(self):
        v1 = 'OpenSSL 1.1.1w'

        exp1 = re.compile(r'^OpenSSL (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>[a-z])?$')
        m = exp1.match(v1)

        self.assertIsInstance(m, re.Match)
        self.assertEqual(m.group('suffix'), 'w')


if __name__ == '__main__':
    unittest.main()
