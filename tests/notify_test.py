import unittest

from base import MyTestCase
from app.core.notify import send_mail
from dotenv import load_dotenv


class NotifyTestCase(MyTestCase):
    def test_send_mail(self):
        load_dotenv(dotenv_path='../.env.dev')

        # ok1 = send_mail(
        #     to=['codeplus@qq.com'],
        #     subject='来自 version-checker 的更新通知',
        #     content="这是一封纯文本测试邮件。"
        # )
        #
        # self.assertEqual(True, ok1)

        html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>软件更新通知</title>
    <style>
        html, body, th, td, p {
            font-family: Arial, sans-serif;
            font-size: 12px;
        }
        body {
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            font-size: 18px;
        }
        p {
            margin: 10px 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 600px;
            margin: 20px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        .footer {
            font-size: 12px;
            color: #777;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Software update notification (From: Github designinlife/version-checker)</h1>
    <p>尊敬的用户，您好！</p>
    <p>以下是最新软件版本更新信息，请查阅：</p>
    
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Latest</th>
                <th>Previous</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>7-zip</td>
                <td>1.0.0</td>
                <td>0.9.9</td>
            </tr>
            <tr>
                <td>Apache Doris</td>
                <td>2.0.16</td>
                <td>2.0.15</td>
            </tr>
        </tbody>
    </table>
    
    <p>如有任何问题，请随时联系我们。</p>
    <p>祝好，</p>
    <p>L.STONE</p>
    <div class="footer">
        <p>此邮件由系统自动发送，请勿回复。</p>
    </div>
</body>
</html>'''
        ok2 = send_mail(
            to=['codeplus@qq.com'],
            subject='HTML 测试邮件',
            content='这是一封 HTML 测试邮件的纯文本版本。',
            html=html_content
        )

        self.assertEqual(True, ok2)


if __name__ == '__main__':
    unittest.main()
