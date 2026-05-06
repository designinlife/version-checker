import os
import unittest
from unittest.mock import patch

from app.core.notify import build_feishu_update_post, send_feishu_updates, send_mail


class NotifyTestCase(unittest.TestCase):
    def test_send_mail_returns_false_when_smtp_config_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(send_mail(to=["user@example.com"], subject="Test", content="content"))

    def test_send_mail_builds_html_message(self):
        env = {
            "SMTP_SERVER": "smtp.example.com",
            "SMTP_PORT": "465",
            "SENDER_EMAIL": "sender@example.com",
            "AUTH_PASSWORD": "secret",
        }

        with patch.dict(os.environ, env, clear=True), patch("app.core.notify.smtplib.SMTP_SSL") as smtp_ssl:
            ok = send_mail(
                to=["user@example.com"],
                subject=" HTML Test ",
                content="plain text",
                html="<strong>html text</strong>",
            )

        self.assertTrue(ok)
        smtp_ssl.assert_called_once_with("smtp.example.com", 465)
        server = smtp_ssl.return_value.__enter__.return_value
        server.login.assert_called_once_with("sender@example.com", "secret")
        message = server.send_message.call_args.args[0]
        self.assertEqual("HTML Test", message["Subject"])
        self.assertEqual("user@example.com", message["To"])
        self.assertTrue(message.is_multipart())

    def test_build_feishu_update_post_builds_rich_text_rows(self):
        payload = build_feishu_update_post([{"name": "demo", "previous": "0.9.0", "latest": "1.0.0"}])

        self.assertEqual("post", payload["msg_type"])
        post = payload["content"]["post"]["zh_cn"]
        self.assertEqual("Software update notification", post["title"])
        self.assertEqual(
            [
                {"tag": "text", "text": "demo: "},
                {"tag": "text", "text": "0.9.0 -> 1.0.0"},
            ],
            post["content"][0],
        )

    def test_send_feishu_updates_returns_false_when_secret_missing(self):
        with patch.dict(os.environ, {}, clear=True), patch("app.core.notify.requests.post") as post:
            self.assertFalse(send_feishu_updates([{"name": "demo", "previous": "0.9.0", "latest": "1.0.0"}]))

        post.assert_not_called()

    def test_send_feishu_updates_posts_signed_payload(self):
        class FakeResponse:
            status_code = 200

            @staticmethod
            def json():
                return {"code": 0, "msg": "success"}

        env = {"FEISHU_SECRET_KEY": "secret"}
        with (
            patch.dict(os.environ, env, clear=True),
            patch("app.core.notify.time.time", return_value=1599360473),
            patch("app.core.notify.requests.post", return_value=FakeResponse()) as post,
        ):
            ok = send_feishu_updates([{"name": "demo", "previous": "0.9.0", "latest": "1.0.0"}])

        self.assertTrue(ok)
        post.assert_called_once()
        payload = post.call_args.kwargs["json"]
        self.assertEqual("1599360473", payload["timestamp"])
        self.assertEqual("post", payload["msg_type"])
        self.assertTrue(payload["sign"])
