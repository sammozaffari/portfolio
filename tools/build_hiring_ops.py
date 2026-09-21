#!/usr/bin/env python3
"""The manager screens for the hiring and onboarding showcase.

Three, and each one is the answer to a finding rather than a feature.

The pipeline carries the waiting time on every card, because the research found
the wait from application to a first human touch ran from days to weeks and
nobody in the business could see it while it was happening.

The review queue arrives with the screening answers attached, because managers
were re-keying candidate data between systems and a candidate who falls outside
the auto-schedule rule is not a rejection, they are a decision somebody has to
make with context.

The human lane exists because work rights was the step that most needed a person
and least had one. A machine can say a photo is unreadable. It must not be
allowed to say a sixteen year old cannot have their first job.

Writes: articles/55/showcase/screens/*.html
Usage: build_hiring_ops.py
"""
import pathlib, html
import hiring_data as D

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "articles/55/showcase/screens"
e = lambda s: html.escape(str(s), quote=False)

# Declared once. The count in the nav is the count on the screen below it.
NAV = [("Pipeline", (str(D.IN_PROGRESS), "")), ("Interviews", None), ("Work rights", ("2", "attn")),
       ("Onboarding", None), ("Reports", None)]
WHERE = f"<b>{D.RESTAURANT}</b> &middot; {D.RESTAURANT_NO} &middot; equity"


def shell(title, current, body, width=1440, who="PM", extra=""):
    nav = []
    for label, count in NAV:
        cur = ' aria-current="page"' if label == current else ""
        c = f'<span class="p-count {count[1]}">{count[0]}</span>' if count else ""
        nav.append(f'<a href="#"{cur}>{e(label)}{c}</a>')
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; Hiring concept</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../../assets/product/tokens.css"><link rel="stylesheet" href="../../../../assets/product/components.css">
<style>html,body{{width:{width}px}}{extra}</style>
</head><body class="p-app">
<div class="p-shell-top" style="position:relative">
  <header class="p-appbar">
    <div class="p-brand-inline"><div class="p-brand-mark">H</div><b>Hiring</b></div>
    <nav class="p-modnav">{''.join(nav)}</nav>
    <div class="p-spacer"></div>
    <div class="p-where">{WHERE}</div>
    <span class="p-avatar">{e(who)}</span>
  </header>
  {body}
</div>
</body></html>
'''


def _write_if_changed(path, content):
    if path.exists() and path.read_text() == content:
        return False
    path.write_text(content)
    return True


def write(name, content):
    SCR.mkdir(parents=True, exist_ok=True)
    changed = _write_if_changed(SCR / name, content)
    print(("wrote " if changed else "same  ") + str((SCR / name).relative_to(ROOT)))


# ------------------------------------------------------------------ pipeline
cols = []
for stage, cards in D.PIPELINE:
    body = []
    for c in cards:
        p = D.CAST[c["who"]]
        cls = {"ok": "", "warn": " warn", "bad": " bad"}[c["flag"]]
        trail = (f'<div class="p-link-ref" style="margin-top:6px">{c["trail"]}</div>'
                 if c.get("trail") else "")
        body.append(
            f'<div class="p-kcard"><b>{e(p["name"])}</b>'
            f'<span class="p-sub">{e(c["sub"])}</span>{trail}'
            f'<div class="p-kmeta"><span class="p-waited{cls}">waited {e(c["waited"])}</span>'
            f'<span class="p-link-ref">{e(p["role"])}</span></div></div>')
    if not cards:
        body.append('<div class="p-empty" style="padding:16px 10px;font-size:var(--p-fs-2)">'
                    'Nobody here</div>')
    cols.append(f'<div><div class="p-col-head">{e(stage)}'
                f'<span class="p-count">{len(cards)}</span></div>{"".join(body)}</div>')

pipeline_body = f'''
<main class="p-work">
  <div class="p-work-head"><h1>Hiring at {D.RESTAURANT}</h1><div class="p-spacer"></div>
    <div class="p-counters">
      <span class="p-counter">{D.IN_PROGRESS} in progress</span>
      <span class="p-counter attn">1 waiting on you</span>
    </div>
    <button class="p-btn p-btn-secondary p-btn-sm">This restaurant</button>
    <button class="p-btn p-btn-primary p-btn-sm">Post a job</button>
  </div>
  <p class="p-work-sub">Every card carries how long that person has been waiting, because the wait from applying to hearing from a human ran from days to weeks and nobody could see it while it was happening. {D.DAYS["offer"][1]}.</p>
  <div class="p-kanban" style="grid-template-columns:repeat(5,minmax(0,1fr))">{"".join(cols)}</div>
  <div class="p-grid p-grid-3" style="margin-top:22px">
    <div class="p-card p-stat p-stat-accent warning"><div class="p-stat-label">Longest wait right now</div>
      <div class="p-stat-value">{D.OTIS_WAIT}</div>
      <div class="p-stat-delta">{D.CAST["otis"]["name"]}, held on a document, not on a decision</div></div>
    <div class="p-card p-stat"><div class="p-stat-label">Applied to offer</div>
      <div class="p-stat-value">{D.APPLY_TO_OFFER}</div>
      <div class="p-stat-delta">{D.CAST["tia"]["name"]}, {D.DAYS["apply"][1]} to {D.DAYS["offer"][1]}</div></div>
    <div class="p-card p-stat"><div class="p-stat-label">Answer guaranteed within</div>
      <div class="p-stat-value">{D.DISPOSITION_DAYS} days</div>
      <div class="p-stat-delta">Reminders at {", ".join(D.REMINDERS[:-1])} and {D.REMINDERS[-1]}, then an answer either way</div></div>
  </div>
