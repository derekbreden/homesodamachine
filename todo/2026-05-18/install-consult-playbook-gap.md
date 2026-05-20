# Founder Edition install consultation: the promised Zoom call has no script

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Siblings today:**
- [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) — post-delivery CO2 consumable supply
- [per-unit-portal-gap.md](per-unit-portal-gap.md) — `/u/NNN` customer-facing software service

**Related (added 2026-05-20):** before drafting the call script, read [`marketing/unboxing-and-quickstart.md`](../../marketing/unboxing-and-quickstart.md). The brief commits the customer to having a single flat quick-start sheet open in front of them during install. The Zoom script can refer to the sheet's nine numbered steps + line drawings rather than re-explaining each one verbally — that changes the call's structure, pacing, and whether it can land in one session or needs the two-session restructure described in [`todo/2026-05-20/first-pour-commissioning-gap.md`](../2026-05-20/first-pour-commissioning-gap.md) (the 60-90 min thermal pulldown is now also Step 8 on the printed sheet).

This todo is distinct from both: those cover the consumable side and the software-portal side of post-delivery ownership. This one is about the **founder-touch service** itself — the explicit Founder Edition deliverable that runs once per unit, between carrier handoff and "the first soda comes out the faucet."

## TL;DR

[marketing/target-market.md:13](../../marketing/target-market.md) and [target-market.md:92](../../marketing/target-market.md) both name **"a personal install consultation (phone or Zoom)"** as one of the three things a Founder Edition customer is buying at the $7,500 price (alongside the machine and a position in the first 50). The repo has:

