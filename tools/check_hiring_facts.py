#!/usr/bin/env python3
"""Fail if the hiring screens disagree with each other or with the facts.

Every check here is something a reader could catch by looking at two screens at
once, which is exactly how the last three errors on this site were caught: a
fryer guard that was fixed and overdue at the same time, a candidate standing in
four pipeline columns, and a crew app showing a correction raised eight days in
its own future.

Four things it will not let through.

A date from the future. Every screen declares the day it is being looked at, and
any date it mentions must be that day or earlier.

A wage that does not reconcile. The junior rate must be the stated percentage of
the adult rate, and both must appear wherever the junior rate is used.

A seventh person. The cast is six, because every other first name on this site
is taken and two of them were close enough to read as a typo.

A name that must never ship: the vendor behind the real chatbot, the chatbot's
real name, or a real suburb.

Usage: check_hiring_facts.py
Exit 0 if every fact holds, 1 with a list of what disagrees.
"""
import re, sys, pathlib, html, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/55/showcase/screens"
IMG = ROOT / "articles/55/showcase/img"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
# An edit that keeps a file the same length can leave a stale .pyc looking
# current. A gate that can be fooled by a cache is not a gate.
sys.dont_write_bytecode = True
import hiring_data as D  # noqa: E402

fails = []


def text(name):
    """The screen as readable text.

    Avatar initials are dropped, because a two letter monogram is not a word and
    reads as a false positive to anything scanning for short tokens. Inputs
    carry their content in a value attribute, so that is pulled out before tags
    go. Entities resolve last, so a check reads the way the screen reads.
    """
    raw = (SCR / name).read_text()
    raw = re.sub(r'<span class="p-avatar[^"]*">[^<]*</span>', " ", raw)
    raw = re.sub(r'<input[^>]*\bvalue="([^"]*)"[^>]*>', r" \1 ", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


ALL = sorted(p.name for p in SCR.glob("*.html"))


def want(name, needle, why):
    if needle not in text(name):
        fails.append(f"{name}: expected {needle!r}\n    because {why}")


def want_not(pattern, why, files=None):
    rx = re.compile(pattern, re.I)
    for n in (files or ALL):
        m = rx.search(text(n))
        if m:
            fails.append(f"{n}: found {m.group(0)!r}\n    which {why}")


# ------------------------------------------------------------- 1. chronology
MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
          "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
DATE_RX = re.compile(r"\b(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", re.I)


def dates_in(name):
    return [datetime.date(2024, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))
            for m in DATE_RX.finditer(text(name))]


def screen_date(slug):
    day, _long = D.DAYS[D.SCREEN_DAY[slug]]
    m = DATE_RX.search(day)
    return datetime.date(2024, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))


for n in ALL:
    slug = n[:-5]
    if slug not in D.SCREEN_DAY:
        fails.append(f"{n}: no day declared in hiring_data.SCREEN_DAY, so nothing can check its dates")
        continue
    today = screen_date(slug)
    # A screen about something not yet happened may name a later date, but only
    # the one it declares. Everything else shows history and is capped at today.
    limit = today
    if slug in D.SCREEN_MAX:
        m = DATE_RX.search(D.DAYS[D.SCREEN_MAX[slug]][0])
        limit = datetime.date(2024, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))
    for d in dates_in(n):
        if d > limit:
            fails.append(
                f"{n}: mentions {d:%-d %b} but may not look past {limit:%-d %b}\n"
                f"    which puts something from its own future on the screen")

# The days themselves must be the weekdays they claim to be.
for key, (short, long_) in D.DAYS.items():
    m = DATE_RX.search(short)
    real = datetime.date(2024, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))
    claimed = short.split()[0]
    if real.strftime("%a") != claimed:
        fails.append(f"hiring_data.DAYS[{key!r}]: {short} is a {real:%A}, not a {claimed}")

# ------------------------------------------------------------------ 2. money
want("offer.html", f"${D.TIA_RATE:.2f}", "the offer states the rate she is actually paid")
want("offer.html", f"${D.ADULT_RATE:.2f}", "and the adult rate it is a percentage of")
want("offer.html", f"{int(D.JUNIOR_PCT[16] * 100)}%", "and the percentage itself, so the figure can be checked")
want("consent.html", f"${D.TIA_RATE:.2f}", "a guardian agreeing to employment can see the rate")
# The arithmetic has to hold, not just appear.
if abs(D.TIA_RATE - D.ADULT_RATE * D.JUNIOR_PCT[16]) > 0.01:
    fails.append(f"hiring_data: ${D.TIA_RATE:.2f} is not {int(D.JUNIOR_PCT[16]*100)}% of ${D.ADULT_RATE:.2f}")
if D.ADULT_RATE < 24.10:
    fails.append(f"hiring_data: ${D.ADULT_RATE:.2f} is below the adult minimum wage for 2024")
# A junior rate must never appear without the percentage that explains it.
for n in ALL:
    t = text(n)
    if f"${D.TIA_RATE:.2f}" in t and f"{int(D.JUNIOR_PCT[16] * 100)}%" not in t:
        fails.append(f"{n}: quotes ${D.TIA_RATE:.2f} with no percentage beside it\n"
                     f"    which reads as a rate below the adult minimum with no explanation")

