#!/usr/bin/env python3
"""Generate the roster screens for the workforce showcase from one data table.

The roster is a 9-person week: 63 cells, a total on every person, a subtotal on
every area and a state count for every chip in the legend strip. Typing that by
hand guarantees the legend disagrees with the grid, which is exactly the class of
error the case study says the product removes. So the week is declared once, as
data, and every number on the screen is counted from it.

Writes: screens/roster.html with three states (week, extended, hardstop).
Usage: build_roster.py
"""
import pathlib, html, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "articles/52/showcase/screens/roster.html"
e = lambda s: html.escape(str(s), quote=False)

DAYS = [("Tue", "5 Nov"), ("Wed", "6 Nov"), ("Thu", "7 Nov"), ("Fri", "8 Nov"),
        ("Sat", "9 Nov"), ("Sun", "10 Nov"), ("Mon", "11 Nov")]
TODAY = 1  # Wednesday: the manager is building next week while this one runs

# A shift is (start, end, role, kind, flag). kind drives the chip; flag is the
# compliance note drawn inside it, and is the only thing that adds colour.
#   ""        a plain rostered shift          leave     approved leave
#   open      nobody on it                    training  paid, not on the floor
#   risk      a break question                over      past a threshold
AREAS = [
    ("Management", "#24405e", [
        ("Nadia A.", "Rostering manager", [
            ("06:00", "14:30", "Rostering", "", ""),
            ("06:00", "14:30", "Rostering", "", ""),
            None,
            ("06:00", "14:30", "Rostering", "", ""),
            ("06:00", "14:30", "Rostering", "", ""),
            None,
            ("06:00", "14:30", "Rostering", "", ""),
        ]),
        ("Chiara B.", "Shift supervisor · 19", [
            ("14:00", "22:30", "Shift sup.", "", ""),
            ("14:00", "22:30", "Shift sup.", "risk", "No break on 8.5 hrs"),
            ("14:00", "22:30", "Shift sup.", "", ""),
            None,
            ("14:00", "23:00", "Shift sup.", "", ""),
            ("14:00", "23:00", "Shift sup.", "", ""),
            None,
        ]),
    ]),
    ("Front counter", "#7d5300", [
        ("Bridget K.", "Team member · part time, 15 hrs", [
            ("17:00", "21:00", "Counter", "", ""),
            ("10:45", "16:00", "Counter", "risk", "5.25 hrs, meal break due"),
            None,
            None,
            ("17:00", "20:00", "Counter", "", ""),
            None,
            None,
        ]),
        ("Jaxon R.", "Team member · 15", [
            None,
            ("16:00", "20:00", "Counter", "", ""),
            ("16:30", "21:30", "Counter", "risk", "School night, 21:30"),
            ("16:00", "20:00", "Counter", "", ""),
            ("11:00", "17:00", "Counter", "", ""),
            None,
            None,
        ]),
        ("Tessa W.", "Team member", [
            ("17:00", "21:00", "Counter", "", ""),
            None,
            ("17:00", "21:00", "Counter", "", ""),
            None,
            ("17:00", "22:00", "Counter", "", ""),
            None,
            None,
        ]),
    ]),
    ("Drive thru", "#1a6042", [
        ("Omar H.", "Team member", [
            ("15:00", "21:00", "Drive thru", "", ""),
            ("15:00", "21:00", "Drive thru", "", ""),
            ("15:00", "21:00", "Drive thru", "", ""),
            ("00:00", "00:00", "Annual leave", "leave", "Awaiting approval"),
            ("00:00", "00:00", "Annual leave", "leave", "Awaiting approval"),
            ("00:00", "00:00", "Annual leave", "leave", "Awaiting approval"),
            ("15:00", "21:00", "Drive thru", "", ""),
        ]),
        ("Open shift", "Nobody rostered", [
            None, None, None, None,
            ("15:00", "21:00", "Drive thru", "open", ""),
            None, None,
        ]),
        ("Rosa V.", "Team member · shared", [
            ("16:00", "22:00", "Drive thru", "", ""),
            None,
            ("16:00", "22:00", "Drive thru", "", ""),
            ("16:00", "22:00", "Drive thru", "", ""),
            ("16:00", "23:00", "Drive thru", "over", "38.5 hrs across 2 sites"),
            None,
            None,
        ]),
    ]),
    ("Cook", "#54407e", [
        ("Hugo N.", "Cook", [
            ("09:00", "17:00", "Cook", "", ""),
            ("09:00", "17:00", "Cook", "", ""),
            ("09:00", "17:00", "Cook", "", ""),
            ("09:00", "17:00", "Cook", "", ""),
            None,
            ("10:00", "18:00", "Cook", "", ""),
            None,
        ]),
        ("Kwame P.", "Cook · in training", [
            ("12:00", "16:00", "Induction", "training", ""),
            ("12:00", "18:00", "Cook", "", ""),
            None,
            ("12:00", "18:00", "Cook", "", ""),
            ("12:00", "20:00", "Cook", "", ""),
            ("12:00", "18:00", "Cook", "", ""),
            None,
        ]),
    ]),
]

