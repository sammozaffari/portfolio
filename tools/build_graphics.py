#!/usr/bin/env python3
"""Put the plan-view graphics on their case pages, and make their cover pages.

One source per graphic: tools/graphics/<name>.html, a <figure class="mo"> with its
SVG, control bar, caption and script. This script does three things with it:

1. Injects it into the case page between <!-- graphic:<name> --> and
   <!-- /graphic:<name> --> markers, replacing whatever was there, and makes sure
   the page loads assets/motion.css and assets/motion.js once.
2. Writes articles/N/graphics/<name>.html, a standalone page with the same figure,
   which is the source the cover capture is taken from (?static=1 freezes it at the
   figure's data-freeze second) and the page a reader lands on for the graphic alone.
3. Writes articles/N/graphics/capture.json so tools/capture.py can render the cover
   to articles/N/images/cover-<name>.png, and tools/check_fresh.py can tell when the
   cover is older than its graphic.

The mapping from graphic to case is the data-case attribute on the figure, or the
GRAPHICS table below. Usage: build_graphics.py [name ...]
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools/graphics"
GRAPHICS = {
    "foyer-flow": 4, "drive-thru-lane": 5, "twelve-weeks": 6, "coding-pipeline": 7,
    "pain-point-triage": 2, "eight-restaurants": 1, "nine-stages": 3,
}
HEAD_CSS = '<link rel="stylesheet" href="{up}assets/motion.css?v=1">'
HEAD_JS = '<script src="{up}assets/motion.js?v=1"></script>'


def write_if_changed(path, content):
    if path.exists() and path.read_text() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def viewbox(frag):
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', frag)
    return (int(m.group(1)), int(m.group(2))) if m else (1200, 680)


def standalone(name, frag, case):
    title = re.search(r'<figcaption[^>]*>(?:<span class="fignum">[^<]*</span>)?([^<.]+)', frag)
    title = (title.group(1).strip() if title else name)
    w, h = viewbox(frag)
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Sam Mozaffari</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../assets/style.css?v=9">
<link rel="stylesheet" href="../../../assets/article-design.css?v=9">
{HEAD_CSS.format(up="../../../")}
{HEAD_JS.format(up="../../../")}
<style>
  body {{ background: var(--paper); }}
  .gp-wrap {{ max-width: {w}px; margin: 0 auto; padding: 24px var(--pad-m) 48px; }}
  .gp-wrap .fig {{ margin: 0; }}
  .gp-back {{ display: inline-block; margin: 18px 0 0; font-size: var(--t-2); border-bottom: 1px solid var(--line-strong); }}
  /* the cover capture wants the drawing alone, edge to edge */
  html.capture .gp-wrap {{ padding: 0; max-width: none; }}
  html.capture .mo svg {{ border: 0; border-radius: 0; }}
  html.capture .mo-bar, html.capture figcaption, html.capture .gp-back {{ display: none; }}
</style>
<script>if (new URLSearchParams(location.search).get('static') === '1') document.documentElement.classList.add('capture');</script>
</head><body>
<main class="gp-wrap" id="main">
{frag}
<a class="gp-back" href="../index.html">Back to the case study</a>
</main>
</body></html>
'''


def inject(page_path, name, frag):
    s = page_path.read_text()
    start, end = f"<!-- graphic:{name} -->", f"<!-- /graphic:{name} -->"
    if start not in s:
        raise SystemExit(f"{page_path}: no marker {start}; place it where the graphic goes")
    a = s.index(start) + len(start); b = s.index(end)
    s = s[:a] + "\n" + frag.strip() + "\n" + s[b:]
    up = "../../"
    if "assets/motion.css" not in s:
        s = s.replace('<script>document.documentElement.classList.add(\'js\')</script>',
                      HEAD_CSS.format(up=up) + "\n" + HEAD_JS.format(up=up) + "\n<script>document.documentElement.classList.add('js')</script>", 1)
    return write_if_changed(page_path, s)


def main():
    names = sys.argv[1:] or sorted(p.stem for p in SRC.glob("*.html"))
    for name in names:
        frag = (SRC / f"{name}.html").read_text()
        m = re.search(r'data-case="(\d+)"', frag)
        case = int(m.group(1)) if m else GRAPHICS.get(name)
        if not case:
            raise SystemExit(f"{name}: no case number (data-case or GRAPHICS table)")
        page = ROOT / f"articles/{case}/index.html"
        changed = inject(page, name, frag)
        gdir = ROOT / f"articles/{case}/graphics"
        wrote = write_if_changed(gdir / f"{name}.html", standalone(name, frag, case))
        w, h = viewbox(frag)
        spec_path = gdir / "capture.json"
        specs = json.loads(spec_path.read_text()) if spec_path.exists() else []
        entry = {"src": f"articles/{case}/graphics/{name}.html?static=1", "w": w, "h": h, "out": f"articles/{case}/images/cover-{name}.png"}
        specs = [e for e in specs if e["out"] != entry["out"]] + [entry]
        write_if_changed(spec_path, json.dumps(specs, indent=1) + "\n")
        print(f"{name}: case {case}, page {'updated' if changed else 'same'}, standalone {'written' if wrote else 'same'}")


if __name__ == "__main__":
    main()
