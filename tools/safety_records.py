#!/usr/bin/env python3
"""The one records table behind the safety reporting screens.

The register, the manager's dashboard, the actions board, the fixes notice, the
incident record and the phone all show the same reports, and they disagreed:
one reference number named two different hazards, the dashboard counted eleven
reports beside a register that counted thirteen, and a report was one day
overdue on one screen and two on the next. The screens are hand-written HTML,
so they are not generated from this table; tools/check_safety_facts.py asserts
every screen against it instead, which is the same guarantee from the other
side: a screen that disagrees with this file fails the build.

Today on every screen is Wednesday 16 September 2026. Period 10 runs from
Monday 31 August.
"""
import datetime

TODAY = datetime.date(2026, 9, 16)
PERIOD_START = datetime.date(2026, 8, 31)
PERIOD = 10
RESTAURANT = "Riverside"
RESTAURANT_NO = "0412"
MANAGER = "Priya M."


def d(day, month=9):
    return datetime.date(2026, month, day)


# One row per report. Reporter None means the period audit raised it, which the
# notice counts separately from team reports. Actions are (title, due, status),
# status one of todo, progress, done, signoff, proposed.
RECORDS = [
    # open
    dict(ref="INC-0412-031", kind="Incident", title="Burn, oil splash while filtering", who="Jordan T.",
         area="Kitchen, fryer 2", reported=d(16), status="open",
         # the refit is the open action on HAZ-0412-112, linked here rather than
         # raised twice: one job, one board card, one close date
         actions=[("Refit the splash guard on fryer 2", d(12), "linked"),
                  ("Move oil filtering to after close", d(21), "proposed")]),
    dict(ref="HAZ-0412-118", kind="Hazard", title="Wet floor at the back door after deliveries", who="Mei L.",
         area="Back of house", reported=d(15), status="open",
         actions=[("Re-fix the anti-slip mat at the back door", d(15), "todo")]),
    dict(ref="HAZ-0412-117", kind="Hazard", title="Blocked fire exit, boxes from the dry store", who="Priya M.",
         area="Back of house", reported=d(14), status="open",
         actions=[("Clear the fire exit and mark a no-stack zone", d(16), "signoff")]),
    dict(ref="INC-0412-030", kind="Incident", title="Cut, opening cartons with a box cutter", who="Elias K.",
         area="Back of house", reported=d(12), status="open",
         actions=[("Swap box cutters for safety cutters at the carton station", d(19), "todo")]),
    dict(ref="HAZ-0412-114", kind="Hazard", title="Cool-room light flickering", who="Aiden R.",
         area="Back of house", reported=d(10), status="open",
         actions=[("Electrician booked for the cool-room light", d(17), "progress")]),
    dict(ref="HAZ-0412-112", kind="Hazard", title="Cracked splash guard on fryer 2", who="Jordan T.",
         area="Kitchen", reported=d(8), status="open",
         actions=[("Replace fryer 2 splash guard", d(12), "progress")]),
    # closed this period, from team reports
    dict(ref="HAZ-0412-116", kind="Hazard", title="Oil on the floor near fryer 2", who="Aiden R.",
         area="Kitchen", reported=d(1), status="closed", fixed=d(2),
         actions=[("Floor degreased and the filter trolley re-routed", d(2), "done")]),
    dict(ref="HAZ-0412-115", kind="Hazard", title="Drive-thru window latch loose", who="Aiden R.",
         area="Drive-thru", reported=d(31, 8), status="closed", fixed=d(6),
         actions=[("Drive-thru window latch repaired", d(6), "done")]),
    dict(ref="HAZ-0412-110", kind="Hazard", title="Cool-room door seal split", who="Mei L.",
         area="Back of house", reported=d(3), status="closed", fixed=d(8),
         actions=[("Cool-room door seal replaced", d(8), "done")]),
    dict(ref="HAZ-0412-108", kind="Hazard", title="Wet floor at the drive-thru pad", who="Jordan T.",
         area="Drive-thru", reported=d(4), status="closed", fixed=d(5),
         actions=[("Wet-floor signs added at the drive-thru pad", d(5), "done")]),
    dict(ref="HAZ-0412-107", kind="Hazard", title="Wet floor at the back door after deliveries", who="Mei L.",
         area="Back of house", reported=d(1), status="closed", fixed=d(1),
         actions=[("Anti-slip mat placed at the back door", d(1), "done")]),
    dict(ref="HAZ-0412-106", kind="Hazard", title="Burn gel missing from the kitchen first-aid kit", who="Jordan T.",
         area="Kitchen", reported=d(8), status="closed", fixed=d(10),
         actions=[("Burn gel stocked in the kitchen first-aid kit", d(10), "done")]),
    dict(ref="HAZ-0412-105", kind="Hazard", title="Loose floor tile at the front counter", who="Elias K.",
         area="Front counter", reported=d(2), status="closed", fixed=d(8),
         actions=[("Loose floor tile at the front counter re-set", d(8), "done")]),
    dict(ref="HAZ-0412-104", kind="Hazard", title="Delivery ramp lip", who="Aiden R.",
         area="Back of house", reported=d(7), status="closed", fixed=d(11),
         actions=[("Delivery ramp lip ground down", d(11), "done")]),
    # closed this period, from the period audit
    dict(ref="HAZ-0412-111", kind="Hazard", title="Fire extinguisher tags out of date", who=None,
         area="Front counter", reported=d(7), status="closed", fixed=d(11),
         actions=[("Fire extinguisher tags replaced", d(11), "done")]),
    dict(ref="HAZ-0412-113", kind="Hazard", title="Chemical store shelving unlabelled", who=None,
         area="Back of house", reported=d(9), status="closed", fixed=d(14),
         actions=[("Chemical store shelving re-labelled", d(14), "done")]),
]

OPEN = [r for r in RECORDS if r["status"] == "open"]
CLOSED = [r for r in RECORDS if r["status"] == "closed" and r["fixed"] >= PERIOD_START]
CLOSED_TEAM = [r for r in CLOSED if r["who"]]
CLOSED_AUDIT = [r for r in CLOSED if not r["who"]]
THIS_PERIOD = [r for r in RECORDS if r["who"] and r["reported"] >= PERIOD_START]   # reports, not audit checks
HAZARDS_THIS_PERIOD = [r for r in THIS_PERIOD if r["kind"] == "Hazard"]
INCIDENTS_THIS_PERIOD = [r for r in THIS_PERIOD if r["kind"] == "Incident"]
OVERDUE = [(r, a) for r in OPEN for a in r["actions"] if a[2] in ("todo", "progress") and a[1] < TODAY]
NEEDS_REVIEW = [r for r in OPEN if r["reported"] == TODAY or any(a[2] == "signoff" for a in r["actions"])]
OPEN_INCIDENTS = [r for r in OPEN if r["kind"] == "Incident"]
OPEN_HAZARDS = [r for r in OPEN if r["kind"] == "Hazard"]
BOARD_ACTIONS = [(r, a) for r in OPEN for a in r["actions"] if a[2] in ("todo", "progress", "signoff")]   # one card each


def days_late(a):
    return (TODAY - a[1]).days


def days_to_fix(r):
    return (r["fixed"] - r["reported"]).days


def median_days():
    xs = sorted(days_to_fix(r) for r in CLOSED)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def by_ref(ref):
    return next(r for r in RECORDS if r["ref"] == ref)
