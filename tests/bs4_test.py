import re
import unittest
import requests
from bs4 import BeautifulSoup


class BeautifulSoupTestCase(unittest.TestCase):
    def test_bs4_apache_flume(self):
        r = requests.get('https://flume.apache.org/releases/index.html')
        r.raise_for_status()
        soup = BeautifulSoup(r.text)
        latest_a_element = soup.select_one('#releases > p:nth-child(3) > a')
        other_a_elements = soup.select('#releases > div:nth-child(6) > ul > li > a')
        print(latest_a_element.attrs['href'])

        for v in other_a_elements:
            print(v.attrs['href'])

    def test_sonatype_nexus3(self):
        r = requests.get('https://raw.githubusercontent.com/sonatype/docker-nexus3/main/Dockerfile')
        r.raise_for_status()

        exp = re.compile(r'ARG NEXUS_VERSION=([0-9-.]+)')
        m = exp.findall(r.text)
        print(m)


if __name__ == '__main__':
    unittest.main()
