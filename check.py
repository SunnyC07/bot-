#!/usr/bin/env python3
"""單次檢查版 (給 GitHub Actions 用)。內容變動時透過 Telegram 通知。"""
import difflib
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://ec-v2.tigerairtw.com/zh-tw/check-flight-status/IT202/2026-10-24"
STATE_FILE = Path("last_content.txt")


def fetch_text() -> str:
    with sync_playwright() as p:
