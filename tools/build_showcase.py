#!/usr/bin/env python3
"""Build a showcase index.html from its showcase.json, the annotation files and
the Mobbin reference tables. Annotations are an HTML layer over each PNG, so
callouts stay live text and scale with the frame. No iframes.

One generator, several showcases: the safety reporting product and the workforce
platform are different products on the same design system, so they are the same
page mechanism with different specs.

Usage: build_showcase.py [showcase-dir]   (default articles/57/showcase)"""
import json, re, pathlib, html, struct, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SC = ROOT / (sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "articles/57/showcase")
if not (SC / "showcase.json").exists():
    raise SystemExit("no showcase.json in " + str(SC))
e = lambda s: html.escape(str(s), quote=False)

def png_size(p):
    d = (SC / p).read_bytes()[:24]
    return struct.unpack(">II", d[16:24])

def load_notes(rel):
    f = SC / rel
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    d["markers"] = sorted(d.get("markers", []), key=lambda m: m["n"])
    return d

def md_tables(paths):
    rows, seen = [], set()
    for f in paths:
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or set("".join(cells)) <= set("-: "):
                continue
            if cells[0].lower().startswith(("screen or component", "pattern")):
                continue
            key = (cells[0], cells[1])
            if key in seen:
                continue
            seen.add(key)
            rows.append(cells[:4])
    return rows

