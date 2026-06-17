import datetime
import fcntl
import os
import sys
import tempfile
import webbrowser

import feedparser
import rumps
from AppKit import NSFont, NSFontAttributeName, NSScreen, NSWorkspace
from Foundation import NSNotificationCenter, NSString

RSS_URL = "https://feeds.nos.nl/nosnieuwsalgemeen"
REFRESH_INTERVAL = 900
MAX_TITLE_WIDTH = 300  # pixels
MAX_TITLE_WORDS = 6
PLACEHOLDER = "NOS"


class NosNewsApp(rumps.App):
    def __init__(self):
        super().__init__(PLACEHOLDER, quit_button="Quit")
        self._url = None
        self._headline = None
        self._open_item = rumps.MenuItem("Open article", callback=self._open)
        self._refresh_item = rumps.MenuItem("Refresh", callback=self._refresh)
        self._last_refreshed_item = rumps.MenuItem("Last refreshed: —")
        self._last_refreshed_item.enabled = False
        self.menu = [self._open_item, None, self._refresh_item, self._last_refreshed_item]
        self._timer = rumps.Timer(self._refresh, REFRESH_INTERVAL)
        self._timer.start()
        NSWorkspace.sharedWorkspace().notificationCenter().addObserver_selector_name_object_(
            self, "_on_wake:", "NSWorkspaceDidWakeNotification", None
        )
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, "_on_screen_change:", "NSApplicationDidChangeScreenParametersNotification", None
        )
        self._fetch()

    def _fetch(self):
        try:
            feed = feedparser.parse(RSS_URL)
            if not feed.entries:
                return
            entry = feed.entries[0]
            self._last_refreshed_item.title = f"Last refreshed: {datetime.datetime.now().strftime('%H:%M')}"
            self._url = entry.link
            self._headline = self._short_title(entry.title)
        except Exception:
            pass
        finally:
            self._update_title()

    def _short_title(self, title):
        return " ".join(title.split()[:MAX_TITLE_WORDS])

    def _external_monitor(self):
        return len(NSScreen.screens()) > 1

    def _update_title(self):
        # The laptop's built-in display is too small for the headline, so only
        # show the article title while an external monitor is connected.
        if self._external_monitor() and self._headline:
            self.title = self._fit(self._headline)
        else:
            self.title = PLACEHOLDER

    def _fit(self, text):
        font = NSFont.menuBarFontOfSize_(0)
        attrs = {NSFontAttributeName: font}
        while text:
            width = NSString.stringWithString_(text).sizeWithAttributes_(attrs).width
            if width <= MAX_TITLE_WIDTH:
                return text
            text = text.rsplit(" ", 1)[0]
        return PLACEHOLDER

    def _on_wake_(self, notification):
        self._fetch()

    def _on_screen_change_(self, notification):
        self._update_title()

    def _refresh(self, _=None):
        self._fetch()

    def _open(self, _):
        if self._url:
            webbrowser.open(self._url)


def _acquire_single_instance_lock():
    # Hold an exclusive lock on a file for the process lifetime so a second
    # launch fails fast instead of running a duplicate menu bar icon. The file
    # handle is intentionally leaked: the OS releases the lock when the process
    # exits.
    lock_path = os.path.join(tempfile.gettempdir(), "latest-nos-news.lock")
    handle = open(lock_path, "w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("Latest NOS News is already running.", file=sys.stderr)
        sys.exit(0)
    return handle


def main():
    _lock = _acquire_single_instance_lock()  # noqa: F841 — kept alive for process lifetime
    NosNewsApp().run()


if __name__ == "__main__":
    main()
