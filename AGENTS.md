# Working in this repository

This is a portfolio site. It is also the design system that the portfolio is arguing for,
so the gates below are part of the work, not overhead. Everything here fails the build
rather than warning.

## Before writing a component

Search `assets/product/components.manifest.json` first. It lists every class the design
system defines, generated from `assets/product/components.css` so it cannot drift. If a
component already exists, use it. If you need a new one, add it to `components.css` and
regenerate the manifest; the lint fails on any `p-` class used in a screen that is neither
in the manifest nor defined in that screen's own style block.

## Tokens

`assets/product/tokens.dtcg.json` is the source, written in the W3C Design Tokens
Community Group shape. `assets/product/tokens.css` is generated from it by
`tools/build_tokens.py`. Never edit the CSS directly: `tools/lint_site.py` runs
`build_tokens.py --check` and fails if the two are out of step.

There is one mode. The DTCG Resolver module is the agreed answer to theming and is still
a preview draft that says not to implement it, so this system does not pretend to have
modes it cannot build.

No raw colour values in a screen. Every colour, space, radius and duration comes from a
token.

## The gates

| Gate | Command | Fails on |
|---|---|---|
| Tokens in step | `tools/build_tokens.py --check` | CSS out of date with the DTCG source |
| Contrast | `tools/contrast_check.py` | Any text pair under 4.5:1, any control border under 3:1 |
| Component registry | `tools/lint_site.py` | A `p-` class that is not declared anywhere |
| Site content | `tools/lint_site.py` | Vendor names, wrong counts, broken local links, cropped artefacts, em dashes |
| Visual regression | `tools/visual_check.py` | A screen that has changed against its committed baseline |
| Side gutter | `tools/check_layout.py` | Any text under `main` within 16px of the window edge, or a page that scrolls sideways, at 390 and 1280 (pages are loaded in an iframe of that width, because headless Chrome will not lay out under about 500px) |
| Facts across surfaces | `tools/check_facts.py` | A hero number typed differently on the case, the home page, the Work page, the showcase, the CV or llms.txt; a Work headline that miscounts its cards; a stat-strip number missing from the case's facts.json |
| Safety facts | `tools/check_safety_facts.py` | A weekday that does not match its date in the safety screens, initials that do not match the name, a reference used for two records, counts that disagree between screens |
| Case graphics | `tools/check_graphics.py` | A label in a case graphic that overlaps another, crowds it, or comes within 6 units of the edge, measured in every state its toggles can reach |

Run `tools/lint_site.py` before you consider anything finished. The lint also holds the type rules: every font-size on a product screen is one of the `--p-fs-0` to `--p-fs-7` tokens, every font-size on a site page is one of the eight `--t-1` to `--t-8` steps in `style.css` (display headings may use `clamp()`), and nothing outside a code block sets `overflow-x` to auto or scroll.

## Case graphics

`tools/graphics/<name>.html` is the source of one animated plan-view graphic: its SVG, its
control bar, its caption and its script, all self-contained. `tools/build_graphics.py`
injects it into its case page between `<!-- graphic:name -->` markers, writes the standalone
page at `articles/N/graphics/<name>.html`, and writes the capture spec for its cover. Edit
the source, never the copy inside a case page, and never the standalone page.

`assets/motion.js` owns the clock. A graphic starts when it scrolls into view, stops when it
leaves, pauses on its button, and freezes to one composed frame under `prefers-reduced-motion`.
Add `?static=1` to a graphics page for that frozen frame, `&t=<seconds>` to pick the moment,
and `&set=host:0` to force a toggle. Covers are captured that way, so a cover cannot drift
from the graphic; `tools/check_fresh.py` hashes `motion.js` and `motion.css` into a graphics
capture, which means changing the runtime makes every cover stale until it is recaptured.

Two failures worth knowing. A CSS `opacity` on a class beats the `opacity` attribute a script
sets, so an element meant to be hidden stays visible. And a ReferenceError inside a draw loop
renders as a blank frame rather than an error, so run `tools/check_graphics.py` after editing:
it loads every graphic and would report nothing drawn.

## Capturing screens

`tools/capture.py manifest.json` renders a page to a 2x PNG. Two things about headless
Chrome are load-bearing: it lays out at about 500px minimum, so anything requested
narrower comes back as a cropped desktop layout rather than a phone view, and it writes
the PNG and then often fails to exit, so success is judged by the written file and the
process group is killed either way.

## Writing

Australian English. No em dashes. Nothing negative about Sam, and nothing that disclaims
the work. Never invent research, counts, quotations or outcomes; scale figures live in
`data-scale.json` and are propagated by `tools/apply_scale.py`.
