import unittest

from bs4 import BeautifulSoup


class BeautifulSoupTestCase(unittest.TestCase):
    def test_apache_flume_release_links(self):
        html = """
        <section id="releases">
            <p><a href="/releases/1.12.0.html">Apache Flume 1.12.0</a></p>
            <div>
                <ul>
                    <li><a href="/releases/1.11.0.html">Apache Flume 1.11.0</a></li>
                    <li><a href="/releases/1.10.1.html">Apache Flume 1.10.1</a></li>
                </ul>
            </div>
        </section>
        """

        soup = BeautifulSoup(html, "html.parser")

        latest = soup.select_one("#releases > p > a")
        others = soup.select("#releases > div > ul > li > a")

        self.assertEqual("/releases/1.12.0.html", latest.attrs["href"])
        self.assertEqual(["Apache Flume 1.11.0", "Apache Flume 1.10.1"], [v.text for v in others])

    def test_sonatype_nexus3_dockerfile_version(self):
        dockerfile = """
        FROM eclipse-temurin:17-jre
        ARG NEXUS_VERSION=3.85.0-03
        """

        self.assertEqual(["3.85.0-03"], __import__("re").findall(r"ARG NEXUS_VERSION=([0-9-.]+)", dockerfile))
