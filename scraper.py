# ============================================================
# scraper.py — 只监控 Reuters、SEC Filing、Earnings 来源
# （早晚报用 daily_report.py 里单独的 RSS，不受此影响）
# ============================================================

import requests
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from config import REQUEST_DELAY_SECONDS

HEADERS = {
    "User-Agent": "NewsBot/1.0 contact@newsbot.com",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

SEC_HEADERS = {
    "User-Agent": "NewsBot research@newsbot.com",
    "Accept": "application/atom+xml, application/xml, text/xml, */*",
    "Host": "www.sec.gov",
}

# ── 监控来源：只保留 Reuters、SEC Filing、Earnings ────────────
RSS_FEEDS = [
    # SEC 重大事件公告（8-K 包含 earnings、重大交易、FDA结果等）
    {
        "source": "SEC Filing",
        "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&dateb=&owner=include&count=40&search_text=&output=atom",
        "headers": SEC_HEADERS,
    },
    # Reuters 财经 & 市场
    {
        "source": "Reuters",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+earnings+OR+results+OR+profit+OR+revenue&hl=en-US&gl=US&ceid=US:en",
        "headers": HEADERS,
    },
    {
        "source": "Reuters",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+stocks+OR+markets+OR+fed+OR+rates&hl=en-US&gl=US&ceid=US:en",
        "headers": HEADERS,
    },
]


def is_recent(published_at: str, minutes: int = 240) -> bool:
    """只保留最近40分钟内发布的文章"""
    if not published_at:
        return True
    try:
        pub_time = parsedate_to_datetime(published_at)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return pub_time >= cutoff
    except Exception:
        pass
    try:
        published_at = published_at.replace("Z", "+00:00")
        pub_time = datetime.fromisoformat(published_at)
        if pub_time.tzinfo is None:
            pub_time = pub_time.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return pub_time >= cutoff
    except Exception:
        return True


def _get_text(element, tag_options):
    for tag in tag_options:
        el = element.find(tag)
        if el is not None and el.text:
            return el.text.strip()
    return ""


def _get_attr(element, tag, attr):
    el = element.find(tag)
    if el is not None:
        return el.get(attr, "")
    return ""


def _strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def fetch_rss(feed):
    url = feed["url"]
    source = feed["source"]
    headers = feed.get("headers", HEADERS)
    articles = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        time.sleep(REQUEST_DELAY_SECONDS)
        root = ET.fromstring(resp.content)

        items = root.findall(".//item")
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items:
            title = _get_text(item, ["title", "{http://www.w3.org/2005/Atom}title"])
            if not title or len(title) < 5:
                continue

            link = (
                _get_text(item, ["link"]) or
                _get_attr(item, "{http://www.w3.org/2005/Atom}link", "href") or
                _get_attr(item, "link", "href")
            )
            if not link:
                continue

            guid = _get_text(item, ["guid", "id", "{http://www.w3.org/2005/Atom}id"]) or link
            article_id = guid.split("?")[0].rstrip("/")

            summary = _get_text(item, [
                "description", "summary",
                "{http://www.w3.org/2005/Atom}summary",
                "{http://www.w3.org/2005/Atom}content",
            ]) or ""
            summary = _strip_html(summary)[:500]

            published_at = _get_text(item, [
                "pubDate", "published", "updated",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated",
            ]) or ""

            articles.append({
                "id": article_id,
                "title": title.strip(),
                "url": link.strip(),
                "source": source,
                "published_at": published_at,
                "summary": summary,
            })

    except ET.ParseError as e:
        print(f"[RSS解析失败] {source} — XML格式错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"[RSS抓取失败] {source} — {e}")
    except Exception as e:
        print(f"[RSS未知错误] {source} — {e}")

    return articles


def fetch_article_content(url):
    try:
        from bs4 import BeautifulSoup
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        content_el = (
            soup.find(class_=re.compile(r"article-body|post-content|story-body", re.I)) or
            soup.find("article") or soup.find("main")
        )
        text = content_el.get_text(separator=" ", strip=True) if content_el else soup.get_text(separator=" ", strip=True)
        return re.sub(r'\s+', ' ', text).strip()[:2000]
    except Exception:
        return ""


def get_latest_articles():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始抓取（Reuters / SEC Filing / Earnings）...")

    all_articles = []
    seen_urls = set()

    for feed in RSS_FEEDS:
        articles = fetch_rss(feed)
        added = 0
        filtered = 0
        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                if is_recent(article["published_at"], minutes=240):
                    all_articles.append(article)
                    added += 1
                else:
                    filtered += 1
        if added > 0:
            print(f"  {feed['source']}: {added} 篇新文章（过滤旧文章 {filtered} 篇）")
        elif filtered > 0:
            print(f"  {feed['source']}: 0 篇（全部超过40分钟）")

    print(f"[抓取完成] 共 {len(all_articles)} 篇待分析")
    return all_articles
