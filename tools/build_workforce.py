#!/usr/bin/env python3
"""Generate the workforce showcase screens that are not the roster.

One shell function, several screens. The module navigation and its counts are
written once here rather than pasted into eight files, so the compliance count in
the nav can never disagree with the compliance screen. That is the same argument
the product makes about the roster legend, applied to the deck that shows it.

Writes: articles/2/showcase/screens/*.html
Usage: build_workforce.py
"""
import pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/2/showcase/screens"
e = lambda s: html.escape(str(s), quote=False)

# The one place the module nav is declared. Counts here are the counts on the
# screens below; change one and the other is wrong, which is the point.
# The compliance count is the list after the shift was extended: two must-fix
# and three should-fix. The roster screen before the extension draws its own.
NAV = [("Roster", None), ("Time and attendance", None), ("Compliance", ("5", "attn")),
       ("Leave", ("2", "")), ("Pay", None), ("Reports", None)]
sys_path = __import__("sys").path
sys_path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_roster as R  # noqa: E402
WHERE = "<b>Riverside</b> &middot; 0412 &middot; equity"


def shell(title, current, body, width=1440, who="NA", where=WHERE, extra="", badges=True):
    # an area-level screen carries no restaurant counts in its nav; the area
    # report used to keep Riverside's compliance and leave badges in area view
    nav = []
    for label, count in NAV:
        cur = ' aria-current="page"' if label == current else ""
        c = f'<span class="p-count {count[1]}">{count[0]}</span>' if (count and badges) else ""
        nav.append(f'<a href="#"{cur}>{e(label)}{c}</a>')
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; Workforce platform concept</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../../assets/product/tokens.css"><link rel="stylesheet" href="../../../../assets/product/components.css">
<style>html,body{{width:{width}px}}{extra}</style>
</head><body class="p-app">
<div class="p-shell-top" style="position:relative">
  <header class="p-appbar">
    <div class="p-brand-inline"><div class="p-brand-mark">W</div><b>Workforce</b></div>
    <nav class="p-modnav">{''.join(nav)}</nav>
    <div class="p-spacer"></div>
    <div class="p-where">{where}</div>
    <span class="p-avatar">{e(who)}</span>
  </header>
  {body}
</div>
</body></html>
'''


def _write_if_changed(path, content):
    """Write only when the bytes differ, so an unchanged screen keeps its mtime
    and the stale-capture check stays meaningful."""
    if path.exists() and path.read_text() == content:
        return False
    path.write_text(content)
    return True


def write(name, content):
    SCR.mkdir(parents=True, exist_ok=True)
    changed = _write_if_changed(SCR / name, content)
    print(("wrote " if changed else "same  ") + str((SCR / name).relative_to(ROOT)))


# ---------------------------------------------------------------- compliance
# The finding: the warnings list is so long and so uniform that managers stopped
# reading it and started dismissing it. Two moves answer that. Split the list by
# what actually happens if it is ignored, and give every warning an owner and a
# date, so it is somebody's rather than the screen's.
COMP_ROWS = [
    ("must", "No break on a 9.5 hour shift", "Chiara B. &middot; Wed 6 Nov",
     "Shift supervisor, meal break required over 9 hrs", "Nadia A.", "Before publish", "Blocks publish"),
    ("must", "Under contracted hours", "Bridget K. &middot; this week",
     "12.25 of 15.0 hrs. Make-up pay $70.54 at the pay run", "Nadia A.", "Before Sun 10 Nov", "Costs $70.54"),
    ("should", "Meal break due, 5.25 hour shift", "Bridget K. &middot; Wed 6 Nov",
     "Over 5 hrs. A 30 minute unpaid meal break applies, and it has to start before 13:15", "Nadia A.", "Before 13:15", "Meal break owed"),
    ("should", "Rostered past 21:00 on a school night", "Jaxon R. &middot; Thu 7 Nov",
     "Under 18. School calendar says term time", "Nadia A.", "Before the shift", "Breaches the rule"),
    ("should", "Hours across two restaurants", "Rosa V. &middot; this week",
     "38.5 hrs counting Lakeside. Overtime starts at 38", "Ravi N.", "Before Sat 9 Nov", "Overtime from 38 hrs"),
    ("info", "Training not yet recorded", "Kwame P. &middot; Mon 11 Nov",
     "Cook certification pending. Rostered as cook from Monday", "Nadia A.", "Before Mon 11 Nov", "Watch only"),
]


def comp_table(rows):
    o = ['<div class="p-table-wrap"><table class="p-table">'
         '<thead><tr><th style="width:34px"></th><th>What is wrong</th><th>Who and when</th>'
         '<th>Why it matters</th><th>Owner</th><th>Fix by</th><th style="width:170px"></th></tr></thead><tbody>']
    for sev, what, who, why, owner, by, cost in rows:
        badge = {"must": "p-badge-danger", "should": "p-badge-warning", "info": "p-badge-info"}[sev]
        word = {"must": "Must fix", "should": "Should fix", "info": "For information"}[sev]
        o.append(
            f'<tr><td><span class="p-badge {badge} p-badge-plain" style="width:22px;padding:0;justify-content:center">'
            f'{"!" if sev != "info" else "i"}</span></td>'
            f'<td class="p-primary-cell">{what}<span class="p-sub">{cost}</span></td>'
            f'<td class="p-nowrap">{who}</td><td>{why}</td>'
            f'<td class="p-nowrap"><span class="p-person"><span class="p-avatar sm">'
            f'{"".join(w[0] for w in owner.split()[:2]).upper()}</span>{owner}</span></td>'
            f'<td class="p-nowrap">{by}</td>'
            f'<td class="p-nowrap"><div class="p-actions"><button class="p-btn p-btn-secondary p-btn-sm">Open the shift</button>'
            f'<button class="p-btn p-btn-ghost p-btn-sm">Dismiss</button></div></td></tr>')
        o.append(f'<tr style="display:none"><td>{word}</td></tr>')
    o.append("</tbody></table></div>")
    return "".join(o)


def compliance(state):
    dismiss = ""
    if state == "dismiss":
        dismiss = '''
