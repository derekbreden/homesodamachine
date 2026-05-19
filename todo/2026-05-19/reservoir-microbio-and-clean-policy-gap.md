# Reservoir microbiology and clean-cycle policy: what protects the syrup once it leaves the SodaStream bottle

**Author:** hourly agent, 2026-05-19 (afternoon, after 12 prior siblings today)
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek

## Distinct from siblings

- 2026-05-19 sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) covers the *upstream* problem (the Amazon SKU goes "Currently unavailable"). This doc covers the *downstream* problem (concentrate sitting in the reservoir for weeks). Different failure mode, different actions.
- 2026-05-19 sibling [`tap-water-quality-spec-gap.md`](tap-water-quality-spec-gap.md) covers what enters the *carbonator* via the diaphragm pump. This doc covers what happens to the *flavor reservoir* contents after they're poured in. Different fluid, different chemistry (pH ~3.5 carbonic acid vs. pH ~3 sucralose syrup), different storage time (seconds in the carbonator headspace vs. weeks in the reservoir).
- 2026-05-19 sibling [`foam-pour-procedure-gap.md`](foam-pour-procedure-gap.md), [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md), [`leak-detection-coverage-gap.md`](leak-detection-coverage-gap.md), [`water-damage-containment-gap.md`](water-damage-containment-gap.md) — all hardware build/safety gaps. None touch food-safety or microbiological policy.
- 2026-05-19 sibling [`integrated-firmware-gap.md`](integrated-firmware-gap.md) covers the firmware-readiness picture broadly. The clean cycle does exist in the prototype's `firmware/src/main.cpp` (lines 487–1463: `CleanState`, `startCleanFill`, `startCleanFlush`, `finishClean`, three rounds of 10 s fill + 15 s flush). What is missing is *when it runs* and *what microbial threat it counters* — a policy/spec layer above the firmware, which is the focus of this doc.
- 2026-05-18 siblings — all post-sale logistics (freight, CO2, install consult, order/payment, portal, warranty). None touch food safety.

This doc is its own focus area: **the food-safety and clean-cycle policy for the flavor reservoirs.**

---

## TL;DR

The integrated build introduces a new vessel that does not exist in the prototype or in any consumer beverage product on the market: a **vented, 0.88 L printed plastic reservoir, held at 8–15 °C inside the appliance, containing one or two SodaStream Pepsi-Co diet-soda concentrate bottles' worth of sucralose syrup, refilled monthly-ish, sitting for the life of the appliance.**

