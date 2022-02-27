import sublime, sublime_plugin  
import re
import urllib.parse
import os
  
class InsertHyperlinkCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        # each entry is a tuple with 1+ elements, 2nd element is abbreviation if it exists
        self.bible_abbrs = self.load_bible_abbrs()
        self.view = view

    def load_bible_abbrs(self):
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path + '/bible_abbr.txt', 'r') as f:
            return [s.replace('\n','').split(', ') for s in f.readlines()]

    def find_bible_abbr(self, abbr):
        clean = lambda s: s.replace(' ','').replace('_', '').lower()
        # remove space and underscore from '1 John', '1_Corinthians', etc.
        it = filter(lambda b: list(filter(lambda x: clean(x).startswith(clean(abbr)), b)), self.bible_abbrs)
        book = next(it)
        s = book[1] if len(book) >= 2 else book[0]
        return re.sub(r'^([1-3]) ', '\\1&nbsp;', s)

    def format_range(self, ch, start, end, end2):
        if end2:
            return '{}:{}–{}:{}'.format(ch, start, end, end2)
        elif start and end:
            return '{}:{}–{}'.format(ch, start, end)
        elif end:
            return '{}–{}'.format(ch, end)
        elif start:
            return '{}:{}'.format(ch, start)
        else:
            return '{}'.format(ch)

    def format_bible_ref(self, b, ch, start, end, end2, comma):
        book = self.find_bible_abbr(b)
        if comma:
            extras = [', ' + self.format_range(ch, start, end, end2) for (ch, start, end, end2) in re.findall(r'(\d+)(?:[.:](\d+)(?:-(\d+)(?:[.:](\d+))?)?)?', comma)]
        else:
            extras = []
        return '{}&nbsp;{}{}'.format(book, self.format_range(ch, start, end, end2), ''.join(extras))

    def parse_bible_refs(self, c):
        m = re.search(r'www\.biblegateway\.com/passage/\?search=([^&]+)|biblehub\.com/(?:text/)?([^/]+)/([0-9]+)-([0-9]+)', urllib.parse.unquote(c))
        if not m:
            return
        if m.group(2):
            refs = [(m.group(2), m.group(3), m.group(4), '', '', '')]
            #print(refs)
        elif m.group(1):
            # deut12.32-13:5,17.14-20
            refs = re.findall(r'(?i)([1-3]?[a-z ]+)(?:(\d+)(?:[.:](\d+))?(?:-(\d+)(?:[.:](\d+))?)?)?(?:,([^;]+))?', m.group(1))
            print(refs);

        fixed = [self.format_bible_ref(b, ch, start, end, end2, comma) for (b, ch, start, end, end2, comma) in refs]
        
        return fixed[0] if len(fixed) == 1 else ' and '.join([', '.join(fixed[:-1])] + [fixed[-1]])


    def run(self, edit):
        region = self.view.sel()[0]
        s = self.view.substr(region)
        c = sublime.get_clipboard()
        wiki_m = re.search(r'^https?://en.wikipedia.org/wiki/(.*)', c)
        
        if len(s) == 0 and wiki_m:
            left = "<a href=\"" + c + "\">"
            s = "WP: " + wiki_m.group(1).replace('_', ' ').replace('#', ' § ')#.replace('%27', '\'')
            s = urllib.parse.unquote(s)
            right = "</a>"
        elif len(s) == 0 and self.parse_bible_refs(c):
            left = "<a href=\"" + c + "\">"
            s = self.parse_bible_refs(c)
            right = "</a>"
        elif re.search(r'^(https?://|#)', c):
            left = "<a href=\"" + c + "\">"
            right = "</a>"
        # if I copy a book hyperlink up to the subtitle, it'll be missing a </a>
        elif re.search(r'^[^<>]*<a href="[^"]+">[^<]+$', c):
            left = c
            # swapping these puts the cursor at the end of the line, which is where we want it
            right = ""
            s = "</a>"
        else:
            left = "<a href=\""
            right = "\">" + c + "</a>"
        self.view.replace(edit, region, left + s + right)
        region = self.view.sel()[0]
        self.view.sel().clear()
        idx = region.b if s != "" else region.a + len(left)
        self.view.sel().add(sublime.Region(idx, idx))