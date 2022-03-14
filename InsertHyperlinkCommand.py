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

    # delimit passages within a book by comma (,) and books by semicolon (;)
    def parse_bible_refs(self, c):
        m = re.search(r'^https?://(?:www\.biblegateway\.com/passage/\?search=([^&]+)|biblehub\.com/(?:text/)?([^/]+)/([0-9]+)-([0-9]+))', urllib.parse.unquote(c))
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
        sel = self.view.substr(region)
        clip = sublime.get_clipboard()
        wiki_m = re.search(r'^https?://en.wikipedia.org/wiki/(.*)', clip)
        book_m = re.search(r'^[^<>]*<a href="[^"]+">[^<]+(</a>)?$', clip)
        url_m = re.search(r'^(https?://|#)', clip)
        url = None
        get_index = None
        is_markdown = self.view.syntax() and self.view.syntax().name == 'Markdown'
        
        if len(sel) == 0 and wiki_m:
            url = clip
            s = "WP: " + wiki_m.group(1).replace('_', ' ').replace('#', ' § ')#.replace('%27', '\'')
            s = urllib.parse.unquote(s)
        elif len(sel) == 0 and self.parse_bible_refs(clip):
            url = clip
            s = self.parse_bible_refs(clip)
        elif url_m:
            url = clip
            s = sel
        elif len(sel) == 0 and book_m:
            print(book_m.group(1))
            s = clip
            if not book_m.group(1):
                s = s + "</a>"
            if is_markdown:
                s = re.sub(r'<a href=["\']([^"\']+).*?>(.*?)</a>', '[\\2](\\1)', s)
        else:
            # the clipbord does not contain a hyperlink
            # ignore sel
            if is_markdown:
                left = "[" + clip + "]("
                right = ")"
                get_index = lambda r: r.end() - len(right)
            else:
                left = "<a href=\""
                right = "\">" + clip + "</a>"
                get_index = lambda r: r.begin() + len(left)

            s = left + right

        if url:
            if is_markdown:
                # a [x] b -> [a \[x\] b](url)
                s = re.sub(r'(?<!\\)([\[\]])', '\\\\\\1', s)
                left = "[" + s
                right = "](" + url + ")"
                if len(s) == 0:
                    get_index = lambda r: r.begin() + len(left)
            else:
                left = "<a href=\"" + url + "\">"
                right = s + "</a>"
                if len(s) == 0:
                    get_index = lambda r: r.end() - len(right)
            s = left + right

        if get_index == None:
            get_index = lambda r: r.end()

        self.view.replace(edit, region, s)
        region = self.view.sel()[0]
        self.view.sel().clear()
        idx = get_index(region)
        self.view.sel().add(sublime.Region(idx, idx))
