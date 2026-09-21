#!/usr/bin/env python3
"""Site lint: fails on self-sabotage strings, blocked names, wrong tooling counts,
em dashes in prose, missing en-AU, stray Library nav, appended arrows and numbered kickers,
and on any local href or src that does not resolve. Run from the site root."""
import re, sys, pathlib, glob, html, struct
ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNED = ['under review', 'unconfirmed', 'illustrative', 'not verified', 'cannot confirm', 'would be fabrication',
          'being confirmed', 'being re-checked', 'Failed at nothing', 'Friday ritual', 'client engagements', 'practice studies',
          'Whether this write-up', 'the client', 'agreed with the client', 'client stakeholders', 'Engagement ·']
# GitHub Pages serves this repository from its root, so every file here is a page
# on the public site, including this one. Spelling the vendor names out in source
# would publish, at a fetchable URL and beside the client's name, the exact list
# of names the site exists to keep out. They are encoded for that reason alone:
# this is not secrecy, it is not printing the list on the website.
import base64 as _b64
_dec = lambda b: _b64.b64decode(b).decode().split("|")
BLOCKED = _dec("TGlmZWxlbnp8TWFjcm9tYXRpeHxWYXVsdHxZdW18RG9uZXNhZmV8Q2xldmVyIEZpcnN0IEFpZHxQYXJhZG94fFNhbmR5")
# Real suburbs and a real area code that reached a draft once. Same reasoning.
PLACES = _dec("Tm9ydGhnYXRlfEFzaGdyb3ZlfDA3MzE=")
WRONG_COUNTS = [r'\b80 (?:methods|skills)', r'\b30(?:-tool| tools| runtime tools)', r'\b(?:38|39) (?:registered |runtime )?(?:artifact|template) kinds', r'\b12 (?:emitted|platform|distribution)', r'\b232 (?:corpus )?resources', r'\b(?:51|50) published', r'\b43 practice']
def text_of(s, keep_svg=False):
    # SVG text is text a reader sees; a wrong tool count sat inside an SVG for
    # a month because this stripped it. Counts are checked with the SVG kept.
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<pre.*?</pre>|<code.*?</code>' + ('' if keep_svg else '|<svg.*?</svg>'), ' ', s, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))
errors = []
pages = sorted(glob.glob(str(ROOT/'*.html')) + glob.glob(str(ROOT/'articles/*.html')) + glob.glob(str(ROOT/'articles/*/index.html')) + glob.glob(str(ROOT/'articles/*/showcase/index.html')) + glob.glob(str(ROOT/'articles/*/artifacts/*.html')))
for f in pages:
    p = pathlib.Path(f); s = p.read_text(errors='ignore'); rel = p.relative_to(ROOT); t = text_of(s)
    for b in BANNED:
        for m in re.finditer(re.escape(b), t, flags=re.I): errors.append(f'{rel}: banned "{b}"')
    for b in BLOCKED:
        if re.search(r'\b'+re.escape(b)+r'\b', s): errors.append(f'{rel}: blocked name {b}')
    for b in PLACES:
        if re.search(r'\b'+re.escape(b)+r'\b', s): errors.append(f'{rel}: real place or store code {b}')
    for pat in WRONG_COUNTS:
        if re.search(pat, text_of(s, keep_svg=True)): errors.append(f'{rel}: wrong tooling count {pat}')
    if '<html lang="en-AU">' not in s: errors.append(f'{rel}: lang is not en-AU')
    if re.search(r'<nav class="main-nav">(?:(?!</nav>).)*library\.html', s, flags=re.S): errors.append(f'{rel}: Library in header nav')
    if re.search(r'brand-title">The Agentic Service Designer', s): errors.append(f'{rel}: wrong brand block')
    # every page on the site, not a list of the ones that used to matter: the
    # Library carried about 190 em dashes while the rule ran on seven pages
    n_dash = len(re.findall(r'—', t)) + len(re.findall(r'—', ' '.join(re.findall(r'<svg.*?</svg>', s, flags=re.S))))
    if n_dash: errors.append(f'{rel}: {n_dash} em dashes in prose')
    # a quotation may keep its contraction: the comment category a guest wrote is theirs
    _unquoted = re.sub(r'["\u201c][^"\u201d]{0,120}["\u201d]', ' ', t)
    for m in re.finditer(r"\b(?:don't|doesn't|didn't|isn't|aren't|wasn't|weren't|won't|can't|couldn't|shouldn't|wouldn't|hasn't|haven't|it's|that's|what's|there's|here's|let's|we're|they're|you're|I'm|I've|we've)\b", _unquoted):
        errors.append(f'{rel}: contraction \"{m.group(0)}\"')
    if re.search(r'<span class="kicker">0\d\s*[—·]', s): errors.append(f'{rel}: numbered kicker')
    # every image on a case or showcase page says what it is; fifty-eight module
    # screens shipped with alt="" and captions that describe the argument, not the screen
    if str(rel).startswith('articles/'):
        for m in re.finditer(r'<img[^>]*\balt=""', s):
            errors.append(f'{rel}: image with an empty alt ({m.group(0)[:60]})')

    # v9: artefacts must not be cropped or scroll inside their container
    for m in re.finditer(r'<iframe[^>]*height:\s*\d+px', s):
        errors.append(f'{rel}: iframe with a fixed pixel height')
    for m in re.finditer(r'<(?:div|figure)[^>]*overflow-x:\s*auto[^>]*>\s*<(?:img|svg|table)', s):
        errors.append(f'{rel}: scrolling wrapper around an artefact')
    for m in re.finditer(r'<figure[^>]*class="([^"]*)"', s):
        cls = m.group(1)
        if str(rel).startswith('articles/') and 'fig-wide' not in cls and 'fig-bleed' not in cls:
            errors.append(f'{rel}: figure is not a bleed figure (class="{cls}")')
    col = 1400 if 'showcase' in str(rel) else 1100
    for m in re.finditer(r'<img[^>]+src="([^"]+\.png)"', s):
        src = p.parent / m.group(1).split('?')[0]
        if not src.exists():
            continue
        try:
            w = struct.unpack('>I', src.read_bytes()[16:20])[0] // 2
        except Exception:
            continue
        if w > col / 0.6:
            errors.append(f'{rel}: {m.group(1)} is {w}px wide and would render at {col*100//w} per cent in a {col}px column')
    for m in re.finditer(r'(?:href|src)="([^"#:]+?)(?:#[^"]*)?"', s):
        tgt = m.group(1)
        if tgt.startswith(('http', 'mailto', 'tel', 'data:')): continue
        tgt = tgt.split('?')[0]
        if not (p.parent / tgt).exists(): errors.append(f'{rel}: missing {tgt}')

