# Custom key bindings

All bindings live in `Default (Windows).sublime-keymap` and `Default (Linux).sublime-keymap`.
The two files are kept in sync by hand; the Linux file also carries two Linux-only extras at the end.

Thirteen of the seventeen bindings shadow a stock Sublime Text binding. The user keymap wins,
so the stock command becomes unreachable by keyboard but remains available in the menus and
the command palette (`ctrl+shift+p`). Checked 2026-09-06 against Sublime Text 4 on Linux;
the Windows defaults are nearly identical.

| Binding            | Command                   | Stock default it hides          |
|--------------------|---------------------------|---------------------------------|
| ctrl+shift+h       | insert_hyperlink          | Replace Next                    |
| ctrl+shift+j       | insert_author_hyperlink   | Join Lines                      |
| ctrl+shift+i       | surround_italics          | Incremental Find (reverse)      |
| ctrl+shift+u       | surround_underline        | Soft Redo                       |
| ctrl+shift+b       | surround_bold             | Build With...                   |
| ctrl+shift+s       | surround_strikethrough    | Save As                         |
| ctrl+shift+q       | copy_disqus_quote         | (none)                          |
| ctrl+shift+alt+q   | copy_disqus_quote_block   | Run Macro                       |
| ctrl+shift+alt+r   | find_reply                | (none)                          |
| ctrl+shift+d       | remove_enclosing_tag      | Duplicate Line                  |
| ctrl+alt+h         | surround_highlight        | (none)                          |
| ctrl+alt+shift+p   | surround_para             | Show Scope Name                 |
| ctrl+m             | convert_to_markdown       | Jump to Matching Bracket        |
| ctrl+0             | reset_font_size           | Focus Side Bar                  |
| ctrl+shift+r       | reverse_text_html         | Goto Symbol in Project          |
| ctrl+alt+s         | insert_url_completion     | (none)                          |
| ctrl+shift+l       | sep_markdown_link         | Split Selection into Lines      |

Linux-only extras:

| Binding            | Command                   | Notes                           |
|--------------------|---------------------------|---------------------------------|
| ctrl+k, ctrl+m     | set_file_type (Markdown)  | chord                           |
| ctrl+alt+j         | pretty_json               | Pretty JSON ships this disabled |

No desktop-level conflicts on the Linux machine (KDE Plasma, Wayland): the only global
Ctrl shortcuts are Ctrl+Alt+Del and UpNote's Ctrl+Alt+N / Ctrl+Alt+G / Ctrl+Alt+Shift+V.