- Zero specification of what the call covers
- No call agenda, no checklist, no script
- No pre-call prep playbook (what the founder reviews about the customer's kitchen, CO2 supply geography, etc.)
- No post-call follow-up schedule
- A **placeholder** install guide ([faucet-and-umbilical.md:127](../../hardware/assembly/faucet-and-umbilical.md): "`install-above-counter.md`, see Open items"), referenced by the install-kit pack-out in [finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md) but not written
- A **promised** "Founder Edition welcome letter on letterhead, hand-signed" ([finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md)) with no content draft
- No recording / archive convention for the calls (each call is currently a one-shot conversation that exits memory)
- No carve-out for the failure case ("what if the customer can't drill their countertop / doesn't have under-cabinet clearance / the existing plumbing won't accept the splitter")

This is the **white-glove deliverable** of the Founder Edition. The plaque (per-unit-portal sibling) and the integrated CO2 service (CO2 sibling) are downstream of it. The install consult is the moment the customer experiences "I bought from a person, not a brand" — or doesn't.

Solo build capacity is ~12 units/year. One install consult per unit = ~1/month, ~1–2 hours per call. This fits inside the founder's existing time budget; it does not fit inside it improvised.

## Why this matters at Founder Edition specifically

The trust-gap argument in [target-market.md:256–262](../../marketing/target-market.md):

> Between discovery ("wait, that's real?") and purchase ($7,500 from a company they've never heard of), there is an enormous trust gap. ... At Founder Edition scale, the answer to "is this a real product?" is not a brand — it's Derek. His face, his kitchen, his story.

The customer has already crossed that gap to buy. The install consultation is the **first** post-purchase moment where Derek-the-person delivers on what they bought. It is also the moment where confidence can be re-built or lost:

- Confidence built: the call is prepared, the founder knows the customer's kitchen photos, the CO2 supplier list is in their hand before they ask, the install runs in 45 minutes, soda comes out of the faucet at the end of the call.
- Confidence lost: the founder asks "so tell me about your kitchen," the customer realizes the call is improvised, the install hits a snag the founder doesn't recognize, the call ends with "let me look into that and get back to you."

The decade math in [target-market.md:131–134](../../marketing/target-market.md) — "this is not a new expense category. It is a format change for money the household is already spending, forever, on the same drink" — is a 10-year story. The install consult is the customer's first lived check on whether the 10-year story is real.

This is also the **lowest-cost moment to learn something** about the customer. Every Ring 1 install call is a chance to harvest a quote, a photo, a video clip, a kitchen layout pattern that the next ring's marketing and product work depends on. Without a recording convention, that data exits with the call.

## What's already locked in by upstream docs

Useful constraints to design against rather than re-litigate:

- **The customer has, in hand, before the call:** a signed plaque on the appliance ([nameplate/README.md](../../hardware/printed-parts/enclosure/nameplate/README.md)), the bagged faucet-and-umbilical sub-assembly ([faucet-and-umbilical.md:11](../../hardware/assembly/faucet-and-umbilical.md)), an install kit (line cord, foam segments, tube cutter, [bom.md §14](../../hardware/bom.md)), a printed quick-start install guide (placeholder), printed safety + regulatory inserts ([finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md)), and the Founder Edition welcome letter (placeholder).
- **The customer does NOT have:** CO2 (sibling todo, Open: maybe a primed cylinder ships in the box — [finish-pack-ship.md:111](../../hardware/assembly/finish-pack-ship.md) Open item), starter SodaStream concentrate pair (same Open item), a drilled countertop, an under-cabinet water-line splitter installed, an outlet under the cabinet, or a plan for where the appliance physically sits.
- **The install consult call is on the customer's calendar already.** Per the [target-market.md:91](../../marketing/target-market.md) framing, it's part of the purchase. Scheduling logistics are out of scope here — assume the call is booked.
- **The carrier-handoff email was already personal** ([finish-pack-ship.md:140](../../hardware/assembly/finish-pack-ship.md)) — `derek@homesodamachine.com`, named serial, rear-panel photo. That email is the call's natural lead-in: "your unit shipped Monday, arrives Thursday, our install call is Saturday morning."
- **The customer paid for "phone or Zoom."** Zoom is the better choice for almost every step here (the customer points their camera under the sink, the founder sees what they see), but a phone fallback has to exist for customers who can't or won't Zoom. The agenda below assumes Zoom unless noted.

## Specific gaps, sized for follow-up tickets

### I1 — Write the install consult call agenda (doc-only, do first)

A single canonical doc — call it `business/install-consult-playbook.md` — that captures the call's shape, in order. Three rough phases, ~90 minutes end-to-end:

**Phase A — pre-install survey (15 min, customer pointing the camera).** The customer has the appliance in the kitchen but not yet installed. Founder visually confirms:

- Cabinet under the kitchen sink: clear of obstructions on the rear and side walls (the airflow plenum, per [future.md:95](../../hardware/future.md)), a 120 V outlet reachable to the rear C14 inlet, an accessible cold-water shut-off, the existing under-counter plumbing layout (single-handle faucet, garbage disposal, dishwasher tee, etc.)
- Countertop above the sink: thickness, material (granite vs. quartz vs. laminate — each has a different drill-bit story), proposed faucet penetration location relative to existing fixtures, backsplash interference
- Where the CO2 cylinder will live (under the sink vs. in an adjacent cabinet — see also [co2-supply-ownership-gap.md C2](co2-supply-ownership-gap.md))
- Photographs the customer took of the cabinet during purchase (if any — Ring 1 customers might have been asked for these during the sale; this is itself an open ticket)

This phase **terminates the install attempt** if the cabinet is wrong for the appliance. Better to find this out in 15 minutes of Zoom than to have the customer drill their granite countertop, attempt the install, and call back. The founder should have an off-ramp: "let's not drill today, let's order you a [plumber referral / different splitter / cabinet shim], reschedule for next weekend."

**Phase B — guided install (45–60 min, customer doing the work).** Step-by-step, in the order the install guide ([I3](#i3--write-the-printed-install-guide-install-above-countermd)) prescribes:

1. Drill the countertop (the highest-stakes step; the founder watches and confirms bit, depth, hole location before the customer pulls the trigger)
2. Drop the faucet+umbilical assembly through the hole; slide the keyhole plate up from underneath; tighten the shank nut
3. Route the umbilical down to the rear-panel PTC bulkheads; cut to length with the Mudder cutter; push-to-connect (blue ring on the carbonated-water bulkhead per [back-panel/README.md](../../hardware/printed-parts/enclosure/back-panel/README.md))
4. Tap the cold-water line at the dishwasher tee (or install the appliance's own splitter — this is an open product decision); connect to the appliance's rear-panel water inlet
5. Connect the CO2 cylinder (per [pressure-vessel.md](../../hardware/assembly/pressure-vessel.md) "CO2 supply"); confirm the WR1110 in-appliance regulator is at the factory 90 PSI setpoint (visible on the customer-side primary regulator's low-side gauge)
6. Plug the C14 line cord; power on
7. Open the cold-water shut-off; watch the carbonator fill (the iOS app shows the fill progress per the level reeds, [future.md:37](../../hardware/future.md))
8. Wait for the refrigeration loop to pull the carbonator to ~2 °C (founder coaches the customer through the expected cycle time — 20–40 min is the working estimate, **this needs measurement on Ring 1 unit #1** before the call playbook claims a number)
9. Pour SodaStream concentrate into the hopper for both flavors; the firmware-controlled solenoid routes each pour to its reservoir
10. Turn the handle. Soda comes out.

The founder is watching for failure modes that don't fit on a printed install guide: a fitting that doesn't seat, a leak at the splitter, the carbonator that refuses to refill because the customer's static water pressure is too low for the SeaFlo pump's NPSH, the customer who tightens the shank nut so much they crack the printed plate.

**Phase C — first-pour debrief + 30-day forward look (15 min).** The customer has soda in their hand. The founder uses this moment, while the dopamine is fresh, to:

- Take a screenshot of the iOS app showing the active dispense (proof of working install, for the per-serial `logs/NNN/finish/` archive)
- Walk the customer through the iOS app's notification settings (CO2 low warnings tie to the [CO2 sibling C3](co2-supply-ownership-gap.md), water-side reed alerts, refrigeration faults)
- Hand off the CO2 supplier list the founder prepared (the three closest food-grade-CGA-320 fill points to the customer's ZIP — see [co2-supply-ownership-gap.md C4 "Better version"](co2-supply-ownership-gap.md))
- Set expectations for the first 30 days: refill expected at week N (estimate based on declared consumption), first clean cycle prompt in app at day N, founder will check back at day 7 and day 30 with one-line emails
- Ask the customer: would they record a 30-second pour video the founder can use as marketing? (This is **the** Ring 1 marketing-yield ask. It's free if requested in this moment, lost if requested two months later.)
- Tell the customer how to text the founder directly. The number, written down on the welcome letter. (See [I4](#i4--write-the-founder-edition-welcome-letter-content).)

Estimated effort: ~1 day to draft the playbook, ~1 day to refine it after the first Ring 1 install actually happens (it will be different than this guess in interesting ways).

### I2 — Write the pre-call prep checklist (doc-only, do first alongside I1)

The 30 minutes before the call. The founder is at their bench with the customer's order open. The checklist:

1. **Re-read the customer's purchase record.** Stated consumption (cans/day), household size, kitchen photos if any. What did they tell the founder at sale?
2. **Look up the customer's address against the CO2 supplier database.** Identify the three closest food-grade CGA-320 fill points (per the [CO2 sibling todo C4](co2-supply-ownership-gap.md)). Print or screenshot them to hand off in Phase C.
3. **Confirm the unit's serial.** Pull `logs/<serial>/` for the burn-in record (per [acceptance-and-burn-in.md](../../hardware/assembly/acceptance-and-burn-in.md), referenced from [finish-pack-ship.md:9](../../hardware/assembly/finish-pack-ship.md)). Know which unit is in front of the customer, what its burn-in showed, what its quirks (if any) were.
4. **Open the iOS app pre-bound to this customer's unit** ([per-unit-portal-gap.md U7](per-unit-portal-gap.md) FCM token binding mechanism — out of scope today, but the prep step depends on it once it exists). Pre-check that the unit is reachable from the cloud side; the worst time to find out the unit's Wi-Fi credential setup is broken is mid-call.
5. **Have the carrier delivery photo open** (the customer's doorbell cam or front-porch photo, if they shared one). It's a small thing but the founder asking "I saw it arrived Thursday morning, did the box look OK?" lands very differently than "did your appliance arrive."
6. **Have the welcome letter draft in front of the founder.** The letter ships in the box but the founder should know what's in it — the customer may reference it.

Estimated effort: ~half day to write the checklist + the underlying customer-record schema (purchase fields, kitchen photo attachments, etc., which is itself a small CRM gap — see [I7](#i7--the-customer-record-format-the-call-prep-reads-from)).

### I3 — Write the printed install guide (`install-above-counter.md`)

The placeholder named in [faucet-and-umbilical.md:127](../../hardware/assembly/faucet-and-umbilical.md). The customer reads this **before** the call (a sticker on the top of the install kit box: "open this first, read pages 1–4, then we'll get on the call together").

Scope (per [faucet-and-umbilical.md:127](../../hardware/assembly/faucet-and-umbilical.md)):

- Countertop drilling — recommended bit per material (granite: diamond core bit; quartz: same; laminate: hole saw), depth, location
- Drop-through-from-above sequence — the TPU gasket is already on the shank, customer does not install it
- Slide-the-keyhole-plate-laterally-onto-the-umbilical step — cylinders enter through the two open-edge channels and seat in their terminal pockets
- Washer + shank-nut tightening sequence (with torque guidance or "snug, then 1/4 turn" — not "as tight as you can")
- Blue-ring-into-blue-bulkhead rule at the rear panel (cold dispense line, the only color-coded one)
- Umbilical trim step at the rear-panel end — measure twice, cut once with the Mudder cutter, push-to-connect into the PTC bulkhead, confirm by gentle tug-test
- Cold-water line tap at dishwasher tee (or appliance's own splitter — open product decision)
- CO2 cylinder connection sequence — paired with the printed CO2 supplier list per [I2](#i2--write-the-pre-call-prep-checklist-doc-only-do-first-alongside-i1) handoff
- First-pour walkthrough and "what does failure look like at each step"

This doc is the customer's reference if the call is somehow missed (technical glitch, schedule conflict, founder unavailable). It is also the **content backbone** of the call agenda in [I1](#i1--write-the-install-consult-call-agenda-doc-only-do-first): the call walks through this doc step by step.

Should include photos. The current repo has [docs/photos/](../../docs/photos/) — assume those will be re-shot purpose-built for this guide once it's drafted. The text comes first.

Estimated effort: ~2 days for the first draft, more for the photography pass after the first Ring 1 install is done.

### I4 — Write the Founder Edition welcome letter content

[finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md) calls for "the Founder Edition welcome letter on letterhead, hand-signed." No draft exists.

The letter is one page. It should contain:

- **Thank you, personally.** The customer is one of 50 humans buying this in its first four years. The letter should say so, by their first name.
- **What this thing is**, in two paragraphs. The founder's voice, not marketing copy. "I built this because I was tired of hauling cans."
- **A direct phone number** — the founder's actual phone, with permission-to-text language. This is the white-glove SLA in physical form. (The Founder Edition story explicitly trades on founder-as-brand; the phone number is the substantive translation of that story.)
- **The QR code is on the plaque, not the letter**, but the letter should mention it: "scan the plaque on the rear of the unit to find your unit's page."
- **The hand-signed signature** — not a stamp, not a printed signature. This is the load-bearing word in "hand-signed by Derek" on the plaque-attestation page (see [per-unit-portal-gap.md U2](per-unit-portal-gap.md)).
- **A close that doesn't oversell.** The customer has already bought; the letter doesn't have to sell. It just has to feel like a person wrote it.

The letter does not include install instructions (those live in [I3](#i3--write-the-printed-install-guide-install-above-countermd)) or safety/regulatory text (those have their own inserts per [finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md)). The letter is single-purpose: this is the human standing behind the appliance.

Estimated effort: ~half day to draft, ~half day for the founder to revise into a voice they'd actually sign. This one is not work to delegate to an agent — the agent can scaffold; the founder writes.

### I5 — Establish the recording / archive convention for the calls

Each Founder Edition install consult is a 90-minute conversation with a Ring 1 customer about the product the founder is building. **It is the highest-density product-research signal in the entire post-launch life of the business**, and right now there is no plan to capture it.

Options, ranked:

- **Best:** Zoom recording (cloud, transcribed). Customer asked at the top of the call: "I'd love to record this so I can refer back to it and so future install playbooks get better — is that OK?" Most Ring 1 customers will say yes (they bought from this person, they're rooting for the product). The recording lives in `logs/<serial>/install/`, alongside the burn-in archive — both feed the per-unit portal ([per-unit-portal-gap.md U4](per-unit-portal-gap.md)) and the broader product-improvement loop.
- **Middle:** Audio-only phone recording (one-party consent in 38 US states; check the customer's state). Less rich, simpler legal stance.
- **Worst:** Founder takes notes during/after the call. What actually happens at solo build cadence is 80% of these notes never get written. This is the default failure mode, and it's why a doc that says "take notes" doesn't count as a recording plan.

The legal stance on recording needs a one-line check (notice + consent at the call's open is the standard answer, but two-party-consent states like California require the customer to consent on the recording itself). Worth a 30-minute consult with the [incorporation.md](../../business/incorporation.md) preparer when the LLC formation conversation happens, not a separate engagement.

The recordings are also the **content reservoir for Ring 2 marketing**. A 90-second clip of a real customer pouring their first soda is more powerful than any founder-only video. With explicit consent, this is shippable content.

Estimated effort: ~half day to write the recording policy + customer-facing consent script + the `logs/<serial>/install/` archive schema.

### I6 — Schedule the 7-day and 30-day post-install touchpoints

[target-market.md:269](../../marketing/target-market.md):

> What's the ongoing hassle? Syrup every few weeks (Amazon). CO2 every few months ... Cleaning automated from the app. Net: less hassle than the weekly store run.

The customer's first 30 days are when "less hassle than the weekly store run" gets validated or invalidated. The founder owns this validation at Ring 1.

Two scheduled touchpoints, both initiated by the founder, both short:

- **Day 7 — one-line email.** "How's the first week? Any surprises?" Targets the early hardware-failure window (a fitting that wasn't quite seated will leak in 4–7 days, not at first pour). Also a chance to surface anything the customer noticed but didn't want to call about.
- **Day 30 — one-paragraph email + ask.** "First month done. What does the appliance feel like in your kitchen now? Two questions: have you re-bought concentrate yet, and what's the CO2 cylinder pressure showing in the app?" Targets the consumption-baseline data ([CO2 sibling C5](co2-supply-ownership-gap.md)) and the "is the format-change story holding up" check.

Both should be templated (founder has a tighter version per Ring 1 customer) but personalized (named, referencing what the install call surfaced). 5 minutes to write each, ~10 minutes/customer/month — well inside solo capacity at 12 units/year.

Estimated effort: ~2 hours to draft both templates + the calendar mechanism (Google Calendar reminders against the customer's ship date is the cheap version; a small CRM table is the proper version — see [I7](#i7--the-customer-record-format-the-call-prep-reads-from)).

### I7 — The customer record format the call prep reads from

The [I2](#i2--write-the-pre-call-prep-checklist-doc-only-do-first-alongside-i1) prep step says "re-read the customer's purchase record." That record does not yet have a defined shape. Today, customer records for unit #1 will probably be Derek's gmail thread plus whatever they said on the sale call. That doesn't scale to unit #5, much less unit #50.

Minimum-viable customer record per unit:

- Name, shipping address, phone number, email
- Purchase date, payment method, payment confirmation reference
- Stated daily soda consumption + household size + flavor preference
- Kitchen photos shared during purchase (if any)
- Static water pressure at the kitchen tap, if reported (relevant to SeaFlo NPSH question, see [I1 Phase A](#i1--write-the-install-consult-call-agenda-doc-only-do-first))
- Where they heard about the appliance (Ring 1 attribution is critical data — see [target-market.md "Finding the first 10 buyers"](../../marketing/target-market.md))
- Linked artifacts: the burn-in run log path `logs/<serial>/`, the per-unit-portal `/u/NNN` route, the install-consult call recording

This is a CRM. At 12 customers/year for ~4 years, a flat-file `business/customers/<serial>.md` schema is sufficient — no SaaS, no database. Whether it lives in the public repo or a private side-repo is a privacy question (probably the latter; the public repo can hold the schema and a placeholder).

This is **the data backbone** for I2, I5, I6, the CO2 sibling's C4 (best version), and the per-unit-portal sibling's U3 (owner page). Worth defining once with all of those audiences in mind.

Estimated effort: ~1 day for the schema definition + a worked example + the private-vs-public decision capture.

### I8 — Define the install-can't-happen escape valve

A real failure mode the playbook needs an answer for: the install consult Phase A reveals that the customer's kitchen cannot accept the appliance as designed. Granite countertop the customer didn't realize they'd have to drill, under-counter water line in copper that needs a plumber to tap, a too-small cabinet, an unreachable outlet.

Today there is no documented response. The implicit one is "Derek improvises, probably promising more than the system can deliver."

Three documented branches:

- **Branch A — fix it locally.** Customer hires a plumber (or counter-fabricator, or electrician). Founder reschedules the call once the fix is in. Customer pays the trade out of pocket. Founder offers no reimbursement but offers to be on a follow-up Zoom with the trade pre-visit if useful.
- **Branch B — defer with a refund window.** Customer can return the appliance (carrier costs split? founder eats? open) and re-buy when the kitchen is ready. This is the only branch with a real money flow at risk; needs the warranty/return-policy doc to exist (also currently a repo gap — out of scope for this todo but flagged).
- **Branch C — abandon the install.** The kitchen will never accept the appliance; the customer keeps the unit as a (very expensive) showpiece, or it ships back. Rare in Ring 1 (the founder pre-screens for this) but possible. The Founder Edition framing has to handle it gracefully — a $7,500 customer who can't install their unit is the worst-case unhappy customer in the cohort.

This is doc-only work that intersects the (currently nonexistent) warranty/return policy. The escape-valve definition can ship without the full warranty doc, but the two should be drafted together when the warranty work happens.

Estimated effort: ~half day, blocked on the warranty/return-policy decision.

## Migration plan / order of operations

Same shape as the siblings — order matters:

1. **I1 + I2 today.** Write the call agenda + the pre-call prep checklist. Both are doc-only, both unblock the first Ring 1 install consult. ~1–2 days.
2. **I4 next.** Draft the welcome letter. It ships in every Founder Edition box ([finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md)) starting with unit #1, so the draft has to exist before the first finish-pack-ship bench session that produces a shippable unit. ~1 day to draft + revise.
3. **I3 before unit #1 ships.** The printed install guide. The customer reads it before the call, the call follows its structure. Without it, the call has no shared reference document. ~2 days for the text + the eventual photo pass.
4. **I5 alongside I1.** The recording / consent policy. Cheap to specify; expensive to retrofit (Ring 1 calls happen once and can't be re-recorded).
5. **I7 alongside I2.** The customer record schema. The pre-call prep reads from it; the per-unit portal renders against it; the CO2 sibling's per-customer supplier lookup depends on it.
6. **I6 by day 7 after the first ship.** The post-install touchpoint templates. Trivial to draft, easy to forget if not on the calendar.
7. **I8 when the warranty/return-policy work happens.** Don't try to write the escape valve in a vacuum; it depends on adjacent policy that isn't drafted yet.

## Out of scope for this todo

- **The warranty and return policy itself.** A separate repo gap. Worth a future hourly-agent focus — currently no doc anywhere defines "what happens at year 3 when the peristaltic pump fails" or "what happens if the customer wants to return the appliance in month 2."
- **Scheduling logistics for the call.** Calendly vs. founder-emails-back-with-times is a sales-ops detail, not a playbook concern. Assume the call gets scheduled.
- **The pre-purchase sales call.** This todo starts at carrier handoff. The conversation that converts a discovery moment into a $7,500 purchase is a different (and currently undocumented) playbook, worth its own focus.
- **What happens during Standard Edition.** [target-market.md:96](../../marketing/target-market.md) explicitly removes the personal install consult from Standard. The Standard install support model is a different doc — likely an asynchronous-only model with the install guide doing all the work. Out of scope here.
- **The above-counter visual install** (the visible part of the appliance — faucet, display, switch). The install guide ([I3](#i3--write-the-printed-install-guide-install-above-countermd)) names this but the visual / UX of the above-counter fixture is its own design problem, separate from the install procedure.

## Suggested next concrete step

Draft **I1** as the spine doc at `business/install-consult-playbook.md`, with placeholder sections for I2 through I8 inline. The spine doc is what makes the sibling docs' contributions visible to the founder when they sit down to do the first call. Everything else in this todo plugs into that spine — and without it, each of I2–I8 is a fragment without a context.

The single most leveraged piece of writing here is the Phase B step-by-step (the 45–60 min install walkthrough). It is also the install guide ([I3](#i3--write-the-printed-install-guide-install-above-countermd))'s table of contents, the call recording's natural structure, the post-install touchpoint's reference for "remember when we did step 7," and the customer-record schema's reason for tracking which step gave which customer the most trouble. One careful pass on that step list is the highest-yield doc-work in this todo.
