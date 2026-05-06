import asyncio
import unittest
from unittest.mock import AsyncMock

from app.core.config import AndroidStudioSoftware
from app.core.http import AsyncHttpClient
from app.parser.android_studio import Parser as AndroidStudioParser


class AsyncHttpClientTestCase(unittest.TestCase):
    def test_client_accepts_external_session(self):
        session = object()
        client = AsyncHttpClient(session=session)

        self.assertIs(session, client.session)

    def test_external_session_request_receives_timeout(self):
        class FakeResponse:
            status = 200
            headers = {}
            url = "https://example.com"

            async def text(self):
                return "ok"

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

        class FakeSession:
            def __init__(self):
                self.kwargs = None

            def request(self, **kwargs):
                self.kwargs = kwargs
                return FakeResponse()

        session = FakeSession()
        client = AsyncHttpClient(session=session)

        asyncio.run(client.request("GET", "https://example.com", timeout=3))

        self.assertEqual(3, session.kwargs["timeout"])

    def test_http_error_includes_response_excerpt(self):
        class FakeResponse:
            status = 429
            headers = {}
            url = "https://example.com/rate"

            async def text(self):
                return "rate limit exceeded because too many requests"

        client = AsyncHttpClient()

        with self.assertRaisesRegex(ValueError, "HTTP request failed.*429.*rate limit exceeded"):
            asyncio.run(client._read_response(FakeResponse(), "https://example.com/rate", is_json=False))

    def test_json_parse_error_includes_url_and_status(self):
        class FakeResponse:
            status = 200
            headers = {}
            url = "https://example.com/json"

            async def json(self):
                raise ValueError("bad json")

            async def text(self):
                return "<html>not json</html>"

        client = AsyncHttpClient()

        with self.assertRaisesRegex(ValueError, "Invalid JSON response.*200.*https://example.com/json"):
            asyncio.run(client._read_response(FakeResponse(), "https://example.com/json", is_json=True))


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
