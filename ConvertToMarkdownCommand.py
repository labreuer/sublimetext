import sublime, sublime_plugin, re
  
class ConvertToMarkdownCommand(sublime_plugin.TextCommand):
    def find_previous(self, rx):
        cur = self.view.sel()[0]
        x = []
        p = self.view.find_all(rx, 0, "$1", x)
        v = None

        # in case we're located after the last match
        x.append(v)
        p.append(cur)

        for r, s in zip(p, x):
            if r.a >= cur.a:
                return v
            v = r

    def convert_blockquote(s):
        def inside(m, pad_with_newlines=False):
            s = m.group(1)
            # only add spaces after a non-empty line, and don't if the next line is empty
            s = re.sub(r'((?<=\S)| +)(\r?\n)(?![\r\n])', '  \\2', s)
            s = re.sub(r'^', '> ', s, flags=re.MULTILINE)
            if pad_with_newlines:
                s = f"\n\n{s}\n\n"
                print(s)
            return s
        s = re.sub(r'</p>\s*<p>', '\n\n', s)
        s = re.sub(r'<p>(.*?)</p>', '\\1', s)

        # so ghetto, but doing a proper HTML parse is too much effort for now
        while re.match(r'<blockquote>((?!</blockquote>).)*<blockquote>', s):
            s = re.sub(r'<blockquote>(((?!</?blockquote>).)*)</blockquote>', lambda p: inside(p, True), s, flags=re.DOTALL)

        return re.sub(r'<blockquote>(.*)</blockquote>', inside, s, flags=re.DOTALL)

    def run(self, edit):
        region = self.view.sel()[0]
        s = self.view.substr(region)

        if re.search(r'(?m)^(\t| {5}(?! ))', s):
            m_whitespace = re.search(r'\s+$', s)
            if m_whitespace:
                region = sublime.Region(region.begin(), region.end() - len(m_whitespace.group(0)))
                self.view.sel().clear()
                self.view.sel().add(region)
                s = self.view.substr(region)


            s = s.replace('         ', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
            s = s.replace('       ', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
            s = s.replace('     ', '&nbsp;&nbsp;&nbsp;&nbsp;')
            s = s.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
            s = re.sub(r'(?m)(?<!\s) *$', '  ', s)
            s = re.sub(r'(?m) +(?=\n\n)', '', s)
            s = re.sub(r'(?m)^', '> ', s)
            s = re.sub(r'Yahweh|the LORD|GOD', 'YHWH', s)
            s = s.strip()
            sub = s;
        else:

            if len(s) == 0:
                left_tag = self.find_previous(r'<a [^>]*>')
                if left_tag == None:
                    return
                right_tag = self.view.find(r'</a>', left_tag.end())
                if right_tag == None:
                    return
                region = sublime.Region(left_tag.begin(), right_tag.end())
                self.view.sel().clear()
                self.view.sel().add(region)

            sub = self.view.substr(region)
            sub = re.sub(r'<a href=["\']([^"\']+).*?>(.*?)</a>', 
                lambda m: '[{}]({})'.format(self.markdown_escape_url_text(m.group(2)), self.markdown_escape_url(m.group(1))),
                sub)
            sub = re.sub(r'<br/>', '\n', sub)
            sub = ConvertToMarkdownCommand.convert_blockquote(sub)
            sub = re.sub(r'<i>(.*?)</i>', '_\\1_', sub)
            sub = re.sub(r'<b>(.*?)</b>', '**\\1**', sub)
            sub = re.sub(r'&nbsp;&nbsp;&nbsp;&nbsp; ?(\d+\.)', '\\1', sub)
            sub = re.sub(r'&nbsp;&nbsp;&nbsp;&nbsp; ?(•)', '-', sub)
        
        self.view.replace(edit, region, sub)
        idx = self.view.sel()[0].end()
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(idx, idx))

    # stolen from InsertHyperlinkCommand
    def markdown_escape_url(self, url):
        return re.sub(r'(?<!\\)([\)])', '\\\\\\1', url)

    def markdown_escape_url_text(self, s):
        return re.sub(r'(?<!\\)([\[\]])', '\\\\\\1', s)