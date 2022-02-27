import sublime
import sublime_plugin
from pprint import pprint

class FindReplyCommand(sublime_plugin.TextCommand):
    def find_previous(self, rx):
        cur = self.view.sel()[0]
        x = []
        p = self.view.find_all(rx, 0, "$1", x)
        v = ""

        for r, s in zip(p, x):
            if r.a > cur.a:
                return (last_s, last_r)
            last_s = s
            last_r = r

    def run(self, edit):
        #print([p for p in self.view.window().panels() if p == 'console'])
        if (not self.view.is_in_edit()):
        	self.view.window().run_command('hide_panel')

        (url, r) = self.find_previous(r'<a href="([^"]+)"[^>]* class="time-ago"')
        
        # I couldn't figure out how to set the find text directly ...
        self.view.sel().clear()
        start = r.a + len('<a href="')
        end = start + len(url)
        self.view.sel().add(sublime.Region(start, end))

        self.view.window().run_command('show_panel', { 'panel': 'find' })
        




