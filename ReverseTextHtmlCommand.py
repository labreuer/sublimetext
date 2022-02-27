import sublime, sublime_plugin  
  
class ReverseTextHtmlCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        region = self.view.sel()[0]
        s = self.view.substr(region)  
        c = sublime.get_clipboard()
        left = "&#8238;"
        right = "&#8236;"
        sub = left + s[::-1] + right #if s != "" else left
        self.view.replace(edit, region, sub)
        region = self.view.sel()[0]
        self.view.sel().clear()
        idx = region.b if s != "" else region.a + len(left)
        self.view.sel().add(sublime.Region(idx, idx))