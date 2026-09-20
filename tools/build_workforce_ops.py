#!/usr/bin/env python3
"""The operational screens of the workforce showcase: the time clock deployment
board, live labour, reporting above a single restaurant, and the feature
console. Shares the app shell with build_workforce.py rather than repeating it,
so the module navigation stays identical across every screen.

Usage: build_workforce_ops.py
"""
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_workforce import shell, write  # noqa: E402

# ------------------------------------------------------- the time clock board
# Journey 1 in the report: during the dinner rush the assistant manager looks
# over at the time clock and all she can see is a list of red compliance
# warnings. This board is what replaces that. It answers the question she
# actually has, which is who is standing where and who is owed a break, and it
# is generated from the published roster instead of being written out by hand
# onto a laminated sheet once or twice a day. The station names are the ones
# photographed on the charts in the restaurants.
LANES = [
    ("Lane 1", "#24405e", [
        ("Expo 1", "Priya S.", "11:00&ndash;15:00", "10 min taken", "done"),
        ("L1 QT", "Natalia F.", "10:45&ndash;16:00", "30 min at 13:00", "due"),
        ("Money taker", "Jaxon R.", "16:00&ndash;20:00", "10 min at 18:00", ""),
        ("Burger 1", "Dev P.", "12:00&ndash;18:00", "30 min taken", "done"),
        ("Pack 1", None, "", "", ""),
    ]),
    ("Lane 2", "#7d5300", [
        ("Expo 2", "Omar H.", "15:00&ndash;21:00", "30 min at 18:00", ""),
        ("L2 QT", "Mia T.", "16:00&ndash;22:00", "10 min at 18:30", ""),
        ("Checker", "Chiara B.", "14:00&ndash;23:30", "30 min at 18:00", "due"),
        ("Burger 2", None, "", "", ""),
        ("Pack 2", None, "", "", ""),
    ]),
    ("Kitchen", "#54407e", [
        ("Cook 1", "Dan R.", "09:00&ndash;17:00", "30 min taken", "done"),
        ("Cook 2", "Dev P.", "12:00&ndash;18:00", "Also on Burger 1", ""),
        ("Cook 3", None, "", "", ""),
        ("Chip 2", "Nadia A.", "06:00&ndash;14:30", "30 min taken", "done"),
    ]),
    ("Delivery and support", "#1a6042", [
        ("Delivery", "Mia T.", "From 19:00", "Moves off L2 QT", ""),
        ("Floor support", "Nadia A.", "Until 14:30", "", ""),
    ]),
]


def timeclock():
    cols = []
    for lane, swatch, posts in LANES:
        filled = sum(1 for post in posts if post[1])
        rows = []
        for station, who, when, brk, bstate in posts:
            if not who:
                rows.append(
                    '<div class="p-post gap"><div class="p-grow"><b>' + station + '</b>'
                    '<span>Nobody on this station</span></div>'
                    '<button class="p-btn p-btn-secondary p-btn-sm">Assign</button></div>')
                continue
            chip = '<span class="p-brk ' + bstate + '">' + brk + '</span>' if brk else ""
            rows.append(
                '<div class="p-post"><div class="p-grow"><b>' + station + '</b>'
                '<span>' + who + ' &middot; ' + when + '</span></div>' + chip + '</div>')
        cols.append(
            '<div class="p-lane"><div class="p-lane-head"><i style="background:' + swatch + '"></i>'
            + lane + '<span class="p-count">' + str(filled) + ' of ' + str(len(posts))
            + '</span></div>' + "".join(rows) + '</div>')

    body = (
        '<div class="p-work">'
        '<div class="p-work-head">'
        '<h1>Deployment, Wednesday 6 November</h1>'
        '<div class="p-spacer"></div>'
        '<div class="p-counters">'
        '<span class="p-counter ok"><b>9</b> on shift</span>'
        '<span class="p-counter quiet"><b>2</b> on a break</span>'
        '<span class="p-counter should"><b>2</b> due a break</span>'
        '<span class="p-counter must"><b>0</b> late</span>'
        '</div>'
        '<button class="p-btn p-btn-secondary p-btn-sm">Print for the wall</button>'
        '<button class="p-btn p-btn-primary p-btn-sm">Rotate stations</button>'
        '</div>'
        '<p class="p-work-sub">Built from the published roster and editable here on the floor. '
        'Before this, the chart was copied out by hand onto a laminated sheet once or twice a day, '
        'with break times pencilled in beside each name.</p>'
        '<div class="p-board">' + "".join(cols) + '</div>'
        '<div class="p-card" style="margin-top:20px">'
        '<div class="p-card-head"><h3>Breaks as a clock, rather than as a warning list</h3>'
        '<span class="p-meta">Updates every minute</span></div>'
        '<div class="p-card-body"><div class="p-figs">'
        '<div class="p-fig live"><div class="p-fig-l">Natalia F., 30 minute meal break</div>'
        '<div class="p-fig-v">due in 12 min</div>'
        '<div class="p-fig-d">Has to start before 13:15 to stay inside the agreement</div></div>'
        '<div class="p-fig live"><div class="p-fig-l">Chiara B., 30 minute meal break</div>'
        '<div class="p-fig-v">due in 41 min</div>'
        '<div class="p-fig-d">Her finish moved to 23:30, so this moved with it</div></div>'
        '<div class="p-fig"><div class="p-fig-l">Jaxon R., 10 minute rest pause</div>'
        '<div class="p-fig-v">at 18:00</div>'
        '<div class="p-fig-d">He is told on his phone, not only the manager</div></div>'
        '</div></div></div>'
        '</div>')
    return shell("Time clock, the deployment board", "Time and attendance", body, who="NA")


