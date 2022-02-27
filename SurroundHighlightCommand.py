import sublime, sublime_plugin  
  
class SurroundHighlightCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        region = self.view.sel()[0]
        s = self.view.substr(region)  
        c = sublime.get_clipboard()
        left = "<span style='background-color: rgb(255, 250, 165);'>"
        right = "</span>"
        sub = left + s + right if s != "" else left
        self.view.replace(edit, region, sub)
        region = self.view.sel()[0]
        self.view.sel().clear()
        idx = region.b if s != "" else region.a + len(left)
        self.view.sel().add(sublime.Region(idx, idx))