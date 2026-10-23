name: monitor

on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install
        run: |
          pip install requests beautifulsoup4 playwright
          playwright install --with-deps chromium

      - name: Check page
        env:
          TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}
          TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
        run: python check.py

      - name: Save state
        run: |
          git config user.name "monitor-bot"
          git config user.email "bot@users.noreply.github.com"
          git add last_content.txt
          git diff --staged --quiet || (git commit -m "update content" && git push)
