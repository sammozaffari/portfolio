#!/usr/bin/env python3
"""Fail if any captured PNG is older than the screen it was captured from.

A screen is HTML; what the case study shows is a PNG of it. Those two drift
silently, and when they do the page shows an image of something that is no
longer true. It happened here: nineteen screens were renamed to take a real
suburb out of the markup, the lint passed because the lint reads markup, and
every PNG still had the old name baked into the pixels.

Driven by the capture specs rather than by filename, because one screen can
produce several PNGs through a state parameter and the names do not match.

Comparing a content hash recorded at capture time (the screen plus both
product stylesheets) makes this a staleness check rather than a correctness
one, which is the right trade: it is cheap, portable to a fresh clone, and
re-capturing is the fix either way.

Usage: check_fresh.py            check every capture spec
       check_fresh.py 52 57      check these articles only
"""
import pathlib, sys, glob, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from freshness import stale_reason  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
want = set(sys.argv[1:])
bad, n, seen = [], 0, set()

for spec_path in sorted(glob.glob(str(ROOT / "articles/*/showcase/capture*.json")) + glob.glob(str(ROOT / "articles/*/graphics/capture*.json"))):
    spec_path = pathlib.Path(spec_path)
    article = spec_path.parent.parent.name
    if want and article not in want:
        continue
    try:
        entries = json.loads(spec_path.read_text())
    except json.JSONDecodeError as e:
        bad.append(f"{spec_path.relative_to(ROOT)}: not valid JSON ({e})")
        continue
    for e in entries:
        src = ROOT / e["src"].split("?")[0]
        out = ROOT / e["out"]
        rel = out.relative_to(ROOT)
        seen.add(str(src.relative_to(ROOT)))
        if not src.exists():
            bad.append(f"{rel}: its screen {e['src']} does not exist")
            continue
        if not out.exists():
            bad.append(f"{rel}: never captured")
            continue
        n += 1
        # Content hashes recorded at capture time, not modification times: a git
        # checkout writes files in any order it likes, which made the mtime
        # version of this check fail on every fresh clone.
        why = stale_reason(out.parent, out.name, src)
        if why:
            bad.append(f"{rel}: {why}")

# a screen nobody captures is a screen the page cannot show
for sc in sorted(glob.glob(str(ROOT / "articles/*/showcase/screens/*.html"))):
    rel = str(pathlib.Path(sc).relative_to(ROOT))
    article = pathlib.Path(sc).parent.parent.parent.name
    if want and article not in want:
        continue
    if rel not in seen:
        bad.append(f"{rel}: in no capture spec, so it is never turned into an image")

# A card thumbnail is its cover scaled down, made by hand, so nothing re-makes it
# when the cover is recaptured. The case 7 card kept an old caption that way.
# Scale the cover to the thumbnail's size and compare the pixels.
try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:
    Image = None
for th in sorted(glob.glob(str(ROOT / "articles/*/images/cover-*-thumb.png"))):
    th = pathlib.Path(th)
    article = th.parent.parent.name
    if want and article not in want:
        continue
    cover = th.with_name(th.name.replace("-thumb.png", ".png"))
    rel = th.relative_to(ROOT)
    if not cover.exists():
        bad.append(f"{rel}: its cover {cover.name} does not exist")
        continue
    if Image is None:
        continue
    t = Image.open(th).convert("RGB")
    c = Image.open(cover).convert("RGB").resize(t.size, Image.LANCZOS)
    # A changed caption is a small patch, so an average over the whole image
    # hides it (0.6 for the stale case 7 card). Take the worst 20px tile instead:
    # a thumb re-made from its cover scores 0; the stale card scored about 20.
    d = ImageChops.difference(t, c).convert("L")
    worst = max(ImageStat.Stat(d.crop((x, y, min(x + 20, d.width), min(y + 20, d.height)))).mean[0]
                for y in range(0, d.height, 20) for x in range(0, d.width, 20))
    n += 1
    if worst > 4:
        bad.append(f"{rel}: differs from its cover scaled down (worst tile {worst:.0f}); re-make it from {cover.name}")

if bad:
    print("STALE CAPTURES")
    for b in bad:
        print(" -", b)
    sys.exit(1)
print(f"CAPTURES FRESH: {n} images match their screen")
