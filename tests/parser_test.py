from base import MyTestCase
from parser import Parser
import asyncio


class ParserTestCase(MyTestCase):
    def test_github_ratelimit(self):
        parser = Parser(self.cfg)

        asyncio.run(parser.ratelimit())
