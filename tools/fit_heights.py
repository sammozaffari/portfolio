#!/usr/bin/env python3
"""Set each capture height to where the screen's content actually ends.

Heights in a capture spec are guesses, and a guess that is too tall leaves a
band of empty canvas under the screen on the showcase page. This renders each
screen at a deliberately generous height, finds the last row of pixels that is
not the page background, and rewrites the spec to that height plus a margin.

The background is read from the top-right corner of the render rather than
assumed, because the workforce screens sit on a canvas grey and the phone
screens sit on white.

Usage: fit_heights.py articles/2/showcase/capture.json [--apply]
Without --apply it reports what it would change and writes nothing.
"""
import json, sys, time, pathlib, subprocess, tempfile, shutil, os, signal, struct, zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROBE_H = 2200          # tall enough that nothing real is cut off
MARGIN = 28             # breathing room below the last element, in CSS px
STEP = 4                # round heights to a multiple of this


def png_rows(path):
    """Decode a PNG into (width, height, rows of RGB tuples). Enough of a
    decoder for what Chrome writes: 8 bit, non-interlaced, RGB or RGBA."""
    data = path.read_bytes()
    pos, w, h, depth, ctype, idat = 8, 0, 0, 0, 0, b""
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        pos += 12 + ln
    if depth != 8 or ctype not in (2, 6):
        raise SystemExit(f"{path.name}: unexpected PNG format, depth {depth} type {ctype}")
    nch = 3 if ctype == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * nch
    out, prev = [], bytearray(stride)
    p = 0
    for _y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if f == 1:
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                b = prev[i]
                c = prev[i - nch] if i >= nch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out.append(bytes(line))
        prev = line
    return w, h, nch, out


def last_content_row(path, tol=6):
    w, h, nch, rows = png_rows(path)
    # Sample the bottom left corner, not the top. A probe render this tall ends
    # in empty page by definition, whereas the top right corner sits inside the
    # app bar, which is white while the page behind it is canvas grey. Reading
    # the background from there made every row look like content and returned
    # the probe height for sixteen screens in a row.
    bg = rows[h - 3][2 * nch:2 * nch + 3]
    for y in range(h - 1, -1, -1):
        r = rows[y]
        for x in range(0, w, 3):                          # every third pixel is enough
            o = x * nch
            if (abs(r[o] - bg[0]) > tol or abs(r[o + 1] - bg[1]) > tol
                    or abs(r[o + 2] - bg[2]) > tol):
                return y, h
    return 0, h


def render(src, w, h, out):
    ud = tempfile.mkdtemp(prefix="fit-")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           f"--user-data-dir={ud}", f"--window-size={w},{h}",
           "--force-device-scale-factor=1", "--virtual-time-budget=3000",
           f"--screenshot={out}", f"file://{ROOT / src}"]
    proc = subprocess.Popen(cmd, start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Chrome writes the PNG and then routinely fails to exit, so waiting for the
    # process wastes the whole timeout on every screen. Wait for the file to
    # appear and stop growing instead, then kill the group.
    deadline, last, stable = time.time() + 45, -1, 0
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        size = out.stat().st_size if out.exists() else -1
        if size > 0 and size == last:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        last = size
        time.sleep(0.4)
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    proc.wait()
    shutil.rmtree(ud, ignore_errors=True)


spec_path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "articles/2/showcase/capture.json")
apply = "--apply" in sys.argv
spec = json.loads(spec_path.read_text())

tmp = pathlib.Path(tempfile.mkdtemp(prefix="fitpng-"))
changed = 0
for item in spec:
    src = item["src"].split("?")[0]
    if not (ROOT / src).exists():
        print(f"  {src}: no such screen, leaving the entry alone")
        continue
    if item["w"] < 500:
        continue                                   # a phone is a fixed device, not a page
    probe = tmp / (pathlib.Path(src).stem + ".png")
    render(src, item["w"], PROBE_H, probe)
    if not probe.exists():
        print(f"  {src}: render failed, keeping {item['h']}")
        continue
    last, _ = last_content_row(probe)
    fit = max(320, -(-(last + MARGIN) // STEP) * STEP)
    if fit >= PROBE_H - MARGIN:
        # A modal scrim or drawer pinned to the viewport fills whatever height
        # it is handed, so this screen cannot be measured. Leave it alone.
        print(f"  {pathlib.Path(src).name:<28} fills the viewport (overlay), keeping {item['h']}")
        continue
    if fit != item["h"]:
        print(f"  {pathlib.Path(src).name:<28} {item['h']} -> {fit}"
              f"  ({item['h'] - fit:+d} of empty canvas removed)" if fit < item["h"]
              else f"  {pathlib.Path(src).name:<28} {item['h']} -> {fit}  (content was being cut off)")
        item["h"] = fit
        changed += 1
    else:
        print(f"  {pathlib.Path(src).name:<28} {item['h']} already fits")
shutil.rmtree(tmp, ignore_errors=True)

if apply and changed:
    spec_path.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"\nwrote {spec_path.relative_to(ROOT)}, {changed} height(s) changed")
elif changed:
    print(f"\n{changed} height(s) would change. Re-run with --apply to write them.")
else:
    print("\nevery height already fits")