# ------------------------------------------------------------ labour on shift
CHART = '''<svg class="p-chart" viewBox="0 0 720 262" role="img" aria-label="Sales by hour as columns with labour worked drawn solid to the current hour and labour forecast drawn dashed beyond it">
  <g class="grid"><line x1="52" y1="20" x2="704" y2="20"/><line x1="52" y1="68" x2="704" y2="68"/><line x1="52" y1="116" x2="704" y2="116"/><line x1="52" y1="164" x2="704" y2="164"/></g>
  <text x="44" y="24" text-anchor="end">$600</text><text x="44" y="120" text-anchor="end">$300</text><text x="44" y="216" text-anchor="end">$0</text>
  <rect x="62" y="180" width="34" height="32" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)"/>
  <rect x="110" y="158" width="34" height="54" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)"/>
  <rect x="158" y="120" width="34" height="92" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)"/>
  <rect x="206" y="74" width="34" height="138" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)"/>
  <rect x="254" y="52" width="34" height="160" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)"/>
  <rect x="302" y="86" width="34" height="126" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)"/>
  <rect x="350" y="132" width="34" height="80" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <rect x="398" y="146" width="34" height="66" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <rect x="446" y="128" width="34" height="84" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <rect x="494" y="70" width="34" height="142" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <rect x="542" y="44" width="34" height="168" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <rect x="590" y="92" width="34" height="120" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <rect x="638" y="150" width="34" height="62" fill="var(--p-w-shift-bg)" stroke="var(--p-w-shift-line)" opacity=".4"/>
  <polyline points="79,186 127,166 175,130 223,88 271,66 319,98" fill="none" stroke="var(--p-w-actual)" stroke-width="2.5"/>
  <polyline points="319,98 367,140 415,152 463,136 511,80 559,56 607,102 655,158" fill="none" stroke="var(--p-w-forecast)" stroke-width="2" stroke-dasharray="5 4"/>
  <line x1="336" y1="14" x2="336" y2="218" stroke="var(--p-brand)" stroke-width="1.5"/>
  <text x="342" y="26" fill="var(--p-brand)" font-weight="600">now, 13:04</text>
  <g class="axis"><line x1="52" y1="212" x2="704" y2="212"/></g>
  <text x="79" y="232" text-anchor="middle">7am</text><text x="175" y="232" text-anchor="middle">9</text>
  <text x="271" y="232" text-anchor="middle">11</text><text x="367" y="232" text-anchor="middle">1pm</text>
  <text x="463" y="232" text-anchor="middle">3</text><text x="559" y="232" text-anchor="middle">5</text>
  <text x="655" y="232" text-anchor="middle">7pm</text>
  <text x="378" y="254" text-anchor="middle">Hour of trading</text>
</svg>'''


