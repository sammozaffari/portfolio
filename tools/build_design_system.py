#!/usr/bin/env python3
"""Build articles/design-system.html: the one page that shows the method the
three product showcases share. The token file as it is, the manifest an agent
must search, the gates that fail the build, the one that failed for real, and
one component photographed on all three products. It replaces three copies of
a token dump at the foot of each showcase.

Usage: build_design_system.py
"""
import json, pathlib, re, html
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "articles/design-system.html"
IMG = ROOT / "articles/design-system"
IMG.mkdir(exist_ok=True)
e = lambda s: html.escape(str(s), quote=False)

tokens = json.loads((ROOT / "assets/product/tokens.dtcg.json").read_text())
css = (ROOT / "assets/product/tokens.css").read_text()
var = dict(re.findall(r"(--p-[a-z0-9-]+)\s*:\s*([^;]+);", css))
manifest = json.loads((ROOT / "assets/product/components.manifest.json").read_text())
groups = {}
for c in manifest["components"]:
    groups.setdefault(c.get("group", "other"), []).append(c["class"])
agents = (ROOT / "AGENTS.md").read_text()
gate_rows = re.findall(r"^\| ([^|]+?) \| `([^`]+)` \| ([^|]+?) \|$", agents, re.M)
gate_rows = [r for r in gate_rows if r[0].strip() not in ("Gate",)]

# the gate that failed for real, told where it happened: the workforce showcase
s52 = json.loads((ROOT / "articles/52/showcase/showcase.json").read_text())
story = [p for p in s52["system"]["body"] if "It caught a real failure" in p]
story = [story[0][story[0].index("It caught a real failure"):]] if story else []

# one component, the status badge in a table row, on all three products
CROPS = [("Safety", "articles/57/showcase/img/register.png", (0.16, 0.36, 0.98, 0.50)),
         ("Workforce", "articles/52/showcase/img/compliance-list.png", (0.02, 0.55, 0.98, 0.71)),
         ("Hiring", "articles/55/showcase/img/pipeline.png", (0.01, 0.29, 0.80, 0.62))]
