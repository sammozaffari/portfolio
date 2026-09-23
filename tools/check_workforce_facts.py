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
SCR = ROOT / "articles/2/showcase/screens"
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

# Bridget is the through-line: her contract, her hours and her make-up pay have
# to agree on the roster, the compliance list, the leave screen and her phone.
NAT = HOURS["Bridget K."]
if abs(NAT - 12.25) > 0.001:
    fails.append(f"Bridget K. works {NAT} hrs in the roster data, but every screen says 12.25")
want("roster-week.html", "12.25 / 15.0 hrs", "her contract and her hours are the whole make-up pay story")
want("roster-week.html", "Make-up pay $70.54", "the cost is shown on the roster before it is incurred")
want("compliance-list.html", "12.25 of 15.0 hrs", "the compliance row must quote the roster's figure")
want("compliance-list.html", "$70.54", "the compliance row prices the same shortfall")
want("leave-drop.html", "12.25 of her guaranteed 15.0 hours", "the drop screen explains the same shortfall")
want("leave-drop.html", "$70.54", "the drop screen prices the same shortfall")
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
# There are two of these, deliberately, and they must not be the same shift. The
# phone is dated Wed 6 November and shows the easy path, a Monday corrected the
# next day while the period was open. The desktop shows the hard path, a Monday
# in a period that has since closed. Putting both on 4 November meant the phone
# displayed a correction raised eight days in its own future.
for f in ("payperiod-correct.html",):
    want(f, "Mon 28 Oct", "the closed-period correction is for a shift in the period that closed")
    want(f, "Period closed 12 Nov", "and the period it belongs to is closed")
    want(f, "5.00", "the journey says five hours")
    want(f, "$128.25", "five hours at the ordinary rate")
want("phone-hours.html", "+$128.25", "the correction reaches her phone at the same figure")
want("phone-hours.html", "Mon 4 Nov", "her punch history shows the day it was added for")
want("phone-hours.html", "Added by Nadia A. on Tue 5 Nov",
     "added the day after the shift, so nothing on a screen dated Wed 6 Nov comes from its future")
if "Mon 28 Oct" in text("phone-hours.html"):
    fails.append("phone-hours.html: shows the closed-period shift, which had not been corrected yet on 6 November")
for _n in ("Amar",):
    for _f in ("payperiod-correct.html", "payperiod-closed.html", "phone-hours.html"):
        if _n in text(_f):
            fails.append(f"{_f}: {_n} is in no roster and no persona in the report")
want("payperiod-closed.html", "Bridget K.", "the closed period keeps the correction with it")

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
                  ("training", "training"), ("risk", "flagged"), ("over", "over threshold")):
    if f"{counts[key]} {word}" not in wk:
        fails.append(f"roster-week.html: legend should say '{counts[key]} {word}' from the data")
notes.append(f"roster grid: {total_chips} chips, {counts['filled']} clear, "
             f"{counts['risk'] + counts['over']} flagged")

# --------------------------------------------- 5b. counts typed on other screens
# "64 shifts" appeared on three screens over a roster that draws 42. Every
# screen that quotes the week or the fortnight now quotes the roster's count.
W, F = R.WEEK_SHIFTS, R.FORTNIGHT_SHIFTS
want("compliance-list.html", f"out of {W} shifts", "the compliance list counts the roster's shifts")
want("compliance-list.html", f"{W - 6} of {W} published shifts", "and its clear figure is the same count minus the six decisions")
want("reports-group.html", f"{W}", "the area report publishes the same weekly count for Riverside")
want("payperiod-open.html", f"{F - 3} / {F}", "the fortnight is two roster weeks of punches")
want("payperiod-closed.html", f"{F} / {F}", "and the closed period sends the same fortnight to payroll")
for n in ("compliance-list.html", "reports-group.html", "payperiod-open.html", "payperiod-closed.html"):
    if re.search(r"(?<![$.\d])64(?![.\d])", text(n)) and W != 64 and F != 64:
        fails.append(f"{n}: still says 64 somewhere, which is not the roster's count")

# ------------------------------------------------ 5c. the board and the clock
# Everyone on the deployment board has a shift on the roster today, and the live
# labour figures are the roster's arithmetic at 13:04, not typed numbers.
today_people = {n for _a, _sw, people in R.AREAS for n, _r, week in people
                if week[R.TODAY] and week[R.TODAY][3] not in ("leave", "open")}
