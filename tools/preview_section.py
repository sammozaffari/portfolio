#!/usr/bin/env python3
"""Extract one <section id="..."> from a built page and write it as a standalone
file, so a tall page can be checked section by section.
Usage: preview_section.py page.html section-id out.html"""
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]); sec_id = sys.argv[2]; out = pathlib.Path(sys.argv[3])
s = src.read_text()
head = s[s.index('<head>') + 6: s.index('</head>')]
# rewrite relative asset paths so the preview can live in the same folder
depth_fix = lambda t: t
m = re.search(r'<section class="[^"]*" id="%s">.*?</section>' % re.escape(sec_id), s, re.S)
if not m:
    raise SystemExit('section not found: ' + sec_id)
wrap_open, wrap_close = ('<main class="art art-article"><div class="art-layout art-layout--body"><aside class="art-rail"></aside><article class="art-body">', '</article></div></main>') if 'art-sec' in m.group(0)[:60] else ('<main class="sc">', '</main>')
# The page's scripts live at the end of <body>, not in <head>. Without them the
# head's inline "js" class still runs, the CSS hides every .reveal, and nothing
# ever reveals it, so a working section previews as a blank gap where its
# artefact should be. Carry the body scripts across too.
scripts = "".join(re.findall(r'<script src="[^"]+"></script>', s[s.index('</main>'):] if '</main>' in s else s))
out.write_text(f'<!doctype html><html lang="en-AU"><head>{head}</head><body>{wrap_open}{m.group(0)}{wrap_close}{scripts}</body></html>')
print('wrote', out, len(m.group(0)), 'bytes,', scripts.count('<script'), 'scripts carried over')