</main>'''
write("pipeline.html", shell("Pipeline", "Pipeline", pipeline_body,
                             extra=".p-kcard .p-sub{display:block;margin-top:-2px}"))

# --------------------------------------------------------------------- queue
# The person who needs a decision leads. Their answers travel with them, which
# is the whole point: the manager decides with context instead of re-keying it
# out of another system. Tia is the contrast in the rail, the one who needed
# nobody at all.
otis_rows = "".join(
    f'<div class="p-list-row"><div class="p-grow"><b>{e(q["ask"])}</b>'
    f'<span class="p-sub">{e(q["why"])}</span></div>'
    f'<span class="p-badge p-badge-{"warning" if a == "Neither" else "neutral"} p-badge-plain">{e(a)}</span></div>'
    for q, a in zip(D.QUESTIONS, D.OTIS_ANSWERS))

queue_body = f'''
<main class="p-work">
  <div class="p-work-head"><h1>Needs a decision</h1><div class="p-spacer"></div>
    <div class="p-counters"><span class="p-counter attn">1 person</span></div>
  </div>
  <p class="p-work-sub">A candidate outside the auto-schedule rule is not a rejection. They arrive here with everything they already told us, so the decision is made with context rather than re-keyed from another system. {D.DAYS["offer"][1]}.</p>
  <div class="p-grid p-grid-8-4">
    <div class="p-card">
      <div class="p-card-head"><h2>{D.CAST["otis"]["name"]}</h2>
        <span class="p-badge p-badge-warning p-badge-plain">Waiting {D.OTIS_WAIT}</span></div>
      <div class="p-card-body">
        <p class="p-meta" style="margin-bottom:12px">Answered all five on {D.DAYS["apply"][1]}. The rule is {D.AUTO_RULE}. He meets it on shifts and misses it on the last question only, so he is a decision, not a rejection.</p>
        <div class="p-list">{otis_rows}</div>
        <div class="p-actions p-mt-4">
          <button class="p-btn p-btn-primary">Offer an interview anyway</button>
          <button class="p-btn p-btn-secondary">Ask if a Saturday could work</button>
          <button class="p-btn p-btn-ghost">Not this time, with a reason</button>
        </div>
        <p class="p-meta p-mt-3">Whichever you choose, he hears back today. Nobody is dispositioned silently.</p>
      </div>
    </div>
    <div class="p-grid" style="gap:var(--p-s-4)">
      <div class="p-card">
        <div class="p-card-head"><h2>{D.CAST["tia"]["name"]}</h2>
          <span class="p-badge p-badge-success p-badge-plain">Never reached this queue</span></div>
        <div class="p-card-body">
          <p class="p-meta" style="margin-bottom:10px">She met the rule, so the conversation booked her in without you. This is what the queue is for: the exceptions, not the applicants.</p>
          <ol class="p-steps">
            <li>{D.ASSISTANT} asked the five questions</li>
            <li>Under 18, so consent went to a parent first</li>
            <li>She picked a time from your real free slots</li>
            <li>You met her, and sent the offer</li>
          </ol>
        </div>
      </div>
      <div class="p-card">
        <div class="p-card-head"><h2>What you never do here</h2></div>
        <div class="p-card-body"><div class="p-list">
          <div class="p-list-row"><div class="p-grow"><b>Re-type an answer</b><span class="p-sub">They travel with the person</span></div></div>
          <div class="p-list-row"><div class="p-grow"><b>Chase a time by text</b><span class="p-sub">The slots are yours already</span></div></div>
          <div class="p-list-row"><div class="p-grow"><b>Leave somebody guessing</b><span class="p-sub">An answer either way within {D.DISPOSITION_DAYS} days</span></div></div>
        </div></div>
      </div>
    </div>
  </div>
