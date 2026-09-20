#!/usr/bin/env python3
"""The one set of facts behind every hiring and onboarding screen.

Both builders read from here, and tools/check_hiring_facts.py asserts against
here, so a figure cannot say one thing on the candidate's phone and another on
the manager's screen. That failure has already happened twice on this site: a
fryer guard that was fixed and overdue at the same time, and a crew app showing
a correction raised eight days in its own future.

Two rules this module exists to enforce.

Chronology. Every screen carries the day it is being looked at, and nothing on
it may come from after that day. The dates below are real weekdays in November
2024 and are ordered application, consent, interview, offer, work rights,
first shift.

Pay. The adult Level 1 rate under the Fast Food Industry Award for 2024 is
$25.65 an hour. Tia is sixteen, so she is on the junior rate, which is a stated
percentage of that adult rate rather than a number that appears from nowhere.
Publishing a rate below the adult minimum with no explanation is what went
wrong on the workforce screens.
"""

# --------------------------------------------------------------- the people
# Six, and no more. Every other first name on this site is taken, and two of
# them were close enough to each other to read as a typo before today.
CAST = {
    "tia":    {"name": "Tia M.",    "first": "Tia",    "initials": "TM",
               "role": "Candidate, first job", "age": 16},
    "nina":   {"name": "Nina M.",   "first": "Nina",   "initials": "NM",
               "role": "Parent or guardian"},
    "keira":  {"name": "Keira B.",  "first": "Keira",  "initials": "KB",
               "role": "Restaurant manager"},
    "vikram": {"name": "Vikram S.", "first": "Vikram", "initials": "VS",
               "role": "Payroll administrator"},
    "otis":   {"name": "Otis D.",   "first": "Otis",   "initials": "OD",
               "role": "Candidate", "age": 24},
}
ASSISTANT = "Ollie"          # a product, not a person, and not its real name

RESTAURANT = "Riverside"
RESTAURANT_NO = "0412"
SECOND_RESTAURANT = "Lakeside"

# ----------------------------------------------------------------- the money
ADULT_RATE = 25.65           # Fast Food Industry Award, Level 1, adult, 2024
JUNIOR_PCT = {16: 0.50, 17: 0.60, 18: 0.70, 19: 0.85, 20: 1.00}


def rate_for(age):
    """The hourly rate for an age, as a percentage of the adult rate.

    Returned rounded to the cent the way a payslip rounds it, half up, because
    16 lands on exactly half a cent and Python's default would take it down.
    """
    pct = JUNIOR_PCT.get(age, 1.00)
    cents = int(ADULT_RATE * pct * 100 + 0.5)
    return cents / 100.0


TIA_RATE = rate_for(16)      # $12.83
OTIS_RATE = rate_for(24)     # $25.65

# ------------------------------------------------------------------ the days
# Real weekdays in November 2024, in the order the service happens.
DAYS = {
    "apply":     ("Mon 4 Nov",  "Monday 4 November"),
    "consent":   ("Mon 4 Nov",  "Monday 4 November"),
    "interview": ("Thu 7 Nov",  "Thursday 7 November"),
    "offer":     ("Fri 8 Nov",  "Friday 8 November"),
    "rights":    ("Sat 9 Nov",  "Saturday 9 November"),
    "before":    ("Mon 11 Nov", "Monday 11 November"),
    "start":     ("Tue 12 Nov", "Tuesday 12 November"),
}
ORDER = ["apply", "consent", "interview", "offer", "rights", "before", "start"]

# The day each screen is being looked at. check_hiring_facts asserts that no
# screen mentions a date later than its own.
SCREEN_DAY = {
    "find":        "apply",
    "questions":   "apply",
    "consent":     "consent",
    "book":        "consent",
    "rights":      "rights",
    "offer":       "offer",
    "before":      "before",
    "pipeline":    "offer",
    "queue":       "offer",
    "humanlane":   "offer",
    "hero":        "offer",   # a composition of the queue screen
}

# Three screens are about something that has not happened yet, so they may name
# a later date: the slot picker offers times, the offer names a start day, and
# the day-before screen counts down to the first shift. Every other screen shows
# history and may not mention a date after its own.
SCREEN_MAX = {
    "book":   "offer",       # the last slot offered is Fri 8 Nov
    "offer":  "start",
    "before": "start",
}

