# Post-delivery failure response: warranty, RMA, damage-claim — all unwritten

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Siblings today:**
- [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) — post-delivery CO2 consumable supply
- [install-consult-playbook-gap.md](install-consult-playbook-gap.md) — the founder-touch Zoom call between delivery and first pour
- [per-unit-portal-gap.md](per-unit-portal-gap.md) — the `/u/NNN` customer-facing software portal

This todo covers a fourth, distinct slice of the post-delivery experience: **what happens when the appliance breaks.** The other three address consumable supply, install hand-holding, and the software portal respectively. None of them addresses the day Derek's phone rings because a $7,500 hand-built appliance in someone's kitchen has stopped pouring soda — or arrived with a cracked enclosure, or started weeping CO2 at month 4, or had its compressor fail in year 3.

## TL;DR

[hardware/assembly/finish-pack-ship.md:163](../../hardware/assembly/finish-pack-ship.md) names this gap explicitly as Open Item #3:

> **Damage-claim + warranty-registration workflow.** Carrier handoff with insurance level, customer-facing claim process, and what the founder commits to on a damaged-in-transit unit (replace? repair? refund?) — all unwritten. Founder Edition unit value at $7,500 makes the answer non-trivial.

A grep across the repo for `warranty`, `RMA`, `return policy`, `refund`, `damage claim`, `field repair`, `loaner`, or `field service` finds:

- **Zero** matches in `business/`, `marketing/`, or any customer-facing surface
- A small handful of `warranty` mentions in `hardware/` — all referring to **third-party part warranties** (the Westbrass faucet, the Touch-Flo cartridge, the Mean Well PSU), never to what the appliance buyer is offered
- One mention of "field repair" in [hardware/handwork.md](../../hardware/handwork.md), used in the construction sense (welding-vs-bolt-on for the pressure vessel), not the customer-service sense

There is no document anywhere in the repo that answers any of these questions:

1. **What does a Founder Edition customer get committed to in writing if their unit fails?**
2. **What is the warranty window** — 30 days? 1 year? 2 years? "Founder will make it right" with no specific window?
3. **In-warranty: who pays for what** — parts, labor, return shipping, install of the repaired unit?
4. **Field repair vs return-to-factory** — which failures are which, and what's the workflow for each?
5. **What spare parts must the founder keep on hand** before unit 1 ships, given solo-build-capacity context?
6. **DOA workflow** — unit arrives, doesn't pour, what now? Carrier claim, replace unit, or repair-in-customer's-kitchen?
7. **What's the customer's promise of remedy** — refund, replace, repair, at-founder's-discretion?
8. **Ring-1 special case** — the 10 friends/family beta units have a different implicit contract; what is it?
9. **End of warranty** — at month 13 or year 6, what's the relationship? Out-of-warranty paid service?

The Founder Edition framing in [marketing/target-market.md:260](../../marketing/target-market.md) — *"the brand is a person. His face, his kitchen, his story… the first 50 buyers are buying from a person they've come to trust"* — means the failure-response posture is **not** a corporate warranty policy. It is a personal commitment from one person. That makes it cheaper to write (no insurance carrier, no legal-department review) but also makes the gap harder to ignore — the customer is paying a premium specifically for the personal commitment, and there is no document anywhere stating what that commitment actually is.

## Project-stance alignment

Following the same frame the [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) sibling established:

This project is **pre-revenue**, treats compliance work as **safety-driven and voluntary** per [business/regulatory.md](../../business/regulatory.md), and operates on a "founder is the brand, founder is the factory" basis through at least unit 50. The appliance business carries **no insurance**, has no plans to add it before the first sale, and explicitly rejects regulatory-posture-for-its-own-sake.

The warranty/RMA posture should follow the same pattern:

