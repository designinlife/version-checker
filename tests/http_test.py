import asyncio
import unittest
from unittest.mock import AsyncMock

from app.core.http import AsyncHttpClient
from app.core.config import AndroidStudioSoftware
from app.parser.android_studio import Parser as AndroidStudioParser


class AsyncHttpClientTestCase(unittest.TestCase):
    def test_client_accepts_external_session(self):
        session = object()
        client = AsyncHttpClient(session=session)

        self.assertIs(session, client.session)


class AndroidStudioParserTestCase(unittest.TestCase):
    def test_android_studio_parser_uses_base_request(self):
        parser = AndroidStudioParser.__new__(AndroidStudioParser)
        parser.request = AsyncMock(
            return_value=(
                "https://jb.gg/android-studio-releases-list.json",
                200,
                {},
                {"content": {"item": [{"channel": "Release", "version": "2025.1.2"}]}},
            )
        )
        parser.write = AsyncMock()
        soft = AndroidStudioSoftware(
            name="android-studio",
            parser="android-studio",
            pattern=r"^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+))$",
        )

        asyncio.run(parser.handle(asyncio.Semaphore(1), soft))

        parser.request.assert_awaited_once()
        parser.write.assert_awaited_once()
