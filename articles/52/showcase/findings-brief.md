# Workforce platform findings report — consolidated brief

Source: the delivered Time and Attendance Findings Report (92 slides, 2 October 2024).
The vendor is never named. Systems are referred to generically:
the timekeeping platform, the forecasting system, the employee records system,
the payroll system, the recruitment system.

## Scale of the evidence
- 175 pain points typed and triaged
- 200 field survey responses (67% team member, 20% assistant restaurant manager, 12% shift supervisor, 1% restaurant general manager)
- Site visits to 6 franchise and 4 equity restaurants
- Above-restaurant interviews: a franchisee, 2 area coaches, payroll
- 5 personas: team member, rostering manager, area coach, payroll, support

## Pain point triage
| Cut | Share |
|---|---|
| Has a backlog item | 27% |
| Solvable by the platform, no backlog item | 38% |
| Not solvable by the platform | 23% |

Solution categories: Technology 41%, Education 26%, Integration 21%, Process change 11%, Other 1%.
Pain points by role: Area Coach 45, Rostering 42, RGM 35, team member 25, Payroll 11, Support 10, central 9.
Largest stage by volume: Schedule Management (~80), then Compensation and Reporting (high 20s).

## Eight lifecycle stages (the blueprint)
Onboarding · Access · Schedule Management · Compensation · Reporting ·
Transferring and sharing employees · Offboarding · Platform changes

## The eight insights

### 01 Compliance
The compliance warnings list is overwhelming and unmanageable, so managers ignore it.
- Break management: the break rule for 5 to 5.49 hour shifts is ambiguous; auto-fill breaks must be re-run by hand after a shift changes; breaks are hard to manage on extended or changed shifts and during busy periods.
- Minor employee protection: school calendar assignments are manual and not integrated; most managers do not know the school calendar feature exists.
- Role-based compliance: deployment options do not align to job role, so a team member can be rostered to shift supervisor without the training or the right pay; the platform cannot recognise a future job role change; compliance across locations for shared employees is hard to manage.
- Pay period management: reopening a pay period is long and difficult; manual pay adjustments cause non-compliant workarounds; some groups refuse to reopen at all; corrections made in payroll do not reflect back.

Quotes:
- "So say someone was scheduled to work a three-and-a-half-hour shift, therefore no breaks required. But then as the shift is progressing, the manager asks, 'Can you stay back?' They say, 'Sure, no worries. I'll stay back for an hour.' They are now entitled to a 10-minute rest pause, but nothing is going to flag to say they need that 10-minute rest pause."
- "Whenever I do a compliance check, I have to open up the exception report, then open up the platform. I check the week, see how many shifts are published, and divide the number of compliance issues I get. It's not difficult, but it's time-consuming."
- "The compliance warnings list is overwhelming and results in managers not actioning issues."

### 02 Lack of standardisation
No standard baseline of enabled features across the business.
- Feature enablement: critical features (shift swaps, communication) are configured differently per location; managers do not know what is available; area coaches cannot enable a feature for a single restaurant inside a larger franchise group.
- Communication: WhatsApp, text, email, Yammer and the platform chat all in use; the platform chat is underused because push notifications do not arrive.
- Process variations: inconsistent payroll processes, leave management and shift planning between franchises.
- Training: resources and knowledge transfer vary by location; updates and new features are not communicated.

Quotes:
- "We haven't used the platform chat. We mainly use WhatsApp for communication. The notifications weren't actually coming through for anyone, so it became super hard to keep track of. It was just easier to stick to something else."
- "No standardisation of features across the business... Education: clearly publish the configurable options so managers know what configurable options are available to them."

### 03 Integration and forecasting
- All forecasting is done in the forecasting system first, with a two-hour delay before the data reaches the timekeeping platform.
- Head office sends three weeks of forecast when managers need four.
- No live sales per hour; hours are not counted as worked until the shift completes, so there is no running labour figure on shift.
- Managers and area coaches maintain their own Excel KPI trackers and labour reports.
- New employees are set up separately in several systems; employee IDs are passed by hand; pay rate changes can take 14 days; training completions are slow to appear.

Quotes:
- "It doesn't count hours as worked until the shift is completed. I can't see why that's such a big drama to fix. I mean, technically it's how most systems work. But they can also do a running calculation."
- "The payroll team do have their own labour report, but there seems to be a disconnect somewhere. The figures payroll sends me are not the figures that I see in the platform."
- "Head office only sends three weeks' worth of forecast, which I've always had an issue with. I wish it was four weeks."

Artefacts photographed: a KPI Tracker spreadsheet filled in nightly, and an Equity Labour Report pivot workbook with tabs for Rate, Hours, MGT Hours, $ vs TGT, % vs TGT, Underutilised hours, TM Overtime $, Overtime Rate.