<div style="position:absolute;inset:0;background:rgba(22,23,26,.4);z-index:30"></div>
<aside class="p-drawer" data-panel style="position:absolute;right:0;top:57px;bottom:0;z-index:31;width:420px;overflow:auto">
  <h2>Dismiss this warning</h2>
  <p class="p-meta" style="margin-bottom:16px">Jaxon R., Thu 7 Nov, rostered to 21:30 on a school night.</p>
  <div class="p-alert p-alert-warning"><b>A dismissal is a record, not a delete.</b> It stays on the shift, it appears in the area coach&rsquo;s weekly dismissal report, and it needs a reason.</div>
  <fieldset class="p-fieldset">
    <legend class="p-legend">Why is this one acceptable?</legend>
    <div class="p-choices one">
      <div class="p-choice"><input type="radio" id="r1" name="r"><label for="r1"><div><b>The rule does not apply here</b><span>School holidays, an exemption, or the person is no longer a minor</span></div></label></div>
      <div class="p-choice"><input type="radio" id="r2" name="r" checked><label for="r2"><div><b>Written consent is on file</b><span>Parent or guardian consent for a later finish</span></div></label></div>
      <div class="p-choice"><input type="radio" id="r3" name="r"><label for="r3"><div><b>The roster is about to change</b><span>Dismiss for now, the warning returns if the shift does not move</span></div></label></div>
    </div>
  </fieldset>
  <label class="p-field"><span>Note for the area coach</span>
    <textarea class="p-textarea">Guardian consent signed 14 Oct, on file with the employee record. Finish moved from 22:00 to 21:30 at the guardian&rsquo;s request.</textarea>
  </label>
  <div class="p-actions"><button class="p-btn p-btn-primary">Record the dismissal</button><button class="p-btn p-btn-secondary">Cancel</button></div>
  <p class="p-meta" style="margin-top:14px">Dismissed by Nadia A., visible to the area coach from Monday. Three dismissals on one rule in a month raise it with the support team automatically.</p>
