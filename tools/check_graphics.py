#!/usr/bin/env python3
"""Fail if any label in a case graphic overlaps another, crowds it, or leaves the frame.

The graphics are drawn by script, so a label's position is computed rather than placed,
and a wrong offset puts four labels on top of each other without any text gate noticing.
That shipped once: the four quadrant labels of the safety graphic were all drawn at the
top-left corner of the first frame, in the arrangement the page opens on.

Every graphic is loaded in headless Chrome, in each state its toggles can reach, and the
bounding box of every visible label is measured. Three things fail:

  overlap   two labels' boxes intersect
  crowding  two labels side by side on a row with under 3 units between them, or two
            stacked labels whose boxes touch (under half a unit). Consecutive lines of
            one wrapped label sit 14 to 16 units apart, which is leading, not crowding.
  margin    a label within 6 units of the edge of the drawing

Usage: check_graphics.py [name ...]
"""
import itertools, json, os, pathlib, re, signal, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HARNESS = ROOT / "tools/graphics/audit-harness.html"
WIDTH = 1280


def graphics():
    """Every graphic, with the toggle keys its control bar offers."""
    out = {}
    for spec in sorted((ROOT / "articles").glob("*/graphics/*.html")):
        if spec.name == "audit-harness.html":
            continue
        src = spec.read_text()
        keys = re.findall(r'data-toggle="([a-z]+)"', src)
        out[spec] = keys
    return out


def states(keys):
    """Every combination of the toggles, capped so a graphic with many stays quick."""
    keys = keys[:3]
    combos = []
    for r in range(len(keys) + 1):
        for c in itertools.combinations(keys, r):
            combos.append(",".join(c))
    return combos or [""]


def measure(page, toggles):
    out = pathlib.Path(tempfile.mkdtemp()) / "dom.html"
    url = f"file://{HARNESS}?page=file://{page}%3Fstatic=1&toggles={toggles}&w={WIDTH}"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
           f"--user-data-dir={tempfile.mkdtemp()}", f"--window-size={WIDTH + 120},1100",
           "--virtual-time-budget=6000", "--dump-dom", url]
    with open(out, "wb") as fh:
        proc = subprocess.Popen(cmd, start_new_session=True, stdout=fh, stderr=subprocess.DEVNULL)
        deadline = time.time() + float(os.environ.get("CAP_TIMEOUT", "60"))
        res = None
        while time.time() < deadline:
            txt = out.read_text(errors="ignore") if out.exists() else ""
            m = re.search(r'data-result="([^"]*)"', txt)
            if m:
                res = json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&"))
                break
            if proc.poll() is not None:
                break
            time.sleep(0.25)
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    return res


def main():
    want = set(sys.argv[1:])
    fails, checked = [], 0
    for page, keys in graphics().items():
        if want and page.stem not in want:
            continue
        for tog in states(keys):
            r = measure(page, tog)
            label = f"{page.stem} [{tog or 'as it opens'}]"
            checked += 1
            if not r or r.get("error"):
                fails.append(f"{label}: could not measure ({r})")
                continue
            for o in r.get("overlaps", []):
                fails.append(f"{label}: {o['a']!r} overlaps {o['b']!r} over {o['area']} square units")
            for o in r.get("tight", []):
                fails.append(f"{label}: {o['a']!r} and {o['b']!r} are {o['axis']} with {o['gap']} units between them")
            for o in r.get("outside", []):
                fails.append(f"{label}: {o['s']!r} is within 6 units of the edge (left {o['left']}, top {o['top']}, right {o['right']}, bottom {o['bottom']})")
            if r.get("barOverflow"):
                fails.append(f"{label}: the control bar overflows by {r['barOverflow']}px")
    if fails:
        print(f"GRAPHICS FAILED, {len(fails)} problem(s) across {checked} states:")
        for f in fails:
            print("  - " + f)
        sys.exit(1)
    print(f"GRAPHICS OK: every label clear of its neighbours and the frame, in {checked} states")


if __name__ == "__main__":
    main()