crops = []
for name, src, (x0, y0, x1, y1) in CROPS:
    im = Image.open(ROOT / src); w, h = im.size
    box = (int(w * x0), int(h * y0), int(w * x1), int(h * y1))
    out = IMG / f"{name.lower()}-row.png"
    im.crop(box).save(out, optimize=True)
    cw, ch = Image.open(out).size
    crops.append((name, out.relative_to(ROOT.joinpath("articles")).as_posix(), cw // 2, ch // 2, src))

def swatches(keys):
    o = []
    for k in keys:
        v = var.get(k, "").strip()
        if v:
            o.append(f'<div class="ds-sw"><i style="background:{e(v)}"></i><span><b>{e(k.replace("--p-", ""))}</b>{e(v)}</span></div>')
    return "".join(o)

scale = sorted(((k, v.strip()) for k, v in var.items() if re.fullmatch(r"--p-fs-\d", k)), key=lambda kv: float(kv[1][:-2]))
scale_rows = "".join(f'<tr><td class="lab">{e(k.replace("--p-", ""))}</td><td>{e(v)}</td><td><span data-sample style="font-size:{e(v)}">The manager classifies from the outcome</span></td></tr>' for k, v in scale)

page = f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>One design system, three products · Sam Mozaffari</title>
<meta name="description" content="The token file, the component manifest, the gates that fail the build, the one that failed for real, and one component photographed on the safety, workforce and hiring products.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css?v=9">
<link rel="stylesheet" href="../assets/showcase.css?v=9">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='8' fill='%23171817'/><text x='50' y='70' font-size='56' text-anchor='middle' fill='%23f8f8f5' font-family='sans-serif' font-weight='600'>S</text></svg>">
<style>
  .ds-sws {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; margin: 12px 0 22px; }}
  .ds-sw {{ display: flex; gap: 10px; align-items: center; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; background: #fff; }}
  .ds-sw i {{ width: 28px; height: 28px; border-radius: 6px; border: 1px solid var(--line-strong); flex: none; }}
  .ds-sw span {{ font-family: var(--mono); font-size: var(--t-1); line-height: 1.4; color: var(--ink-soft); }}
  .ds-sw b {{ display: block; color: var(--ink); font-weight: 500; }}
  .ds-crop {{ border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: #fff; margin: 10px 0 4px; }}
  .ds-crop img {{ display: block; width: 100%; height: auto; }}
  .ds-cap {{ font-family: var(--mono); font-size: var(--t-1); color: var(--muted); letter-spacing: 0.04em; text-transform: uppercase; margin: 0 0 22px; }}
  .ds-list {{ columns: 3; column-gap: 24px; font-family: var(--mono); font-size: var(--t-1); line-height: 1.7; color: var(--ink-soft); max-width: none; }}
  .sc code {{ font-size: var(--t-1); }}
  @media (max-width: 720px) {{ .ds-list {{ columns: 1; }} }}
</style>
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-head">
  <a class="brand" href="../index.html"><div class="brand-title">Sam Mozaffari</div><div class="brand-sub">Experience Designer</div></a>
  <nav class="main-nav"><a href="../index.html">Home</a><a href="../articles.html" class="on">Work</a><a href="../about.html">About</a><a href="../cv.html">CV</a></nav>
</header>
<main id="main" class="sc">
<div class="sc-wrap sc-hero">
  <span class="sc-eyebrow">Design system · Three products · One token file</span>
  <h1>One design system, three products</h1>
  <p class="sc-deck">The safety, workforce and hiring concepts are built on one token file and one component file, with gates that fail the build rather than warn. This page shows the files as they are, the gate that failed for real, and one component photographed on all three products.</p>
</div>

<section class="sc-sec"><div class="sc-wrap">
  <span class="sc-num">01</span><h2>The token file</h2>
  <p class="sc-prose"><code>assets/product/tokens.dtcg.json</code> is the source, written in the W3C Design Tokens Community Group format. <code>tools/build_tokens.py</code> compiles it to the stylesheet the screens load, and the lint fails if the two drift. The values below are read from the compiled file when this page is built, so what you see is what the screens use. There is one mode: the DTCG resolver module is still a preview draft that says not to implement it, so this system does not pretend to have modes it cannot build.</p>
  <h3>Surfaces and ink</h3><div class="ds-sws">{swatches(["--p-canvas", "--p-panel", "--p-panel-2", "--p-sidebar", "--p-line", "--p-line-strong", "--p-ink", "--p-ink-2", "--p-ink-3", "--p-ink-inverse"])}</div>
  <h3>Status pairs</h3><div class="ds-sws">{swatches(["--p-danger", "--p-danger-bg", "--p-warning", "--p-warning-bg", "--p-success", "--p-success-bg", "--p-info", "--p-info-bg", "--p-neutral", "--p-neutral-bg"])}</div>
  <h3>Roster states, the workforce product only</h3><div class="ds-sws">{swatches(["--p-w-shift", "--p-w-open", "--p-w-leave", "--p-w-training", "--p-w-break-risk", "--p-w-overtime", "--p-w-forecast", "--p-w-actual"])}</div>
  <h3>The type scale</h3>
  <p class="sc-prose">Eight steps from a 14px base, the smallest 11px for badges and labels. A pixel font-size anywhere in a screen's style block or in the component file fails the lint, so nineteen sizes cannot creep back in.</p>
  <table class="sc-table"><thead><tr><th>Token</th><th>Size</th><th>Sample</th></tr></thead><tbody>{scale_rows}</tbody></table>
</div></section>

<section class="sc-sec"><div class="sc-wrap">
  <span class="sc-num">02</span><h2>The manifest an agent must search</h2>
  <p class="sc-prose"><code>assets/product/components.manifest.json</code> lists every class the component file defines, {len(manifest["components"])} of them, generated from <code>components.css</code> so it cannot drift. <code>AGENTS.md</code> tells an agent to search it before writing a component; the lint fails on any <code>p-</code> class used in a screen that is neither in the manifest nor defined in that screen's own style block. Components were lifted into the shared file once a second screen needed them, which is how the drawer, the numbered step list, the comparison pair and the oversized search field arrived.</p>
  <p class="ds-list">{" · ".join(e(c["class"]) for c in manifest["components"])}</p>
</div></section>

<section class="sc-sec"><div class="sc-wrap">
  <span class="sc-num">03</span><h2>The gates, and the one that failed</h2>
  <table class="sc-table"><thead><tr><th>Gate</th><th>Command</th><th>Fails on</th></tr></thead><tbody>
  {"".join(f"<tr><td>{e(g[0].strip())}</td><td><code>{e(g[1])}</code></td><td>{e(g[2].strip())}</td></tr>" for g in gate_rows)}
  </tbody></table>
  <div class="sc-finding"><b>The one that failed for real</b><p>{e(story[0]) if story else ""}</p></div>
  <p class="sc-prose">Two products on this site have already shipped a screen where the same record appeared in two states at once, and a reader spotted it before any check did. The three fact checkers exist because of that: they assert the screens against one data table each, and staleness is a content hash written at capture time, so they pass on a fresh clone as well as on the machine that captured them.</p>
</div></section>

<section class="sc-sec"><div class="sc-wrap">
  <span class="sc-num">04</span><h2>One component, three products</h2>
  <p class="sc-prose">The same badge with a dot and a word, the same avatar and the same secondary button, photographed on the safety register, the workforce compliance list and the hiring pipeline. The row and the card are the same component family drawn for different jobs. Nothing here is a picture of a component; each crop is cut from the captured screen.</p>
  {"".join(f'<div class="ds-crop"><img src="{e(rel)}" width="{w}" height="{h}" alt="A table row with a status badge on the {name.lower()} product, cut from its captured screen"></div><p class="ds-cap">{e(name)} · from {e(src.split("/")[-1])}</p>' for name, rel, w, h, src in crops)}
</div></section>

<div class="sc-wrap"><div class="sc-foot-nav">
  <a class="btn-ink" href="57/showcase/index.html">The safety product</a>
  <a class="btn-ghost" href="52/showcase/index.html">The workforce product</a>
  <a class="btn-ghost" href="55/showcase/index.html">The hiring product</a>
</div></div>
</main>
<footer class="footer">
  <span>Sam Mozaffari · Experience Designer, Sydney.</span>
  <span><a href="../library.html">Library</a> · <a href="../llms.txt">llms.txt</a> · <a href="https://github.com/sammozaffari">GitHub</a> · <a href="https://www.linkedin.com/in/sam-mozaffari-210588a7">LinkedIn</a></span>
</footer>
</body></html>
"""
OUT.write_text(page)
print("wrote", OUT.relative_to(ROOT), len(page), "bytes,", len(crops), "crops")