Comparable commercial systems either (a) keep the syrup in its sealed bag-in-box at room temperature for a few weeks (commercial post-mix), (b) keep the syrup in its sealed bottle in a household fridge at 2–4 °C (SodaStream's own product), or (c) pasteurize / hot-fill / spray-clean / batch-discard between fills (commercial open-syrup systems, soft-serve, frozen drink machines). The home soda machine reservoir is none of these. It is a **novel storage environment** for this concentrate.

The repo treats the reservoir as a passive vessel:

- [`hardware/future.md:73`](../../hardware/future.md) says the reservoirs are "vented, not service-pressure vessels … cleaned in place by a software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat)."
- [`hardware/future.md:41`](../../hardware/future.md) notes the *carbonator* needs no clean cycle because pH ~3.5 + 2 °C suppresses biofilm. That argument **does not transfer** to the reservoir: the reservoir is warmer (8–15 °C), the contents are different (sweetened syrup, not carbonated water), and the reservoir is vented to atmosphere through a hydrophobic-but-non-sterile membrane.
- [`hardware/printed-parts/cold-core/reservoir/vent.md:7`](../../hardware/printed-parts/cold-core/reservoir/vent.md) specifies a ø13 mm × 0.5 mm hydrophobic PTFE membrane to keep splashed syrup off the membrane and keep dried syrup off the appliance interior. It is **not** specified as a sterile-air vent (a sterile vent would be 0.2 µm rated, e.g. a Pall Acro 50 or similar — the LVDALAB B0D41KT345 lab filter is sold as a coarser "hydrophobic PTFE" disc, pore size unspecified in the listing and likely 0.45–1.0 µm). The vent is a splash baffle, not a microbiological barrier.
- The firmware has a `CleanState` state machine ([`firmware/src/main.cpp:487`](../../firmware/src/main.cpp)) with three rounds of 10 s fill + 15 s flush, but **no caller in the user-facing code path documents when it must run.** It is a tool, not a schedule.

**The gap is the policy layer between "we have a clean cycle" and "the customer's syrup is safe to drink five weeks after they poured it in." The hardware exists. The decision tree does not.**

This is a Ring-1-readiness gap, not a hardware blocker. Unit #1 can ship without it. But every Ring-1 customer will, within their first month, ask one of the following:

1. "How often does the machine clean itself?"
2. "When I want to switch from Diet Mountain Dew to Pepsi Zero Sugar, what do I do?"
3. "I haven't used it for two weeks while I was on vacation. Is the syrup OK?"
4. "There's a tiny black spot in the bottom of the reservoir. Should I worry?"

The repo currently has no documented answer for any of these.

---

## What's actually in the reservoir

Per [`hardware/future.md:73`](../../hardware/future.md) and the SodaStream Pepsi-Co concentrate ingredient list (off-the-shelf data, not in repo):

- **Volume:** ~0.88 L usable, ~1.18 L geometric. Sized for two SodaStream 0.44 L bottles per refill — i.e. a single full reservoir is a *single retail SKU's full contents.*
- **Temperature:** 8–15 °C, passively pre-chilled by the cold core gradient ([`future.md:81`](../../hardware/future.md)). This is *warmer* than a household fridge (2–4 °C) and *colder* than room temperature (20–22 °C).
- **Composition:** ~5× SodaStream Pepsi-Co diet concentrate dilution at use (the system meters 1:20-ish at the nozzle). The concentrate itself is sucralose-sweetened (no sugar — see [`marketing/target-market.md:11`](../../marketing/target-market.md)), with potassium sorbate and/or sodium benzoate listed as preservatives on the SodaStream Pepsi line (verify against current label — this is the public ingredient list and is subject to PepsiCo reformulation, same risk surface as [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) §3).
- **pH:** ~2.8–3.2 (phosphoric acid in the Pepsi line, citric acid in the Mountain Dew line — both well below the 4.6 threshold below which most foodborne pathogens cannot grow).
- **Headspace:** vented to atmosphere through a hydrophobic PTFE splash baffle. **Air with viable mold spores can pass; liquid water cannot.**
- **Refill cadence:** one 14.9 fl oz / 440 mL bottle per refill cycle. At 2–3 servings/day per typical buyer ([`target-market.md:50`](../../marketing/target-market.md)) with ~25 mL concentrate per serving, a single bottle lasts ~6–9 days. At one bottle per cycle, full reservoir lasts ~12–18 days. At two bottles per cycle (full reservoir), ~24–36 days. **Anything stored longer than ~30 days at 8–15 °C is outside the typical SodaStream-after-opening labeled shelf life of 60 days refrigerated** — and SodaStream's label assumes 2–4 °C fridge, not 8–15 °C.

## What the carbonator's "no clean cycle needed" argument does *not* prove about the reservoir

[`future.md:41`](../../hardware/future.md):

> Carbonated water at ~2 °C and pH ~3.5–4 naturally suppresses biofilm and scale formation in the vessel — no scheduled clean cycle is required for the carbonator.

Three reasons this does not extend to the reservoir:

1. **Temperature.** Carbonator is at ~2 °C. Reservoir is at 8–15 °C. The most common spoilage organisms in low-pH sugar/sweetener solutions (*Zygosaccharomyces*, *Aspergillus*, *Penicillium*, lactic acid bacteria) are slow but not arrested at 8–15 °C — they merely grow more slowly than at room temperature. At 2 °C they are essentially dormant. The 6–13 °C gap matters.
2. **Sugar / sweetener substrate.** Carbonator is plain water. Reservoir contains concentrated sweetener, acidulants, flavor oils, and preservatives. Sucralose itself is not metabolized by most spoilage organisms, but the **flavor oils and any residual sugars from the natural-flavor components** are — and those are present in every SodaStream concentrate SKU. The carbonator argument assumes a non-substrate fluid; the reservoir contains a substrate.
3. **Vent geometry.** Carbonator is sealed pressure vessel — fully closed system except during refill events through valves. Reservoir is open to atmosphere through a hydrophobic-but-non-sterile membrane that splashes mostly-but-not-perfectly drain syrup back into the reservoir. The reservoir has a path for outside air (and mold spores carried in outside air) to reach the headspace. The carbonator does not.

Conclusion: the carbonator-clean-cycle-not-needed reasoning is valid for the carbonator and **not transferable** to the reservoir. The reservoir needs its own argument.

---

## What we know and don't know about SodaStream concentrate stability

What is on the label (off-the-shelf data, not in repo — verify against the current SKU):

- "Refrigerate after opening." Typical shelf life after opening, refrigerated: **45–60 days**. This is *PepsiCo's* spec, not ours. It assumes the bottle is closed between uses and a household refrigerator at 2–4 °C.
- Best-by date on unopened bottle: typically 9–12 months from manufacture.

What we are doing differently:

- Transferring concentrate out of the sealed bottle into a vented reservoir.
- Holding it at 8–15 °C, not 2–4 °C.
- Mixing two batches of concentrate from different bottles, possibly from different production lots, in the same reservoir (each refill empties the previous remnant into the new pour).
- Holding the *total* time-in-system across multiple refills indefinitely — there is no per-reservoir "best by" tracking in the firmware.

These differences invalidate the bottle's printed shelf life. PepsiCo's 45–60 days assumes their conditions, not ours. **We do not currently have a substitute number, and we do not have a way to derive one from the literature without a test.**

What the literature suggests, conservatively (general food microbiology, not SodaStream-specific):

- Sucralose syrups with potassium sorbate at ~0.1% w/w and pH < 4 typically resist *Zygosaccharomyces* (sorbate-resistant osmophilic yeast) for **30–90 days at refrigeration** in *sealed* containers. The presence of sorbate-resistant strains is the dominant failure mode in soft-drink syrup industry experience.
- In a *vented* container at 8–15 °C, the dominant failure mode is **surface mold growth** — *Penicillium*, *Aspergillus*, *Cladosporium* — landing from airborne spores onto the syrup surface. These molds grow visibly within 7–21 days under favorable conditions and can grow under sorbate/benzoate doses that suppress yeast.

**The honest answer is:** we don't know how long PepsiCo-formulated SodaStream concentrate stays safe and palatable in our specific reservoir geometry, and we cannot derive it from the bottle label. Ring 1 is the test that produces this number.

---

## The clean cycle: what it actually does and doesn't do

What the firmware does today (3-cycle, water-only fill/flush — verified in `firmware/src/main.cpp:487–1463`):

1. Fill the reservoir with ~10 s of tap-water flow through the source-selector valves into the reservoir.
2. Flush the reservoir by running the pump for ~15 s, sending the contents to the nozzle (into the user's drain or sink).
3. Repeat 3×.
4. (Implicit) end on a flushed-empty state, ready for re-fill from the user's hopper pour.

What this **does** accomplish:

- Mechanical dilution and rinse of bulk syrup residue from the reservoir walls, sump, outlet bulkhead, and downstream peristaltic tube + nozzle. Three rinses with tap water dilute any soluble residue by roughly 10³–10⁴ at most.
- Visible reservoir interior — a customer who opens the cap sees water, not sticky syrup.

What this **does not** accomplish:

- It is **not a sanitization step**. Tap water at municipal residual chlorine (0.2–2 ppm free chlorine) has some sanitizing power on planktonic bacteria but is *ineffective* against established biofilm and against mold spores adhered to wall surfaces, and most municipal water has been sitting in household plumbing long enough that residual chlorine has decayed.
- It does not address **biofilm** that may have formed on the reservoir walls during weeks of syrup storage. Biofilms in low-pH sugar/sweetener systems are thin but tenacious and survive water rinses.
- It does not address **the peristaltic-tube interior**. The peristaltic pump's silicone tube is squeezed by rotor lobes — geometry that traps residue in the squeeze lines. The clean flush passes water through it, which helps, but the tube is a known biofilm habitat in commercial dispenser experience.
- It does not address **the vent's splash-baffle slots**, which collect dried syrup that the upward splash deposited.

A real commercial sanitizer cycle would (a) use a chemical sanitizer (peracetic acid, chlorine-based at 100–200 ppm, or a quaternary ammonium), (b) include a contact-time dwell (typically 1–3 minutes), and (c) include a final potable-water rinse to remove sanitizer residue. The current cycle does none of those.

The current cycle is a **rinse cycle**, not a **sanitization cycle**. The repo's language conflates them.

---

## The four customer questions, today

Restating from the TL;DR with the answers the system can currently provide:

1. **"How often does the machine clean itself?"**
   - *Current answer:* It doesn't, automatically. The clean cycle is a tool the user invokes manually (per the firmware state machine, there is no scheduler). The user is not told when to invoke it.
   - *Honest answer to put in customer-facing docs:* "We are still calibrating this. For now, run the clean cycle from the app any time you change flavors, or once a month if you haven't."

2. **"When I want to switch from Diet Mountain Dew to Pepsi Zero Sugar, what do I do?"**
   - *Current answer:* Empty the reservoir (pump-to-nozzle until low-reed sees empty), run the clean cycle, pour the new flavor into the hopper, route to the same reservoir.
   - *Repo gap:* This procedure is not documented anywhere customer-facing. The valve states for "empty bag A to nozzle as syrup, then clean, then refill with new flavor" exist in [`fluid-topology.md`](../../hardware/topology/fluid-topology.md) but the *user-facing flavor-changeover workflow* does not exist as a single doc.

3. **"I was on vacation for two weeks. Is the syrup OK?"**
   - *Current answer:* Probably yes — 2 weeks at 8–15 °C is well within the bottle's 45–60-day spec, and our holding temperature is at the warm end of that spec. But there is no instrumented confirmation and no firmware-side "you've been away — run a clean cycle before next dispense" prompt.
   - *Likely failure modes for longer absences:* (a) low-level flavor degradation noticeable to the daily user, (b) surface mold colonies on the syrup, (c) elevated yeast count not visible but tasted as off-notes.

4. **"There's a tiny black spot in the bottom of the reservoir."**
   - *Current answer:* No documented user response. The reservoir is meant to be sealed-and-printed; there is no service procedure for "inspect and visually re-clean." The transparent-vs-opaque material choice for the reservoir is not specified in the cold-core docs reviewed.

---

## Six concrete recommendations (R1–R6)

Sized roughly by effort. R1–R3 are doc-only and cheap. R4 is firmware + UX work. R5–R6 are physical / supplier work.

### R1 — Write `hardware/food-safety.md`

A single doc that names the food-safety surface explicitly. Sections:

1. The fluids in the system (potable tap water, carbonated water, CO2 gas, diluted concentrate, undiluted concentrate, drain water from clean cycle) and which materials each touches.
2. The wetted-materials inventory for the **diluted** path (water + carbonated + nozzle delivery): all 316/316L SS, food-grade silicone, JG PTC bodies. This is already implicitly covered across `cold-core.md` and `pressure-vessel.md`; consolidate.
3. The wetted-materials inventory for the **concentrated** path (reservoir, peristaltic tube, nozzle): the printed-part materials, the silicone-tube material, the JG bulkhead bodies. **This is where the food-safety surface is undocumented**, because PET-CF (or whatever filament the reservoir uses) is not commodity food-contact in the same way SS and silicone are. The doc must either (a) commit to a food-contact certified filament with documented FDA 21 CFR compliance, or (b) document the migration test that proves the chosen filament meets the standard in this service.
4. **The reservoir clean-cycle policy** (R2).
5. **The reservoir shelf-life policy** (R3).
6. Open items: a list of things we don't know and intend to learn from Ring 1.

Audience: founder, future agents, regulators if they ever ask, customers (a customer-facing one-pager summary is the artifact of R5 below). The doc itself can be terse — 1–2 pages.

### R2 — Specify the clean-cycle trigger policy

Pick a policy from this short list, document it, implement the missing pieces in firmware:

| Policy | Trigger | Effort | Risk |
|---|---|---|---|
| A. Manual only | User opens app, hits "Clean now" | Already done in firmware; needs UX surfacing and a doc | User forgets. Most likely failure mode. |
| B. Manual + reminder | Manual button + app reminder every N days | Add a notification scheduler to the app; pick N from R3 | Cheap. Likely the right answer for Ring 1. |
| C. Automatic on flavor change | Detect flavor reservoir going empty + user selecting a different SKU at hopper | Hopper UX doesn't yet identify the SKU; needs an input | Best UX. Requires more work. |
| D. Automatic on schedule | Run nightly clean if reservoir hasn't been used in > N days | Adds a clock-driven cleanup; consumes water and time | Wastes water on non-dormant systems. |
| E. Automatic on absence | "You've been away — run a clean cycle before next dispense" prompt at first dispense after > N idle days | App + firmware coordination | Good UX. Moderate effort. |

**Recommended:** B + E for Ring 1. B sets the baseline maintenance cadence with a customer-facing reminder. E catches the vacation case where the customer has been honest about the absence (they're using the app to dispense again).

The policy must be paired with a recommended N. The honest default is "every 30 days" — paired with R3 below, this is roughly the SodaStream after-opening label's halfway point, halved again for the warmer 8–15 °C vs. fridge 2–4 °C.

### R3 — Specify the reservoir shelf-life policy

Same shape as R2. Document:

- Maximum time concentrate may remain in the reservoir at 8–15 °C before mandatory dump-and-clean. **Default to 30 days as the Ring-1 starting number**, derived from PepsiCo's 45–60-day refrigerated spec discounted for the warmer holding temperature.
- Track this in firmware. The reservoir's last-refilled timestamp should already be implicit in level-sensing event logs; expose it as a field, age it, alarm when it exceeds the threshold.
- Distinguish:
  - **Soft alarm:** "Your reservoir was last refilled 31 days ago. Run a clean cycle, or top off with fresh concentrate." (App notification only.)
  - **Hard alarm:** "Your reservoir was last refilled 45 days ago. The next dispense will be blocked until you run a clean cycle." (App + display + dispense interlock.)
- Reset the clock on (a) successful clean cycle followed by a refill, (b) substantial refill (≥ 50% of full reservoir, i.e. one fresh bottle dumped in).

### R4 — Decide whether tap-water rinse is sufficient or whether a sanitizer step is needed

The current cycle is a rinse. The question is whether the policy in R3 (30-day intervals at 8–15 °C with a vented headspace) requires more than that.

Two paths:

**Path A: rinse is sufficient.** Defend this with the following argument: (1) concentrate is acidic enough (pH < 4) and contains preservatives that suppress yeast and bacteria; (2) the reservoir holds for ≤ 30 days at refrigeration-adjacent temperature; (3) the user dumps and rinses every 30 days; (4) the dilute path downstream is pH 3.5 carbonated water which itself suppresses biofilm.

This path is **plausible but not proven**. To make it the policy, Ring 1 must include an instrumented test: pull a sample from the reservoir at days 7, 14, 21, 30 across multiple installs, plate or send to a food-microbiology lab, compare results. If no growth at 30 days across all installs, rinse-only is defensible.

**Path B: rinse plus periodic sanitizer dose.** Add a user-supplied sanitizer step every N cycles. The mechanism is:

- Customer-supplied food-grade sanitizer (commercial homebrewer Star San at 1 oz/5 gal is the obvious commodity — pH ~2.1, no-rinse, contact time 30 s, available at every homebrew shop and on Amazon Prime).
- Customer pours sanitizer into the hopper instead of concentrate; the same routing valves direct it to the reservoir.
- Cycle: fill with sanitizer → dwell 60 s → flush sanitizer to nozzle (drain or sink) → triple-rinse with tap water → ready.

Path B is more rigorous and more disruptive. It moves the appliance closer to a commercial dispenser's clean schedule, which is the model that we have working examples for. It also adds a consumable to the customer's ownership cost (~$15/year of Star San at one bottle annually).

**Recommended:** Path A for the Founder Edition's first 10 units (Ring 1), explicitly framed as "we are testing whether rinse-only suffices." Path B as the fallback if Ring 1 data shows growth, or as a quarterly cycle layered over the monthly rinse from R2 (the belt-and-suspenders option).

### R5 — Write the customer-facing one-pager

A single, short, customer-readable doc — likely `docs/cleaning-and-shelf-life.md` or `web/public/cleaning.html`. The content is whatever the R2/R3/R4 decisions land on, translated into the founder's voice. The point is to make the answers to the four customer questions printable, shareable, and bundled with the install kit.

The shape that fits the "founder's kitchen, founder's story" Ring-1 voice:

- "I built this. I keep mine cleaned on a 30-day rhythm. Here's exactly how, and why."
- A photograph of a clean reservoir.
- A photograph of what month-old syrup looks like before the next clean cycle (this exists in Derek's prototype — surface a real photo from the running unit, not a stock image).
- A "when in doubt, run the clean cycle" callback. The whole point of having the clean cycle as a button in the app is that the customer can use it any time. Make this the default cultural rhythm.

### R6 — Decide on the vent membrane spec

The current vent membrane (LVDALAB B0D41KT345, [`vent.md`](../../hardware/printed-parts/cold-core/reservoir/vent.md)) is sold as "hydrophobic PTFE filter" without a documented pore size in the Amazon listing. For sterile air venting in pharmaceutical / brewing applications, the standard is 0.2 µm rated PTFE (e.g. Pall Acro 50, Sartorius Midisart, Whatman Polyvent).

Two paths:

**Path A: keep the current splash-baffle-with-coarse-PTFE design.** Defend this by reaffirming the reservoir is *not* a sterile environment and the cleaning policy handles the bioburden that gets in. This is consistent with consumer-grade beverage equipment.

**Path B: upgrade to a 0.2 µm rated sterile vent disc.** Same ø13 mm form factor exists in 0.2 µm rated PTFE from lab suppliers (Sterlitech, Cytiva, Cole-Parmer) at $0.50–2.00 per disc rather than $0.13. Same retaining ring, same pocket — drop-in change.

**Recommended:** Path B. The cost delta is trivial ($0.40 × 2 caps × per-build ≈ $1/unit) and the design margin against the "tiny black spot in the reservoir" customer report is large. The Path-A argument that "we have a clean cycle so the spores don't matter" depends on the customer running the clean cycle on time, which is the weakest link in the whole system. Adding 0.2 µm sterile filtration at the vent removes one threat vector entirely.

The substitution does not change any geometry or assembly procedure.

---

## What changes vs. what stays

What stays:

- Hardware. Reservoir geometry, pump cartridge, valve manifold, plumbing — unchanged. The clean-cycle mechanism in firmware exists and works.
- The carbonator's "no clean cycle needed" argument — it remains valid for the carbonator; only the read-across to the reservoir is wrong.
- The "He hates these cans" market position — this gap doesn't touch marketing.

What changes:

- A new doc, `hardware/food-safety.md`, names the food-safety surface and the reservoir policy explicitly.
- The firmware grows a scheduler / age-tracker for the reservoir and a soft/hard alarm pair. Modest C++ work.
- The customer-facing install kit grows a one-pager about cleaning and shelf life.
- The vent membrane spec optionally moves from generic hydrophobic PTFE to 0.2 µm sterile-rated PTFE (R6).
- Ring 1 picks up two instrumented questions: (a) "what does month-old reservoir syrup actually look like under our conditions?" and (b) "does the rinse-only clean cycle suffice or does Star San need to be in the kit?"

What this is **not**:

- This is not a regulatory compliance push. [`business/regulatory.md`](../../business/regulatory.md) commits to following standards where they codify safe handling but not pursuing listings. Nothing here requires NSF/ANSI 18 or FDA 21 CFR formal certification at Ring 1 scale. The doc exists for the founder's own engineering rigor and for the customer's reassurance, not for a checklist.
- This is not a pre-sale blocker. Unit #1 can ship with R1, R2 (Policy B at 30 days), R3 (default 30/45-day soft/hard), R5, and R6. R4 is a Ring-1 data-collection question, not a pre-sale decision.

## Effort estimate

- R1 (doc): 1 evening of writing, reusing material already in repo.
- R2 + R3 (policy + firmware): ~1 day of firmware (timestamp tracking + soft/hard alarms + app surfacing) once the integrated firmware track is unblocked (see sibling [`integrated-firmware-gap.md`](integrated-firmware-gap.md)).
- R4 (microbio test plan): ~$200–500 in lab plating fees across Ring 1 installs over six months, plus the founder's coordination time. The cost lives inside the Ring-1 budget, which is uncapped per [`target-market.md:170`](../../marketing/target-market.md) ("ten machines, in real kitchens, used daily, generating real-world data").
- R5 (customer one-pager): a couple of hours, drafted into the install-kit set.
- R6 (vent membrane swap): one supplier search, one re-purchase, no design change.

Total: low single-digit days of work + a small Ring-1 test budget. The leverage is high because this is the doc that answers "is the syrup safe to drink?" — a question every Ring-1 customer will eventually ask, and the founder will be asked in his own kitchen on a Saturday by a friend who is considering a unit.

## Open questions for Derek

1. The PTFE vent membrane's actual pore size — confirmable by reading the LVDALAB datasheet if it exists, or by asking the seller. Without that number, the R6 recommendation defaults to swap-to-0.2µm.
2. SodaStream Pepsi-Co concentrate's current preservative declarations on the label — the public ingredient lists vary by SKU and by year. The R3 default (30 days at 8–15 °C) assumes potassium sorbate at typical commercial dosage; if a SKU lacks sorbate the default tightens.
3. Whether the prototype reservoir (the 1 L Platypus bladder rig per [`future.md:75`](../../hardware/future.md)) has ever sat with concentrate in it for > 14 days — if it has, the founder already has a one-data-point read on what month-old syrup looks like and feels like in this system. Surface it if so.
4. Whether the founder's voice on cleaning matches "every 30 days, here's how" (R5) or something less prescriptive. The doc defaults to prescriptive because Ring 1 customers want to be told.
