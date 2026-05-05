# Latest NOS News

A macOS menu bar app that shows the latest NOS headline as an ultra-short (4–6 word) AI-generated summary. Clicking the summary opens the full article.

---

## Requirements

- macOS
- [UV](https://docs.astral.sh/uv/) package manager
- `ANTHROPIC_API_KEY` environment variable set

---

## Run manually (one-off)

```bash
cd "Latest-nos-news"
uv run latest-nos-news
```

---

## Run automatically at login (LaunchAgent)

Create `~/Library/LaunchAgents/com.markwekking.latest-nos-news.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.markwekking.latest-nos-news</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/mark.wekking/.local/bin/uv</string>
        <string>run</string>
        <string>--directory</string>
        <string>/Users/mark.wekking/Documents/Claude projects/Latest-nos-news</string>
        <string>latest-nos-news</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>ANTHROPIC_API_KEY</key>
        <string>YOUR_API_KEY_HERE</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

### Start

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.markwekking.latest-nos-news.plist
```

### Stop (current session only)

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.markwekking.latest-nos-news.plist
```

### Check status

```bash
launchctl print gui/$(id -u)/com.markwekking.latest-nos-news
```

---

## Project structure

```
Latest-nos-news/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .venv/
└── latest_nos_news/
    ├── __init__.py
    └── app.py
```
