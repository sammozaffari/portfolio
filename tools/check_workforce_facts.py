#!/usr/bin/env python3
"""Fail if the workforce screens disagree with each other.

The safety showcase shipped, briefly, with a fryer guard that was both fixed and
overdue on two different screens, and a register that said twenty items next to
a dashboard that said eleven. Nobody reading one screen could see the other, so
nothing caught it. This does.

Every fact below is something a reader can check by looking at two screens at
once. The script asserts each one against the generated HTML, and against the
roster data structure where the figure is computed rather than written. It fails
loudly rather than warning, because a warning in a build nobody reads is the
same as no check at all.

Usage: check_workforce_facts.py
Exit 0 if every fact holds, 1 with a list of what disagrees.
"""
import re, sys, pathlib, html, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/52/showcase/screens"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
# An edit that keeps the file the same length can leave a stale .pyc looking
# current, and this check once read a week of shifts that was no longer there.
# A gate that can be fooled by a cache is not a gate.
sys.dont_write_bytecode = True
import build_roster as R  # noqa: E402

fails = []
notes = []


def text(name):
    """The screen as readable text.

    Three things matter here. An input carries its content in a value attribute,
    so that is pulled out before tags are stripped or half the pay period screen
    disappears. Avatar initials are dropped, because a two letter monogram is
    not a word and reads as a false positive to anything scanning for short
    tokens. Entities are resolved last, so a check can be written the way the
    screen reads rather than the way it is encoded."""
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


# ---------------------------------------------------------------- 1. the week
# Every hours figure on the roster is computed from the shift table, so the
# check here is that the totals the screen prints are the totals the data
# implies, and that the screens which quote those totals quote the same ones.
def person_hours():
    out = {}
    for _area, _sw, people in R.AREAS:
        for name, _role, week in people:
            out[name] = round(sum(R.hours(s) for s in week), 2)
    return out


HOURS = person_hours()

for who, hrs in HOURS.items():
    if who == "Open shift":
        continue
    shown = f"{hrs:g} hrs"
    if who in R.SHORTFALL:
        continue  # shortfall people show contract, checked separately
    if shown not in text("roster-week.html"):
        fails.append(f"roster-week.html: {who} works {shown} by the data, and that figure is not on the screen")

# Natalia is the through-line: her contract, her hours and her make-up pay have
# to agree on the roster, the compliance list, the leave screen and her phone.
NAT = HOURS["Natalia F."]
if abs(NAT - 12.25) > 0.001:
    fails.append(f"Natalia F. works {NAT} hrs in the roster data, but every screen says 12.25")
want("roster-week.html", "12.25 / 15.0 hrs", "her contract and her hours are the whole make-up pay story")
want("roster-week.html", "Make-up pay $38.61", "the cost is shown on the roster before it is incurred")
want("compliance-list.html", "12.25 of 15.0 hrs", "the compliance row must quote the roster's figure")
want("compliance-list.html", "$38.61", "the compliance row prices the same shortfall")
want("leave-drop.html", "12.25 of her guaranteed 15.0 hours", "the drop screen explains the same shortfall")
want("leave-drop.html", "$38.61", "the drop screen prices the same shortfall")
want("phone-home.html", "15 contracted hours", "her phone shows the same contract")

# ------------------------------------------------------ 2. the extended shift
# Chiara's Wednesday runs 14:00 to 22:30 until the manager extends it, and the
# extension is what triggers the wizard and then the hard stop.
want("roster-week.html", "No break on 8.5 hrs", "her shift is 8.5 hours before the change")
want("roster-extended.html", "9.5 hrs, no break", "extending it to 23:30 makes it 9.5 hours")
want("roster-extended.html", "Chiara B. went from 8.5 to 9.5 hours", "the wizard has to name both figures")
want("roster-hardstop.html", "14:00\u201323:30", "the hard stop quotes the extended shift")
want("compliance-list.html", "No break on a 9.5 hour shift", "the compliance list carries the extended shift")
want("timeclock-board.html", "14:00\u201323:30", "the board shows the shift as extended")

# ------------------------------------------------------------- 3. the counters
# The nav says four compliance items. The compliance screen has to have four
# that are not information only, and the roster counters have to add to them.
comp = text("compliance-list.html")
if "Everything 6" not in comp:
    fails.append("compliance-list.html: the tab total is not 6")
for n, label in ((2, "Must fix"), (3, "Should fix"), (1, "For information")):
    if f"{label} {n}" not in comp:
        fails.append(f"compliance-list.html: expected '{label} {n}' in the severity tabs")
