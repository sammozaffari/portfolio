#!/usr/bin/env python3
"""Fail if the main content of a page touches the window edge.

The home, Work and About pages and the three showcases shipped with a 0px side
gutter at every width under their max-width, including a 1280px laptop and every
phone, because a section rule set the four-value padding shorthand on the same
element that carries the wrapper's side padding. Every text gate passed.

Headless Chrome lays out at about 500px minimum, so a 390px window is not a
phone. The page is loaded into an iframe of the requested width inside a wide
window instead, which is how the review measured it, and the iframe's DOM is
read for the left edge of every visible text element under <main>. Chrome writes
the DOM and then hangs, so the output file is polled rather than the process.

Usage: check_layout.py                 every page in PAGES at 390 and 1280
       check_layout.py --json          also print the measurements
       check_layout.py index.html ...  these pages only
"""
import json, os, pathlib, re, signal, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGES = ["index.html", "articles.html", "about.html", "cv.html", "library.html",
         "articles/57/index.html", "articles/52/index.html", "articles/55/index.html", "articles/50/index.html", "articles/51/index.html", "articles/53/index.html", "articles/54/index.html",
         "articles/57/showcase/index.html", "articles/52/showcase/index.html",
         "articles/55/showcase/index.html"]
WIDTHS = [390, 1280]
MIN_GUTTER = 16

HARNESS = """<!doctype html><html><body><script>
const q=new URLSearchParams(location.search);const w=+q.get('w');
const f=document.createElement('iframe');f.style.cssText='width:'+w+'px;height:900px;border:0';f.src=q.get('page');
f.onload=()=>{try{const d=f.contentDocument;
const root=d.querySelector('main')||d.body;const els=[...root.querySelectorAll('*')].filter(e=>e.children.length===0&&e.textContent.trim()&&e.offsetParent!==null);
let min=1e9,who='';for(const el of els){const r=el.getBoundingClientRect();if(r.width>0&&r.right>0&&r.left<min){min=r.left;who=el.tagName+' '+el.textContent.trim().slice(0,40);}}
document.body.setAttribute('data-result',JSON.stringify({vw:d.documentElement.clientWidth,min:Math.round(min*10)/10,who,scroll:d.documentElement.scrollWidth}));
}catch(e){document.body.setAttribute('data-result',JSON.stringify({err:String(e)}))}};
document.body.appendChild(f);</script></body></html>"""


def measure(page, w):
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="lay-"))
    h = tmp / "h.html"; h.write_text(HARNESS)
    out = tmp / "dom.html"
    url = f"file://{h}?w={w}&page=file://{ROOT / page}"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
           f"--user-data-dir={tmp / 'ud'}", "--window-size=1500,1000",
           "--virtual-time-budget=4000", "--dump-dom", url]
    with open(out, "wb") as fh:
        proc = subprocess.Popen(cmd, start_new_session=True, stdout=fh, stderr=subprocess.DEVNULL)
        deadline = time.time() + float(os.environ.get("CAP_TIMEOUT", "60"))
        res = None
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


fails, rows = [], []
pages = [a for a in sys.argv[1:] if not a.startswith("--")] or PAGES
for page in pages:
    for w in WIDTHS:
        r = measure(page, w)
        if not r or "err" in r:
            fails.append(f"{page} at {w}px: could not measure ({r})"); continue
        rows.append((page, w, r))
        if r["vw"] != w:
            fails.append(f"{page}: asked for {w}px and laid out at {r['vw']}px")
        if r["min"] < MIN_GUTTER:
            fails.append(f"{page} at {w}px: text starts {r['min']}px from the edge ({r['who']!r}); the gutter must be at least {MIN_GUTTER}px")
        if r["scroll"] > w:
            fails.append(f"{page} at {w}px: the page scrolls sideways ({r['scroll']}px wide)")

if "--json" in sys.argv or fails:
    for page, w, r in rows:
        print(f"  {page:40s} {w:5d}px  left edge {r['min']:6.1f}px  scroll width {r['scroll']}px  ({r['who']})")
if fails:
    print("LAYOUT FAILED"); [print(" -", f) for f in fails]; sys.exit(1)
print(f"LAYOUT OK {len(rows)} measurements, every left edge at least {MIN_GUTTER}px and no sideways scroll")
