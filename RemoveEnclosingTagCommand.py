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
        left_tag = self.find_previous(r'<[^>]*>')
        right_tag = self.view.find(r'<[^>]*>', self.view.sel()[0].a)
        self.view.erase(edit, right_tag)
        self.view.erase(edit, left_tag)