### 04 Preference for flexibility
- Managers prefer to deploy people to stations in real time rather than roster by role.
- Deployment charts are transcribed by hand from the roster once or twice a day: a spiral-bound duty log, a laminated station chart with columns Name / Shift / 10 min / 30 min / Station and stations Expo 1, L1 QT, Money Taker, Burger 1, Pack 1, Cooks, Expo 2, L2 QT, Checker, Burger 2, Pack 2, Chip 2, Delivery.
- A custom management roster is kept in Excel because the platform's is hard to read.
- No place to record a team member's skills.

Quotes:
- "Make the platform auto generate a deployment chart that they can fill out manually and change."
- "Above our time clock, we have a whiteboard that shows who needs rest breaks more clearly. We write the deployment on the whiteboard, showing start and finish times, and whether they need a 10-minute or 30-minute break."
- "We use the platform's deployment as a guide... But for specific stations, I leave it up to the team to figure out where they want to have people."

### 05 Reporting
- Managers do not know which reports exist or which are useful.
- Reports are per restaurant; area and group figures are compiled by hand.
- Reports are capped at a 30-day window.
- Custom spreadsheets fill the gap.

Quotes:
- "The data that we find hard to get is all segregated by stores, where with another rostering system, we can pull one report for all stores that we have."
- "Reports are pulled at a restaurant level and have to be aggregated manually for an area/org level."
- "Can only generate reports for a 30-day time period... I would love for it to be a much longer, unlimited time frame."
- "I personally haven't had to generate a report in the platform for quite some time."

### 06 Lack of team member visibility
- No punch times in the mobile app and no clock in/out history.
- No view of elapsed break time and no notification when a break should end.
- Two break types (10 minute and 30 minute) are hard to track.
- Leave balance updates only at the pay run.
- No visibility of pending leave request status, of who the manager on a shift is, or of coworker schedules.

Quotes:
- "We've heard team members saying they want to see how much time they have left on their break. A few times they've walked back in saying, 'Oh, I've got another five minutes.'"
- "Yeah, you're one of the few people who thinks that not being able to see your punch times is an issue. I've thought that's an issue from the beginning."
- "I wish I could see my expected pay and also my leave balance after every shift."
- "I wish I could see an accurate representation of how much leave a team member actually has. I sometimes make mistakes when approving leave because I approve a leave shift for a team member who actually doesn't have those hours accrued to use."

### 07 Leave management
- A leave shift must be created by hand after approval, one shift at a time; a year of parental leave is entered shift by shift.
- No automatic leave when a part-time employee drops a shift, so the manager gets a compliance warning for not meeting contracted hours.
- Consent is not captured when leave is entered on a team member's behalf.
- Leave balances are not real time and payroll absorbs the enquiry load.
- Reopening a pay period is long and difficult.

Quotes:
- "If someone is taking a week of leave, they have to go in and enter every shift of leave for their time off, which is painful for them."
- "Especially if someone's off a month or six weeks, or if someone was going to go on maternity leave for a year, they have to put in those shifts manually."
- "When a part-timer drops a shift, I feel like there should be an option to mark it as leave with or without pay."
- "It's frustrating when you think you're doing well all week, and then you check your compliance and suddenly you've got warnings for people not meeting their hours because of their part-time contract."

Platform warnings seen on screen: "Part time employees rostered to work less than their guaranteed minimum hours per week will be paid makeup pay. $32.23 (2.5 hrs)" and "Part time employee working more than their scheduled hours will be paid overtime."

### 08 Payroll workarounds
- Restaurant general managers add missed pay as empty shifts in the next week to avoid reopening the pay period, which creates overtime and compliance pay and breaks part-timers' contracted hours.
- Compliance warnings are dismissed without investigation, with no documentation and no oversight of the dismissal.
- Corrections by email are missed.

Quotes:
- "We don't reopen pay periods. If there was a problem, then they would be fixing it in the next pay cycle. RGMs are adding missed pay as empty shifts in the next pay cycle, creating problems for part-timers."
- "But it's also really important for us to pay in the pay period as much as we can that it's due, because it actually affects other things like child support payments, Centrelink benefits, et cetera."
- "You need to log a ticket and take note of what needs to be done. We'd reopen the pay period and go back to the shift. It's a long process, but I'd rather it be done properly than have it come back to bite me later doing a workaround."

## The top ten prioritised tickets (the delivered plan)
Category counts: Tech 3, Experience 16, Compliance 10.

| Rank | Ticket | Category | Release |
|---|---|---|---|
| 1 | Soft warning on 5 hour shifts | Compliance | 1.63, November 2024 |
| 2 | Hard stop on shift supervisor breaks | Compliance | 1.63, November 2024 |
| 9 | Time off shift history | Compliance | 1.63, November 2024 |
| 3 | Manager breaks auto-wizard | Compliance | 1.64, 2025 |
| 4 | Reporting at multiple levels | Experience | 1.64, 2025 |
| 6 | Auto-populate leave on the schedule | Compliance | 1.64, 2025 |
| 7 | Ability to change a shift to a leave shift | Compliance | 1.64, 2025 |
| 8 | Consent workflow for leave | Compliance | 1.64, 2025 |
| 5 | Shared employee punches and leave visible | Compliance | pending confirmation |
| 10 | Leave shifts on the mobile shift list | Experience | pending confirmation |

