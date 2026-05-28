import datetime
import webbrowser

import anthropic
import feedparser
import rumps
from AppKit import NSFont, NSFontAttributeName, NSWorkspace
from Foundation import NSString

RSS_URL = "https://feeds.nos.nl/nosnieuwsalgemeen"
REFRESH_INTERVAL = 900
MAX_TITLE_WIDTH = 300  # pixels


class NosNewsApp(rumps.App):
    def __init__(self):
        super().__init__("NOS", quit_button="Quit")
        self._url = None
        self._open_item = rumps.MenuItem("Open article", callback=self._open)
        self._refresh_item = rumps.MenuItem("Refresh", callback=self._refresh)
        self._last_refreshed_item = rumps.MenuItem("Last refreshed: —")
        self._last_refreshed_item.enabled = False
        self.menu = [self._open_item, None, self._refresh_item, self._last_refreshed_item]
        self._client = anthropic.Anthropic()
        self._timer = rumps.Timer(self._refresh, REFRESH_INTERVAL)
        self._timer.start()
        NSWorkspace.sharedWorkspace().notificationCenter().addObserver_selector_name_object_(
            self, "_on_wake:", "NSWorkspaceDidWakeNotification", None
        )
        self._fetch()

    def _fetch(self):
        try:
            feed = feedparser.parse(RSS_URL)
            if not feed.entries:
                return
            entry = feed.entries[0]
            self._last_refreshed_item.title = f"Last refreshed: {datetime.datetime.now().strftime('%H:%M')}"
            if entry.link == self._url:
                return
            self._url = entry.link
            self.title = f"{self.title} ↻"
            summary = entry.get("summary", "")
            msg = self._client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=20,
                messages=[{
                    "role": "user",
                    "content": (
                        "Summarize this Dutch news item in as few Dutch words as possible, max 6, no punctuation:\n"
                        f"Title: {entry.title}\n{summary}"
                    ),
                }],
            )
            self.title = self._fit(msg.content[0].text.strip())
        except Exception:
            self.title = self.title.removesuffix(" ↻")

    def _fit(self, text):
        font = NSFont.menuBarFontOfSize_(0)
        attrs = {NSFontAttributeName: font}
        while text:
            width = NSString.stringWithString_(text).sizeWithAttributes_(attrs).width
            if width <= MAX_TITLE_WIDTH:
                return text
            text = text.rsplit(" ", 1)[0]
        return "NOS"

    def _on_wake_(self, notification):
        self._fetch()

    def _refresh(self, _=None):
        self._fetch()

    def _open(self, _):
        if self._url:
            webbrowser.open(self._url)


def main():
    NosNewsApp().run()


if __name__ == "__main__":
    main()
