"""
sep_markdown_link.py — Sublime Text plugin
==========================================
Reads a Stanford Encyclopedia of Philosophy URL from the clipboard,
fetches the entry page, and inserts a formatted Markdown link at every
cursor position (replacing any selection), e.g.:

    [SEP: Concepts of Disease and Health](https://plato.stanford.edu/entries/health-disease/)

Also copies the result to the clipboard so it's available elsewhere.

STANDALONE USE
--------------
The core function fetch_sep_link() can be imported and used independently
of Sublime Text — pass it a URL and a callback:

    from sep_markdown_link import fetch_sep_link

    fetch_sep_link(
        "https://plato.stanford.edu/entries/health-disease/",
        on_success=lambda link: print(link),
        on_error=lambda msg: print("Error:", msg),
    )

The callbacks are invoked from a background thread, so marshal to your
own main thread if needed (e.g. sublime.set_timeout, wx.CallAfter, etc.).

INSTALL (Sublime Text)
----------------------
Copy this file to your User package directory:
    Packages/User/sep_markdown_link.py

You can find the directory via:
    Preferences → Browse Packages… → User/

USAGE (Sublime Text)
--------------------
Bind a key in Preferences → Key Bindings (User):

    { "keys": ["ctrl+alt+s"], "command": "sep_markdown_link" }

Or invoke via the Command Palette as "SEP: Insert Markdown Link".
"""

import re
import threading
import urllib.request
from html.parser import HTMLParser
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Minimal HTML parser — grabs the first <title> and the first <h1> text so
# we can pick whichever looks cleaner.
# ---------------------------------------------------------------------------

class _PageTitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._tag_stack: list[str] = []
        self.title_text = ""   # from <title>
        self.h1_text    = ""   # from first <h1>

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data):
        if not self._tag_stack:
            return
        current = self._tag_stack[-1]
        if current == "title" and not self.title_text:
            self.title_text = data.strip()
        elif current == "h1" and not self.h1_text:
            self.h1_text = data.strip()


# ---------------------------------------------------------------------------
# Helper — strip the boilerplate SEP suffix from the <title> tag text.
# e.g. "Concepts of Disease and Health (Stanford Encyclopedia of Philosophy)"
#   -> "Concepts of Disease and Health"
# ---------------------------------------------------------------------------

_SEP_SUFFIX = re.compile(
    r"\s*\(Stanford Encyclopedia of Philosophy[^)]*\)\s*$",
    re.IGNORECASE,
)

_SEP_URL = re.compile(
    r"^https?://plato\.stanford\.edu/entries/[A-Za-z0-9_-]+/?$"
)

def _clean_title(raw: str) -> str:
    return _SEP_SUFFIX.sub("", raw).strip()


# ---------------------------------------------------------------------------
# Public API — usable outside Sublime Text
# ---------------------------------------------------------------------------

def fetch_sep_link(
    url: str,
    on_success: Callable[[str], None],
    on_error: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Fetch a Stanford Encyclopedia of Philosophy entry and asynchronously
    deliver a formatted Markdown hyperlink to *on_success*.

    Parameters
    ----------
    url:
        A plato.stanford.edu entry URL, e.g.
        "https://plato.stanford.edu/entries/health-disease/"
    on_success:
        Called with the completed Markdown link string, e.g.
        "[SEP: Concepts of Disease and Health](https://plato.stanford.edu/entries/health-disease/)"
        Invoked from a background thread — marshal to your UI thread if needed.
    on_error:
        Optional. Called with a human-readable error string if anything goes
        wrong (bad URL, network failure, title not found).
        Invoked from a background thread.

    Returns immediately; the fetch runs on a daemon thread.
    """
    def _error(msg: str) -> None:
        if on_error is not None:
            on_error(msg)

    if not _SEP_URL.match(url.strip()):
        _error(f"Not a plato.stanford.edu entry URL: {url!r}")
        return

    def _worker():
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SEP Markdown Link)"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")

        except Exception as exc:
            _error(f"Fetch failed: {exc}")
            return

        parser = _PageTitleParser()
        parser.feed(html)

        # Prefer <h1> (already clean on SEP pages), else strip <title> suffix.
        if parser.h1_text:
            title = parser.h1_text.strip()
        elif parser.title_text:
            title = _clean_title(parser.title_text)
        else:
            _error("Could not find a page title in the response")
            return

        if not title:
            _error("Page title was empty after cleaning")
            return

        on_success(f"[SEP: {title}]({url})")

    threading.Thread(target=_worker, daemon=True).start()


# ---------------------------------------------------------------------------
# Sublime Text integration — only loaded when sublime is available
# ---------------------------------------------------------------------------

try:
    import sublime
    import sublime_plugin

    class SepInsertLinkCommand(sublime_plugin.TextCommand):
        """Internal: replace every selection/cursor with *link*."""

        def run(self, edit, link=""):
            for region in self.view.sel():
                self.view.replace(edit, region, link)

    class SepMarkdownLinkCommand(sublime_plugin.TextCommand):
        """
        Read a plato.stanford.edu URL from the clipboard, fetch the page, and
        insert '[SEP: <Title>](<url>)' at every cursor / selection in the view.
        """

        def run(self, edit):
            url = sublime.get_clipboard().strip()
            sublime.status_message("SEP: fetching entry…")

            def on_success(link: str):
                def _main():
                    self.view.run_command("sep_insert_link", {"link": link})
                    #sublime.set_clipboard(link)
                    sublime.status_message(f"SEP: inserted → {link}")
                sublime.set_timeout(_main, 0)

            def on_error(msg: str):
                sublime.set_timeout(
                    lambda: sublime.status_message(f"SEP: {msg}"), 0
                )

            fetch_sep_link(url, on_success=on_success, on_error=on_error)

except ImportError:
    pass  # Running outside Sublime Text — Sublime classes simply won't exist.