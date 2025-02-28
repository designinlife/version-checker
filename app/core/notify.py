import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import List, Optional

from loguru import logger


def send_mail(to: List[str], subject: str, content: str, html: Optional[str] = None) -> bool:
    """
    发送邮件函数。

    Args:
        to (List[str]): 收件人邮箱地址列表
        subject (str): 邮件标题
        content (str): 纯文本邮件内容
        html (Optional[str]): HTML 邮件内容，若非空则发送 HTML 邮件，默认为 None

    Returns:
        bool: 发送成功返回 True，否则返回 False
    """
    # SMTP 配置
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', '465'))  # SSL 端口
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_display = f'{sender_email} <L.STONE>'
    username = sender_email  # 登录名
    password = os.environ.get('AUTH_PASSWORD')  # 请替换为你的邮箱授权码或密码

    # 检查 SMTP 配置是否完整
    if not all([smtp_server, smtp_port, sender_email, username, password]):
        logger.error("SMTP configuration is incomplete.")
        return False

    try:
        # 创建邮件对象
        if html:
            # 发送 HTML 邮件
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(content, "plain", "utf-8"))  # 纯文本作为备用
            msg.attach(MIMEText(html, "html", "utf-8"))  # HTML 内容
        else:
            # 发送纯文本邮件
            msg = MIMEText(content, "plain", "utf-8")

        # 设置邮件头信息
        msg["Subject"] = subject.strip()
        msg["From"] = formataddr(('L.STONE (126)', sender_email))
        msg["To"] = ",".join(email.strip() for email in to if email.strip())  # 将收件人列表转换为逗号分隔的字符串

        # 连接并发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  # 使用 SSL
            server.login(username, password)  # 登录
            server.send_message(msg)  # 发送邮件
        return True

    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False
