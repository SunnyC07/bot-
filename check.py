#!/usr/bin/env python3
"""單次檢查版 (給 GitHub Actions 用)。內容變動時透過 Telegram 通知。"""
import difflib
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://ec-v2.tigerairtw.com/zh-tw/check-flight-status/IT202/2026-10-24"
STATE_FILE = Path("last_content.txt")

# 會自動變動、不代表航班異動的行，比對前先排除
IGNORE_PATTERNS = [
    r"^\d{1,2}:\d{2},\s*\d{4}-\d{2}-\d{2}$",  # 14:51, 2026-10-23
    r"^最新更新$",
    r"^台北時間.*$",
]


def fetch_text() -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(10000)
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    lines = [
        ln for ln in lines
        if ln and not any(re.match(pat, ln) for pat in IGNORE_PATTERNS)
    ]
    return "\n".join(lines)


def notify(text: str) -> None:
    token, chat_id = os.getenv("TG_BOT_TOKEN"), os.getenv("TG_CHAT_ID")
    print(text)
    if token and chat_id:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text[:4000]},
            timeout=15,
        )


def main() -> None:
    new = fetch_text()
    print("抓到內容長度:", len(new))
    old = STATE_FILE.read_text(encoding="utf-8") if STATE_FILE.exists() else None

    if old is None:
        print("首次記錄完成")
    elif new != old:
        diff = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
        added = [d[1:] for d in diff if d.startswith("+") and not d.startswith("+++")]
        diff = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
        removed = [d[1:] for d in diff if d.startswith("-") and not d.startswith("---")]
        msg = "IT202 航班狀態已更新\n" + URL
        msg += "\n\n【新】\n" + "\n".join(added[:30])
        msg += "\n\n【舊】\n" + "\n".join(removed[:30])
        notify(msg)
    else:
        print("無變動")

    STATE_FILE.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