- **No paid third-party warranty backstop.** No Asurion-style extended warranty, no carrier insurance on the appliance's full declared value (that's a separate decision at the carrier handoff, scoped narrowly to in-transit damage).
- **No formal returns process** in the e-commerce sense. The product is hand-built and sold one at a time to a known buyer; "return for any reason within 30 days" is not the model.
- **The founder's personal commitment is the entire warranty.** Written down honestly, scoped to what one person with a day job and 12-units-a-year of solo build capacity can actually deliver.
- **The customer is buying from a person, not a company.** That cuts both ways — the upside is the personal accountability the buyer is paying for; the downside is the founder cannot promise infinite parts availability, 24-hour response, or warehouse-backed swap programs. Both sides of that need to be honest in the commitment.

Everything below is calibrated to this stance. The recommendations are scoped to what a solo founder running a craft-volume operation can credibly commit to and deliver. Nothing in this doc requires insurance, a warranty database, an RMA-processing partner, or a service depot.

---

## Part 1 — The decision space, split four ways

The post-delivery failure space breaks cleanly into four sub-cases, each with different costs, mechanics, and customer-expectation shape. The current gap is that all four are undefined.

### W1. Damage-in-transit (carrier-caused)

**Mechanism:** Carton drops, crushes, or punctures between shop-loading and customer-doorstep. Visible at unboxing.

**Existing infrastructure:** [finish-pack-ship.md:117](../../hardware/assembly/finish-pack-ship.md) describes molded foam end-caps in a sized carton (still TBD per Open Item #6 in that doc), the rear-panel photograph archived at `logs/<serial>/finish/` (the "what it looked like leaving the shop" comparison shot — already in the procedure), and carrier handoff with declared value at $7,500 working-default (Open Item #3 of that doc, undecided).

**Gap:**
- No customer-facing instruction for "what do I do at unboxing if the carton is damaged?"
- No founder-side decision for the **insurance/declared-value/no-insurance** trade. Carrier insurance at $7,500 declared value adds ~$50-150 per shipment depending on carrier; self-insuring saves that cost on every unit at the price of eating the loss when one unit in N is destroyed in transit.
- No defined RMA path back to the factory if the customer accepts delivery and *then* finds damage on inspection.
- No defined replacement timeline — at 12 units/year solo build capacity, a "replacement unit shipped within X" promise is bounded by physics.

**Recommended commit (low-cost, doc-only):**
- Customer is instructed at unboxing to **photograph the carton before opening** if there is any visible damage to the outer carton, and to delay opening until those photos exist. The install consult Zoom call (per the [install-consult-playbook-gap.md](install-consult-playbook-gap.md) sibling) is the natural moment to deliver this instruction, before the customer is alone with the carton.
- **Inside-the-carton damage** discovered at unboxing is handled by the founder personally: customer texts/emails photos, founder confirms within 24 hours, the appliance is either repaired-on-site (if the damage is cosmetic and the founder can talk the customer through it), returned to factory at founder's expense, or replaced from a buffer unit if one exists.
- **The buffer unit decision.** At the Founder Edition's solo cadence, a single buffer unit on the shop floor (built but unshipped, held against the next ring's worth of orders as the parking-lot replacement unit) is a low-cost insurance policy that doesn't depend on a carrier insurance product. The buffer unit is built into the Founder Edition's 50-unit count, not on top of it — every 51st unit shipped is the previous buffer, with a new buffer rolled in behind. This trades 1 unit's worth of working capital for "if your unit arrived destroyed, the next one ships from my shop within 2 weeks instead of the 3-4 months a new build would take."

**Recommended commit (later, optional):**
- Carrier insurance at full declared value, evaluated against the buffer-unit cost. Insurance is per-shipment; the buffer is one-time capital. If the carrier-claim filing pattern proves easy enough that insurance is just a fee for predictability, it may be the cheaper of the two. If the carrier-claim process is the kind of multi-month dispute that requires legal escalation to actually collect, the buffer unit is more reliable. **No data yet to choose**; recommend operating with buffer-only for the first 10 units and revisiting.

### W2. Dead-on-arrival (DOA) — first 30 days

