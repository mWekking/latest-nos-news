import webbrowser

import anthropic
import feedparser
import rumps

RSS_URL = "https://feeds.nos.nl/nosnieuwsalgemeen"
REFRESH_INTERVAL = 300


class NosNewsApp(rumps.App):
    def __init__(self):
        super().__init__("NOS", quit_button="Quit")
        self._url = None
        self._open_item = rumps.MenuItem("Open artikel", callback=self._open)
        self._refresh_item = rumps.MenuItem("Vernieuwen", callback=self._refresh)
        self.menu = [self._open_item, None, self._refresh_item]
        self._client = anthropic.Anthropic()
        self._timer = rumps.Timer(self._refresh, REFRESH_INTERVAL)
        self._timer.start()
        self._fetch()

    def _fetch(self):
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            return
        entry = feed.entries[0]
        self._url = entry.link
        summary = entry.get("summary", "")
        msg = self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            messages=[{
                "role": "user",
                "content": (
                    "Summarize this Dutch news item in 4–6 Dutch words, no punctuation:\n"
                    f"Title: {entry.title}\n{summary}"
                ),
            }],
        )
        self.title = msg.content[0].text.strip()

    def _refresh(self, _=None):
        self._fetch()

    def _open(self, _):
        if self._url:
            webbrowser.open(self._url)


def main():
    NosNewsApp().run()


if __name__ == "__main__":
    main()
