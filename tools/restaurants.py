#!/usr/bin/env python3
"""The one list of fictional restaurants, codes and managers behind all three
products.

Riverside 0412 is the restaurant every product is built around, and it had a
different manager in each: one on the safety screens, one on the workforce
screens, one on the hiring screens, on a site that says the same manager uses
all three in the same week. Two codes also named different restaurants in
different products. Every builder imports from here and the safety checker
asserts the hand-written safety screens against it, so a name and a code mean
one place everywhere.

Nothing here is a real place. The names are common English words chosen so
they read as a restaurant and not as a suburb.
"""

# code: (name, restaurant manager)
RESTAURANTS = {
    "0402": ("Marketplace", "Isla F."),
    "0409": ("Station Street", "Wei Z."),
    "0412": ("Riverside", "Priya M."),
    "0415": ("Eastside", "Grace O."),
    "0418": ("Lakeside", "Ravi N."),
    "0421": ("Junction", "Nour R."),
    "0427": ("Parkside", "Hana S."),
    "0430": ("Bayview", "Marcus D."),
    "0433": ("Parkway", None),
    "0436": ("Harbourside", "Reuben B."),
    "0440": ("Hilltop", "Chloe W."),
    "0444": ("Airport", "Noah J."),
    "0448": ("Crossroads", "Leon P."),
    "0455": ("Fairwater", None),
    "0461": ("Harbour", None),
    "0478": ("Greenway", None),
    "0490": ("Stonebridge", None),
}
NAME_TO_CODE = {v[0]: k for k, v in RESTAURANTS.items()}

HOME = "0412"                                  # the restaurant every product opens on
HOME_NAME, HOME_MANAGER = RESTAURANTS[HOME]    # Riverside, Priya M.
ROSTERING_MANAGER = "Nadia A."                 # Riverside's assistant manager, who rosters

# The safety product's area: twelve restaurants under one area manager.
SAFETY_AREA = "Northern area"
SAFETY_AREA_MANAGER = "Felix K."
SAFETY_AREA_CODES = ["0436", "0421", "0448", "0412", "0415", "0409", "0427", "0430", "0402", "0418", "0440", "0444"]

# The workforce product's area: seven restaurants, mixed equity and franchise.
WORKFORCE_AREA_CODES = ["0412", "0418", "0433", "0455", "0461", "0478", "0490"]


def code_of(name):
    return NAME_TO_CODE[name]


def manager_of(code):
    return RESTAURANTS[code][1]