want("roster-week.html", "1 must fix", "before the shift is extended only one item blocks publishing")
want("roster-extended.html", "2 must fix", "extending the shift adds the second blocker")

# ---------------------------------------------------------- 4. the pay period
# Journey 2, as the report tells it: a five hour Monday shift, never punched.
for f in ("payperiod-correct.html",):
    want(f, "Mon 4 Nov", "the journey puts the missed shift on a Monday")
    want(f, "5.00", "the journey says five hours")
    want(f, "$70.20", "five hours at the ordinary rate")
want("phone-hours.html", "+$70.20", "the correction reaches her phone at the same figure")
want("phone-hours.html", "Mon 4 Nov", "her punch history shows the day it was added for")
want("payperiod-closed.html", "Natalia F.", "the closed period keeps the correction with it")

# --------------------------------------------------------- 5. the roster grid
# The legend counts every chip on the grid, so they must sum to the shifts.
counts = collections.Counter()
for _area, _sw, people in R.AREAS:
    for _n, _r, week in people:
        for s in week:
            if s:
                counts[s[3] or "filled"] += 1
total_chips = sum(counts.values())
wk = text("roster-week.html")
for key, word in (("filled", "clear"), ("open", "open"), ("leave", "leave"),
                  ("training", "training"), ("risk", "break question"), ("over", "over threshold")):
    if f"{counts[key]} {word}" not in wk:
        fails.append(f"roster-week.html: legend should say '{counts[key]} {word}' from the data")
notes.append(f"roster grid: {total_chips} chips, {counts['filled']} clear, "
             f"{counts['risk'] + counts['over']} flagged")

# ------------------------------------------------------- 6. things never said
want_not(r"[vendor names removed]",
         "is a blocked vendor name")
want_not(r"northgate|ashgrove|southbank|westfield|\b0731\b",
         "is a real place or a store code that reads as one")
want_not(r"\u2014", "is an em dash")
# the entity form slipped past a sweep that only looked for the character
for _n in ALL:
    if "&mdash;" in (SCR / _n).read_text():
        fails.append(f"{_n}: contains an &mdash; entity, which renders as an em dash")
want_not(r"\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b", "is a state, which narrows a restaurant to a place")

# a role should not contradict itself across screens
if "Natalia" in text("phone-home.html") and "Nadia" not in text("phone-home.html"):
    fails.append("phone-home.html: Nadia is the manager who asked about the leave and should be named")
for f in ("phone-home.html", "phone-break.html", "phone-shifts.html", "phone-hours.html"):
    t = text(f)
    if "Afternoon, Nadia" in t or "Nadia&rsquo;s shifts" in t:
        fails.append(f"{f}: the crew app belongs to Natalia, the part-time team member, not to the manager")

# ------------------------------------------------------- 7. stale captures
# The lint reads markup, so a screen can be corrected and still ship the old
# picture. That happened once here: the markup said one restaurant and the PNG
# still said another, and every text gate passed. A capture older than the
# screen it came from is now a failure, not something a reader has to notice.
IMG = ROOT / "articles/52/showcase/img"
CSS_MTIME = max((ROOT / "assets/product/tokens.css").stat().st_mtime,
                (ROOT / "assets/product/components.css").stat().st_mtime)
for n in ALL:
    png = IMG / (n[:-5] + ".png")
    if not png.exists():
        fails.append(f"{n}: no capture at img/{png.name}")
        continue
    # Every screen depends on the two stylesheets as much as on its own markup,
    # so a token or component change makes every capture stale, not just the
    # ones whose HTML moved. Missing that is how a switch that read as off
    # survived a green build.
    newest_source = max((SCR / n).stat().st_mtime, CSS_MTIME)
    if png.stat().st_mtime < newest_source:
        why = "the screen" if (SCR / n).stat().st_mtime >= CSS_MTIME else "the stylesheets it uses"
        fails.append(f"img/{png.name}: captured before {n} or its design system was last "
                     f"written, so the picture is older than {why}")
notes.append(f"captures: {sum(1 for n in ALL if (IMG / (n[:-5] + '.png')).exists())} of {len(ALL)} present")

# ------------------------------------------------------------------- report
print(f"checked {len(ALL)} screens")
for n in notes:
    print("  " + n)
if fails:
    print(f"\nFACT CHECK FAILED, {len(fails)} disagreement(s):\n")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("FACTS OK")