# llms.txt is the machine-readable summary of the whole site, so a recruiter's
# assistant reads it before anything else. It is plain text and was therefore
# outside every check above, which is how it kept four lines the site had
# already dropped: an availability line, a sentence describing Sam by what he
# has not shipped, and two figures held "under review".
_llms = ROOT / 'llms.txt'
if _llms.exists():
    _t = _llms.read_text()
    for b in BANNED:
        if re.search(re.escape(b), _t, flags=re.I):
            errors.append(f'llms.txt: banned "{b}"')
    for b in BLOCKED + PLACES:
        if re.search(r'\b' + re.escape(b) + r'\b', _t):
            errors.append(f'llms.txt: blocked name {b}')
    if '\u2014' in _t:
        errors.append(f'llms.txt: {_t.count(chr(8212))} em dashes')
    if re.search(r'(has not (shipped|built|delivered|led|run)|does not (manage|lead|run))', _t, flags=re.I):
        errors.append('llms.txt: describes Sam by what he has not done')

# the artefact pages a case study links to are read by the same people, so they
# are held to the same rules: no em dashes, no blocked vendor names
for f in sorted(glob.glob(str(ROOT / 'articles/*/artifacts/*.html'))
                + glob.glob(str(ROOT / 'articles/*/prototypes/*.html'))
                + glob.glob(str(ROOT / 'articles/*/showcase/index.html'))
                + glob.glob(str(ROOT / 'articles/*/showcase/screens/*.html'))):
    p = pathlib.Path(f); s = p.read_text(errors='ignore'); rel = p.relative_to(ROOT); t = text_of(s)
    n = len(re.findall(r'—', t)) + len(re.findall(r'\\u2014', s))
    if n:
        errors.append(f'{rel}: {n} em dashes in a linked artefact')
    for b in BLOCKED:
        if re.search(r'\b' + re.escape(b) + r'\b', s):
            errors.append(f'{rel}: blocked name {b} in a linked artefact')
    for b in PLACES:
        if re.search(r'\b' + re.escape(b) + r'\b', s):
            errors.append(f'{rel}: real place or store code {b} in a linked artefact')
    # The hedges were only ever checked on case-study pages, but a linked
    # artefact is read by the same person and a screenshot of one gets published
    # as pixels no text gate can see. An "unconfirmed" reached the safety case
    # that way, baked into an image, while every check passed.
    for b in BANNED:
        if re.search(re.escape(b), t, flags=re.I):
            errors.append(f'{rel}: banned "{b}" in a linked artefact')

