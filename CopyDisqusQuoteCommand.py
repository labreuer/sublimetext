import sublime, sublime_plugin, re
  
class CopyDisqusQuoteCommand(sublime_plugin.TextCommand):
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

        s = re.sub(' rel="nofollow( noopener)?"', '', s)
        url = self.find_previous(r'<a href="([^"]+)"[^>]* class="time-ago"')
        user = self.find_previous(r'<a href="[^"]+"[^>]* data-username[^>]*>([^<]+)')
        abbr = re.sub("[^A-Z]", "", user) or user[0]

        #sublime.set_clipboard('<blockquote><a href="%s">%s</a>: %s</blockquote>' % (url, abbr, s))
        sublime.set_clipboard('<a href="%s">"%s"</a>' % (url, s))