## The roadmaps
2024, August to January: compliance lane carried cross-schedule compliance, the labour dashboard,
the pay-period reopening review, the shift supervisor break hard stop, the 5 to 5.5 hour shift
warning and time off shift history. Experience lane carried the blueprint and platform
standardisation. Tech lane carried single sign-on, the data and architecture review and the user
management review. A change freeze covered mid-December to January. Comms ran the whole length,
with three user-group milestones.

2025 draft, February to July: pay period reopening process review, labour dashboard, leave
management tickets, reporting at multiple levels, compliance and deactivation reports, a new
enterprise agreement from June. Ongoing: platform standardisation, labour modelling, forecasting
and live sales data development. Tech: the API and data architecture review. A change freeze
gates the start.

## Other named backlog items
- Soft constraint for 5 to 5.49 hour shifts
- Automatically refresh the compliance rules when the timekeeping screen is loaded
- Cross schedule compliance: shared employees and cross state employees
- Ability to perform or reopen pay period adjustments directly in the platform
- Leave management: auto populate in schedule and timekeeping
- Leave: consent workflow for leave and reporting
- Compliance pay dismissal mitigation
- Time clock: deployment plan view for the day
- Reporting at multiple levels
- Break end alerts and notifications on mobile

---

# The incumbent platform, studied before anything was drawn

Working notes. The vendor is never named, on this page or anywhere else. What
follows was assembled from the product's own public web shell and its published
feature list, its app store listings and screenshots, its help material and its
marketing stylesheet. It matters because a successor has to be recognisably the
same job, not a different product with the same nouns.

## What it does
Nine modules, in the vendor's own grouping: people, forecasting, scheduling,
compliance, time clock, timekeeping, reporting, pay, and one app for employees
and managers. Forecasting produces required headcount by workstation across the
trading day. Scheduling assigns people to roles and intervals against cost and
service targets. The time clock is a fixed terminal, offline capable. Pay
detects compliance and premium pay and hands off to a payroll system.

## Three visual systems, not one
The marketing site, the web product and the time clock terminal share almost
nothing: different typefaces, different palettes, different corner radii. The
product itself is mid-migration between two front ends, so old and new pages sit
beside each other. A successor has to tolerate that rather than pretend it away.

## What is genuinely good, and was kept
- **Density is the character.** The screens managers live in are ten and twelve
  column tables. Trading density for whitespace would be rejected by the people
  who use it, so the roster and the pay period here stay dense.
- **Compliance is priced.** Warnings carry a dollar figure. That is the single
  best idea in the product and it is carried through every screen here, on the
  roster chip, the compliance row, the dropped shift and the correction.
- **Workstation colour is the organising device.** Lanes and stations get
  consistent hues across the forecast, the roster and the deployment chart.
- **The terminal is designed for a kitchen**, with near-black high contrast
  buttons for a greasy touchscreen, which is a serious piece of thinking.

## What was deliberately changed
- **Colour carries severity, not category.** In the incumbent, status colour
  floods whole cards and every category has its own hue, including a distinct
  colour for young-worker breaches. That is why a list of sixty warnings reads
  as sixty alerts. Here a shift is grey unless something is wrong with it.
- **Numbers align right.** Numeric columns in the incumbent are left aligned,
  which is unusual for anything finance adjacent and makes a column of figures
  hard to compare.
- **Contrast is a build gate.** The incumbent publishes no accessibility
  statement, and its 10px uppercase table headers and near-black-on-red cards
  are legibility risks. Every text pair here clears 4.5 to 1 and every border
  3 to 1, checked by a script before a screen is captured.
- **The icons are drawn, not borrowed.** The incumbent uses a stock icon font
  throughout, which is why its iconography reads as generic.

## Capability gaps that the findings independently confirmed
Each of these is absent from everything about the product that can be reached
publicly, and each matches a pain point the research found in the restaurants.
1. **No intra-shift deployment or positioning board.** The restaurants filled
   the gap with laminated paper.
2. **No named interpretation of the Australian agreement**, penalty rates or
   allowances. This is the largest gap against the product's own home market,
   and it is the direct cause of the five to five and a half hour break question.
3. **No leave accrual or balance engine.** Time off requests exist; a balance
   that is true today does not.
4. **No multi-site or district rollup.** Everything observable is single store,
   which is why area coaches keep their own workbooks.
5. **No mobile punching.** Punching is terminal only, which is why there is a
   queue at changeover.
6. **No scheduled report delivery or named export formats.**
7. **No certification or right-to-work expiry tracking**, including permits for
   working with minors.
8. **No cross-site open shift pool**, so a call-out cannot be covered from a
   nearby restaurant.

## One thing to be careful about in the case study
The findings report records a stakeholder validation session and three user
group milestones on the 2024 roadmap. It does not record usability testing of
any of these features. Say validated with the user group, which is true. Do not
say tested with users, which is not.
