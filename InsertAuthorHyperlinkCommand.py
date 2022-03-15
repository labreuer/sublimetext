import sublime, sublime_plugin
import re

  
class InsertAuthorHyperlinkCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        c = sublime.get_clipboard()
        region = self.view.sel()[0]
        s = self.view.substr(region)

        is_markdown = self.view.syntax() and self.view.syntax().name == 'Markdown'
        if is_markdown:
            c = re.sub(r'(?<!\\)([\)])', '\\\\\\1', c)
            left = "["
            right = "](" + c + "): "
            if s != "":
                left = "> " + left
                right = right + s
        else:
            left = "<a href=\"" + c + "\">"
            right = "</a>: "
            if s != "":
                left = "<blockquote>" + left
                right = right + s + "</blockquote>"

        #region = self.view.sel()[0]
        self.view.replace(edit, region, left + right)
        region = self.view.sel()[0]
        self.view.sel().clear()
        idx = region.a + len(left)
        self.view.sel().add(sublime.Region(idx, idx))