</aside>'''

    body = f'''
  <div class="p-work">
    <div class="p-work-head">
      <h1>Compliance</h1>
      <div class="p-weekpick"><button>&lsaquo;</button><b>Wk 45</b><button>&rsaquo;</button></div>
      <div class="p-spacer"></div>
      <button class="p-btn p-btn-secondary p-btn-sm">Dismissal report</button>
      <button class="p-btn p-btn-secondary p-btn-sm">Export</button>
    </div>
    <p class="p-work-sub">Six things need a decision this week, out of {R.WEEK_SHIFTS} shifts. Two of them would stop the roster publishing or cost money.</p>
    <div class="p-triage">
      <div class="p-card p-triage-panel">
        <div class="p-tri-head"><b>Clear</b><em>{R.WEEK_SHIFTS - 6}</em></div>
        <div class="p-bar"><i class="ok" style="width:{100 * (R.WEEK_SHIFTS - 6) / R.WEEK_SHIFTS:.1f}%"></i><i class="should" style="width:{100 * 4 / R.WEEK_SHIFTS:.1f}%"></i><i class="must" style="width:{100 * 2 / R.WEEK_SHIFTS:.1f}%"></i></div>
        <p class="p-meta">{R.WEEK_SHIFTS - 6} of {R.WEEK_SHIFTS} published shifts this week raise nothing. Last week it was {R.WEEK_SHIFTS - 3}.</p>
        <div class="p-breakdown">
          <div class="ok">Checked against the agreement<b>{R.WEEK_SHIFTS}</b></div>
          <div class="ok">Checked against state rules for minors<b>11</b></div>
          <div class="ok">Checked across restaurants<b>7</b></div>
        </div>
      </div>
      <div class="p-card p-triage-panel">
        <div class="p-tri-head"><b>Needs a decision</b><em>6</em></div>
        <p class="p-meta" style="margin-top:8px">Sorted by what happens if nobody does anything, not by when the warning appeared.</p>
        <div class="p-breakdown">
          <div class="must">Stops the roster publishing or costs money<b>2</b></div>
          <div class="should">Breaches a rule, no automatic cost<b>3</b></div>
          <div class="ok">Worth knowing, no action needed yet<b>1</b></div>
        </div>
        <div class="p-actions" style="margin-top:16px">
          <button class="p-btn p-btn-primary p-btn-sm">Fix the two must-fixes</button>
          <span class="p-meta">Both are Nadia&rsquo;s and one is on Wednesday</span>
        </div>
      </div>
    </div>
    <div class="p-sevtabs">
      <button aria-selected="true">Everything <b>6</b></button>
      <button class="must">Must fix <b>2</b></button>
      <button class="should">Should fix <b>3</b></button>
      <button class="info">For information <b>1</b></button>
      <button>Dismissed this month <b>4</b></button>
    </div>
    <div class="p-filters">
      <button class="p-chip on">This restaurant</button>
      <button class="p-chip">Rule<span class="p-chev">&#9662;</span></button>
      <button class="p-chip">Person<span class="p-chev">&#9662;</span></button>
      <button class="p-chip">Owner<span class="p-chev">&#9662;</span></button>
      <div class="p-spacer"></div>
      <span class="p-meta">Rules refreshed when this screen loaded, 09:41</span>
    </div>
    {comp_table(COMP_ROWS)}
  </div>
  {dismiss}'''
    return shell("Compliance" + (", dismissing a warning" if state == "dismiss" else ""),
                 "Compliance", body)


# ---------------------------------------------------------------------- leave
def leave(state):
    if state == "range":
        panel = '''
    <div class="p-grid p-grid-8-4">
      <div class="p-card">
        <div class="p-card-head"><h3>Annual leave &middot; Omar H.</h3><span class="p-badge p-badge-info">Awaiting approval</span></div>
        <div class="p-card-body">
          <div class="p-grid p-grid-2" style="margin-bottom:18px">
            <label class="p-field"><span>First day</span><input class="p-input" value="Fri 8 Nov 2024"></label>
            <label class="p-field"><span>Last day</span><input class="p-input" value="Sun 10 Nov 2024"></label>
          </div>
          <h4 style="font-size:var(--p-fs-3);margin-bottom:8px">The three shifts this covers</h4>
          <p class="p-meta" style="margin-bottom:10px">Built from the published roster the moment the dates were entered. Approving the request writes these; nobody types them.</p>
          <div class="p-table-wrap"><table class="p-table"><tbody>
            <tr><td class="p-primary-cell">Fri 8 Nov<span class="p-sub">Drive thru</span></td><td>15:00&ndash;21:00</td><td class="p-num">6.0 hrs</td><td><span class="p-badge p-badge-success">Will become leave</span></td></tr>
            <tr><td class="p-primary-cell">Sat 9 Nov<span class="p-sub">Drive thru</span></td><td>15:00&ndash;21:00</td><td class="p-num">6.0 hrs</td><td><span class="p-badge p-badge-success">Will become leave</span></td></tr>
            <tr><td class="p-primary-cell">Sun 10 Nov<span class="p-sub">Drive thru</span></td><td>15:00&ndash;21:00</td><td class="p-num">6.0 hrs</td><td><span class="p-badge p-badge-success">Will become leave</span></td></tr>
          </tbody></table></div>
          <div class="p-alert p-alert-info" style="margin-top:16px"><b>Sat 9 Nov leaves the drive thru one short.</b> An open shift was created on the roster rather than left silent. <a href="#">Fill it</a></div>
          <div class="p-actions"><button class="p-btn p-btn-primary">Approve and write the leave</button><button class="p-btn p-btn-secondary">Decline</button></div>
        </div>
      </div>
      <div class="p-grid">
        <div class="p-card p-stat p-stat-accent success">
          <div class="p-stat-label">Annual leave available<span class="p-meta">Live</span></div>
          <div class="p-stat-value">54.2</div>
          <div class="p-stat-delta">hours, updated after Omar&rsquo;s shift last night. This request uses <b>18.0</b>, leaving <b>36.2</b>.</div>
        </div>
        <div class="p-card">
          <div class="p-card-head"><h3>What this replaced</h3></div>
          <div class="p-card-body">
            <p class="p-meta">Approving used to be the start of the work, not the end of it. A manager then opened the roster and created a leave shift by hand, one day at a time. A week of leave was five entries. Parental leave for a year was, in the words of one rostering manager, entered shift by shift.</p>
            <p class="p-meta" style="margin-top:10px">The balance was also a fortnight old, because it only moved at the pay run. Payroll absorbed the enquiries that caused.</p>
          </div>
        </div>
      </div>
    </div>'''
        title = "Leave, entered once"
    elif state == "consent":
        panel = '''
    <div class="p-grid p-grid-8-4">
      <div class="p-card">
        <div class="p-card-head"><h3>Entering leave for somebody else</h3><span class="p-badge p-badge-warning">Consent needed</span></div>
        <div class="p-card-body">
          <p class="p-meta" style="margin-bottom:16px">You are entering annual leave on behalf of Bridget K. for Thu 7 Nov. Because you are not the person taking the leave, she has to agree to it before it is written.</p>
          <div class="p-consent">
            <b>Bridget will get one notification</b>
            <p>It names the day, the hours, the leave type and who asked. She taps agree or asks a question. Nothing is written to the roster or the pay run until she does.</p>
            <div class="p-sent"><span class="p-avatar sm">BK</span>Sent to Bridget K. at 09:44 &middot; not yet answered</div>
          </div>
          <h4 style="font-size:var(--p-fs-3);margin:20px 0 8px">What she is being asked to agree to</h4>
          <div class="p-impact"><dl>
            <dt>Day</dt><dd>Thu 7 Nov 2024</dd>
            <dt>Shift being replaced</dt><dd>17:00 &ndash; 21:00, counter</dd>
            <dt>Leave type</dt><dd>Annual leave, paid</dd>
            <dt>Hours drawn from her balance</dt><dd>4.0 hrs</dd>
            <dt class="tot">Balance after</dt><dd class="tot">21.5 hrs</dd>
          </dl></div>
          <div class="p-actions" style="margin-top:16px"><button class="p-btn p-btn-secondary">Send a reminder</button><button class="p-btn p-btn-ghost">Withdraw the request</button></div>
        </div>
      </div>
      <div class="p-grid">
        <div class="p-card">
          <div class="p-card-head"><h3>Why consent is a screen</h3></div>
          <div class="p-card-body">
            <p class="p-meta">The research found leave being entered on people&rsquo;s behalf with nothing recorded, which is a problem the week somebody disputes a balance. Nobody was acting badly. There was simply no place in the product to capture the agreement, so the agreement happened in a conversation at the pass and then evaporated.</p>
            <p class="p-meta" style="margin-top:10px">Making consent a step costs the manager one tap and produces a record that survives both of them leaving.</p>
          </div>
        </div>
        <div class="p-card">
          <div class="p-card-head"><h3>Consent on file</h3><span class="p-meta">Last 90 days</span></div>
          <div class="p-list">
            <div class="p-list-row"><div class="p-grow"><b>Agreed</b><span class="p-sub">11 requests, median 14 minutes to answer</span></div><span class="p-badge p-badge-success">11</span></div>
            <div class="p-list-row"><div class="p-grow"><b>Questioned</b><span class="p-sub">Answered by the manager, then agreed</span></div><span class="p-badge p-badge-warning">2</span></div>
            <div class="p-list-row"><div class="p-grow"><b>Waiting</b><span class="p-sub">Reminder goes out after 24 hours</span></div><span class="p-badge p-badge-neutral">1</span></div>
          </div>
        </div>
      </div>
    </div>'''
        title = "Leave, consent captured"
    else:  # drop
        panel = '''
    <div class="p-grid p-grid-8-4">
      <div class="p-card">
        <div class="p-card-head"><h3>Bridget K. dropped Thu 7 Nov</h3><span class="p-badge p-badge-danger">Costs money if ignored</span></div>
        <div class="p-card-body">
          <div class="p-alert p-alert-danger"><b>She is now on 12.25 of her guaranteed 15.0 hours.</b> Left alone, the pay run adds make-up pay of $70.54 and the warning arrives after the money has gone.</div>
          <h4 style="font-size:var(--p-fs-3);margin-bottom:6px">What do you want to do with the shift?</h4>
          <p class="p-meta" style="margin-bottom:12px">This is the question the product never asked. A dropped shift simply vanished, and the consequence turned up at the pay run as a compliance warning about contracted hours.</p>
          <fieldset class="p-fieldset">
            <div class="p-choices one">
              <div class="p-choice"><input type="radio" id="d1" name="d" checked><label for="d1"><span class="p-glyph">A</span><div><b>Annual leave, paid</b><span>Draws 4.0 hrs from her balance of 25.5. Contracted hours met, no make-up pay.</span></div></label></div>
              <div class="p-choice"><input type="radio" id="d2" name="d"><label for="d2"><span class="p-glyph">U</span><div><b>Leave without pay</b><span>Contracted hours waived for the week by agreement. Needs her consent.</span></div></label></div>
              <div class="p-choice"><input type="radio" id="d3" name="d"><label for="d3"><span class="p-glyph">O</span><div><b>Offer the shift to the team</b><span>Goes to the three people qualified for counter who are under their hours.</span></div></label></div>
              <div class="p-choice"><input type="radio" id="d4" name="d"><label for="d4"><span class="p-glyph">M</span><div><b>Leave it short and pay the difference</b><span>Records the decision and the $70.54 now, rather than finding it later.</span></div></label></div>
            </div>
          </fieldset>
          <div class="p-actions"><button class="p-btn p-btn-primary">Apply and tell Bridget</button><button class="p-btn p-btn-secondary">Decide later</button></div>
        </div>
      </div>
      <div class="p-grid">
        <div class="p-card">
          <div class="p-card-head"><h3>Either way, the cost is shown first</h3></div>
          <div class="p-card-body">
            <div class="p-impact"><dl>
              <dt>Annual leave, paid</dt><dd class="good">$0 extra</dd>
              <dt>Leave without pay</dt><dd class="good">$0 extra</dd>
              <dt>Offer to the team</dt><dd class="good">$0 extra</dd>
              <dt class="tot">Leave it short</dt><dd class="tot bad">$70.54</dd>
            </dl></div>
            <p class="p-meta" style="margin-top:12px">The number comes from the same rule that generated the warning, so the manager is choosing with the figure in front of them rather than discovering it a fortnight later.</p>
          </div>
        </div>
        <div class="p-card p-stat p-stat-accent warning">
          <div class="p-stat-label">Make-up pay, this restaurant</div>
          <div class="p-stat-value">$412</div>
          <div class="p-stat-delta">over the last quarter, all of it from dropped part-time shifts nobody was asked about. <span class="good">Down $180</span> since the question moved to the drop.</div>
        </div>
      </div>
    </div>'''
        title = "Leave, a dropped part-time shift"

    body = f'''
  <div class="p-work">
    <div class="p-work-head">
      <h1>Leave</h1>
      <div class="p-spacer"></div>
      <button class="p-btn p-btn-secondary p-btn-sm">Leave calendar</button>
      <button class="p-btn p-btn-primary p-btn-sm">Enter leave</button>
    </div>
    <p class="p-work-sub">Approving leave writes the shifts. Entering leave for somebody else asks them first. Dropping a shift asks what it should become.</p>
    {panel}
  </div>'''
    return shell(title, "Leave", body)


# ------------------------------------------------------------------ pay period
def payperiod(state):
    if state == "open":
        head = f'''
    <div class="p-grid p-grid-4" style="margin-bottom:20px">
      <div class="p-card p-stat"><div class="p-stat-label">Pay period</div><div class="p-stat-value" style="font-size:var(--p-fs-5)">28 Oct &ndash; 10 Nov</div><div class="p-stat-delta">Closes Tue 12 Nov, 10:00</div></div>
      <div class="p-card p-stat p-stat-accent success"><div class="p-stat-label">Punches approved</div><div class="p-stat-value">{R.FORTNIGHT_SHIFTS - 3} / {R.FORTNIGHT_SHIFTS}</div><div class="p-stat-delta">Three left, all on the same day</div></div>
      <div class="p-card p-stat p-stat-accent warning"><div class="p-stat-label">Exceptions</div><div class="p-stat-value">3</div><div class="p-stat-delta">One missed clock-out, two early finishes</div></div>
      <div class="p-card p-stat"><div class="p-stat-label">Corrections after close</div><div class="p-stat-value">0</div><div class="p-stat-delta">Available for 21 days without reopening</div></div>
    </div>'''
        rows = '''
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">HN</span>Hugo N.</span><span class="p-sub">Cook</span></td>
        <td>Thu 7 Nov</td><td class="p-diff-cell"><span class="p-diff settled"><s>09:00&ndash;17:00 rostered</s><b>09:02&ndash;17:04 worked</b></span></td>
        <td>30 min unpaid</td><td class="p-num">7.53</td><td><span class="p-badge p-badge-success">Approved</span></td><td></td></tr>
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">CB</span>Chiara B.</span><span class="p-sub">Shift supervisor</span></td>
        <td>Fri 8 Nov</td><td><span class="p-diff"><s>14:00&ndash;23:00 rostered</s><b>14:00 in, never clocked out</b></span></td>
        <td>30 min unpaid</td><td class="p-num">&ndash;</td><td><span class="p-badge p-badge-danger">Missed clock-out</span></td>
        <td class="p-nowrap"><button class="p-btn p-btn-secondary p-btn-sm">Set the finish</button></td></tr>
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">TW</span>Tessa W.</span><span class="p-sub">Team member</span></td>
        <td>Fri 8 Nov</td><td><span class="p-diff"><s>11:00&ndash;15:00 rostered</s><b>11:00&ndash;14:12 worked</b></span></td>
        <td>None</td><td class="p-num">3.20</td><td><span class="p-badge p-badge-warning">Finished early</span></td>
        <td class="p-nowrap"><button class="p-btn p-btn-secondary p-btn-sm">Ask why</button></td></tr>
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">BK</span>Bridget K.</span><span class="p-sub">Team member</span></td>
        <td>Sat 9 Nov</td><td><span class="p-diff"><s>17:00&ndash;20:00 rostered</s><b>17:00&ndash;19:40 worked</b></span></td>
        <td>None</td><td class="p-num">2.67</td><td><span class="p-badge p-badge-warning">Finished early</span></td>
        <td class="p-nowrap"><button class="p-btn p-btn-secondary p-btn-sm">Ask why</button></td></tr>
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">RV</span>Rosa V.</span><span class="p-sub">Shared with Lakeside</span></td>
        <td>Sat 9 Nov</td><td><span class="p-diff settled"><s>16:00&ndash;23:00 rostered</s><b>16:00&ndash;23:06 worked</b></span></td>
        <td>30 min unpaid</td><td class="p-num">6.60</td><td><span class="p-badge p-badge-success">Approved</span></td>
        <td class="p-meta">Lakeside punches included</td></tr>'''
        panel = ""
        title = "Pay period, before close"
    elif state == "correct":
        head = ""
        rows = ""
        panel = '''
    <div class="p-grid p-grid-8-4">
      <div class="p-card">
        <div class="p-card-head"><h3>Correct a shift in a closed period</h3><span class="p-badge p-badge-neutral">Period closed 12 Nov</span></div>
        <div class="p-card-body">
          <p class="p-meta" style="margin-bottom:16px">Bridget K. worked her Monday shift on 28 October and forgot to clock on. She told Chiara B., the supervisor on shift, the same evening. The period closed on the 12th. This pays the five hours in the period they were worked, without reopening anything and without asking payroll.</p>
          <div class="p-grid p-grid-2" style="margin-bottom:4px">
            <label class="p-field"><span>Day worked</span><input class="p-input" value="Mon 28 Oct 2024"></label>
            <label class="p-field"><span>Hours</span><input class="p-input" value="5.00"></label>
          </div>
          <label class="p-field"><span>What happened</span><textarea class="p-textarea">Rostered 11:00 to 16:00 and worked the full shift. Did not clock on. Confirmed by Chiara B., who was the supervisor on shift, and by the drive thru till log.</textarea></label>
          <div class="p-alert p-alert-success"><b>Paid at Monday&rsquo;s ordinary rate, in the period it was worked.</b> No overtime, no compliance pay, and Bridget&rsquo;s contracted hours for that week are met rather than carried into the next one.</div>
          <div class="p-actions"><button class="p-btn p-btn-primary">Send to payroll</button><button class="p-btn p-btn-secondary">Save as draft</button></div>
          <p class="p-meta" style="margin-top:12px">Everything here is on the shift, so the area coach reading next week&rsquo;s compliance report sees a correction with a reason rather than an unexplained overtime payment.</p>
        </div>
      </div>
      <div class="p-grid">
        <div class="p-card">
          <div class="p-card-head"><h3>What this pays</h3></div>
          <div class="p-card-body">
            <div class="p-impact"><dl>
              <dt>5.00 hrs, ordinary rate</dt><dd>$128.25</dd>
              <dt>Superannuation</dt><dd>$14.75</dd>
              <dt>Overtime incurred</dt><dd class="good">None</dd>
              <dt>Effect on next week&rsquo;s hours</dt><dd class="good">None</dd>
              <dt class="tot">Paid on</dt><dd class="tot">26 Nov, this cycle</dd>
            </dl></div>
          </div>
        </div>
        <div class="p-card">
          <div class="p-card-head"><h3>The workaround it replaces</h3></div>
          <div class="p-card-body">
            <p class="p-meta" style="margin-bottom:12px">The research followed this exact correction through the old process. Payroll would not reopen the period, so the five hours went onto the following week&rsquo;s roster as an extra shift.</p>
            <div class="p-impact"><dl>
              <dt>5.00 hrs added to the next week</dt><dd>$128.25</dd>
              <dt>Pushes her past her contracted hours</dt><dd class="bad">+$42.75 overtime</dd>
              <dt>Compliance pay triggered</dt><dd class="bad">+$25.65</dd>
              <dt class="tot">Costs the restaurant</dt><dd class="tot bad">$68.40 more</dd>
            </dl></div>
            <p class="p-meta" style="margin-top:12px">It also reached her as a pay rise she had not earned, which she found confusing and embarrassing, and reached the area coach as an unexplained overtime line on the weekly compliance report. Three people spent time on a five hour shift that nobody disputed.</p>
          </div>
        </div>
      </div>
    </div>'''
        title = "Pay period, correcting after close"
    else:  # closed
        head = f'''
    <div class="p-grid p-grid-4" style="margin-bottom:20px">
      <div class="p-card p-stat"><div class="p-stat-label">Pay period</div><div class="p-stat-value" style="font-size:var(--p-fs-5)">28 Oct &ndash; 10 Nov</div><div class="p-stat-delta">Closed Tue 12 Nov, 09:58, by Nadia A.</div></div>
      <div class="p-card p-stat p-stat-accent success"><div class="p-stat-label">Sent to payroll</div><div class="p-stat-value">{R.FORTNIGHT_SHIFTS} / {R.FORTNIGHT_SHIFTS}</div><div class="p-stat-delta">No shift left unapproved</div></div>
      <div class="p-card p-stat p-stat-accent success"><div class="p-stat-label">Corrections</div><div class="p-stat-value">1</div><div class="p-stat-delta">Paid in the period it was worked</div></div>
      <div class="p-card p-stat"><div class="p-stat-label">Reopened</div><div class="p-stat-value">0</div><div class="p-stat-delta">The period never had to be reopened</div></div>
    </div>'''
        rows = '''
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">HN</span>Hugo N.</span><span class="p-sub">Correction, Sun 3 Nov</span></td>
        <td>Raised 14 Nov</td><td>1.00 hr at Sunday rate</td><td class="p-num">$38.48</td>
        <td><span class="p-badge p-badge-success">Paid 26 Nov</span></td><td class="p-meta">Nadia A. &middot; confirmed by Chiara B.</td></tr>
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">JR</span>Jaxon R.</span><span class="p-sub">Dismissal, Thu 7 Nov</span></td>
        <td>Recorded 6 Nov</td><td>Rostered past 21:00, school night</td><td class="p-num">&ndash;</td>
        <td><span class="p-badge p-badge-neutral">On the shift</span></td><td class="p-meta">Guardian consent on file, 14 Oct</td></tr>
      <tr><td class="p-primary-cell"><span class="p-person"><span class="p-avatar sm">BK</span>Bridget K.</span><span class="p-sub">Dropped shift, Thu 7 Nov</span></td>
        <td>Resolved 6 Nov</td><td>Became paid annual leave, 4.0 hrs</td><td class="p-num">$0.00</td>
        <td><span class="p-badge p-badge-success">Consented</span></td><td class="p-meta">Agreed by Bridget K. at 10:02</td></tr>'''
        panel = ""
        title = "Pay period, closed with its record"

    table = ""
    if rows:
        cols = ('<th>Person</th><th>Day</th><th>Rostered against worked</th><th>Break</th>'
                '<th class="p-num">Hours</th><th>State</th><th></th>') if state == "open" else (
               '<th>Person</th><th>Raised</th><th>What changed</th><th class="p-num">Amount</th><th>State</th><th>Recorded by</th>')
        table = (f'<div class="p-table-wrap"><table class="p-table"><thead><tr>{cols}</tr></thead>'
                 f'<tbody>{rows}</tbody></table>'
                 f'<div class="p-table-foot"><span>'
                 f'{"Showing the five shifts with something to say. 59 more are clean." if state == "open" else "Everything that happened to this period, kept with the period."}'
                 f'</span></div></div>')

    sub = {"open": "Three punches need a decision before Tuesday. Rostered and worked are shown together, because the gap between them is the only thing worth reading.",
           "correct": "A correction is a first-class thing that happens inside a closed period, not a reason to reopen one.",
           "closed": "Closed, and everything that happened to it kept with it: one correction, one dismissal and one dropped shift that became leave."}[state]
    body = f'''
  <div class="p-work">
    <div class="p-work-head">
      <h1>Pay period</h1>
      <div class="p-spacer"></div>
      {'<button class="p-btn p-btn-secondary p-btn-sm">Export for payroll</button><button class="p-btn p-btn-primary p-btn-sm">Close the period</button>' if state == "open" else '<button class="p-btn p-btn-secondary p-btn-sm">Export for payroll</button><button class="p-btn p-btn-secondary p-btn-sm">Raise a correction</button>'}
    </div>
    <p class="p-work-sub">{sub}</p>
    {head}{panel}{table}
  </div>'''
    return shell(title, "Pay", body, who="AM")


def main():
    for st in ("list", "dismiss"):
        write(f"compliance-{st}.html", compliance(st))
    for st in ("range", "consent", "drop"):
        write(f"leave-{st}.html", leave(st))
    for st in ("open", "correct", "closed"):
        write(f"payperiod-{st}.html", payperiod(st))


if __name__ == "__main__":
    main()
