#!/usr/bin/env python3
"""Fail if the safety screens disagree with the calendar or with each other.

The concept ran on the 2025 calendar with 2026 stamped on it: every weekday name
was one day out, and the first image on the home page said "Wednesday 17
September" in a year when that is a Thursday. Nothing checked it, because the
two fact checkers cover the workforce and hiring products only.

Usage: check_safety_facts.py
Exit 0 if every fact holds, 1 with a list of what disagrees.
"""
import datetime, html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/1/showcase/screens"
YEAR = 2026
fails = []


def text(name):
    raw = (SCR / name).read_text()
    raw = re.sub(r"<style.*?</style>|<script.*?</script>|<title>.*?</title>", " ", raw, flags=re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


ALL = sorted(p.name for p in SCR.glob("*.html"))
MON = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
       "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
DAY = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

# ---------------------------------------------------------------- 1. calendar
# Every "Weekday D Month" on a screen must be that weekday in the concept's year.
PAIR = re.compile(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*[ ,]+(\d{1,2}) "
                  r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b")
n_pairs = 0
for n in ALL:
    for m in PAIR.finditer(text(n)):
        n_pairs += 1
        d = datetime.date(YEAR, MON[m.group(3).lower()], int(m.group(2)))
        if d.weekday() != DAY[m.group(1).lower()]:
            fails.append(f"{n}: '{m.group(0)}' but {d:%-d %B %Y} is a {d:%A}")


# ------------------------------------------------------------- 2. initials
# An avatar shows the initials of the person named beside it. Three did not.
AV = re.compile(r'<span class="p-avatar[^"]*">([A-Z]{2})</span>(.{0,90}?)\b([A-Z][a-z]+) ([A-Z])\.', re.S)
for n in ALL:
    raw = (SCR / n).read_text()
    for m in AV.finditer(raw):
        if "</span>" in m.group(2) and m.group(2).count("<") > 4:
            continue  # the name belongs to a later element
        if m.group(1) != m.group(3)[0] + m.group(4):
            fails.append(f"{n}: avatar {m.group(1)} beside {m.group(3)} {m.group(4)}.")

# ---------------------------------------------------------- 3. the registry
# Names, codes and managers come from tools/restaurants.py, shared with the
# workforce and hiring products, so Riverside 0412 has one manager everywhere.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import restaurants as REG  # noqa: E402
import safety_records as S  # noqa: E402
PAIR_RX = re.compile(r"([A-Z][a-z]+(?: [A-Z][a-z]+)?)(?:</b>|</h2>)?[^0-9]{0,80}?Restaurant (04\d\d)")
for n in ALL:
    t = text(n)
    for m in re.finditer(r"([A-Z][a-z]+(?: Street)?) Restaurant (04\d\d)", t):
        name, code = m.group(1), m.group(2)
        if code not in REG.RESTAURANTS:
            fails.append(f"{n}: restaurant code {code} is not in the registry")
        elif REG.RESTAURANTS[code][0] != name:
            fails.append(f"{n}: {name} is shown as {code}; the registry says {code} is {REG.RESTAURANTS[code][0]}")
    for word in ("Westfield", "North Sydney"):
        if word in t:
            fails.append(f"{n}: {word} is a real place")
    if "Northern area" not in t and "area" in n:
        fails.append(f"{n}: the area is called {REG.SAFETY_AREA} in the registry")
    if re.search(r"Restaurant manager", t) and REG.HOME_MANAGER not in t:
        fails.append(f"{n}: names a restaurant manager who is not {REG.HOME_MANAGER}")

# ------------------------------------------------------------ 4. the records
# Every reference on every screen names the record the table names, and the
# counts each screen shows are the table's counts.
REF_RX = re.compile(r"(?:HAZ|INC)-0412-\d{3}")
refs = {r["ref"] for r in S.RECORDS}
for n in ALL:
    t = text(n)
    for m in REF_RX.finditer(t):
        if m.group(0) not in refs:
            fails.append(f"{n}: {m.group(0)} is not in tools/safety_records.py")
            continue
        # a reference must sit with its own record: the title, one of its
        # actions, or at least the opening words of the title, within a short
        # window either side. HAZ-0412-115 was the latch on the register and the
        # cool-room light on the actions board, and nothing noticed.
        r = S.by_ref(m.group(0))
        window = t[max(0, m.start() - 220): m.end() + 220].lower()
        keys = [r["title"].lower()] + [a[0].lower() for a in r["actions"]] + [r["title"].lower().split()[0].strip(",")]
        if not any(k in window for k in keys):
            fails.append(f"{n}: {m.group(0)} appears without its record ({r['title']}) beside it")


def wantf(name, needle, why):
    if needle not in text(name):
        fails.append(f"{name}: expected {needle!r}\n    because {why}")


n_open, n_closed = len(S.OPEN), len(S.CLOSED)
wantf("register.html", f"Open {n_open}", "the register's open count is the table's")
wantf("register.html", f"Closed this period {n_closed}", "and its closed count")
wantf("register.html", f"All {n_open + n_closed}", "and the total is the sum")
wantf("register.html", f"Needs review {len(S.NEEDS_REVIEW)}", "reports needing review: reported today or awaiting sign-off")
wantf("register.html", f"Overdue actions {len(S.OVERDUE)}", "overdue actions counted from due dates against today")
wantf("register.html", f"Everything this period {len(S.THIS_PERIOD)}", "the saved view counts reports made this period")
wantf("register.html", f"See all {n_closed}", "the closed list link counts the closed records")
for r in S.OPEN:
    wantf("register.html", r["ref"], "every open record is on the register")
for r, a in S.OVERDUE:
    late = S.days_late(a)
    wantf("register.html", f"Overdue {late} day" + ("s" if late != 1 else ""), f"{r['ref']} is {late} day(s) late by its due date")
    wantf("actions.html", f"Overdue {late} day" + ("s" if late != 1 else ""), f"the board shows {r['ref']} the same number of days late")
    wantf("actions.html", f"{a[1]:%-d %b} · {late} days late" if late != 1 else f"{a[1]:%-d %b} · 1 day late", "and the list dates the lateness from the due date")
for r in S.CLOSED_TEAM:
    dt = S.days_to_fix(r)
    wantf("fixes-notice.html", r["actions"][0][0], "every closed team report is a line on the notice")
    wantf("fixes-notice.html", f"Reported by {r['who']}", "credited to the person who reported it")
wantf("fixes-notice.html", f"{n_closed} things fixed this period, {len(S.CLOSED_TEAM)} of them because someone on the team reported it",
      "the notice counts the closed records")
wantf("fixes-notice.html", f"{len(S.CLOSED_TEAM)} from team reports, {len(S.CLOSED_AUDIT)} from the audit", "and splits them the same way")
wantf("fixes-notice.html", f"Median {S.median_days():g} days", "median days to fix, from the table")
wantf("fixes-notice.html", f"Still open: {len(S.OVERDUE)}", "the notice names the overdue count")
for r in S.OPEN[:4]:
    wantf("dashboard-manager.html", r["ref"], "the dashboard lists the newest open reports")
wantf("dashboard-manager.html", f"{len(S.NEEDS_REVIEW) + len(S.OVERDUE)} things need you today", "review plus overdue")
wantf("dashboard-manager.html", f"{len(S.CLOSED_TEAM)} from team reports", "fixed this period, from team reports")
wantf("dashboard-manager.html", f"{len(S.CLOSED_AUDIT)} from audits", "and from audits")
wantf("dashboard-manager.html", f"{len(S.HAZARDS_THIS_PERIOD)} hazards, {len(S.INCIDENTS_THIS_PERIOD)} incidents", "reports this period split by kind")
for n in ("register.html", "dashboard-manager.html", "actions.html", "incident-record.html", "emergency.html", "chemicals.html", "contractors.html", "knowledge.html"):
    wantf(n, f"Incidents {len(S.OPEN_INCIDENTS)}", "the sidebar counts open incidents")
    wantf(n, f"Hazards {len(S.OPEN_HAZARDS)}", "and open hazards")
    wantf(n, f"Corrective actions {len(S.BOARD_ACTIONS)}", "and the actions on the board")
wantf("actions.html", f"To do {sum(1 for r, a in S.BOARD_ACTIONS if a[2] == 'todo')}", "board column counts come from the table")
wantf("actions.html", f"In progress {sum(1 for r, a in S.BOARD_ACTIONS if a[2] == 'progress')}", "board column counts come from the table")
wantf("actions.html", f"Awaiting sign-off {sum(1 for r, a in S.BOARD_ACTIONS if a[2] == 'signoff')}", "board column counts come from the table")
for r, a in S.BOARD_ACTIONS:
    wantf("actions.html", a[0], "every board action is on the board screen")
    wantf("actions.html", f"created {r['reported']:%-d %b}", "the list dates each action from its report")
row = f"{len(S.THIS_PERIOD)} {len(S.HAZARDS_THIS_PERIOD)} {len(S.INCIDENTS_THIS_PERIOD)} {len(S.HAZARDS_THIS_PERIOD) / len(S.INCIDENTS_THIS_PERIOD):.1f}"
wantf("dashboard-area.html", row, "the area table's Riverside row is this period's reports, hazards, incidents and ratio")

print(f"checked {len(ALL)} screens")
print(f"  calendar: {n_pairs} weekday and date pairs against {YEAR}")
if fails:
    print(f"\nFACT CHECK FAILED, {len(fails)} disagreement(s):\n")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("FACTS OK")
