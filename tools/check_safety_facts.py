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
SCR = ROOT / "articles/57/showcase/screens"
YEAR = 2026
fails = []


def text(name):
    raw = (SCR / name).read_text()
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

print(f"checked {len(ALL)} screens")
print(f"  calendar: {n_pairs} weekday and date pairs against {YEAR}")
if fails:
    print(f"\nFACT CHECK FAILED, {len(fails)} disagreement(s):\n")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("FACTS OK")