# The one unfilled part-time obligation the manager has to see: Bridget is short of
# her contracted hours because Thursday came off, which is the make-up pay
# trap the research found managers being warned about after the fact.
SHORTFALL = {"Bridget K.": ("12.25 / 15.0 hrs", "Make-up pay $70.54")}


# Every screen that quotes a shift count reads it from here, so the compliance
# list, the area report and the pay period cannot say 64 over a roster that
# draws 42. The week is every entry on the grid; the pay period is two of them.
def _count_chips():
    return sum(1 for _a, _sw, people in AREAS for _n, _r, week in people for s in week if s)


WEEK_SHIFTS = _count_chips()          # 42
FORTNIGHT_SHIFTS = WEEK_SHIFTS * 2    # the pay period 28 Oct to 10 Nov


def on_today(now="13:04"):
    """Hours worked so far and hours rostered for TODAY, from the shift table.
    The live labour screen showed 46.2 hours worked at 13:04 when the roster
    could not have produced 17 by then."""
    mins = int(now[:2]) * 60 + int(now[3:])
    worked = rostered = 0.0
    for _a, _sw, people in AREAS:
        for _n, _r, week in people:
            s = week[TODAY]
            if not s or s[3] in ("leave", "open"):
                continue
            a = int(s[0][:2]) * 60 + int(s[0][3:]); b = int(s[1][:2]) * 60 + int(s[1][3:])
            rostered += (b - a) / 60
            if mins > a:
                worked += (min(mins, b) - a) / 60
    return round(worked, 1), round(rostered, 1)


def hours(s):
    if not s or s[3] in ("leave", "open"):
        return 0.0
    a, b = s[0], s[1]
    h = (int(b[:2]) * 60 + int(b[3:])) - (int(a[:2]) * 60 + int(a[3:]))
    return round(h / 60, 2)


def chip(s, sel=False, override=None):
    if not s:
        return '<div class="p-cell empty"></div>'
    start, end, role, kind, flag = override or s
    cls = "p-shift" + ((" " + kind) if kind else "") + (" sel" if sel else "")
    label = role if kind in ("leave", "training") else f"{start}&ndash;{end}"
    sub = "All day" if kind == "leave" else role
    body = f'<b>{label}</b><span>{e(sub)}</span>'
    if flag:
        body += f'<span class="p-flag">{e(flag)}</span>'
    return f'<div class="p-cell"><div class="{cls}">{body}</div></div>'


