#!/usr/bin/env python3
"""The candidate screens for the hiring and onboarding showcase.

Seven screens, in the order a sixteen year old meets them: finding the job,
answering five questions, waiting on a parent, booking her own interview,
sending her documents once, reading the offer, and turning up.

Every one of them answers something the research recorded. Candidates uploaded
the same documents more than once even when everything was correct. Offers
landed in spam. The wait for a first human touch ran from days to weeks. Work
rights was the step that most needed a person and least had one.

The phone is drawn at 393 by 852, the size the device frame on the showcase
page is built at, and captured at 2x. The frame's own border and shadow are
switched off here because the page draws them.

Usage: build_hiring.py
"""
import pathlib
import hiring_data as D
from statusbar import status_bar

# The clock on each screen: a sixteen year old applies after school, a parent
# consents in the evening (Nina agreed at 6:48pm), the offer is read after
# school on Friday and the work-rights check is a Saturday morning.
TIMES = {
    "find": "16:12", "questions": "16:15", "consent": "18:46", "book": "18:52",
    "rights": "10:20", "offer": "15:41", "before": "19:05",
}

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/3/showcase/screens"
SCR.mkdir(parents=True, exist_ok=True)


def phone(slug, title, body, cta="", step=None, bar=None):
    """One candidate screen.

    step is (done, total) and draws the progress bar, because a form with no
    visible end is the thing candidates abandoned.
    """
    stepper = ""
    if step:
        done, total = step
        cells = "".join(
            f'<span class="{"done" if i < done - 1 else "now" if i == done - 1 else ""}"></span>'
            for i in range(total))
        stepper = f'<div class="p-stepper">{cells}</div>'
    appbar = ""
    if bar:
        appbar = ('<div class="p-app-bar"><span class="p-back">'
                  '<svg class="p-ico" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" '
                  'stroke-width="1.8"><path d="M11 3L5.5 9l5.5 6"/></svg></span>'
                  f'<h1>{bar}</h1></div>')
    html = f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; Hiring concept</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../../assets/product/tokens.css"><link rel="stylesheet" href="../../../../assets/product/components.css">
<style>html,body{{width:393px;height:852px;overflow:hidden}}
.p-phone{{width:393px;height:852px;border:0;border-radius:0;box-shadow:none}}</style>
</head><body class="p-app">
<div class="p-phone">
  {status_bar(TIMES.get(slug, "16:12"))}
  {appbar}
  <div class="p-screen" style="display:flex;flex-direction:column;padding-bottom:0">
    <div style="flex:1;overflow:hidden">{stepper}{body}</div>
  </div>
  {cta}
  <div class="p-home"></div>
</div>
</body></html>
'''
    (SCR / f"{slug}.html").write_text(html)
    return slug


def cta(label, secondary=None, note=None):
    n = f'<p class="p-meta" style="text-align:center;margin-top:2px">{note}</p>' if note else ""
    s = f'<button class="p-btn p-btn-secondary p-btn-lg">{secondary}</button>' if secondary else ""
    return f'<div class="p-cta"><button class="p-btn p-btn-primary p-btn-lg p-btn-block">{label}</button>{s}{n}</div>'


# ------------------------------------------------------------------ 1. find
JOBS = [
    ("Crew member", f"KFC {D.RESTAURANT}", "1.2 km", "Casual &middot; after school and weekends",
     "3 shifts a week", True),
    ("Crew member", f"KFC {D.SECOND_RESTAURANT}", "4.6 km", "Casual &middot; weekends",
     "2 shifts a week", False),
    ("Cook", f"KFC {D.RESTAURANT}", "1.2 km", "Part time &middot; weekday evenings",
     "4 shifts a week", False),
]
rows = []
for role, where, dist, when, shifts, near in JOBS:
    cls = "p-ledge pick" if near else "p-ledge"
    tag = ('<div style="margin-top:8px;font-size:var(--p-fs-1);font-weight:600;'
           'text-transform:uppercase;letter-spacing:var(--p-tracking-caps)">Closest to you</div>'
           if near else "")
    rows.append(
        f'<div class="{cls}" style="margin-bottom:16px">'
        f'<b style="display:block;font-size:var(--p-fs-5);letter-spacing:var(--p-tracking-tight)">{role}</b>'
        f'<span class="p-sub" style="display:block;margin-top:2px">{where} &middot; {dist} away</span>'
        f'<em style="display:block;font-style:normal;font-size:var(--p-fs-2);margin-top:8px">{when}<br>{shifts}</em>'
        f'{tag}</div>')
find_body = f'''
<div class="p-mhead" style="padding-left:0;padding-right:0">
  <h1>Jobs near you</h1>
  <p>3 open at 2 restaurants within 5 km</p>
