import sublime, sublime_plugin, re
  
class RemoveEnclosingTagCommand(sublime_plugin.TextCommand):
    def find_previous(self, rx):
        cur = self.view.sel()[0]
        x = []
        p = self.view.find_all(rx, 0, "$1", x)
        v = ""

        for r in p:
            if r.a > cur.a:
                return v
            v = r

    def run(self, edit):
        cur = self.view.sel()[0]
 
        # Check if cursor is inside a Markdown link [text](url)
        # NOTE: doesn't deal with escaped []
        md_links = self.view.find_all(r'\[([^\]]*)\]\([^\)]*\)')
        for link in md_links:
            if link.contains(cur.a):
                link_content = self.view.substr(link)
                m = re.match(r'\[([^\]]*)\]\([^\)]*\)', link_content)
                if m:
                    #self.view.replace(edit, link, m.group(1))
                    self.view.replace(edit, link, '')
                return
 
        # NOTE: doesn't deal with escaped markdown
        rx = r'<[^>]*>|\*\*|~~|\*|_'
        left = self.find_previous(rx)
        if not left:
            return
 
        left_text = self.view.substr(left)
 
        if left_text.startswith('<'):
            right_rx = r'<[^>]*>'
        else:
            right_rx = re.escape(left_text)
 
        right = self.view.find(right_rx, self.view.sel()[0].a)
        if not right:
            return
 
        self.view.erase(edit, right)
        self.view.erase(edit, left)