def build(state):
    """state: week | extended | hardstop"""
    counts = collections.Counter()
    rows = []
    for area, swatch, people in AREAS:
        area_h = 0.0
        body = []
        for name, role, week in people:
            ph = 0.0
            cells = []
            for di, s in enumerate(week):
                override, sel = None, False
                # Wednesday, the manager extends Chiara's shift by an hour. The
                # roster does not wait to be asked: the break rule re-runs.
                if state in ("extended", "hardstop") and name == "Chiara B." and di == 1:
                    override = ("14:00", "23:30", "Shift sup.", "risk", "9.5 hrs, no break")
                    sel = True
                cells.append(chip(s, sel, override))
                h = hours(override or s)
                ph += h
                if s:
                    counts[s[3] or "filled"] += 1
                    if s[3] in ("risk", "over"):
                        counts["warn"] += 1
            area_h += ph
            short = SHORTFALL.get(name)
            flagged = " flagged" if short else ""
            if name == "Open shift":
                mark = '<span class="p-avatar sm p-avatar-open"></span>'
                sub = "Nobody rostered"
            else:
                mark = f'<span class="p-avatar sm">{e("".join(w[0] for w in name.split()[:2]))}</span>'
                sub = short[0] if short else f"{ph:g} hrs"
            note = f'<span class="p-flag">{e(short[1])}</span>' if short else ""
            rows.append(
                f'<div class="p-rname{flagged}">{mark}'
                f'<div class="p-grow"><b>{e(name)}</b><span>{e(sub)}</span>{note}</div></div>' + "".join(cells))
            body.append("")
        # the area band is emitted before its people
        idx = len(rows) - len(people)
        rows.insert(idx, f'<div class="p-rarea"><i style="background:{swatch}"></i>{e(area)}'
                         f'<span class="p-rarea-sum">{area_h:g} hrs</span></div>')
    head = ['<div class="p-rhead"><span class="p-caps">Team member</span></div>']
    on = [0] * len(DAYS)
    for _a, _sw, _pp in AREAS:
        for _n, _r, _wk in _pp:
            for di, sh in enumerate(_wk):
                if sh and sh[3] not in ("leave", "open"):
                    on[di] += 1
    for i, (d, dt) in enumerate(DAYS):
        cls = "p-rhead today" if i == TODAY else "p-rhead"
        head.append(f'<div class="{cls}"><b>{e(d)} {e(dt)}</b><span>{on[i]} on</span></div>')

    must = 1 if state == "week" else 2
    should = 3

    legend = (f'<div class="p-legendbar">'
              f'<span class="f">{counts["filled"]} clear</span>'
              f'<span class="o">{counts["open"]} open</span>'
              f'<span class="l">{counts["leave"]} leave</span>'
              f'<span class="t">{counts["training"]} training</span>'
              f'<span class="r">{counts["risk"]} flagged</span>'
              f'<span class="x">{counts["over"]} over threshold</span>'
              f'<div class="p-spacer"></div>'
              f'<span style="border:0;padding:0">Rules last checked 09:41, on load</span></div>')

    wizard = ""
    if state == "extended":
        wizard = f'''
<div class="p-card" data-panel style="position:absolute;right:28px;top:210px;width:376px;z-index:20;box-shadow:var(--p-shadow-2)">
  <div class="p-card-head"><h3>This shift now needs a break</h3><span class="p-badge p-badge-warning">Changed</span></div>
  <div class="p-card-body">
    <p class="p-meta" style="margin-bottom:12px">Chiara B. went from 8.5 to 9.5 hours when you moved the finish to 23:30. Under the agreement that adds a paid rest pause and moves the meal break.</p>
    <div class="p-impact" style="margin-bottom:12px"><dl>
      <dt>Meal break, 30 min unpaid</dt><dd>18:00 &ndash; 18:30</dd>
      <dt>Rest pause, 10 min paid</dt><dd>21:00 &ndash; 21:10</dd>
      <dt class="tot">Shift after breaks</dt><dd class="tot">9.0 hrs paid</dd>
    </dl></div>
    <div class="p-actions"><button class="p-btn p-btn-primary p-btn-sm">Apply breaks</button><button class="p-btn p-btn-secondary p-btn-sm">Choose times myself</button></div>
    <p class="p-meta" style="margin-top:10px">Previously the wizard had to be re-run by hand after every change, so it usually was not.</p>
  </div>
</div>'''

    stop = ""
    if state == "hardstop":
        stop = f'''
<div style="position:absolute;inset:0;background:rgba(22,23,26,.44);z-index:30"></div>
<div class="p-card" data-panel style="position:absolute;left:50%;top:180px;transform:translateX(-50%);width:520px;z-index:31;box-shadow:var(--p-shadow-2)">
  <div class="p-card-head"><h3>This roster cannot be published</h3><span class="p-badge p-badge-danger">Must fix</span></div>
  <div class="p-card-body">
    <div class="p-alert p-alert-danger"><b>Chiara B., Wed 6 Nov, 14:00&ndash;23:30.</b> A shift supervisor working more than nine hours must take an unpaid meal break. There is no break on this shift.</div>
    <p class="p-meta" style="margin-bottom:14px">This is one of two rules in the product that stop rather than warn. Everything else is a warning, because a hard stop on a rule that managers cannot satisfy is what pushes them into recording hours that did not happen.</p>
    <div class="p-actions"><button class="p-btn p-btn-primary">Add the break and publish</button><button class="p-btn p-btn-secondary">Back to the roster</button></div>
  </div>
</div>'''

    title = {"week": "Roster", "extended": "Roster, shift extended", "hardstop": "Roster, hard stop"}[state]
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; Workforce platform concept</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../../assets/product/tokens.css"><link rel="stylesheet" href="../../../../assets/product/components.css">
<style>html,body{{width:1440px}}</style>
</head>
<body class="p-app">
<div class="p-shell-top" style="position:relative">
  <header class="p-appbar">
    <div class="p-brand-inline"><div class="p-brand-mark">W</div><b>Workforce</b></div>
    <nav class="p-modnav">
      <a href="#" aria-current="page">Roster</a>
      <a href="#">Time and attendance</a>
      <a href="#">Compliance<span class="p-count attn">{must + should}</span></a>
      <a href="#">Leave<span class="p-count">2</span></a>
      <a href="#">Pay</a>
      <a href="#">Reports</a>
    </nav>
    <div class="p-spacer"></div>
    <div class="p-where"><b>Riverside</b> &middot; 0412 &middot; equity</div>
    <span class="p-avatar">NA</span>
  </header>
  <div class="p-work">
    <div class="p-work-head">
      <h1>Week of Tue 5 November</h1>
      <div class="p-weekpick"><button>&lsaquo;</button><b>Wk 45</b><button>&rsaquo;</button></div>
      <div class="p-spacer"></div>
      <div class="p-counters">
        <span class="p-counter must"><b>{must}</b> must fix</span>
        <span class="p-counter should"><b>{should}</b> should fix</span>
      </div>
      <button class="p-btn p-btn-secondary p-btn-sm">Auto-fill breaks</button>
      <button class="p-btn p-btn-primary p-btn-sm">Publish week</button>
    </div>
    <p class="p-work-sub">Compliance runs as you build, not when you publish. Everything here is checked against the agreement and the state rules for each person, including Rosa V., whose hours are counted across Riverside and Lakeside together.</p>
    <div class="p-roster">
      <div class="p-rgrid">{''.join(head)}{''.join(rows)}</div>
      {legend}
    </div>
  </div>
  {wizard}{stop}
</div>
</body></html>
'''


OUT.parent.mkdir(parents=True, exist_ok=True)
for st in ("week", "extended", "hardstop"):
    f = OUT.with_name(f"roster-{st}.html")
    body = build(st)
    changed = not (f.exists() and f.read_text() == body)
    if changed:
        f.write_text(body)
    print(("wrote " if changed else "same  ") + str(f.relative_to(ROOT)))
