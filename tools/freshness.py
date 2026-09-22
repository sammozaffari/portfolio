#!/usr/bin/env python3
"""Is a capture current? Answered by content, not by modification time.

capture.py writes img/sources.json beside the PNGs: for each PNG, a hash of the
screen it came from plus the two product stylesheets. A checker compares that
recorded hash with the hash of the files as they are now. A fresh clone has
whatever modification times git gave it, which made the mtime version of this
check fail on every reviewer's machine while passing in the working copy.
"""
import hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STYLES = (ROOT / "assets/product/tokens.css", ROOT / "assets/product/components.css")


def source_hash(src_path):
    h = hashlib.sha1()
    deps = (pathlib.Path(src_path),) + STYLES
    if "/graphics/" in str(src_path):
        deps += (ROOT / "assets/motion.js", ROOT / "assets/motion.css")
    for f in deps:
        h.update(f.read_bytes() if f.exists() else b"")
    return h.hexdigest()[:16]


def recorded(img_dir):
    store = pathlib.Path(img_dir) / "sources.json"
    try:
        return json.loads(store.read_text()) if store.exists() else {}
    except json.JSONDecodeError:
        return {}


def stale_reason(img_dir, png_name, src_path):
    """None if the PNG was captured from the current screen and stylesheets,
    otherwise a sentence saying why it is stale."""
    png = pathlib.Path(img_dir) / png_name
    if not png.exists():
        return "never captured"
    rec = recorded(img_dir).get(png_name)
    if rec is None:
        return "has no recorded source hash; re-capture it with tools/capture.py"
    if rec != source_hash(src_path):
        return "was captured from an earlier version of the screen or its stylesheets; re-capture it"
    return None
