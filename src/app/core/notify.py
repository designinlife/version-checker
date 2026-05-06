import base64
import hashlib
import hmac
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import List, Optional

import requests
from loguru import logger

FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/1432d31b-6ec1-438d-81fc-59fd4b9354c9"


def send_mail(to: List[str], subject: str, content: str, html: Optional[str] = None) -> bool:
    """按环境变量中的 SMTP 配置发送邮件，配置缺失或发送失败时返回 False。"""
    # SMTP 配置
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))  # SSL 端口
    sender_email = os.environ.get("SENDER_EMAIL")
    username = sender_email  # 登录名
    password = os.environ.get("AUTH_PASSWORD")  # 请替换为你的邮箱授权码或密码

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
        msg["From"] = formataddr(("L.STONE (126)", sender_email))
        msg["To"] = ",".join(email.strip() for email in to if email.strip())  # 将收件人列表转换为逗号分隔的字符串

        # 连接并发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:  # 使用 SSL
            server.login(username, password)  # 登录
            server.send_message(msg)  # 发送邮件
        return True

    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False


def gen_feishu_sign(timestamp: int, secret: str) -> str:
    """按飞书自定义机器人签名规则生成签名。"""
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def build_feishu_update_post(items: List[dict[str, str]]) -> dict:
    """构建飞书富文本更新列表消息体。"""
    content = []
    for item in items:
        previous = item.get("previous") or "-"
        latest = item.get("latest") or "-"
        name = item.get("name") or "unknown"
        content.append(
            [
                {"tag": "text", "text": f"{name}: "},
                {"tag": "text", "text": f"{previous} -> {latest}"},
            ]
        )

    if not content:
        content.append([{"tag": "text", "text": "No updates."}])

    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "Software update notification",
                    "content": content,
                }
            }
        },
    }


def send_feishu_updates(items: List[dict[str, str]]) -> bool:
    """通过飞书自定义机器人发送更新列表，配置缺失或发送失败时返回 False。"""
    secret = os.environ.get("FEISHU_SECRET_KEY")
    if not secret:
        logger.error("Feishu secret key is missing.")
        return False

    timestamp = int(time.time())
    payload = build_feishu_update_post(items)
    payload["timestamp"] = str(timestamp)
    payload["sign"] = gen_feishu_sign(timestamp, secret)

    try:
        response = requests.post(
            FEISHU_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code != 200:
            logger.error(f"Feishu notification failed: HTTP {response.status_code}.")
            return False

        result = response.json()
        if result.get("code") != 0:
            logger.error(f"Feishu notification failed: {result.get('msg', 'unknown error')}.")
            return False

        return True
    except Exception as e:
        logger.error(f"Feishu notification failed: {e}")
        return False
