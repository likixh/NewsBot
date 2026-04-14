# ============================================================
# feishu.py — 飞书 Webhook 推送
# ============================================================

import requests
import json
from config import FEISHU_WEBHOOK_URL


def send_feishu_text(text: str) -> bool:
    """发送纯文本消息到飞书"""
    payload = {
        "msg_type": "text",
        "content": {"text": text}
    }
    return _post(payload)


def send_feishu_markdown(title: str, content: str) -> bool:
    """
    发送富文本卡片消息（飞书自定义机器人支持的格式）
    content 支持基础 markdown
    """
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }
    return _post(payload)


def send_news_alert(title_header: str, content: str, color: str = "blue") -> bool:
    """
    发送单条新闻推送卡片
    color: green=看涨, red=看跌, blue=中性
    """
    color_map = {"green": "green", "red": "red", "blue": "blue", "orange": "orange"}
    template = color_map.get(color, "blue")

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title_header},
                "template": template
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }
    return _post(payload)


def send_daily_report(report_type: str, content: str) -> bool:
    """
    发送早报/晚报
    report_type: "早报" 或 "晚报"
    """
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"全球财经{report_type} — {today}"
    color = "orange" if report_type == "早报" else "purple"

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }
    return _post(payload)


def _post(payload: dict) -> bool:
    """底层POST请求"""
    if not FEISHU_WEBHOOK_URL:
        print("[飞书] 未配置 FEISHU_WEBHOOK_URL，跳过推送")
        return False

    try:
        resp = requests.post(
            FEISHU_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        result = resp.json()
        if result.get("code") == 0 or result.get("StatusCode") == 0:
            return True
        else:
            print(f"[飞书] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[飞书] 请求异常: {e}")
        return False