</div>
<div class="p-field" style="margin-bottom:16px">
  <div class="p-input" style="display:flex;align-items:center;gap:8px;color:var(--p-ink);border-radius:var(--p-r-2)">
    <svg class="p-ico" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.7" style="flex:none"><path d="M9 16s5.5-4.7 5.5-8.5a5.5 5.5 0 1 0-11 0C3.5 11.3 9 16 9 16z"/><circle cx="9" cy="7.5" r="2"/></svg>
    Your suburb
  </div>
</div>
{"".join(rows)}
<p class="p-meta" style="margin-top:4px">The whole ad is on this page. You do not leave to read it, and you do not need an account to start.</p>
'''
phone("find", "Jobs near you", find_body, cta("Start with the Riverside job"), bar=None)

# ------------------------------------------------------------- 2. questions
# Two answered, the third being asked. Showing the conversation mid-flow is the
# only way to show that an answer is a chip and not a typed field.
def msg(text, who=None):
    w = f'<span class="p-who">{who}</span>' if who else ""
    return f'<div class="p-msg">{w}{text}</div>'


def you(text):
    return f'<div class="p-msg you">{text}</div>'


q0, q1, q2 = D.QUESTIONS[0], D.QUESTIONS[1], D.QUESTIONS[2]
chips = "".join(
    f'<span class="{"on" if c == q2["answer"].split(" and ")[0] else ""}">{c}</span>'
    for c in q2["chips"])
questions_body = f'''
<div class="p-chat">
  {msg(f"I am {D.ASSISTANT}, an assistant, not a person. Five questions and I will book you in with the manager. Nothing you say here is a decision on its own.", who=D.ASSISTANT)}
  {msg(q0["ask"])}
  {you(q0["answer"])}
  {msg(q1["ask"])}
  {you(q1["answer"])}
  {msg(q2["ask"])}
</div>
<p class="p-why">{q2["why"]}</p>
<div class="p-quick" style="margin-top:12px">{chips}</div>
<p class="p-meta" style="margin-top:16px">Question 3 of 5</p>
'''
phone("questions", "Five questions", questions_body,
      cta("Next", note="You can change any answer before you finish."),
      step=(3, 5), bar=D.ASSISTANT)

# --------------------------------------------------------------- 3. consent
# The compliance-locked branch. It runs before any decision, and the screen says
# so, because a sixteen year old who is not told why nothing is happening will
# assume they were rejected.
consent_body = f'''
<div class="p-consent">
  <b>We have asked {D.CAST["nina"]["name"]} first</b>
  <p>You are 16, so a parent or guardian has to agree before anything else happens. This is not a decision about your application.</p>
  <div class="p-sent">Sent {D.DAYS["consent"][0]}, 4:12pm to a mobile number</div>
</div>
<div class="p-list" style="margin-top:18px">
  <div class="p-list-row"><div class="p-grow"><b>What they are agreeing to</b>
    <span class="p-sub">The hours a 16 year old can work, the casual junior rate of ${D.TIA_RATE:.2f} an hour, and that you can stop at any time.</span></div></div>
  <div class="p-list-row"><div class="p-grow"><b>What happens if they do not</b>
    <span class="p-sub">Nothing on your record. No rejection, and you can come back when you turn 17.</span></div></div>
</div>
<h3 style="font-size:var(--p-fs-3);margin:20px 0 6px">While you wait</h3>
<ol class="p-steps">
  <li>{D.CAST["nina"]["first"]} taps the link and agrees</li>
  <li>You pick an interview time that suits you</li>
  <li>You meet {D.CAST["keira"]["name"]} at the restaurant</li>
</ol>
<p class="p-meta" style="margin-top:14px">Your rate is {int(D.JUNIOR_PCT[16]*100)}% of the adult Level 1 rate of ${D.ADULT_RATE:.2f}, plus {int(D.CASUAL_LOADING*100)}% casual loading, and it steps up on each birthday.</p>
'''
phone("consent", "Consent first", consent_body,
      cta("Remind Nina", secondary="Use a different contact"), step=(4, 5), bar="Almost there")

# ------------------------------------------------------------------ 4. book
days = []
for d in D.INTERVIEW_SLOTS:
    if not d["slots"]:
        days.append(f'<div class="p-slotday"><b>{d["day"]}</b><em>{d["note"]}</em></div>')
    else:
        pills = "".join(
            f'<span class="p-slot{" on" if s == d.get("picked") else ""}">{s}</span>'
            for s in d["slots"])
        days.append(f'<div class="p-slotday"><b>{d["day"]}</b><div class="p-slotrow">{pills}</div></div>')
book_body = f'''
<div class="p-mhead" style="padding-left:0;padding-right:0">
  <h1>Pick a time</h1>
  <p>These are {D.CAST["keira"]["name"]}&rsquo;s real free times, so nobody has to text back and forth.</p>
</div>
<div class="p-slots">{"".join(days)}</div>
<div class="p-alert p-alert-info" style="margin-top:18px">
  <b>{D.INTERVIEW_WHERE}</b>
  <p>15 minutes. Wear what you like. You do not need to bring anything.</p>
