import sublime, sublime_plugin
import re

  
class InsertUrlCompletionCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        c = sublime.get_clipboard()
        region = self.view.sel()[0]
        #s = self.view.substr(region)

        is_markdown = re.search(r'\[.*\]\(.*\)', c)
        if is_markdown:
            r = re.search(r'^(?P<p>[^_[]*)\[(?P<t>[^]]+)\]\((?P<u>([^)]|\\\))+)\)$', c)
            text = r['t']
            url = r['u']
            prefix = r['p']
        else:
            r = re.search(r'^(?P<p>[^<>]*)<a href="(?P<u>[^"]+)">(?P<t>.*)</a>', c)
            if r == None:
                r = re.search(r'^(?P<p>[^<>]*)<a href=\'(?P<u>[^\']+)\'>(?P<t>.*)</a>', c)
            if r != None:
                text = r['t']
                url = r['u']
                prefix = r['p']
                url = url.replace(')', '\\)')

        if r == None:
            raise ValueError('Regex did not match.')
            return
        else:
            url = url.replace('\\', '\\\\')

        annotation = ''
        trigger = ''
        if re.search(r'^(\d&nbsp;)?\w+&nbsp;\d+', text):
            trigger = text.replace('&nbsp;', '').replace(':', '.').replace('–', '-').lower()
            annotation = f""",
            "annotation": "{text.replace('&nbsp;', ' ')}\""""

        completion = f""",
        {{
            "trigger": "{trigger or text}",
            "contents": "{prefix}[{text}]({url})",
            "kind": "snippet"{annotation}
        }}"""

        if region.empty():
            self.view.insert(edit, region.begin(), completion)
        else:
            self.view.replace(edit, region, completion)