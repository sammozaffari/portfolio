#!/usr/bin/env python3
"""The phone status bar, drawn once for every product.

Every phone screen showed 9:41 with a text label where the signal and battery
sit, and the time was earlier than the events on the screen below it. The time
now comes from the screen's own data and the right-hand cluster is the real
one: signal, wifi and battery as strokes in the current ink.
"""

ICONS = (
    '<span class="p-status-icons" aria-hidden="true">'
    '<svg viewBox="0 0 18 12" fill="currentColor"><rect x="0" y="8" width="3" height="4" rx="0.8"/>'
    '<rect x="5" y="5.5" width="3" height="6.5" rx="0.8"/><rect x="10" y="3" width="3" height="9" rx="0.8"/>'
    '<rect x="15" y="0" width="3" height="12" rx="0.8"/></svg>'
    '<svg viewBox="0 0 16 12" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">'
    '<path d="M1 4.2a10.5 10.5 0 0 1 14 0"/><path d="M3.6 6.9a6.6 6.6 0 0 1 8.8 0"/><path d="M6.2 9.5a2.8 2.8 0 0 1 3.6 0"/></svg>'
    '<svg viewBox="0 0 27 12" fill="none" stroke="currentColor" stroke-width="1.2"><rect x="0.6" y="0.6" width="22" height="10.8" rx="3"/>'
    '<rect x="2.6" y="2.6" width="16" height="6.8" rx="1.4" fill="currentColor" stroke="none"/>'
    '<path d="M24.6 4.2v3.6a1.8 1.8 0 0 0 0-3.6z" fill="currentColor" stroke="none"/></svg>'
    '</span>'
)


def status_bar(time, style=""):
    st = f' style="{style}"' if style else ""
    return f'<div class="p-status"{st}><span>{time}</span>{ICONS}</div>'