for who in re.findall(r"\b([A-Z][a-z]+ [A-Z])\.", text("timeclock-board.html")):
    if who + "." not in today_people:
        fails.append(f"timeclock-board.html: {who}. is on a station but has no shift on the roster today")
worked, rostered = R.on_today("13:04")
want("labour-live.html", f"{worked:.1f}", "hours worked by 13:04 come from the roster")
want("labour-live.html", f"Rostered {rostered:.1f}", "hours rostered today come from the roster")
if worked > rostered:
    fails.append("labour-live.html: hours worked exceed hours rostered, which cannot happen")
# The open shift that Omar's leave creates is his shift: same role, same time.
open_shifts = [(n, s) for _a, _sw, people in R.AREAS for n, _r, week in people for s in week if s and s[3] == "open"]
if len(open_shifts) != 1 or open_shifts[0][1][:3] != ("15:00", "21:00", "Drive thru"):
    fails.append(f"build_roster: the open shift is {open_shifts}, and the leave screen says Sat 9 Nov, 15:00 to 21:00, drive thru")
want("leave-range.html", "Sat 9 Nov leaves the drive thru one short", "the leave screen names the gap the open shift fills")
want_not(r"\bSarah\b", "is an owner who is in no cast; owners are First L. and come from the registry")
want_not(r"break unclear|Break rule unclear", "hedges a rule the product decides: a 5.25 hour shift attracts a meal break")

# ------------------------------------------------------- 6. things never said
# The names are encoded for the same reason as the lists in tools/lint_site.py:
# this repository is served as the website, so spelling them out would publish them.
import base64 as _b64
_VENDORS = r"\b(?:" + "|".join(re.escape(n) for n in _b64.b64decode("bGlmZWxlbnp8bWFjcm9tYXRpeHxkb25lc2FmZXxjbGV2ZXIgZmlyc3QgYWlkfHBhcmFkb3h8eXVt").decode().split("|")) + r")\b"
want_not(_VENDORS,
         "is a blocked vendor name")
# Encoded because this repository is served as the website, so a plain-text
# list of real suburbs beside the client name would publish the thing it exists
# to catch. See the same note in tools/lint_site.py.
want_not(__import__("base64").b64decode("bm9ydGhnYXRlfGFzaGdyb3ZlfHNvdXRoYmFua3x3ZXN0ZmllbGR8XGIwNzMxXGI=").decode(),
         "is a real place or a store code that reads as one")
want_not(r"\u2014", "is an em dash")
# the entity form slipped past a sweep that only looked for the character
for _n in ALL:
    if "&mdash;" in (SCR / _n).read_text():
        fails.append(f"{_n}: contains an &mdash; entity, which renders as an em dash")
want_not(r"\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b", "is a state, which narrows a restaurant to a place")

# a role should not contradict itself across screens
if "Bridget" in text("phone-home.html") and "Nadia" not in text("phone-home.html"):
    fails.append("phone-home.html: Nadia is the manager who asked about the leave and should be named")
for f in ("phone-home.html", "phone-break.html", "phone-shifts.html", "phone-hours.html"):
    t = text(f)
    if "Afternoon, Nadia" in t or "Nadia&rsquo;s shifts" in t:
        fails.append(f"{f}: the crew app belongs to Bridget, the part-time team member, not to the manager")

# ------------------------------------------------------- 7. stale captures
# The lint reads markup, so a screen can be corrected and still ship the old
# picture. That happened once here: the markup said one restaurant and the PNG
# still said another, and every text gate passed. A capture older than the
# screen it came from is now a failure, not something a reader has to notice.
IMG = ROOT / "articles/2/showcase/img"
from freshness import stale_reason  # noqa: E402
for n in ALL:
    # Every screen depends on the two stylesheets as much as on its own markup,
    # so a token or component change makes every capture stale, not just the
    # ones whose HTML moved. Missing that is how a switch that read as off
    # survived a green build. The comparison is a content hash recorded when
    # the PNG was captured, so it holds on a fresh clone as well as here.
    why = stale_reason(IMG, n[:-5] + ".png", SCR / n)
    if why:
        fails.append(f"img/{n[:-5]}.png: {why}")
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