# ------------------------------------------------------------------- 3. cast
ALLOWED = {p["name"] for p in D.CAST.values()} | {D.ASSISTANT}
NAME_RX = re.compile(r"\b([A-Z][a-z]{2,10}) ([A-Z])\.")
for n in ALL:
    for m in NAME_RX.finditer(text(n)):
        who = f"{m.group(1)} {m.group(2)}."
        if who not in ALLOWED:
            fails.append(f"{n}: {who} is not in the cast\n"
                         f"    and every other first name on this site is already taken")

# An avatar must show the initials of the person beside it.
AV_RX = re.compile(r'<span class="p-avatar[^"]*">([A-Z]{2})</span>')
for n in ALL:
    raw = (SCR / n).read_text()
    for m in AV_RX.finditer(raw):
        if m.group(1) not in {p["initials"] for p in D.CAST.values()}:
            fails.append(f"{n}: avatar {m.group(1)} belongs to nobody in the cast")

# ------------------------------------------------- 4. names that must not ship
want_not(r"[vendor names removed]",
         "is a blocked vendor name and must never reach a published screen")
# Encoded for the same reason as the lists in tools/lint_site.py: this file is
# served as a page, so spelling the real name out here would publish it.
want_not(__import__("base64").b64decode("XGJzYW5keVxi").decode(),
         "is the real name of the assistant, which is Ollie here")
want_not(r"northgate|ashgrove|\b0731\b", "is a real suburb or area code")
want_not(r"—", "is an em dash, which this site never uses")

# --------------------------------------------------------- 5. the five things
# The five questions are the spine of the whole case, so they are asserted
# against the data rather than trusted to the markup.
for q in D.QUESTIONS:
    want("queue.html", q["ask"], "the manager sees every question the candidate answered")
if len(D.QUESTIONS) != 5:
    fails.append(f"hiring_data: {len(D.QUESTIONS)} questions, and the case study says five")
want("questions.html", "Question 3 of 5", "the candidate can see how far through they are")

# Nothing is ever auto-rejected, and the screens must keep saying so.
want("rights.html", "ever rejected by a machine", "the promise is on the candidate's screen")
want("humanlane.html", "cannot be allowed to say somebody cannot have a job",
     "and the reason is on the administrator's screen")
# Consent runs before any decision.
want("consent.html", "before anything else happens", "the branch is stated, not implied")
want("consent.html", "No rejection", "silence must not read as a rejection")
# Nobody is left waiting.
for n in ("offer.html", "pipeline.html"):
    want(n, str(D.DISPOSITION_DAYS), "the disposition window is a promise on the screen")

# ------------------------------------------------------------ 6. the pipeline
# A person stands in exactly one column. This is the check that would have
# caught the same candidate appearing in four of them.
seen = {}
for stage, cards in D.PIPELINE:
    for c in cards:
        if c["who"] in seen:
            fails.append(f"hiring_data.PIPELINE: {D.CAST[c['who']]['name']} is in both "
                         f"{seen[c['who']]} and {stage}, and a person is in one stage")
        seen[c["who"]] = stage
n_cards = sum(len(cards) for _s, cards in D.PIPELINE)
if n_cards != D.IN_PROGRESS:
    fails.append(f"hiring_data: the board draws {n_cards} cards and the nav says {D.IN_PROGRESS}")
want("pipeline.html", f"{D.IN_PROGRESS} in progress", "the counter matches the board under it")

# ---------------------------------------------------------- 7. the interview
picked = next((d for d in D.INTERVIEW_SLOTS if d.get("picked")), None)
if not picked:
    fails.append("hiring_data.INTERVIEW_SLOTS: no slot is marked as the one she picked")
else:
    want("book.html", picked["picked"], "the time she chose is shown as chosen")
    want("pipeline.html", picked["day"], "and the manager's board shows the same day")
    want("pipeline.html", picked["picked"], "and the same time")

# --------------------------------------------------------- 8. stale captures
# The lint reads markup, so a screen can be corrected and still ship the old
# picture. Both stylesheets count as sources: a token change makes every capture
# stale, not only the ones whose own markup moved.
CSS_MTIME = max((ROOT / "assets/product/tokens.css").stat().st_mtime,
                (ROOT / "assets/product/components.css").stat().st_mtime)
for n in ALL:
    png = IMG / (n[:-5] + ".png")
    if not png.exists():
        fails.append(f"{n}: no capture at img/{png.name}")
        continue
    newest = max((SCR / n).stat().st_mtime, CSS_MTIME)
    if png.stat().st_mtime < newest:
        why = "the screen" if (SCR / n).stat().st_mtime >= CSS_MTIME else "the stylesheets it uses"
        fails.append(f"img/{png.name}: captured before {why} was last written")

# ---------------------------------------------------------------------- done
print(f"checked {len(ALL)} screens")
print(f"  cast: {len(D.CAST)} people and one assistant")
print(f"  rates: ${D.TIA_RATE:.2f} is {int(D.JUNIOR_PCT[16]*100)}% of ${D.ADULT_RATE:.2f}")
print(f"  pipeline: {n_cards} cards across {len(D.PIPELINE)} stages")
if fails:
    print(f"\nFACT CHECK FAILED, {len(fails)} disagreement(s):\n")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("FACTS OK")
