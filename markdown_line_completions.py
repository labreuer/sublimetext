import os
import re
import sublime
import sublime_plugin


# Paths are passed through os.path.expanduser / os.path.expandvars, so "~"
# resolves to the home directory on both Linux (/home/<user>) and Windows
# (C:\Users\<user>). Forward slashes work on both platforms.
SEARCH_FILES = [
    "~/Dropbox/snippets.md",
    "~/Dropbox/books.md",
]

COMPLETIONS_RESOURCE = "Packages/User/Markdown.sublime-completions"


# Matches common explicit URLs:
#   https://example.com/path
#   http://example.com/path
#   ftp://example.com/path
#   www.example.com/path
URL_RE = re.compile(
    r"""
    (?:
        (?:https?|ftp)://[^\s<>()\[\]{}]+
        |
        www\.[^\s<>()\[\]{}]+
    )
    """,
    re.IGNORECASE | re.VERBOSE
)

# Matches the destination portion of Markdown links:
#   [visible text](https://example.com/path)
#
# Only the URL/destination is removed. The visible link text remains searchable.
MARKDOWN_LINK_DESTINATION_RE = re.compile(
    r"""
    (?<=\]\()
    [^)\s]+
    (?=\))
    """,
    re.VERBOSE
)


class MarkdownLineCompletions(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if prefix == "":
            return

        filename = view.file_name() or ""
        syntax = view.settings().get("syntax", "")

        is_markdown = (
            filename.lower().endswith((".md", ".markdown", ".mdown"))
            or "Markdown" in syntax
        )

        if not is_markdown:
            return []

        prefix_lower = prefix.lower()

        completions, existing_values = self.load_sublime_completions()
        completions = []

        # Tracks complete file-derived lines already added during this query.
        seen_lines = set()

        for path in SEARCH_FILES:
            expanded_path = os.path.expandvars(
                os.path.expanduser(path)
            )

            try:
                with open(
                    expanded_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as source:
                    for raw_line in source:
                        line = raw_line.rstrip("\r\n")

                        if not line:
                            continue

                        searchable_text = self.remove_urls(line).lower()

                        # Search outside URLs, but return the complete line.

                        new_completion = None
                        for word in re.findall(r"\b[\w'-]+\b", searchable_text):
                            if word.lower().startswith(prefix_lower):
                                new_completion = word + "\t" + searchable_text
                                break

                        #if not any(word.startswith(prefix_lower) for word in re.findall(r"\b[\w'-]+\b", searchable_text.lower())):
                        #    continue

                        if not new_completion:
                            continue;

                        normalized_line = line.casefold()

                        # Do not duplicate:
                        #   1. entries from Markdown.sublime-completions
                        #   2. lines already found in another search file
                        if (
                            normalized_line in existing_values
                            or normalized_line in seen_lines
                        ):
                            continue

                        seen_lines.add(normalized_line)
                        completions.append((searchable_text, line))
                        #completions.append((new_completion + "\t" + searchable_text, line))

            except OSError as error:
                print(
                    "MarkdownLineCompletions: "
                    "could not read {!r}: {}".format(
                        expanded_path,
                        error
                    )
                )

        return completions

    def load_sublime_completions(self):
        """
        Return:
            completions:
                Sublime completion tuples in their original order.

            existing_values:
                Case-insensitive set containing both the displayed trigger
                and inserted contents of each completion. File-derived lines
                matching either value will not be added.
        """
        try:
            contents = sublime.load_resource(COMPLETIONS_RESOURCE)
            data = sublime.decode_value(contents)
        except Exception as error:
            print(
                "MarkdownLineCompletions: "
                "could not load {}: {}".format(
                    COMPLETIONS_RESOURCE,
                    error
                )
            )
            return [], set()

        completions = []
        existing_values = set()

        for entry in data.get("completions", []):
            if isinstance(entry, str):
                completions.append((entry, entry))
                existing_values.add(entry.casefold())
                continue

            if not isinstance(entry, dict):
                continue

            trigger = entry.get("trigger")
            insertion = entry.get("contents", trigger)

            if not trigger or insertion is None:
                continue

            completions.append((trigger, insertion))
            existing_values.add(trigger.casefold())

            if isinstance(insertion, str):
                existing_values.add(insertion.casefold())

        return completions, existing_values

    @staticmethod
    def remove_urls(text):
        """
        Remove URL text for matching purposes only.

        Examples:
            See [Sublime](https://www.sublimetext.com/)
                -> See [Sublime]()

            Visit https://www.sublimetext.com/docs/
                -> Visit
        """
        text = MARKDOWN_LINK_DESTINATION_RE.sub("", text)
        text = URL_RE.sub("", text)
        return text