def labour():
    body = (
        '<div class="p-work">'
        '<div class="p-work-head"><h1>Labour, right now</h1><div class="p-spacer"></div>'
        '<div class="p-where">Wed 6 Nov &middot; 13:04</div>'
        '<button class="p-btn p-btn-secondary p-btn-sm">This week</button>'
        '<button class="p-btn p-btn-secondary p-btn-sm">Send somebody home</button></div>'
        '<p class="p-work-sub">Hours count as they are worked rather than when a shift completes. '
        'That single change is the difference between a decision taken at 13:04 and a report read on Thursday.</p>'
        '<div class="p-card" style="padding:20px 24px 24px;margin-bottom:20px"><div class="p-figs">'
        '<div class="p-fig live"><div class="p-fig-l">Sales per labour hour</div><div class="p-fig-v">$71.40</div>'
        '<div class="p-fig-d">Target <b>$74.00</b> &middot; <span class="up">3.5% under</span></div></div>'
        '<div class="p-fig live"><div class="p-fig-l">Labour cost, today so far</div><div class="p-fig-v">$1,284</div>'
        '<div class="p-fig-d">Forecast to close at <b>$2,910</b> &middot; <span class="up">$118 over</span></div></div>'
        '<div class="p-fig live"><div class="p-fig-l">Hours worked, today</div><div class="p-fig-v">46.2</div>'
        '<div class="p-fig-d">Rostered <b>52.0</b> &middot; 5.8 still to come</div></div>'
        '<div class="p-fig"><div class="p-fig-l">Sales, today so far</div><div class="p-fig-v">$3,298</div>'
        '<div class="p-fig-d">Forecast <b>$3,410</b> &middot; <span class="down">3.3% behind</span></div></div>'
        '</div></div>'
        '<div class="p-grid p-grid-8-4"><div class="p-card">'
        '<div class="p-card-head"><h3>Today, by hour</h3>'
        '<span class="p-meta">Labour solid to now, dashed beyond it</span></div>'
        '<div class="p-card-body">' + CHART +
        '<div class="p-legend">'
        '<span><i style="background:var(--p-w-shift-bg);border:1px solid var(--p-w-shift-line)"></i>Sales by hour</span>'
        '<span><i style="background:var(--p-w-actual)"></i>Labour worked</span>'
        '<span><i style="background:var(--p-w-forecast)"></i>Labour forecast</span></div>'
        '</div></div>'
        '<div class="p-grid">'
        '<div class="p-card"><div class="p-card-head"><h3>What this replaced</h3></div><div class="p-card-body">'
        '<p class="p-meta">Managers kept their own spreadsheet. A tracker filled in each night with the store '
        'number, the week, last year&rsquo;s sales, the forecast, actual sales, transactions, hours rostered, '
        'hours used and the rate against target, all typed in by hand from two systems that disagreed with '
        'each other.</p>'
        '<p class="p-meta" style="margin-top:10px">Area coaches kept a second one, a workbook with a tab per '
        'measure, because nothing would report above a single restaurant.</p></div></div>'
        '<div class="p-card"><div class="p-card-head"><h3>The forecast, four weeks out</h3>'
        '<span class="p-badge p-badge-success">New</span></div><div class="p-card-body">'
        '<p class="p-meta" style="margin-bottom:10px">Three weeks were sent when four were needed, so the '
        'fourth week was rostered against nothing. The feed now carries four, and it arrives in minutes '
        'rather than on a two hour delay.</p>'
        '<div class="p-impact"><dl>'
        '<dt>Weeks of forecast available</dt><dd>4</dd>'
        '<dt>Age of the figures</dt><dd class="good">Under 2 min</dd>'
        '<dt class="tot">Was</dt><dd class="tot">3 weeks, 2 hrs old</dd>'
        '</dl></div></div></div>'
        '</div></div></div>')
    return shell("Labour, live on shift", "Reports", body, who="AN")


# --------------------------------------------------- reporting at every level
GROUP = [
    ("Northgate", "0731", "equity", "64", "6", "9.4%", "$71.40", "ok"),
    ("Riverside", "0412", "equity", "71", "4", "5.6%", "$76.10", "ok"),
    ("Parkway", "0588", "franchise", "58", "19", "32.8%", "$62.90", "bad"),
    ("Eastgate", "0244", "franchise", "66", "11", "16.7%", "$69.80", "warn"),
    ("Harbour", "0903", "equity", "49", "3", "6.1%", "$78.40", "ok"),
    ("Westfields", "0155", "franchise", "82", "24", "29.3%", "$64.20", "bad"),
    ("Southbank", "0677", "equity", "55", "5", "9.1%", "$73.10", "ok"),
]