**Mechanism:** Unit installs cleanly, but exhibits a real defect within the first 30 days of use. Possibilities span:
- A weld leak that didn't show at factory hydro-test (180 PSI, 30 min) but shows after thermal cycling in service
- A peristaltic pump cartridge tube that fatigued in transit and tears on first dispense
- A reed switch that came loose during shipping vibration
- A compressor that fails its capacitor on first cold start
- A leak at a JG quick-connect that the install kit's cabinet-routing required the customer to assemble
- Firmware behavior that didn't surface in the 8-hour burn-in but surfaces over 30 days of actual use

**Existing infrastructure:** The per-serial archive at `logs/<serial>/` ([finish-pack-ship.md:99](../../hardware/assembly/finish-pack-ship.md)) lets the founder pull up the burn-in log, the as-shipped photos, and the build history. The acceptance bench's "fail mode → escalate" calls ([acceptance-and-burn-in.md](../../hardware/assembly/acceptance-and-burn-in.md) steps 1-11) document many of the failure modes that *should* never reach a customer; a DOA is by definition a mode that slipped past those gates.

**Gap:**
- No customer-facing first-30-day commitment. The Founder Edition framing demands one — the install consult promise per [target-market.md:13](../../marketing/target-market.md) implicitly extends to "the first soda comes out the faucet on this call," but does not state what happens if a soda doesn't come out a week later.
- No decision rule for **field-fix vs return-to-factory** by subsystem. See "Per-subsystem failure-mode posture" below for the proposed mapping.

**Recommended commit:**
- **30-day "founder will make it right" period.** Any defect surfaced in the first 30 days is fixed at no cost to the customer, by whichever path is most practical for that defect (see per-subsystem mapping). Return shipping in either direction, if needed, is on the founder. This is the natural extension of the install consult — the consult got the unit pouring; the 30-day window keeps it pouring through the customer's actual settling-in period.
- **Honest about workflow.** "Make it right" means: customer texts/emails the founder; founder responds within 1 business day (this is a real commitment a person with a day job can keep, as long as the volume stays at craft scale — see capacity-implications below); founder and customer agree on the path (field-fix walkthrough, return-to-factory, or remote firmware update); the founder personally executes or arranges that path. No support ticket system, no first-line CSR, no escalation matrix — at 50 units total it is one person.

### W3. In-warranty failure (after 30 days, before warranty expiration)

**Mechanism:** Same failure-mode space as W2, but surfaced after the customer has had the unit working for a while. The probability shifts toward wear-out failures (peristaltic tubing, compressor capacitor, solenoid coil) and away from infant-mortality failures (transit damage, manufacturing oversight).

**Existing infrastructure:** None.

**Gap:** The whole question. What is the warranty window? What does it cover?

**Recommended commit:**

**Warranty window: 1 year from the date of the install consult call** (not from ship date — the install consult is the explicit "first soda" moment per the [install-consult-playbook-gap.md](install-consult-playbook-gap.md) sibling, which gives a clean date stamp the customer and founder both have in their calendars).

