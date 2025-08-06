import unittest

from app.core.version import VersionHelper
from app.core.config import JetbrainsPluginSoftware, AppSetting
import tomllib


class VersionHelperTestCase(unittest.TestCase):
    def test_parse_pattern(self):
        with open('../test.toml', encoding='utf-8', mode='r') as f:
            cfg_data = tomllib.loads(f.read())
            data = AppSetting.model_validate(cfg_data)

            for soft in data.softwares:
                vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)
                vhlp.append('252.23892.458')
                vhlp.append('251.25410.999.1')
                print(vhlp.versions)

            # self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