</main>'''
write("queue.html", shell("Review queue", "Pipeline", queue_body))

# ----------------------------------------------------------------- humanlane
rows = []
for c in D.OTIS_CHECKS:
    glyph = {"pass": "&check;", "review": "?", "fail": "!"}[c["state"]]
    who = "Automatic" if c["how"] == "auto" else "A person"
    rows.append(f'<div class="p-vcheck {c["state"]}"><i>{glyph}</i>'
                f'<div><b>{e(c["what"])}</b><span>{e(c["note"])}</span></div>'
                f'<em>{who}</em></div>')

human_body = f'''
<main class="p-work">
  <div class="p-work-head"><h1>Work rights, human lane</h1><div class="p-spacer"></div>
    <div class="p-counters"><span class="p-counter attn">1 person, 2 checks</span></div>
    <div class="p-where" style="margin-right:8px">{D.CAST["vikram"]["name"]} &middot; {D.CAST["vikram"]["role"]}</div>
  </div>
  <p class="p-work-sub">An automated check can say a photo is unreadable. It cannot be allowed to say somebody cannot have a job. Anything a machine will not pass arrives here, and a person accepts or rejects it with a reason that gets emailed. {D.DAYS["offer"][1]}.</p>
  <div class="p-grid p-grid-8-4">
    <div class="p-card">
      <div class="p-card-head"><h2>{D.CAST["otis"]["name"]}</h2>
        <span class="p-badge p-badge-warning p-badge-plain">{D.OTIS_WAIT} in the lane</span></div>
      <div class="p-card-body">
        {"".join(rows)}
        <div class="p-alert p-alert-warning p-mt-4">
          <b>Neither of these is a rejection</b>
          <p>A cut-off photo is a photo problem. A student visa with a fortnightly cap is a rostering constraint, not a refusal. Both need a person to say so.</p>
        </div>
        <div class="p-field p-mt-4">
          <span>Reason, which is emailed to {D.CAST["otis"]["first"]} in these words</span>
          <div class="p-textarea">We need one more photo of your visa page with all four corners showing. Nothing is wrong with your application. Once we have it you are cleared to start.</div>
        </div>
        <div class="p-actions p-mt-3">
          <button class="p-btn p-btn-primary">Ask for one more photo</button>
          <button class="p-btn p-btn-secondary">Accept as is</button>
          <button class="p-btn p-btn-ghost">Cannot proceed, with a reason</button>
        </div>
      </div>
    </div>
    <div class="p-grid" style="gap:var(--p-s-4)">
      <div class="p-card">
        <div class="p-card-head"><h2>What runs automatically</h2></div>
        <div class="p-card-body"><div class="p-list">
          <div class="p-list-row"><div class="p-grow"><b>Document is readable</b></div>
            <span class="p-badge p-badge-neutral p-badge-plain">Machine</span></div>
          <div class="p-list-row"><div class="p-grow"><b>Name and date of birth match</b></div>
            <span class="p-badge p-badge-neutral p-badge-plain">Machine</span></div>
          <div class="p-list-row"><div class="p-grow"><b>Right to work register</b></div>
            <span class="p-badge p-badge-neutral p-badge-plain">Machine</span></div>
          <div class="p-list-row"><div class="p-grow"><b>Anything that did not pass</b></div>
            <span class="p-badge p-badge-warning p-badge-plain">A person</span></div>
          <div class="p-list-row"><div class="p-grow"><b>Anyone under 18</b></div>
            <span class="p-badge p-badge-warning p-badge-plain">A person</span></div>
        </div></div>
      </div>
      <div class="p-card">
        <div class="p-card-head"><h2>Locked in the specification</h2></div>
        <div class="p-card-body">
          <p class="p-meta">Age and consent logic cannot be changed without sign-off. A false negative on a first job is not an acceptable error, and the compliance exposure is real.</p>
        </div>
      </div>
    </div>
  </div>
</main>'''
write("humanlane.html", shell("Human lane", "Work rights", human_body, who="VS"))