# ------------------------------------------------------- the five questions
# Reduced from a multi-system form to the five that change a decision. Each one
# is asked as a question with tappable answers, because a sixteen year old on a
# phone should not be typing a date format into a field that rejects it.
QUESTIONS = [
    {"id": "age",   "ask": "First up, how old are you?",
     "chips": ["Under 16", "16", "17", "18 to 20", "21 or over"],
     "answer": "16",
     "why": "Sets the junior rate and the hours the law allows on a school night."},
    {"id": "rights", "ask": "Do you have the right to work in Australia?",
     "chips": ["Australian citizen", "Permanent resident", "Visa", "Not sure"],
     "answer": "Australian citizen",
     "why": "Decides which documents you will be asked for later, and nothing else."},
    {"id": "avail", "ask": "When can you work?",
     "chips": ["After school", "Weekends", "Weekdays", "Any time"],
     "answer": "After school and weekends",
     "why": "Matched against the shifts the restaurant is short of."},
    {"id": "shifts", "ask": "How many shifts a week suit you?",
     "chips": ["1", "2", "3", "4 or more"],
     "answer": "3",
     "why": "Sets the contract offered, so nobody is hired into hours they cannot do."},
    {"id": "peak",  "ask": "Could you do a Friday or Saturday night?",
     "chips": ["Friday", "Saturday", "Both", "Neither"],
     "answer": "Saturday",
     "why": "The one shift the restaurant is genuinely short of. It is asked last, not first."},
]

# Otis answered the same five. He falls outside the rule on the last question
# only, which is exactly why he is a decision and not a rejection.
OTIS_ANSWERS = ["21 or over", "Visa", "Weekdays", "4 or more", "Neither"]

# The rule that decides whether the conversation books an interview itself or
# hands the candidate to a person. Tia meets it. Otis does not.
AUTO_RULE = "available on a Friday or Saturday night and two or more shifts a week"

# ------------------------------------------------------------ the interview
INTERVIEW_SLOTS = [
    {"day": "Wed 6 Nov", "slots": [], "note": "Keira is on close, no interview times"},
    {"day": "Thu 7 Nov", "slots": ["3:30pm", "4:00pm", "4:30pm"], "picked": "4:00pm"},
    {"day": "Fri 8 Nov", "slots": ["10:00am", "10:30am"]},
]
INTERVIEW_WHERE = "The crew room, not a table in the dining room"

# ----------------------------------------------------------- the work rights
# Automated where it is safe, human where a wrong answer costs someone a job.
RIGHTS_CHECKS = [
    {"what": "Document is readable",        "how": "auto",  "state": "pass",
     "note": "Checked in a few seconds"},
    {"what": "Name matches your application", "how": "auto", "state": "pass",
     "note": "Tia M., matched"},
    {"what": "Date of birth matches",       "how": "auto",  "state": "pass",
     "note": "Sets your rate and your hours"},
    {"what": "Right to work confirmed",     "how": "auto",  "state": "pass",
     "note": "Australian citizen, no further check needed"},
    {"what": "Parent or guardian consent",  "how": "human", "state": "pass",
     "note": "Nina M. agreed on Mon 4 Nov, 6:48pm"},
]
# Otis, the case where the automated check cannot decide and a person must.
OTIS_CHECKS = [
    {"what": "Document is readable",        "how": "auto",  "state": "fail",
     "note": "Photo cut off at the edge"},
    {"what": "Visa conditions",             "how": "human", "state": "review",
     "note": "Student visa, 48 hours a fortnight, needs a person"},
]

# -------------------------------------------------------------- the pipeline
# A person is in exactly one stage. Tia's card carries her trail instead, so the
# board shows how fast she moved without putting her in four columns at once.
# Two candidates is what a single restaurant's week actually looks like; padding
# it with invented names would be a worse lie than an honest empty column.
PIPELINE = [
    ("Applied", [
        {"who": "otis", "waited": "2 days", "flag": "warn",
         "sub": "Work rights need a person, not a decision"},
    ]),
    ("Screened", []),
    ("Interview booked", []),
    ("Offer sent", [
        {"who": "tia", "waited": "1 day", "flag": "ok",
         "sub": "Sent Fri 8 Nov, 9:10am",
         "trail": "Applied Mon 4 &middot; screened same day &middot; interviewed Thu 7 Nov, 4:00pm"},
    ]),
    ("Accepted", []),
]
IN_PROGRESS = 2          # the count in the nav and in the counter pill
APPLY_TO_OFFER = "4 days"   # Tia, Mon 4 Nov to Fri 8 Nov

# Reminders and the promise that nobody is left waiting.
REMINDERS = ["24 hours", "48 hours", "72 hours"]
DISPOSITION_DAYS = 10
