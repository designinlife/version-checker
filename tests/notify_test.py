import unittest

from base import MyTestCase
from app.core.notify import send_mail
from dotenv import load_dotenv


class NotifyTestCase(MyTestCase):
    def test_send_mail(self):
        load_dotenv(dotenv_path='../.env.dev')

        ok1 = send_mail(
            to=['codeplus@qq.com'],
            subject='来自 version-checker 的更新通知',
            content="这是一封纯文本测试邮件。"
        )

        self.assertEqual(True, ok1)

        html_content = '<h1>Hello</h1><p>这是一封 <b>HTML</b> 测试邮件。</p>'
        ok2 = send_mail(
            to=['codeplus@qq.com'],
            subject='HTML 测试邮件',
            content='这是一封 HTML 测试邮件的纯文本版本。',
            html=html_content
        )

        self.assertEqual(True, ok2)


if __name__ == '__main__':
    unittest.main()