</div>
'''
phone("book", "Pick a time", book_body,
      cta(f'Book {D.INTERVIEW_SLOTS[1]["day"]}, {D.INTERVIEW_SLOTS[1]["picked"]}',
          note="You can move it once without asking anyone."),
      step=(5, 5), bar="Your interview")

# ---------------------------------------------------------------- 5. rights
checks = []
for c in D.RIGHTS_CHECKS:
    glyph = {"pass": "&check;", "review": "?", "fail": "!"}[c["state"]]
    label = "Automatic" if c["how"] == "auto" else "A person"
    checks.append(f'<div class="p-vcheck {c["state"]}"><i>{glyph}</i>'
                  f'<div><b>{c["what"]}</b><span>{c["note"]}</span></div>'
                  f'<em>{label}</em></div>')
rights_body = f'''
<div class="p-mhead" style="padding-left:0;padding-right:0">
  <h1>Sent once</h1>
  <p>One photo of your birth certificate or passport. You will not be asked for it again.</p>
</div>
<div class="p-alert p-alert-success" style="margin-bottom:16px">
  <b>All five checks are done</b>
  <p>Nothing here is ever rejected by a machine. If a check cannot decide, a person looks at it.</p>
</div>
{"".join(checks)}
<p class="p-meta" style="margin-top:16px">Payroll, rostering and the restaurant all read this one record, so the same document is never asked for twice.</p>
'''
phone("rights", "Work rights", rights_body, cta("Done"), bar="Your documents")

# ----------------------------------------------------------------- 6. offer
offer_body = f'''
<div class="p-mhead" style="padding-left:0;padding-right:0">
  <h1>You have the job</h1>
  <p>Sent {D.DAYS["offer"][0]}, 9:10am by {D.CAST["keira"]["name"]}</p>
</div>
<div class="p-list" style="border:1px solid var(--p-line);border-radius:var(--p-r-2);padding:2px 14px;margin-bottom:16px">
  <div class="p-list-row"><div class="p-grow"><b>Crew member, KFC {D.RESTAURANT}</b><span class="p-sub">Casual</span></div></div>
  <div class="p-list-row"><div class="p-grow"><b>${D.TIA_RATE:.2f} an hour</b><span class="p-sub">{int(D.JUNIOR_PCT[16]*100)}% of the adult Level 1 rate of ${D.ADULT_RATE:.2f}, plus {int(D.CASUAL_LOADING*100)}% casual loading, stepping up each birthday</span></div></div>
  <div class="p-list-row"><div class="p-grow"><b>3 shifts a week</b><span class="p-sub">After school and Saturdays, the hours you said suited you</span></div></div>
  <div class="p-list-row"><div class="p-grow"><b>Starts {D.DAYS["start"][1]}</b><span class="p-sub">4:00pm to 8:00pm</span></div></div>
</div>
<div class="p-alert p-alert-info">
  <b>This will not land in your spam</b>
  <p>It is here, and we text you. We will nudge you at {", ".join(D.REMINDERS[:-1])} and {D.REMINDERS[-1]}, and if you do nothing for {D.DISPOSITION_DAYS} days we will tell you where you stand either way.</p>
</div>
'''
phone("offer", "The offer", offer_body,
      cta("Accept", secondary="Ask a question first"), bar="Your offer")

# ---------------------------------------------------------------- 7. before
before_body = f'''
<div class="p-mhead" style="padding-left:0;padding-right:0">
  <h1>Tomorrow, 4:00pm</h1>
  <p>{D.DAYS["start"][1]} &middot; KFC {D.RESTAURANT} &middot; your first shift</p>
</div>
<div class="p-mrow next"><div class="p-mdate"><i>Tue</i><b>12</b></div>
  <div class="p-grow"><b>4:00pm to 8:00pm</b><span>Front counter, with a trainer</span>
  <em>Ask for {D.CAST["keira"]["name"]} at the counter</em></div></div>
<h3 style="font-size:var(--p-fs-3);margin:20px 0 6px">Bring</h3>
<ol class="p-steps">
  <li>Closed black shoes. Everything else we give you</li>
  <li>Nothing else. Your documents are already done</li>
</ol>
<h3 style="font-size:var(--p-fs-3);margin:20px 0 6px">Getting there</h3>
<div class="p-list">
  <div class="p-list-row"><div class="p-grow"><b>Arrive 3:50pm</b><span class="p-sub">Ten minutes early is paid. Come to the counter, not the back door.</span></div></div>
  <div class="p-list-row"><div class="p-grow"><b>If something goes wrong</b><span class="p-sub">Text the restaurant. Being late on a first shift is not a problem, not turning up without a word is.</span></div></div>
</div>
'''
phone("before", "Before your first shift", before_body,
      cta("Add to my calendar", secondary="I cannot make it"), bar="First shift")

print("wrote 7 candidate screens to", SCR.relative_to(ROOT))
