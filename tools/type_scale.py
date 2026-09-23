#!/usr/bin/env python3
"""Report the distinct computed font sizes on a page, the way the review measured
them: the page loaded in an iframe of the requested width, every element's
computed font-size read from the DOM. Fails if a site page renders a size
under 12px or more distinct sizes than the scale allows.

Usage: type_scale.py [width] [page ...]
"""
import json, os, pathlib, re, signal, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGES = ["index.html", "articles.html", "about.html", "library.html",
         "articles/1/index.html", "articles/1/showcase/index.html", "articles/design-system.html"]
MAX_DISTINCT = 12   # eight steps plus the display clamps a page may use
MIN_PX = 12.0

HARNESS = """<!doctype html><html><body><script>
const q=new URLSearchParams(location.search);const w=+q.get('w');
const f=document.createElement('iframe');f.style.cssText='width:'+w+'px;height:900px;border:0';f.src=q.get('page');
f.onload=()=>{try{const d=f.contentDocument;const sizes={};
for(const el of d.querySelectorAll('body *')){if(!el.textContent.trim()||el.offsetParent===null||el.closest('[data-sample]'))continue;
const s=getComputedStyle(el).fontSize;if(!sizes[s])sizes[s]=(el.tagName+'.'+(el.className||'')).slice(0,40);}
document.body.setAttribute('data-result',JSON.stringify(sizes));}catch(e){document.body.setAttribute('data-result',JSON.stringify({err:String(e)}))}};
document.body.appendChild(f);</script></body></html>"""


def measure(page, w):
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ts-")); h = tmp / "h.html"; h.write_text(HARNESS); out = tmp / "dom.html"
    url = f"file://{h}?w={w}&page=file://{ROOT / page}"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", f"--user-data-dir={tmp / 'ud'}",
           "--window-size=1500,1000", "--virtual-time-budget=4000", "--dump-dom", url]
    with open(out, "wb") as fh:
        proc = subprocess.Popen(cmd, start_new_session=True, stdout=fh, stderr=subprocess.DEVNULL)
        deadline = time.time() + 60; res = None
        while time.time() < deadline:
            txt = out.read_text(errors="ignore") if out.exists() else ""
            m = re.search(r'data-result="([^"]*)"', txt)
            if m:
                res = json.loads(m.group(1).replace("&quot;", '"')); break
            if proc.poll() is not None:
                break
            time.sleep(0.25)
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait()
    return res


args = [a for a in sys.argv[1:]]
w = int(args.pop(0)) if args and args[0].isdigit() else 1440
fails = []
for page in (args or PAGES):
    r = measure(page, w)
    if not r or "err" in r:
        fails.append(f"{page}: could not measure ({r})"); continue
    sizes = sorted(float(k[:-2]) for k in r)
    print(f"  {page:36s} {len(sizes):2d} distinct sizes: {', '.join(f'{s:g}' for s in sizes)}")
    if sizes[0] < MIN_PX:
        fails.append(f"{page}: {sizes[0]:g}px is under {MIN_PX:g}px ({r[f'{sizes[0]:g}px']})")
    if len(sizes) > MAX_DISTINCT:
        fails.append(f"{page}: {len(sizes)} distinct sizes, more than the scale allows ({MAX_DISTINCT})")
if fails:
    print("TYPE SCALE FAILED"); [print(" -", f) for f in fails]; sys.exit(1)
print(f"TYPE SCALE OK at {w}px: no size under {MIN_PX:g}px, at most {MAX_DISTINCT} distinct sizes a page")