def reports():
    rows = []
    for name, num, kind, shifts, issues, rate, sph, state in GROUP:
        badge = {"ok": "p-badge-success", "warn": "p-badge-warning", "bad": "p-badge-danger"}[state]
        word = {"ok": "In range", "warn": "Watch", "bad": "Needs a visit"}[state]
        rows.append(
            '<tr><td class="p-primary-cell">' + name + '<span class="p-sub">' + num + ' &middot; ' + kind +
            '</span></td><td class="p-num">' + shifts + '</td><td class="p-num">' + issues +
            '</td><td class="p-num">' + rate + '</td><td class="p-num">' + sph +
            '</td><td class="p-num">$74.00</td><td><span class="p-badge ' + badge + '">' + word +
            '</span></td></tr>')
    body = (
        '<div class="p-railed p-work"><div>'
        '<nav class="p-rail">'
        '<div class="p-rail-group"><span class="p-caps">Every week</span></div>'
        '<a href="#" aria-current="page">Compliance rate<span class="p-count">7 sites</span></a>'
        '<a href="#">Labour against forecast<span class="p-count">7 sites</span></a>'
        '<a href="#">Exception summary<span class="p-count">7 sites</span></a>'
        '<a href="#">Dismissals and reasons<span class="p-count">7 sites</span></a>'
        '<div class="p-rail-group"><span class="p-caps">Every pay period</span></div>'
        '<a href="#">Corrections raised</a>'
        '<a href="#">Make-up pay and overtime</a>'
        '<a href="#">Leave taken and accrued</a>'
        '<div class="p-rail-group"><span class="p-caps">On request</span></div>'
        '<a href="#">Punch history by person</a>'
        '<a href="#">Shared employees across sites</a>'
        '<a href="#" class="new">Deployment against plan</a>'
        '<a href="#" class="new">Break adherence</a>'
        '</nav>'
        '<div class="p-card" style="margin-top:16px">'
        '<div class="p-card-head"><h3>Sent to you</h3></div><div class="p-list">'
        '<div class="p-list-row"><div class="p-grow"><b>Monday, 07:00</b>'
        '<span class="p-sub">Compliance rate, your seven</span></div><span class="p-switch on"></span></div>'
        '<div class="p-list-row"><div class="p-grow"><b>Pay period close</b>'
        '<span class="p-sub">Corrections and dismissals</span></div><span class="p-switch on"></span></div>'
        '</div></div></div>'
        '<div>'
        '<div class="p-work-head"><h1>Compliance rate, week 45</h1><div class="p-spacer"></div>'
        '<div class="p-seg"><button>Restaurant</button><button aria-pressed="true">Area</button>'
        '<button>Group</button></div>'
        '<button class="p-btn p-btn-primary p-btn-sm">Download</button></div>'
        '<p class="p-work-sub">Issues divided by published shifts, every restaurant in the area, one table. '
        'This is the spot check an area coach used to do by opening each restaurant in turn and writing the '
        'numbers down.</p>'
        '<div class="p-grid p-grid-4" style="margin-bottom:18px">'
        '<div class="p-card p-stat"><div class="p-stat-label">Published shifts</div>'
        '<div class="p-stat-value">445</div><div class="p-stat-delta">across 7 restaurants</div></div>'
        '<div class="p-card p-stat p-stat-accent warning"><div class="p-stat-label">Issues raised</div>'
        '<div class="p-stat-value">72</div><div class="p-stat-delta"><span class="up">18 more</span> than week 44</div></div>'
        '<div class="p-card p-stat"><div class="p-stat-label">Compliance rate</div>'
        '<div class="p-stat-value">16.2%</div><div class="p-stat-delta">Two restaurants carry 60% of it</div></div>'
        '<div class="p-card p-stat p-stat-accent success"><div class="p-stat-label">Window</div>'
        '<div class="p-stat-value" style="font-size:var(--p-fs-5)">Any range</div>'
        '<div class="p-stat-delta">The thirty day cap is gone</div></div>'
        '</div>'
        '<div class="p-table-wrap"><table class="p-table"><thead><tr><th>Restaurant</th>'
        '<th class="p-num">Published</th><th class="p-num">Issues</th><th class="p-num">Rate</th>'
        '<th class="p-num">Sales per hour</th><th class="p-num">Target</th><th>State</th></tr></thead>'
        '<tbody>' + "".join(rows) + '</tbody></table>'
        '<div class="p-table-foot"><span>Seven restaurants, one row each. Two franchise sites carry most of '
        'the exceptions, which is a conversation about process rather than about rostering.</span></div>'
        '</div></div></div>')
    return shell("Reporting at every level", "Reports", body, who="SA",
                 where="<b>Area 12</b> &middot; 7 restaurants")