# --- no artefact is ever blown up beyond its own resolution ------------
# A 393px phone screenshot in a 1100px wide figure renders at nearly three times
# its own size and every word in it is huge. That shipped, and a 700px capture
# in the safety case was doing a softer version of the same thing. Captures are
# taken at 2x, so the natural width is half the pixel width.
import struct as _struct
for _f in glob.glob(str(ROOT / 'articles/*/index.html')):
    _p = pathlib.Path(_f); _s2 = _p.read_text(errors='ignore'); _rel = _p.relative_to(ROOT)
    for _m in re.finditer(r'<figure class="fig fig-wide[^"]*">.*?<img src="([^"]+\.png)"([^>]*)>', _s2, re.S):
        _img = (_p.parent / _m.group(1))
        if not _img.exists():
            continue
        try:
            _w, _h = _struct.unpack('>II', _img.read_bytes()[16:24])
        except Exception:
            continue
        _nat = _w // 2
        if _nat < 900 and 'max-width' not in _m.group(2):
            errors.append(f'{_rel}: {_m.group(1)} is {_nat}px natural in a wide figure; '
                          f'cap it with max-width or use a wider capture')

# --- everything here is a page -------------------------------------------
# GitHub Pages serves this repository from its root, so the site is not the HTML
# files, it is every file. That was missed until a check found the blocked vendor
# names, real suburb names and a confidential client brief all fetchable at
# public URLs while every page-level gate passed. This walks the whole tree.
_SERVED_SKIP = {'.git', 'node_modules', '__pycache__', 'baseline'}
_TEXT = {'.html', '.txt', '.md', '.json', '.py', '.css', '.js', '.svg', '.csv', '.xml'}
for _p in ROOT.rglob('*'):
    if not _p.is_file() or any(part in _SERVED_SKIP for part in _p.parts):
        continue
    _rel = _p.relative_to(ROOT)
    if _p.suffix.lower() not in _TEXT:
        continue
    try:
        _t = _p.read_text(errors='ignore')
    except OSError:
        continue
    for b in BLOCKED:
        if re.search(r'\b' + re.escape(b) + r'\b', _t):
            errors.append(f'{_rel}: blocked name {b} is fetchable at a public URL')
    for b in PLACES:
        if re.search(r'\b' + re.escape(b) + r'\b', _t):
            errors.append(f'{_rel}: real place or store code {b} is fetchable at a public URL')
    # Working notes are not pages, and the site's content is HTML. The one
    # exception is a README that documents a deliverable a reader can download,
    # which is the point of publishing it.
    _ALLOWED_MD = {'articles/57/prototype/figma/README.md'}
    if (_p.suffix.lower() == '.md' and _rel.parts[0] in ('articles', 'writing')
            and str(_rel) not in _ALLOWED_MD):
        errors.append(f'{_rel}: internal notes under a served path; keep them outside the repository')

# --- the site type scale --------------------------------------------------
# Twenty-nine distinct sizes rendered across the site pages under stylesheets
# that claimed a scale. Eight named steps live in style.css; any other pixel
# font-size on a site page or in a site stylesheet fails, print styles aside.
def _outside_print(css):
    return re.sub(r'@media print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', ' ', css, flags=re.S)
