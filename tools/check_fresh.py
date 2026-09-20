#!/usr/bin/env python3
"""Fail if any captured PNG is older than the screen it was captured from.

A screen is HTML; what the case study shows is a PNG of it. Those two drift
silently, and when they do the page shows an image of something that is no
longer true. It happened here: nineteen screens were renamed to take a real
suburb out of the markup, the lint passed because the lint reads markup, and
every PNG still had the old name baked into the pixels.

Driven by the capture specs rather than by filename, because one screen can
produce several PNGs through a state parameter and the names do not match.

Comparing modification times makes this a staleness check rather than a
correctness one, which is the right trade: it is cheap, and re-capturing is
the fix either way.

Usage: check_fresh.py            check every capture spec
       check_fresh.py 52 57      check these articles only
"""
import pathlib, sys, glob, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
want = set(sys.argv[1:])
bad, n, seen = [], 0, set()

for spec_path in sorted(glob.glob(str(ROOT / "articles/*/showcase/capture*.json"))):
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
        drift = src.stat().st_mtime - out.stat().st_mtime
        if drift > 0:
            bad.append(f"{rel}: {drift:.0f}s older than {src.name}; re-capture it")

# a screen nobody captures is a screen the page cannot show
for sc in sorted(glob.glob(str(ROOT / "articles/*/showcase/screens/*.html"))):
    rel = str(pathlib.Path(sc).relative_to(ROOT))
    article = pathlib.Path(sc).parent.parent.parent.name
    if want and article not in want:
        continue
    if rel not in seen:
        bad.append(f"{rel}: in no capture spec, so it is never turned into an image")

if bad:
    print("STALE CAPTURES")
    for b in bad:
        print(" -", b)
    sys.exit(1)
print(f"CAPTURES FRESH: {n} images match their screen")
