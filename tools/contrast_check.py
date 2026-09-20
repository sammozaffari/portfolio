#!/usr/bin/env python3
"""Check WCAG contrast for the product tokens. Text pairs must reach 4.5:1, borders 3:1."""
import re, sys, pathlib

TOK = pathlib.Path(__file__).resolve().parent.parent / "assets/product/tokens.css"

def hex_to_rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def lum(rgb):
    def ch(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb); return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    la, lb = lum(hex_to_rgb(a)), lum(hex_to_rgb(b)); hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

tokens = dict(re.findall(r"(--p-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", TOK.read_text()))
TEXT = [  # (foreground, background, label)
    ("--p-ink", "--p-panel"), ("--p-ink-2", "--p-panel"), ("--p-ink-3", "--p-panel"),
    ("--p-ink", "--p-canvas"), ("--p-ink-2", "--p-canvas"), ("--p-ink-3", "--p-canvas"),
    ("--p-ink-3", "--p-panel-2"), ("--p-ink-on-sidebar", "--p-sidebar"), ("--p-ink-on-sidebar-2", "--p-sidebar"),
    ("--p-ink-inverse", "--p-brand"), ("--p-brand", "--p-panel"), ("--p-brand-ink", "--p-brand-quiet"), ("--p-brand-ink", "--p-panel"),
    ("--p-link", "--p-panel"),
    ("--p-danger", "--p-danger-bg"), ("--p-warning", "--p-warning-bg"), ("--p-success", "--p-success-bg"),
    ("--p-info", "--p-info-bg"), ("--p-neutral", "--p-neutral-bg"),
    ("--p-danger", "--p-panel"), ("--p-warning", "--p-panel"), ("--p-success", "--p-panel"), ("--p-info", "--p-panel"),
]
# the workforce product: a shift chip is read at a glance across a whole week,
# so its label has to clear 4.5:1 on its own ground, not only on white
TEXT += [
    ("--p-w-shift", "--p-w-shift-bg"), ("--p-w-shift", "--p-panel"),
    ("--p-w-open", "--p-w-open-bg"), ("--p-w-open", "--p-panel"),
    ("--p-w-overtime", "--p-w-overtime-bg"), ("--p-w-overtime", "--p-panel"),
    ("--p-w-break-risk", "--p-w-break-risk-bg"), ("--p-w-break-risk", "--p-panel"),
    ("--p-w-leave", "--p-w-leave-bg"), ("--p-w-leave", "--p-panel"),
    ("--p-w-training", "--p-w-training-bg"), ("--p-w-training", "--p-panel"),
    ("--p-w-actual", "--p-panel"),
]
BORDER = [("--p-line-strong", "--p-panel"), ("--p-line-strong", "--p-canvas"),
          ("--p-w-open-line", "--p-panel"), ("--p-w-open-line", "--p-canvas"),
          ("--p-w-forecast", "--p-panel")]
bad = 0
for fg, bg in TEXT:
    r = ratio(tokens[fg], tokens[bg]); ok = r >= 4.5
    bad += not ok; print(f"{'OK ' if ok else 'BAD'} {r:5.2f}  {fg} on {bg}")
for fg, bg in BORDER:
    r = ratio(tokens[fg], tokens[bg]); ok = r >= 3.0
    bad += not ok; print(f"{'OK ' if ok else 'BAD'} {r:5.2f}  border {fg} on {bg}")
print("CONTRAST", "FAILED" if bad else "OK"); sys.exit(1 if bad else 0)