for _f in glob.glob(str(ROOT / 'assets/*.css')) + glob.glob(str(ROOT / '*.html')) + glob.glob(str(ROOT / 'articles/*/index.html')) + glob.glob(str(ROOT / 'articles/*/showcase/index.html')) + glob.glob(str(ROOT / 'articles/*/artifacts/*.html')):
    _p = pathlib.Path(_f); _rel = _p.relative_to(ROOT); _s = _p.read_text(errors='ignore')
    _css = _s if _f.endswith('.css') else ' '.join(re.findall(r'<style>(.*?)</style>', _s, re.S))
    for _m in re.finditer(r'font-size:\s*([0-9.]+px)', _outside_print(_css)):
        errors.append(f'{_rel}: font-size {_m.group(1)} is not one of the eight type steps')

# --- nothing scrolls inside its container ------------------------------
# The rule was matched against inline styles only, so a class that set
# overflow-x: auto on the blueprint wrapper put an 1100px table in a 292px
# box on every phone. Any served stylesheet or page style block that sets
# overflow-x to auto or scroll fails, except the vendor directory.
# Code blocks may scroll (a long line of configuration is not an artefact), and
# the product stylesheet is exempt because screens are published as pictures.
for _f in glob.glob(str(ROOT / 'assets/*.css')) + glob.glob(str(ROOT / '*.html')) + glob.glob(str(ROOT / 'articles/*/index.html')) + glob.glob(str(ROOT / 'articles/*/artifacts/*.html')):
    _p = pathlib.Path(_f); _rel = _p.relative_to(ROOT); _css = _p.read_text(errors='ignore')
    for _m in re.finditer(r'overflow-x\s*:\s*(auto|scroll)', _css):
        _sel = _css[max(0, _css.rfind('}', 0, _m.start())):_m.start()].split('{')[0].strip()
        if re.search(r'\b(pre|code)\b', _sel):
            continue
        errors.append(f'{_rel}: overflow-x: {_m.group(1)} on "{_sel[-60:]}" lets something scroll inside its container')

# --- design system gates -------------------------------------------------
import subprocess, json as _json
_ds = []
_r = subprocess.run([sys.executable, str(ROOT / 'tools/build_tokens.py'), '--check'], capture_output=True, text=True)
if _r.returncode != 0:
    _ds.append('tokens.css is out of date with tokens.dtcg.json; run tools/build_tokens.py')
_r = subprocess.run([sys.executable, str(ROOT / 'tools/build_manifest.py'), '--check'], capture_output=True, text=True)
if _r.returncode != 0:
    _ds.append('components.manifest.json is out of date with components.css; run tools/build_manifest.py')
_man = _json.loads((ROOT / 'assets/product/components.manifest.json').read_text())
_declared = {c['class'] for c in _man['components']}
for f in glob.glob(str(ROOT / 'articles/*/showcase/screens/*.html')):
    p = pathlib.Path(f); s2 = p.read_text()
    style = ' '.join(re.findall(r'<style>(.*?)</style>', s2, re.S))
    local = set(re.findall(r'\.(p-[a-z0-9-]+)', re.sub(r'\{[^{}]*\}', ' ', style)))
    used = set(re.findall(r'class="([^"]*)"', s2))
    names = {c for chunk in used for c in chunk.split() if c.startswith('p-')}
    undeclared = names - _declared - local
    for u in sorted(undeclared):
        _ds.append(f'{p.relative_to(ROOT)}: uses .{u}, which is not in components.manifest.json and not defined locally')
# Every size on a screen comes from the type scale. Nineteen distinct pixel
# sizes were rendered under a claim of seven steps; now a pixel font-size in a
# screen's style block or in the component file fails the build.
for f in glob.glob(str(ROOT / 'articles/*/showcase/screens/*.html')) + [str(ROOT / 'assets/product/components.css')]:
    p = pathlib.Path(f); s2 = p.read_text()
    src = ' '.join(re.findall(r'<style>(.*?)</style>', s2, re.S)) if f.endswith('.html') else s2
    for m in re.finditer(r'font-size:\s*([0-9.]+px)', src):
        _ds.append(f'{p.relative_to(ROOT)}: font-size {m.group(1)} is not a type-scale token')
if _ds:
    print('DESIGN SYSTEM FAILED'); [print(' -', e) for e in _ds]; sys.exit(1)

if errors:
    print('LINT FAILED'); [print(' -', e) for e in sorted(set(errors))]; sys.exit(1)
print('LINT OK', len(pages), 'pages')
