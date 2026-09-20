#!/usr/bin/env python3
"""Build assets/product/components.manifest.json from components.css.

The manifest is what an agent reads before it writes a component, and what
tools/lint_site.py checks every screen against, so it has to be generated from
the stylesheet rather than maintained by hand. Several rules can share one line,
so selectors are taken from the text before each brace, not before the first.

Usage: build_manifest.py            build the manifest
       build_manifest.py --check    fail if the manifest on disk is out of date
"""
import re, json, pathlib, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "assets/product/components.css"
OUT = ROOT / "assets/product/components.manifest.json"

text = CSS.read_text()

# the nearest preceding short comment names the group a class belongs to
groups = []
for m in re.finditer(r'/\*(.*?)\*/', text, re.S):
    body = " ".join(m.group(1).split()).strip(" -")
    if body and len(body) < 220:
        groups.append((m.start(), body))

def group_at(pos):
    name = ""
    for start, body in groups:
        if start < pos:
            name = body
        else:
            break
    return name

found = {}
for m in re.finditer(r'([^{}/]+)\{', text):
    sel, pos = m.group(1), m.start(1)
    if "*/" in sel:
        sel, pos = sel.split("*/")[-1], pos + sel.rindex("*/") + 2
    for c in re.findall(r'\.(p-[a-z0-9-]+)', sel):
        found.setdefault(c, group_at(pos))

doc = collections.OrderedDict([
    ("$description", json.loads(OUT.read_text())["$description"] if OUT.exists()
     else "Every component class this design system defines."),
    ("source", "assets/product/components.css"),
    ("tokens", "assets/product/tokens.dtcg.json"),
    ("count", len(found)),
    ("components", [collections.OrderedDict([("class", c), ("group", g)])
                    for c, g in sorted(found.items())]),
])
built = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"

if "--check" in sys.argv:
    if not OUT.exists() or OUT.read_text() != built:
        print("components.manifest.json is out of date. Run tools/build_manifest.py")
        sys.exit(1)
    print(f"manifest matches components.css ({len(found)} classes)")
    sys.exit(0)

OUT.write_text(built)
print(f"wrote {OUT.relative_to(ROOT)}: {len(found)} classes")
