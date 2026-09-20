#!/usr/bin/env python3
"""The crew app screens for the workforce showcase.

Four screens, each one answering something the research recorded a team member
being unable to see: their own punch times, how much of a break is left, what
their leave balance is today rather than at the pay run, and whether a day of
approved leave shows up on their shift list at all.

The phone is drawn at 390 by 844 and captured at 2x. Every figure on these
screens comes from the same week as the roster screens, so a reader moving
between them sees one restaurant rather than four sets of invented numbers.

Usage: build_crew_app.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/52/showcase/screens"

ICON = {
    "home": '<svg class="p-ico" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 9l7-6 7 6v8a1 1 0 0 1-1 1h-4v-5H8v5H4a1 1 0 0 1-1-1z"/></svg>',
    "cal": '<svg class="p-ico" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="14" height="13" rx="2"/><path d="M3 8h14M7 2v4M13 2v4"/></svg>',
    "clock": '<svg class="p-ico" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="10" cy="10" r="7.5"/><path d="M10 5.5V10l3 2"/></svg>',
    "me": '<svg class="p-ico" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="10" cy="7" r="3.2"/><path d="M4 17c.9-3.2 3.1-4.8 6-4.8s5.1 1.6 6 4.8"/></svg>',
}


def tabbar(current):
    items = [("home", "Home", "home"), ("cal", "Shifts", "cal"),
             ("clock", "My hours", "clock"), ("me", "Me", "me")]
    out = []
    for key, label, ico in items:
        cur = ' aria-current="page"' if key == current else ""
        dot = ' class="p-dot"' if key == "cal" else ""
        out.append(f'<a href="#"{cur}><span{dot}>{ICON[ico]}</span>{label}</a>')
    return '<nav class="p-tabbar">' + "".join(out) + '</nav>'


def phone(title, screen, current, cta=""):
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; Workforce crew app concept</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../../assets/product/tokens.css"><link rel="stylesheet" href="../../../../assets/product/components.css">
<style>html,body{{width:390px;height:844px;overflow:hidden}}
.p-phone{{width:390px;height:844px;border:0;border-radius:0;box-shadow:none}}</style>
</head><body class="p-app">
<div class="p-phone">
  <div class="p-status"><span>9:41</span><span>KFC Riverside</span></div>
  <div class="p-screen" style="padding:0 0 0;display:flex;flex-direction:column">
    <div style="flex:1;overflow:hidden;padding:0 16px">{screen}</div>
    {cta}
    {tabbar(current)}
  </div>
</div>
</body></html>
'''


# ----------------------------------------------------------------------- home
HOME = '''
<div class="p-mhead"><h1>Afternoon, Natalia</h1><p>Wednesday 6 November</p></div>
<div class="p-mrow next">
  <div class="p-mdate"><i>Wed</i><b>6</b></div>
  <div class="p-grow"><b>On now, front counter</b><span>10:45 &ndash; 16:00 &middot; 5 hrs 15 min</span>
  <em>Chiara B., shift supervisor, is on with you</em></div>
</div>
<div class="p-alert p-alert-warning" style="margin:12px 0 14px"><b>Your meal break is due in 12 minutes.</b> Thirty minutes, unpaid, and it has to start before 13:15.</div>
<div class="p-card" style="padding:4px 14px 8px;margin-bottom:12px">
  <div class="p-mstat"><div class="p-mstat-l">This week so far<span>Of your 15 contracted hours</span></div><div class="p-mstat-v">9.25 hrs</div></div>
  <div class="p-mstat"><div class="p-mstat-l">Expected pay this week<span>Updates when you clock out</span></div><div class="p-mstat-v">$214.60</div></div>
  <div class="p-mstat"><div class="p-mstat-l">Annual leave available<span>Updated after your last shift</span></div><div class="p-mstat-v good">25.5 hrs</div></div>
</div>
<div class="p-card" style="padding:12px 14px">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:10px">
    <div><b style="font-size:var(--p-fs-3)">Thursday off, still unpaid</b>
    <div class="p-meta" style="margin-top:2px">Nadia A., your rostering manager, asked whether to make it annual leave. One tap either way.</div></div>
  </div>
  <div class="p-actions" style="margin-top:10px"><button class="p-btn p-btn-primary p-btn-sm">Use annual leave</button><button class="p-btn p-btn-secondary p-btn-sm">Leave it unpaid</button></div>
</div>
'''

# ---------------------------------------------------------------------- break
BREAK = '''
<div class="p-mhead"><h1>On a break</h1><p>Started 13:02 &middot; back at 13:32</p></div>
<div class="p-ring" style="--p-pct:62%"><div><b>18:24</b><span>minutes left</span></div></div>
<div class="p-alert p-alert-info" style="margin-bottom:14px"><b>You will get a nudge at five minutes to go.</b> The manager gets the same one, so nobody has to watch the clock for you.</div>
<div class="p-card" style="padding:4px 14px 8px;margin-bottom:12px">
  <div class="p-mstat"><div class="p-mstat-l">Break type<span>Unpaid, comes off your hours</span></div><div class="p-mstat-v">30 min</div></div>
  <div class="p-mstat"><div class="p-mstat-l">Rest pause today<span>Ten minutes, paid</span></div><div class="p-mstat-v good">Taken 11:20</div></div>
  <div class="p-mstat"><div class="p-mstat-l">Back on station<span>L1 QT, lane 1</span></div><div class="p-mstat-v">13:32</div></div>
</div>
<p class="p-meta" style="padding:0 2px">Before this, a team member on a break had no way to see the time left and would come back early or late by a few minutes, and the only record of either was a manager keeping a note in their head.</p>
'''
BREAK_CTA = '<div class="p-cta"><button class="p-btn p-btn-primary p-btn-lg p-btn-block">End my break now</button></div>'

# --------------------------------------------------------------------- shifts
SHIFTS = '''
<div class="p-mhead"><h1>My shifts</h1><p>Week of 5 November</p></div>
<div class="p-datestrip">
  <div><i>Tue</i><b>5</b></div>
  <div class="on"><i>Wed</i><b>6</b></div>
  <div class="leave"><i>Thu</i><b>7</b></div>
  <div class="off"><i>Fri</i><b>8</b></div>
  <div><i>Sat</i><b>9</b></div>
  <div class="off"><i>Sun</i><b>10</b></div>
  <div class="off"><i>Mon</i><b>11</b></div>
</div>
<div class="p-mrow">
  <div class="p-mdate"><i>Tue</i><b>5</b></div>
  <div class="p-grow"><b>Front counter</b><span>17:00 &ndash; 21:00 &middot; 4 hrs</span><em>Worked &middot; 17:01 to 21:04</em></div>
</div>
<div class="p-mrow next">
  <div class="p-mdate"><i>Wed</i><b>6</b></div>
  <div class="p-grow"><b>Front counter, L1 QT</b><span>10:45 &ndash; 16:00 &middot; 5 hrs 15 min</span><em>On now &middot; break at 13:02</em></div>
</div>
<div class="p-mrow leave">
  <div class="p-mdate"><i>Thu</i><b>7</b></div>
  <div class="p-grow"><b>Annual leave</b><span>All day &middot; 4 hrs drawn</span><em>You agreed to this at 10:02 today</em></div>
</div>
<div class="p-mrow">
  <div class="p-mdate"><i>Sat</i><b>9</b></div>
  <div class="p-grow"><b>Front counter</b><span>17:00 &ndash; 20:00 &middot; 3 hrs</span><em>Chiara B., shift supervisor</em></div>
</div>
<div class="p-mrow pending">
  <div class="p-mdate"><i>Sun</i><b>10</b></div>
  <div class="p-grow"><b>Offered to you, front counter</b><span>17:00 &ndash; 21:00 &middot; 4 hrs</span><em>Offered to three people trained on counter</em></div>
</div>
<p class="p-meta" style="padding:2px">A day of approved leave now appears here as a day. It used to be a gap, which is why people rang the restaurant to ask whether their leave had gone through.</p>
'''

# -------------------------------------------------------------------- history
HISTORY = '''
<div class="p-mhead"><h1>My hours</h1><p>Pay period 28 Oct to 10 Nov</p></div>
<div class="p-card" style="padding:4px 14px 8px;margin-bottom:14px">
  <div class="p-mstat"><div class="p-mstat-l">Worked this period<span>Nine shifts</span></div><div class="p-mstat-v">37.4 hrs</div></div>
  <div class="p-mstat"><div class="p-mstat-l">Expected pay<span>Before tax, paid 26 Nov</span></div><div class="p-mstat-v">$867.20</div></div>
  <div class="p-mstat"><div class="p-mstat-l">Correction added<span>Mon 4 Nov, five hours you were not paid for</span></div><div class="p-mstat-v good">+$70.20</div></div>
</div>
<h3 style="font-size:var(--p-fs-3);margin-bottom:4px">Every punch, as it was recorded</h3>
<div class="p-card" style="padding:4px 14px 10px">
  <div class="p-punch"><span class="p-pd">Wed 6</span><div><b>10:44 in</b><span class="p-pb">Break 13:02 to 13:32</span></div><span class="p-ph">on now</span></div>
  <div class="p-punch"><span class="p-pd">Tue 5</span><div><b>17:01 in &middot; 21:04 out</b><span class="p-pb">No break, under 5 hrs</span></div><span class="p-ph">4.05</span></div>
  <div class="p-punch amended"><span class="p-pd">Mon 4</span><div><b>11:00 in &middot; 16:00 out</b><span class="p-pb">Added by Amar on 14 Nov. You worked it and did not clock on.</span></div><span class="p-ph">5.00</span></div>
  <div class="p-punch"><span class="p-pd">Sat 2</span><div><b>16:58 in &middot; 22:03 out</b><span class="p-pb">Break 19:00 to 19:30</span></div><span class="p-ph">4.58</span></div>
  <div class="p-punch"><span class="p-pd">Fri 1</span><div><b>17:00 in &middot; 21:02 out</b><span class="p-pb">Rest pause 19:10</span></div><span class="p-ph">4.03</span></div>
</div>
<p class="p-meta" style="padding:8px 2px 0">A corrected punch is shown as a correction, with who added it and why, rather than quietly replacing what the clock recorded.</p>
'''

if __name__ == "__main__":
    SCR.mkdir(parents=True, exist_ok=True)
    for name, title, screen, cur, cta in (
        ("phone-home.html", "Home", HOME, "home", ""),
        ("phone-break.html", "Break countdown", BREAK, "home", BREAK_CTA),
        ("phone-shifts.html", "My shifts", SHIFTS, "cal", ""),
        ("phone-hours.html", "My hours", HISTORY, "clock", ""),
    ):
        (SCR / name).write_text(phone(title, screen, cur, cta))
        print("wrote", (SCR / name).relative_to(ROOT))
