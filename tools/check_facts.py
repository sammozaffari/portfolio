#!/usr/bin/env python3
"""Fail if a hero number is typed differently on two surfaces.

Each case carries articles/NN/facts.json. Every surface that states one of its
facts (the case's stat strip, the home page, the Work page, the showcase, the CV
and llms.txt) must state the number in facts.json, and every number in a case's
stat strip must be a fact. "Twelve personas" sat on three surfaces beside a
persona set of four; "eight projects" sat over seven cards.

Usage: check_facts.py
"""
import json, pathlib, re, html, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
fails = []
W = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 12: "twelve"}


def text(rel):
    s = (ROOT / rel).read_text(errors="ignore")
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def forms(n):
    return [str(n)] + ([W[n]] if n in W else [])


def want(rel, needles, why):
    t = text(rel)
    if not any(x in t for x in needles):
        fails.append(f"{rel}: expected one of {needles!r}\n    because {why}")


facts = {n: json.loads((ROOT / f"articles/{n}/facts.json").read_text()) for n in ("1", "2", "3", "4", "5", "6", "7")}

# 1. every number on a stat strip is a fact of that case
for n, f in facts.items():
    s = (ROOT / f"articles/{n}/index.html").read_text()
    m = re.search(r'<div class="art-stats">(.*?)</div>', s, re.S)
    if not m:
        continue
    strip = html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))
    nums = [int(x) for x in re.findall(r"\b(\d+)\b", strip) if int(x) not in (2024, 2025, 2026)]
    for x in nums:
        if x not in f.values():
            fails.append(f"articles/{n}/index.html: stat strip says {x}, which is not in facts.json")

# 1b. the lane count on a strip is the lane count of the blueprint table on the page
for n, f in facts.items():
    if "lanes" not in f:
        continue
    s = (ROOT / f"articles/{n}/index.html").read_text()
    # a failure-points row is a reading aid, not a lane
    lanes = len([m for m in re.findall(r'<tr class="lane"><td data-label="Stage / lane">([^<]*)', s) if "Failure" not in m])
    if lanes and lanes != f["lanes"]:
        fails.append(f"articles/{n}/index.html: the strip says {f['lanes']} lanes and the blueprint table draws {lanes}")

# 2. the surfaces that repeat a fact repeat it exactly
f57, f52, f55 = facts["1"], facts["2"], facts["3"]
S = ("index.html", "articles.html", "cv.html", "llms.txt")
want("index.html", [f"{f57['records']} insight records"], "the home panel quotes the record count")
want("index.html", [f"{f57['items']} items"], "the home panel quotes the blueprint item count")
want("index.html", [f"{W[f57['modules']]}-module", f"{f57['modules']}-module"], "the home panel names the safety module count")
want("index.html", [f"{f57['hours']} hours"], "the home panel quotes the estimated hours")
want("index.html", [f"{f52['pain_points']} pain points"], "the home panel quotes the pain-point count")
want("index.html", [f"{f52['responses']} field survey responses", f"{f52['responses']} survey responses"], "and the survey count")
want("index.html", [f"{W[f52['visits']]} restaurant visits".capitalize(), f"{W[f52['visits']]} restaurant visits"], "and the visit count")
want("index.html", [f"{W[f52['personas']]} personas"], "and the persona count")
want("index.html", [f"{W[f52['modules']]}-module"], "and the workforce module count")
want("index.html", [f"{W[f55['stages']]} stages"], "and the hiring stage count")
want("index.html", [f"{W[f55['candidate_screens']]} screens for the candidate, {W[f55['manager_screens']]} for the manager"], "and the split of hiring screens")
want("index.html", [f"answer within {W[f55['answer_days']]} days"], "and the disposition promise")
want("articles.html", [f"{f52['pain_points']} pain points"], "the Work card quotes the pain-point count")
want("articles.html", [f"{W[f55['stages']]} stages".capitalize(), f"{W[f55['stages']]} stages"], "the Work card quotes the hiring stage count")
want("cv.html", [f"{f57['interviews']} in-depth interviews"], "the CV quotes the safety interview count")
want("cv.html", [f"{f57['responses']}-response"], "and the safety survey count")
want("cv.html", [f"{f57['records']} linked records"], "and the record count")
want("cv.html", [f"{f52['responses']} survey responses"], "and the workforce survey count")
want("cv.html", [f"{f52['pain_points']} pain points"], "and the pain-point count")
want("cv.html", [f"{W[f55['stages']]}-stage"], "and the hiring stage count")
want("llms.txt", [f"{f52['pain_points']} pain points"], "llms.txt quotes the pain-point count")
want("llms.txt", [f"{f52['responses']} survey responses"], "and the survey count")
want("llms.txt", [f"{W[f52['modules']]}-module"], "and the workforce module count")
want("llms.txt", [f"{W[f57['modules']]}-module"], "and the safety module count")
want("llms.txt", [f"{W[f55['stages']]}-stage"], "and the hiring stage count")
for n, f in (("1", f57), ("2", f52), ("3", f55)):
    want(f"articles/{n}/showcase/index.html", [f"{W[f['modules']]} modules", f"{W[f['modules']].capitalize()} modules"], "the showcase names its module count")
want("articles/2/showcase/index.html", [f"{W[f52['personas']]} personas"], "the showcase quotes the persona count")
# the Work page headline count equals its card count
work = (ROOT / "articles.html").read_text()
cards = len(re.findall(r'<a class="pf-card"', work))
h1 = re.search(r"<h1>(.*?)</h1>", work).group(1)
if not h1.startswith(W.get(cards, str(cards)).capitalize()):
    fails.append(f"articles.html: the H1 says {h1!r} over {cards} cards")

if fails:
    print(f"FACTS ACROSS SURFACES FAILED, {len(fails)} disagreement(s):")
    for x in fails:
        print("  " + x)
    sys.exit(1)
print(f"FACTS ACROSS SURFACES OK: {sum(len(f) for f in facts.values())} facts checked on {len(S) + 3} surfaces, {cards} cards under {h1!r}")
