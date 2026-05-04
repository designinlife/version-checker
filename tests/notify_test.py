import os
import unittest
from unittest.mock import patch

from app.core.notify import send_mail


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