**Coverage scope:**
- All defects in fabrication or design: yes (founder makes it right)
- All third-party component failures: yes (founder handles the upstream warranty claim with the part manufacturer where applicable; customer is not asked to chase Mean Well, SeaFlo, Kamoer, etc., on their own — that is the founder's job because the founder is the integrator)
- Consumables (peristaltic tubing in pump cartridges, foam pipe insulation, customer-visible silicone gasket on faucet shank): excluded — these are user-serviceable wear parts and the install kit + future parts kits should cover their replacement
- Customer-caused damage (drops, flood, power surge): handled case by case; the founder's stance should be "I will tell you honestly whether your situation is or isn't covered, and even when it isn't, I'll quote you the at-cost repair price" — not "warranty void, contact our service department"
- CO2 cylinder, regulator, and any customer-supplied upstream equipment: not covered (these were not supplied by the founder)
- Cosmetic wear (kitchen-wipe scuffing on the rear plaque, scale buildup on the faucet spout, finger smudges on the front face): not covered

**Founder commitment under W3:**
- Within 1 business day: acknowledge the report, ask for diagnostics (photo/video, the `/u/NNN` portal's recent telemetry if that exists per the [per-unit-portal-gap.md](per-unit-portal-gap.md) sibling)
- Within 1 week: a diagnosis and a path (field-fix walkthrough, parts shipped to customer for self-install, parts + remote-walkthrough, return-to-factory, or full unit swap from the buffer)
- **No promised resolution time** for the actual fix. At 12 units/year solo capacity, "fixed within X days" is a promise the founder cannot reliably keep against unknowable demand. The honest commitment is "I will diagnose within a week and tell you the realistic timeline; if that timeline isn't acceptable, the buffer-unit swap is on the table."

### W4. Out-of-warranty (after the 1-year window closes)

**Mechanism:** Same wear-out failures as W3, but the warranty clock has expired.

**Existing infrastructure:** None.

**Gap:** The whole question. Is there paid service? Are spare parts available? Is the relationship over?

**Recommended commit:**

**The relationship is not over.** The Founder Edition customer paid $7,500 for a hand-built unit and a position in the first 50; the founder's commitment to those 50 customers is not bounded by a 1-year window — it is bounded by what one person can sustain across the full design life of the appliance (target: 10 years per [future.md:113](../../hardware/future.md)).

**Out-of-warranty service is paid, transparent, and offered for as long as the founder is reachable.**

- **Field-serviceable parts** (peristaltic tubing, foam insulation, pump cartridges, faucet cartridge): customer can buy replacements from the founder at cost-plus-shipping; the install consult playbook should include the "where to get parts later" pointer per the [install-consult-playbook-gap.md](install-consult-playbook-gap.md) sibling
- **Factory-serviceable repairs** (welded vessel work, compressor swap, electronics-shelf rework): shipped back to the founder; quoted at the founder's hourly rate plus parts; turnaround driven by the queue, not a commitment date
- **End-of-life / orphan path:** at some future point the founder may not be in a position to service these units — death, retirement, life change. The honest commitment is "as long as I am building these, I will service these"; not a perpetual obligation. The customer accepts this when they buy a 1-of-50 hand-built unit from a single person.

---

## Part 2 — Per-subsystem failure-mode posture

Each subsystem fails in characteristic ways. The field-fix vs return-to-factory call depends on three things: tooling required, safety hazard if mishandled, and whether the customer can credibly execute the fix with founder guidance.

The table below proposes a posture per subsystem. None of this is in the repo today.

| Subsystem | Likely failure | Field-fix or RTF? | Rationale |
|---|---|---|---|
| **Carbonator vessel** (welded 316L SS) | Pinhole leak at weld, plate-to-tube joint failure | **RTF — always** | Pressure vessel work requires the laser welder, hydro-test rig, and citric-acid passivation. Customer cannot field-fix. A failure here also implicates the design margin and warrants a per-incident review. |
| **Pressure relief valve (Control Devices SV-125)** | PRV weeps or sticks closed | **Field-replace** | Threaded 1/4" NPT swap. Customer can do it with founder walkthrough and the PRV in the parts kit. Hazard is low (PRV is a passive component); critical-safety component, so the spare must always ship with the install kit, not as an after-the-fact shipment. |
| **WR1110 secondary CO2 regulator** | Fails to hold 90 PSI setpoint, weeps at outlet | **Field-replace** | Inline regulator with two threaded connections. Customer-serviceable with walkthrough. Spare in parts kit. |
| **Backflow preventer (Multiplex 19-0897)** | Check valve weeps to atmospheric vent (the telltale fires) | **Field-replace** | Customer just lived through the "your machine is alerting" experience; founder walks them through the FFL swivel disconnect, ASSE 1022 swap, reseat. Spare in parts kit. |
| **SeaFlo diaphragm pump** | No-prime, vibration noise, output pressure low | **Field-replace** | 3/8" hose-barb in/out, single 12 V connection. Customer-serviceable with walkthrough. Spare on the founder's shelf, shipped on request. |
| **Kamoer peristaltic pump cartridges** | Silicone tube fatigue → leak inside cartridge → flavor pump degraded output | **Customer self-service from the start** | Per [future.md:129](../../hardware/future.md), this is *already* designed as a tool-free swap. The "front-face pump-cartridge access door" exists specifically so the customer can do this without contacting the founder. Replacement cartridges should be available at amazon.com listings or via the per-unit portal store. |
| **Compressor** (harvested from donor ice maker) | Capacitor failure, start relay fail, refrigerant leak | **RTF unless capacitor-only** | Capacitor + start relay swap is a screwdriver-level repair the founder can walk a confident customer through. Anything inside the refrigerant loop — recharge, finger-plate weld, suction-line work — is RTF. R-600a's flammability is the safety constraint: customer field-work on the refrigerant loop is **not okay** even with the founder on Zoom. |
| **Condenser + fan** | Fan bearing failure, fan no-start, dust occlusion | **Field-fix** | Fan is a 12 V DC component on the Mean Well bus; cabin-side swap with the founder on Zoom is fine. Dust occlusion is annual cabinet-shop-vac maintenance the customer can do at the side grilles per [future.md:131](../../hardware/future.md). |
| **Foam-shell cold core insulation** | Foam delamination, moisture intrusion, mildew | **RTF** | Pour-in-place foam was applied at the factory in a controlled cavity; field rework requires disassembling the cold-core stack. RTF, and a candidate for a buffer-unit swap if the failure renders the unit unusable in the meantime. |
| **Flavor reservoirs (printed hard reservoirs)** | Crack, leak past sump seal, vent clog | **RTF for the cracked-reservoir case; field-clean for the vent case** | Reservoir is sized to the cold-core foam-shell cavity; replacement requires opening the foam shell. Field-clean of the high-mounted filtered vent is a small task with founder walkthrough. |
| **Faucet (Westbrass + Touch-Flo cartridge)** | Touch-Flo cartridge wear (drip when closed), spout aerator clog | **Field-fix** | Westbrass faucets are designed for field-service; Touch-Flo cartridge is a single-screw swap. Already a commodity-faucet repair path; founder just stocks the replacement cartridge SKU. |
| **Electronics shelf (ESP32, displays, drivers)** | Boot failure, BLE pairing failure, sensor fault | **Field-diagnose, possibly RTF** | Power-supply level failures are field-replace (the Mean Well IRM-90-12ST is an off-the-shelf swap). MCU + GPIO-expander + driver-stack failures usually mean RTF because troubleshooting on the bench is faster than over Zoom. |
| **Wiring + AC distribution + chassis grounding** | Loose ground, intermittent neutral, blown SF76E thermal fuse | **Field-diagnose, RTF if not obvious** | A blown SF76E means the compressor compartment got too hot — a real safety event that warrants RTF for investigation, not a field-reset. |
| **Firmware** | Boot loop, BLE drop, control-loop misbehavior, false freeze-protect trip | **Field-fix (OTA or USB)** | Firmware updates over BLE or USB are a Zoom-walkthrough operation. The per-unit portal per the [per-unit-portal-gap.md](per-unit-portal-gap.md) sibling could host the per-unit firmware images directly. |

The table above is a working proposal, not a commitment — it is intended as the starting point for a `business/warranty-and-rma.md` document Derek would review and adjust.

The **safety-driven hard rules** that should not be relaxed:

- **No customer work inside the refrigerant loop, ever.** R-600a is flammable; the factory recharge process per [refrigerant-loop.md](../../hardware/assembly/refrigerant-loop.md) requires the BPV31 piercing valve, the Enviro-Safe charge can, and the hydrocarbon sensor + thermal fuse safety stack. Customer field-work here is not safe even with the founder on Zoom.
- **No customer work on the welded pressure vessel.** Same reasoning as above; the 90 PSI service pressure and the customer-side CO2 supply make any cracked-vessel field repair unacceptable.
- **No customer work on the AC mains side of the electronics shelf** while energized. C14 inlet swap and ground-wire repair are okay with the unit unplugged and the founder on Zoom; anything live is RTF.

---

## Part 3 — Spare parts inventory implications

The recommendations above imply the founder must keep a small inventory of swap parts on hand from the day unit 1 ships. The current [bom.md](../../hardware/bom.md) and [purchases.md](../../hardware/purchases.md) are written against per-unit build cost, not against service-stock. Bridging that gap means a single new doc — call it `hardware/service-stock.md` — that lists the per-unit field-replaceable parts and the founder's commitment to keep N spares of each.

A working draft of that list, based on the per-subsystem table above:

| Part | Why stocked | Minimum stock-on-hand |
|---|---|---|
| Control Devices SV-125 PRV | Safety-critical, must ship with install kit | 5 (1 per unit + 5 buffer for the first 5 deployed units) |
| Interstate Pneumatics WR1110 secondary regulator | High-impact failure (no CO2 → no soda) | 2 |
| Multiplex 19-0897 backflow preventer | Backflow vent alert is the user-visible failure mode | 2 |
| SeaFlo 22-Series diaphragm pump | Carbonator refill failure → unit unusable | 1 |
| Kamoer peristaltic pump cartridges (complete assemblies) | Designed-for-replacement; consumable behavior | 4 (2 per flavor × 2 units' worth) |
| Touch-Flo cartridge for Westbrass faucet | Common faucet-cartridge wear part | 2 |
| Mean Well IRM-90-12ST PSU | Spans the entire low-voltage system; single point of failure | 1 |
| SF76E thermal fuse | Safety component, blown = signal to investigate but also signal that the unit needs the part replaced before re-service | 5 |
| Reed switches (Gebildet level-sensing) | 8 per unit on the reservoirs + 2 on the carbonator; transit/install failure modes | 12 |
| 3M 425 aluminum foil tape | Coil-to-vessel thermal bond; consumable for any cold-core rework | 1 roll |
| PRV-Tee + 1/4" NPT misc swaps | Plumbing-side joint repair | small kit |

The point is not the exact list; the point is the list exists today as zero parts. Even if Derek doesn't commit to this specific inventory, the recommendation is to **commit to *an* inventory before unit 1 ships**.

---

## Part 4 — The Ring-1 special case

Per [target-market.md:174](../../marketing/target-market.md):

> The first 10 units go to people the founder knows directly, or one degree out — friends, family, friends-of-friends. Pricing is whatever moves the unit. Probably $2,000-3,000. Possibly some at cost or below for family members willing to be beta testers. The "product" of ring 1 is not revenue. It is three things: units in homes generating real-world use data; supplier relationships established at quantity-of-50 for the BOM items where that matters; and a tighter, faster-to-build design by the time ring 1 closes out.

Ring 1 buyers are explicitly beta testers. The implicit contract with them is different from the cold-arrival Founder Edition buyer at $7,500. **That implicit contract should be written down** — not as a customer-facing legal document, but as a one-page agreement (email is fine) the founder and the ring-1 buyer both have in their inbox.

Recommended elements:

- **Pricing:** as agreed per unit ($2,000-3,000 working range; "at cost or below" for some family/friend cases)
- **Beta-tester status:** the buyer understands this is unit N of the first 10, the design is iterating, the next 10 will have improvements they don't, and some things will break that wouldn't break in a more mature unit
- **Quid pro quo:** the buyer agrees to share data, report failures honestly, accept a sometimes-disruptive iteration cycle (founder may need to come out and swap a part, or take the unit back for a week to upgrade something), and to be a real-world data source
- **Warranty: same shape as Founder Edition's, with one specific difference** — ring-1 buyers may be asked to host an upgrade/swap at the founder's request, not just at theirs. They get the upside of priority service and the downside of being the first to receive a beta change that may itself fail.
- **No public expectation around the price.** Ring-1 prices are not a discount off the Founder Edition; they are a different transaction, and ring-1 buyers should be asked not to publicly anchor the appliance at $2,000-3,000 (the Founder Edition anchor at $7,500 is doing work for the cold buyer, per [target-market.md:184](../../marketing/target-market.md)).

This is a small doc — half a page. The recommendation is to write it before ring-1 unit 1 sells, not after.

---

## Part 5 — What the customer-facing welcome letter must say

The Founder Edition customer-documentation packet per [finish-pack-ship.md:109](../../hardware/assembly/finish-pack-ship.md) includes a "Founder Edition welcome letter, personally signed." That letter is the customer's first physical contact with the warranty/RMA posture above.

The letter does not need to be a legalese document. It needs to be honest, specific, and short. Recommended elements:

1. **A name, a number, a date.** "Unit SFI1-FE-NNN, built and shipped on [date], hand-signed on the rear plaque."
2. **The install consult promise** (per the [install-consult-playbook-gap.md](install-consult-playbook-gap.md) sibling).
3. **The 30-day make-it-right window.** "If anything is wrong in the first 30 days after our install call, write me and I will fix it — at my cost, by whichever path is most practical for the issue."
4. **The 1-year warranty.** Plain English. What's covered, what isn't, how to reach the founder.
5. **What to do at unboxing if the carton is damaged** (photograph first, do not open until the photos exist; text/email those photos).
6. **The CO2 supply pointer** (per the [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) sibling).
7. **The portal pointer** (per the [per-unit-portal-gap.md](per-unit-portal-gap.md) sibling, once it exists).
8. **The end-of-warranty relationship.** "After the first year, I am still your contact for this machine. Service is paid; my hourly rate is X; spare parts are at cost; I will work this with you for as long as I am building these."
9. **One line on the design-life expectation.** "This appliance is designed for a 10-year service life. If you keep it longer than 10 years, you and I will figure it out — I am not promising it will be running in 2050."
10. **A real signature, a real email address, a phone number** (the founder's; this is the entire Founder Edition value proposition manifest in the letter).

A first cut of this letter is a half-page document. The recommendation is: write it now, store it under `business/welcome-letter-template.md`, treat each unit's letter as a per-serial filled-in copy of the template — same way the nameplate is per-serial.

---

## Part 6 — Capacity and incident-rate implications

A solo founder at 12 units/year build capacity has a finite warranty-service throughput. The arithmetic:

- 50 Founder Edition units shipped over ~4 years
- Year 1: 12 units in the field, all within their 1-year window → 12 unit-years of in-warranty exposure
- Year 2: 24 units in the field, of which 12 are in-warranty → ~24 unit-years of total exposure
- Year 4: 48 units in the field, of which 12 are in-warranty (the most recent 12) → ~48 unit-years of total exposure
- Year 5 onward: 50 units in the field, 0 in formal warranty, all eligible for out-of-warranty paid service

If the appliance achieves a 1-failure-per-unit-year rate, year-4 implies **48 service events per year** — about one per week. That is real founder-time the build pipeline does not account for.

If the failure rate is lower (one per 3 unit-years), year-4 implies 16 service events per year — about one every 3 weeks. Still real time, more sustainable.

**The recommendation** is not to model the failure rate (we have no data; the first ring-1 units don't even exist yet). It is to **flag this**: warranty service draws from the same hours as new builds. The Founder Edition's 12-unit-a-year build cadence is the headline number, but the actual sustainable cadence drops as the installed base grows. Year 4 build cadence may be closer to 8 new units a year + 4 units of warranty time — which the public-facing scarcity story does not currently reflect, and may need to.

This is a finding the [target-market.md](../../marketing/target-market.md) authors should consider; not a doc to write today, but a calibration to fold into the public scarcity narrative in some future revision.

---

## What to do today (low-cost, doc-only)

The recommendations above are dense. The minimum viable subset, ordered by what unblocks the most downstream:

1. **Write `business/warranty.md`** — a single document that answers W1–W4 with the postures proposed in Part 1. Roughly 300 lines. Audience: the founder, future agents, and (when extracted) the customer-facing welcome letter.
2. **Write `business/welcome-letter-template.md`** — the half-page per-serial letter that ships in every Founder Edition install kit, per Part 5.
3. **Write `hardware/service-stock.md`** — the spare-parts inventory Derek must keep on hand from the day unit 1 ships, per Part 3. Cross-reference into [bom.md](../../hardware/bom.md) and [purchases.md](../../hardware/purchases.md).
4. **Write `business/ring-1-agreement.md`** — the half-page implicit-contract document for the first 10 beta-tester units, per Part 4.
5. **Close [finish-pack-ship.md](../../hardware/assembly/finish-pack-ship.md) Open Item #3** by replacing it with a pointer into `business/warranty.md` and the carrier-claim/buffer-unit decision in Part 1's W1.
6. **Cross-reference into the [install-consult-playbook-gap.md](install-consult-playbook-gap.md) sibling's call agenda** — the install consult is the natural moment to verbally introduce the warranty/30-day commitment, in addition to the welcome letter that arrives in the carton.

Nothing in this list costs money. Nothing requires hardware or firmware work. All of it is writing-and-thinking work that can be done before unit 1 sells, must be done before unit 1 ships, and currently has no owner.

---

## What is **not** recommended (explicitly)

To avoid scope creep and stay aligned with the project's pre-revenue stance:

- **Not recommended:** purchasing product-liability insurance, third-party warranty backstops, or extended-service-plan partnerships before first sale. These are appropriate at a different scale of business, not at 50-units-from-one-person scale.
- **Not recommended:** building a support-ticket system, RMA-portal software, or warranty-database tooling. At ~50 units total, an email folder works fine. Re-evaluate at Standard Edition scale (≥100 units/year).
- **Not recommended:** writing a customer-facing "Terms of Sale" or "Limited Warranty" legal document with sweeping disclaimers. The Founder Edition framing is "buying from a person you trust"; a wall of disclaimer text actively undermines that frame. The plain-English commitment in the welcome letter is the right surface for the buyer.
- **Not recommended:** committing to a specific repair-turnaround time as a marketing promise. The honest commitment is "I'll diagnose within a week and tell you the realistic timeline"; a public "repaired within 14 days" promise the founder cannot guarantee against solo capacity is worse than no promise.
- **Not recommended:** offering returns-for-any-reason. The product is hand-built to a known buyer; "return for any reason within 30 days" is e-commerce convention that does not fit the Founder Edition's actual transaction shape. The 30-day make-it-right window covers actual defects; buyer's-remorse returns are a different beast and arguably are not on the table at Founder Edition pricing and sales-process shape.

---

## How this connects to today's other recommendations

- **[co2-supply-ownership-gap.md](co2-supply-ownership-gap.md)** — covers the consumable-supply rough edge. This doc covers the *hardware-failure* rough edge. They share the same project-stance frame (pre-revenue, no insurance, voluntary safety) but address non-overlapping failure modes of the post-delivery experience.
- **[install-consult-playbook-gap.md](install-consult-playbook-gap.md)** — the install consult is the explicit "first soda" moment, the natural date stamp for warranty start, and the natural moment to verbally introduce the make-it-right commitments here. The install consult playbook's agenda should reference the warranty doc; the warranty doc should reference the install consult as the warranty-start trigger.
- **[per-unit-portal-gap.md](per-unit-portal-gap.md)** — the `/u/NNN` portal is the natural surface for (a) the customer's per-unit warranty status; (b) the per-unit log archive that supports remote diagnosis; (c) the spare-parts ordering store; (d) the per-unit firmware images. The warranty doc and the portal doc are mutually reinforcing — neither blocks the other, but each makes the other more useful.

All four of today's siblings sit between "the customer has paid" and "the customer is happily pouring soda for a decade." Three address the path *into* that decade; this one addresses *what keeps the customer there* when something inevitably breaks.