# ------------------------------------------ feature enablement, per restaurant
FEATURES = [
    ("Shift swap between team members",
     "A team member offers a shift, a qualified person picks it up, the manager approves", "on", "Area coach", "5 of 7"),
    ("Leave requests from the app",
     "Requests reach the rostering manager instead of a conversation at the pass", "on", "Area coach", "7 of 7"),
    ("Punch times visible to team members",
     "Clock in, clock out and break times on the person&rsquo;s own phone", "on", "Locked on", "7 of 7"),
    ("Break end alerts",
     "The person and the manager are both told, not only the manager", "on", "Area coach", "6 of 7"),
    ("In-app messaging",
     "One channel with read receipts, instead of five", "off", "Area coach", "2 of 7"),
    ("School calendar on minors",
     "Term dates enforced whenever somebody under 18 goes on the roster", "on", "Locked on", "7 of 7"),
    ("Deployment board on the time clock",
     "The station chart, generated from the published roster", "on", "Restaurant manager", "4 of 7"),
    ("Open shift offers across the area",
     "A dropped shift is offered to qualified people at nearby restaurants", "off", "Area coach", "0 of 7"),
]


def features():
    rows = []
    for name, why, state, who, where in FEATURES:
        sw = "p-switch on" if state == "on" else "p-switch"
        if who == "Locked on":
            sw = "p-switch on locked"
        rows.append(
            '<div class="p-togglerow"><div class="p-grow"><b>' + name + '</b><span>' + why + '</span></div>'
            '<span class="p-scope">' + who + '</span>'
            '<span class="p-meta" style="width:48px;text-align:right">' + where + '</span>'
            '<span class="' + sw + '"></span></div>')
    body = (
        '<div class="p-work">'
        '<div class="p-work-head"><h1>Features, by restaurant</h1><div class="p-spacer"></div>'
        '<button class="p-btn p-btn-secondary p-btn-sm">Compare all seven</button>'
        '<button class="p-btn p-btn-primary p-btn-sm">Apply the area baseline</button></div>'
        '<p class="p-work-sub">What is switched on, where, and who is allowed to change it. Restaurants inside '
        'one franchise group shared a single configuration, so a feature could not be turned on for one '
        'restaurant without turning it on for all of them.</p>'
        '<div class="p-grid p-grid-3" style="margin-bottom:20px">'
        '<div class="p-card p-stat p-stat-accent success"><div class="p-stat-label">On the area baseline</div>'
        '<div class="p-stat-value">6 / 8</div><div class="p-stat-delta">The two that are not are opt-in by design</div></div>'
        '<div class="p-card p-stat p-stat-accent warning"><div class="p-stat-label">Restaurants off the baseline</div>'
        '<div class="p-stat-value">3</div><div class="p-stat-delta">One franchise group, three sites, messaging off</div></div>'
        '<div class="p-card p-stat"><div class="p-stat-label">Changed in the last 90 days</div>'
        '<div class="p-stat-value">11</div><div class="p-stat-delta">Each one recorded with who and why</div></div>'
        '</div>'
        '<div class="p-card"><div class="p-card-head"><h3>Northgate &middot; 0731</h3>'
        '<span class="p-badge p-badge-success">Matches the area baseline</span></div>'
        + "".join(rows) + '</div>'
        '<p class="p-work-sub" style="margin-top:18px">The figure on the right is how many of the seven '
        'restaurants in this area have the feature on, so a manager can see whether they are the odd one out. '
        'That was the other half of the finding: people did not know which features existed, let alone which '
        'ones their neighbours were already using.</p>'
        '</div>')
    return shell("Features, by restaurant", "Compliance", body, who="SA",
                 where="<b>Area 12</b> &middot; 7 restaurants")


if __name__ == "__main__":
    write("timeclock-board.html", timeclock())
    write("labour-live.html", labour())
    write("reports-group.html", reports())
    write("features-console.html", features())
