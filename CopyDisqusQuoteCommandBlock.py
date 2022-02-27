import sublime, sublime_plugin, re
  
class CopyDisqusQuoteBlockCommand(sublime_plugin.TextCommand):
    def find_previous(self, rx):
        cur = self.view.sel()[0]
        x = []
        p = self.view.find_all(rx, 0, "$1", x)
        v = ""

        # in case we're located after the last match
        x.append(v)
        p.append(cur)

        for r, s in zip(p, x):
            if r.a >= cur.a:
                return v
            v = s

    def run(self, edit):
        #c = sublime.get_clipboard()
        region = self.view.sel()[0]
        s = self.view.substr(region)
        if s == "":
            return

        special_abbr = {
            'dcleve': 'dc',
            'guerillasurgeon': 'gs',
            '3lemenope': '3l',
            '(((J_Enigma32)))': 'JE',
            '90Lew90': '90',
            '3vil5triker .': '35',
            'Rick O\'Shea': 'RO\'S'
        }

        s = re.sub(' rel="nofollow( noopener)?"', '', s)
        url = self.find_previous(r'<a href="([^"]+)"[^>]* class="time-ago"')
        user = self.find_previous(r'<a href="[^"]+"[^>]* data-username[^>]*>([^<]+)')
        abbr = special_abbr[user] if user in special_abbr else re.sub("(?<!^)(?<![ _-])[^A-Z]", "", user)

        sublime.set_clipboard('<blockquote><a href="%s">%s</a>: %s</blockquote>' % (url, abbr, s))
        #sublime.set_clipboard('<a href="%s">"%s"</a>' % (url, s))