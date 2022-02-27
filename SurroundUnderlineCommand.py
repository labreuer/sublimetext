import sublime, sublime_plugin  
  
class SurroundUnderlineCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        region = self.view.sel()[0]
        s = self.view.substr(region)  
        c = sublime.get_clipboard()
        left = "<u>"
        right = "</u>"
        sub = left + s + right if s != "" else left
        self.view.replace(edit, region, sub)
        region = self.view.sel()[0]
        self.view.sel().clear()
        idx = region.b if s != "" else region.a + len(left)
        self.view.sel().add(sublime.Region(idx, idx))