def md_inline(s):
    s = e(s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', s)
    # a relative link renders too; the intro of one showcase shipped one as raw markdown
    s = re.sub(r'\[([^\]]+)\]\(((?:\.{1,2}/|#)[^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    return s

def ref_link(s):
    m = re.match(r'(.*?)\s+[—-]\s+(https?://\S+)$', str(s).strip())
    if m:
        return f'<a href="{e(m.group(2))}">{e(m.group(1))}</a>'
    m = re.search(r'(https?://\S+)', str(s))
    if m:
        return f'<a href="{e(m.group(1))}">{e(str(s).replace(m.group(1), "").strip(" —-"))}</a>'
    return e(s)

def first_sentence(s):
    s = re.sub(r'\*\*|\[([^\]]+)\]\([^)]+\)', r'\1', str(s)).strip()
    m = re.match(r'(.+?[.!?])(\s|$)', s)
    return (m.group(1) if m else s).strip()

def shot(img, markers=None, phone=False, alt=""):
    # every screen carries an alt that says what it is; the caption carries the
    # argument, and a screen reader got nothing from fifty-eight empty alts
    w, h = png_size(img)
    if phone:
        # a real device frame: the display size, corner radius, island and safe
        # areas are the iPhone 15 specification scaled, not an eyeballed crop
        return (f'<div class="dv-phone"><div class="dv-screen">'
                f'<img src="{e(img)}" width="{w//2}" height="{h//2}" alt="{e(alt)}" loading="lazy">'
                f'</div></div>')
    return (f'<div class="shot reveal"><img src="{e(img)}" width="{w//2}" height="{h//2}" alt="{e(alt)}" loading="lazy"></div>')

def notes_block(d, limit=None):
    o = ['<div class="notes">']
    for m in (d["markers"][:limit] if limit else d["markers"]):
        o.append(f'<div class="note"><span class="n">{m["n"]}</span><div>')
        # "Design decision" is a kicker, not part of the heading sentence and not
        # the first words of a finding; it rendered as both, four times, on one page
        finding = str(m.get("finding", "")).strip()
        dd = finding.lower().startswith("design decision")
        if dd:
            finding = re.sub(r'^design decision[.,]?\s*', '', finding, flags=re.I)
        o.append(f'<h4>{e(m["title"])}</h4>{"<span class=\'dd\'>Design decision</span>" if dd else ""}')
        if finding:
            o.append(f'<p><b>Finding</b>{e(finding)}</p>')
        if m.get("decision"):
            o.append(f'<p><b>Decision</b>{e(m["decision"])}</p>')
        if m.get("rejected"):
            o.append(f'<p><b>Rejected</b>{e(m["rejected"])}</p>')
        # the pattern a decision was checked against stays in the working notes, not on the page
        o.append("</div></div>")
    o.append("</div>")
    return "".join(o)

def tokens_section():
    css = (ROOT / "assets/product/tokens.css").read_text()
    var = dict(re.findall(r'(--p-[a-z0-9-]+)\s*:\s*([^;]+);', css))
    groups = [
        ("Surfaces", ["--p-canvas", "--p-panel", "--p-panel-2", "--p-sidebar", "--p-line", "--p-line-strong"]),
        ("Ink", ["--p-ink", "--p-ink-2", "--p-ink-3", "--p-ink-inverse"]),
        ("Status", ["--p-danger", "--p-warning", "--p-success", "--p-info", "--p-neutral"]),
        ("Status grounds", ["--p-danger-bg", "--p-warning-bg", "--p-success-bg", "--p-info-bg", "--p-neutral-bg"]),
    ]
    # The family that makes the workforce product what it is. Four content
    # states drawn low in chroma so a shift is never coloured for being a
    # shift, two that borrow from the status family because something is
    # actually wrong, and the two lines on the labour chart. Shown only on the
    # product that uses it: the safety product shares every token above and
    # none of these, and listing them there would describe a system it is not
    # built on.
    if any((SC / "screens").glob("roster-*.html")):
        groups.append(("Roster states", ["--p-w-shift", "--p-w-open", "--p-w-leave", "--p-w-training",
                                         "--p-w-break-risk", "--p-w-overtime", "--p-w-forecast", "--p-w-actual"]))
    o = []
    for name, keys in groups:
        o.append(f"<h3>{name}</h3><div class=\"swatches\">")
        for k in keys:
            v = var.get(k, "").strip()
            if not v:
                continue
            o.append(f'<div class="sw"><i style="background:{e(v)}"></i><span><b>{e(k.replace("--p-", ""))}</b>{e(v)}</span></div>')
        o.append("</div>")
    scale = [(k, v.strip()) for k, v in var.items() if re.fullmatch(r'--p-fs-\d', k)]
    o.append('<h3>Type scale</h3><div class="scale">')
    for k, v in sorted(scale, key=lambda kv: float(re.sub(r'[^\d.]', '', kv[1]) or 0)):
        px = re.sub(r'[^\d.]', '', v)
        o.append(f'<div><code>{e(k)}</code><em>{e(v)}</em><span style="font-size:{e(v)}">The manager classifies from the outcome</span></div>')
    o.append("</div>")
    return "".join(o)



def story_block(mod, notes):
    """A scroll-driven story: the stage stays, the copy moves past it, the screen
    changes with the step. Steps come either from the module's own story spec or
    from its annotation file, in which case each marker becomes a step and its
    coordinates become the lens."""
    spec = mod.get("story")
    if not spec:
        return ""
    device = spec.get("device", "phone")
    align = spec.get("align", "right")
    shots = spec.get("shots") or ([mod["img"]] if mod.get("img") else [])
    steps = spec.get("steps")
    if not steps and notes:
        steps = []
        for m in notes["markers"]:
            steps.append({
                "shot": 0,
                "zoom": f'{m["x"]:.1f},{m["y"]:.1f},{spec.get("zoom", 2.1)}',
                "kind": "Design decision" if str(m.get("finding", "")).strip().lower().startswith("design decision") else "Finding",
                "title": m.get("title", ""),
                "body": m.get("decision", ""),
                "quote": "" if str(m.get("finding", "")).strip().lower().startswith("design decision") else m.get("finding", ""),
                "rejected": m.get("rejected", ""),
            })
    if not steps:
        return ""

    stages = spec.get("devices") or [{"device": device, "shots": shots}]
    o = [f'<section class="st" data-align="{e(align)}">']
    o.append(f'<div class="st-rail"><div class="st-stage" data-devices="{len(stages)}">')
    for si, st_dev in enumerate(stages):
        dv = st_dev.get("device", "phone")
        ratio, tall = "", False
        if st_dev["shots"] and dv != "phone":
            rw, rh = png_size(st_dev["shots"][0])
            tall = rh > rw          # a page longer than a window: show the top of it
            ratio = ' style="--st-ratio: 1440 / 900"' if tall else f' style="--st-ratio: {rw} / {rh}"'
        live = " is-live" if si == 0 else ""
        if tall:
            dv += " from-top"
        o.append(f'<div class="st-device {e(dv)}{live}"><div class="st-screen"{ratio}>')
        for i, sh in enumerate(st_dev["shots"]):
            w, h = png_size(sh)
            on = " is-on" if (si == 0 and i == 0) else ""
            o.append(f'<img class="st-shot{on}" src="{e(sh)}" width="{w//2}" height="{h//2}" alt="{e(mod["kicker"])}, {e(mod["title"])}, screen {i + 1}" decoding="async">')
        o.append('</div></div>')
    o.append('</div></div>')
    o.append('<ol class="st-copy">')
    for i, st in enumerate(steps):
        zoom = f' data-zoom="{e(st["zoom"])}"' if st.get("zoom") else ""
        stg = f' data-stage="{st.get("stage", 0)}"'
        o.append(f'<li class="st-step" data-shot="{st.get("shot", i)}"{stg}{zoom}>')
        o.append(f'<span class="st-n">{i + 1:02d} / {len(steps):02d}</span>')
        if st.get("kind"):
            o.append(f'<span class="st-kind">{e(st["kind"])}</span>')
        o.append(f'<h3>{e(st.get("title", ""))}</h3>')
        if st.get("body"):
            o.append(f'<p>{md_inline(st["body"])}</p>')
        if st.get("quote"):
            o.append(f'<p class="st-quote">{md_inline(st["quote"])}</p>')
        if st.get("rejected"):
            o.append(f'<p class="st-rej"><b>Replaced</b>{md_inline(st["rejected"])}</p>')
        o.append('</li>')
    o.append('</ol></section>')
    return "".join(o)


spec = json.loads((SC / "showcase.json").read_text())
parts = []
for mod in spec["modules"]:
    d = load_notes(mod["annotations"]) if mod.get("annotations") else None
    img = mod.get("img") or (d and d.get("img"))
    if not img or not (SC / img).exists():
        print("skip (no image yet):", mod["id"]); continue
    parts.append(f'<section class="sc-sec" id="{e(mod["id"])}"><div class="sc-wrap">')
    parts.append(f'<span class="sc-num">{e(mod["kicker"])}</span><h2>{e(mod["title"])}</h2>')
    if mod.get("finding"):
        parts.append(f'<div class="sc-finding"><b>{e(mod.get("findingLabel", "What the research found"))}</b><p>{md_inline(mod["finding"])}</p></div>')
    for p in mod.get("body", []):
        parts.append(f'<p class="sc-prose">{md_inline(p)}</p>')
    sb = story_block(mod, d)
    if sb:
        parts.append(sb)
    else:
        # only pin what the page goes on to explain, so no number is left orphaned
        limit = mod.get("noteLimit", 4)
        pins = d["markers"][:limit] if d else None
        parts.append(shot(img, pins, mod.get("phone"), alt=f'{mod["kicker"]}, {mod["title"]}: {first_sentence(mod["caption"])}'))
    parts.append(f'<p class="shot-cap"><span class="fignum">{e(mod["figure"])}</span>{md_inline(mod["caption"])}</p>')
    if d and not sb:
        # a module without a story shows the decisions that carry it, not all of them
        parts.append(notes_block(d, limit=mod.get("noteLimit", 4)))
    states = [s for s in mod.get("states", []) if (SC / s["img"]).exists()]
    if sb:
        # the story already walks these screens; showing them again as a grid is
        # the same content twice, so only states the story does not cover survive
        told = set()
        for dev in (mod["story"].get("devices") or [{"shots": mod["story"].get("shots", [])}]):
            told.update(dev.get("shots", []))
        states = [s for s in states if s["img"] not in told]
    if states:
        parts.append(f'<h3>{e(mod.get("statesTitle", "The states that matter"))}</h3>')
        state_notes = []
        parts.append('<div class="states phones">' if mod.get("phone") else '<div class="states">')
        for s in states:
            sd = load_notes(s["annotations"]) if s.get("annotations") else None
            parts.append(f'<figure>{shot(s["img"], sd["markers"] if sd else None, mod.get("phone"), alt=s["title"] + ": " + first_sentence(s["cap"]))}<figcaption><b>{e(s["title"])}</b>{md_inline(s["cap"])}</figcaption></figure>')
            if sd:
                state_notes.append((s["title"], sd))
        parts.append("</div>")
        for title, sd in state_notes:
            parts.append(f'<h3>{e(title)}, decision by decision</h3>')
            parts.append(notes_block(sd))
    parts.append("</div></section>")

refs = []  # kept in the repo as working material; not published
ref_rows = "" and "".join(
    f'<tr><td data-label="Pattern">{md_inline(r[0])}</td><td data-label="Reference">{md_inline(r[1])}</td>'
    f'<td data-label="Taken">{md_inline(r[2])}</td><td data-label="Rejected">{md_inline(r[3])}</td></tr>' for r in refs)

page = f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(spec['description'])}">
<title>{e(spec['title'])} · Sam Mozaffari</title>
<meta property="og:type" content="website"><meta property="og:title" content="{e(spec['title'])} · Sam Mozaffari"><meta property="og:description" content="{e(spec['description'])}"><meta property="og:url" content="https://sammozaffari.github.io/the-agentic-service-designer-site/{SC.relative_to(ROOT)}/index.html"><meta property="og:image" content="https://sammozaffari.github.io/the-agentic-service-designer-site/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(spec['title'])} · Sam Mozaffari"><meta name="twitter:description" content="{e(spec['description'])}"><meta name="twitter:image" content="https://sammozaffari.github.io/the-agentic-service-designer-site/assets/og.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../assets/style.css?v=9">
<link rel="stylesheet" href="../../../assets/showcase.css?v=9">
<link rel="stylesheet" href="../../../assets/scrollytell.css?v=13">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='8' fill='%23171817'/><text x='50' y='70' font-size='56' text-anchor='middle' fill='%23f8f8f5' font-family='sans-serif' font-weight='600'>S</text></svg>">
<script>document.documentElement.classList.add('js')</script>
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-head">
  <a class="brand" href="../../../index.html">
    <div class="brand-title">Sam Mozaffari</div>
    <div class="brand-sub">Experience Designer</div>
  </a>
  <nav class="main-nav">
    <a href="../../../index.html">Home</a>
    <a href="../../../articles.html" class="on">Work</a>
    <a href="../../../about.html">About</a>
    <a href="../../../cv.html">CV</a>
  </nav>
</header>
<main id="main" class="sc">
<div class="sc-wrap sc-hero">
  <span class="sc-eyebrow">{e(spec['eyebrow'])}</span>
  <h1>{e(spec['title'])}</h1>
  <p class="sc-deck">{md_inline(spec['deck'])}</p>
  <dl class="sc-hero-facts">{''.join(f'<div><dt>{e(f["dt"])}</dt><dd>{md_inline(f["dd"])}</dd></div>' for f in spec['facts'])}</dl>
</div>
<section class="sc-sec"><div class="sc-wrap">
  <span class="sc-num">{e(spec['intro']['kicker'])}</span><h2>{e(spec['intro']['title'])}</h2>
  {''.join(f'<p class="sc-prose sc-lede">{md_inline(p)}</p>' for p in spec['intro']['body'])}
</div></section>
{''.join(parts)}
<section class="sc-sec" id="design-system"><div class="sc-wrap">
  <span class="sc-num">{e(spec['system']['kicker'])}</span><h2>{e(spec['system']['title'])}</h2>
  {''.join(f'<p class="sc-prose">{md_inline(p)}</p>' for p in spec['system']['body'])}
  {tokens_section()}
</div></section>

<div class="sc-wrap"><div class="sc-foot-nav">
  {''.join(f'<a class="{e(l.get("kind","btn-ghost"))}" href="{e(l["href"])}">{e(l["text"])}</a>' for l in spec.get("footNav", [{"kind": "btn-ink", "href": "../index.html", "text": "Back to the case study"}]))}
</div></div>
</main>
<script src="../../../assets/scrollytell.js?v=13"></script>
<script src="../../../assets/playonce.js?v=12"></script>
<footer class="footer">
  <span>Sam Mozaffari · Experience Designer, Sydney.</span>
  <span><a href="../../../library.html">Library</a> · <a href="../../../llms.txt">llms.txt</a> · <a href="https://github.com/sammozaffari">GitHub</a> · <a href="https://www.linkedin.com/in/sam-mozaffari-210588a7">LinkedIn</a></span>
</footer>
</body></html>
"""
(SC / "index.html").write_text(page)
print("wrote", (SC / "index.html").relative_to(ROOT), len(page), "bytes,", sum(1 for x in parts if x.startswith("<section")), "modules,", len(refs), "reference rows")
