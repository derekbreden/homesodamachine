# Front-panel CAD does not exist, and the most-touched customer interaction on the appliance is undefined

**Author:** hourly agent, 2026-05-19 (sixth of the day)
**Status:** prototype-blocker — recommendation only, not for direct execution
**Audience:** Derek, future agents
**Distinct from siblings:**
- Morning sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — post-sale brand-name legal exposure.
- Midday sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — post-sale SKU stockout policy.
- Earlier today [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md) — meta doc; this routine should bias toward the appliance.
- Earlier today [`integrated-firmware-gap.md`](integrated-firmware-gap.md) — firmware-side prototype-blocker (no integrated controller code exists).
- Earlier today [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md) — vessel-side prototype-blocker (pass/fail criteria for hydro undefined).

This doc continues taking the appliance bias seriously. If executed, it commits geometry into [`hardware/printed-parts/enclosure/front-panel/`](../../hardware/printed-parts/enclosure/front-panel/) — the only customer-facing exterior surface where the customer's hands actually live during ownership, and currently the only enclosure face that has **no CAD generator at all**.

---

## TL;DR

[`hardware/printed-parts/enclosure/front-panel/README.md`](../../hardware/printed-parts/enclosure/front-panel/README.md) closes with `Status: Design-in-progress. No CAD generator yet.` Its four Open items are the entire physical interface between the customer and the appliance under the sink:

1. **Cradle / strap / inlet-height geometry** for the customer's 5 lb aluminum CGA-320 CO2 cylinder.
2. **Red accent ring mechanism** (shared open question with the back-panel's blue ring).
3. **WR1110 mounting bracket geometry** against the inner face.
4. **Double-shutoff quick-disconnect** on the inlet to close the "hose not seated when cylinder valve opens" failure mode.

None of these are abstract. The CO2 cylinder is the **only part of the appliance the owner physically handles on a recurring schedule** — every ~6-12 weeks, they disconnect a stranded 5 lb / ~9 lb-full pressurized aluminum cylinder, haul it to a fill station, and reinstall it. That interaction happens inside a kitchen base cabinet, beside the appliance, next to two flavor reservoirs, an electronics shelf, an R-600a refrigerant compressor, and a backflow drip pan with a moisture sensor. It is the single highest-touch, highest-stakes user moment in the entire product, and as of today the geometry that mediates it is one bulkhead and four sentences.

The recent commit `5dd6b2c` moved this surface from "back panel afterthought" to "front-panel source-of-truth" and inherited the underlying issue from [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md): the cylinder lives beside the appliance, the customer sees it, the customer touches it, and the appliance has to make that work. The README captures intent. CAD does not exist.

This is a prototype-blocker because **the front panel cannot be printed**, and the enclosure cannot be assembled, until this geometry lands. Unit 001 is gated on it.

---

## Why this matters now

Two reasons it can't slide to "the week before unit 001 ships":

**1. Print-iteration latency dominates the lead time on enclosure parts.** [`hardware/printed-parts/cold-core/foam-shell/`](../../hardware/printed-parts/cold-core/foam-shell/) carries a print log with three cancelled / re-spun jobs in late April / early May — print bring-up of large-format parts on the Bambu H2C at 0.8 mm nozzle takes 8-14 hours per attempt and converges over multiple iterations. The faucet shell ([`hardware/printed-parts/faucet/touch-flo-shell/`](../../hardware/printed-parts/faucet/touch-flo-shell/), recent commits d38aaaa / b4e6239 / fb4ffd4 logging attempts 10 + 11 and the 3-piece slice) shows the same iteration tail. A panel this big with a cradle feature is plausibly 5+ print iterations before fit-and-feel is right against a real 5 lb cylinder. That is weeks of wall-clock time, not days. Start now.

**2. Several other open items are downstream of this geometry.** [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) Open items §1 (pump-cartridge install method, "tool-free swap via the front-face access door — exact mechanism not specified") and §6 (WR1110 mechanical fixturing, "should add a printed bracket … coordinate with the mechanical doc") both depend on the front panel having a committed geometry to anchor against. So does [`enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md) Open item §5 (the printed build-fixture cradle that holds the chassis upright). Three production-procedure docs reference a front-panel CAD that doesn't exist, which means three procedures are currently un-rehearsable.

Founder Edition cadence (~12 units/year per [`marketing/target-market.md`](../../marketing/target-market.md)) means a hidden iteration loop here delays not just unit 001 but the entire 4-year run by whatever the wall-clock-cost of the loop turns out to be. The procedure-cost of resolving it on paper today is roughly the same as resolving it at the bench in November, with the difference that today's resolution costs filament + time and November's resolution costs filament + time + a stalled chassis on the bench.

The CO2 ownership thread that this routine harvested on 2026-05-18 is one of the few times an hourly recommendation has changed the appliance (per [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md)). The opportunity now is to finish the geometry the inlet-on-the-front-panel decision implied, rather than leave it as four open bullets in a README.

---

## What the README captures, and what's missing from it

### Captured

- The CO2 inlet hardware: DERPIPE 5/16"-tube × 1/4" NPT push-to-connect bulkhead, red accent ring, downstream stack (GASHER check + WR1110).
- The user-experience intent: "fit-and-feel — customer reads 'cylinder goes here' before they read any instructions."
- The pump-cartridge access door coexists on this same face (geometry owned by the cartridge, not the panel).
- Material: Bambu PET-CF (per back-panel material rationale).
- Tube color coding: red CO2 line inlet matches industry beverage convention.
- Internal CO2 routing handoff to [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) §1.

### Missing

Everything dimensional. Specifically:

- **Cylinder geometry envelope.** A 5 lb aluminum CGA-320 cylinder (Catalina / Luxfer / equivalent — the project owns 2 of them, both Airgas pickup per `purchases.md`) is nominally **5.25" OD × ~17.7" tall over the valve, ~9.0 lb fully filled (~4.4 lb tare + 5 lb CO2 + ~0.3 lb regulator)**. The README's parenthetical "~12" tall × ~5" OD" understates the cylinder height; 12" is closer to the body height *below* the cylinder collar, with the valve, primary regulator (TAPRITE E-T742), and gauge stack adding 5-7" on top. The panel CAD has to host the *taller* of those numbers because the regulator stays on the cylinder during refill swaps. Get the dimension right before drawing anything.
- **Recess depth and panel-face protrusion.** Is the cradle a *recess into the panel* (cylinder partially nests into the front face, projecting forward by ~3-4"), or a *shelf bracket forward of the panel face* (cylinder sits entirely in front of the panel, panel face flush)? The choice changes panel thickness budget, print orientation, and the available width remaining for the pump-cartridge access door alongside.
- **Vertical position on the panel.** Cylinder bottom sits on the cabinet floor (per `front-panel/README.md` "Cylinder placement"). What's the front-panel bottom edge height above the cabinet floor? If the panel doesn't extend to the cabinet floor, the cradle is an unsupported cantilever off the panel face only — fine for a 9 lb static load but vibration-loaded over years. If the panel *does* extend to the floor and the cradle blends into the floor edge, the cradle becomes a stable wedge — the cylinder's own weight retains it against the panel.
- **Restraint mechanism.** README enumerates "retention strap or printed cradle"; doesn't pick. Three plausible families:
  1. **Hook-and-loop strap (Velcro One-Wrap or equivalent)** anchored to two captive M3 bosses on the panel. Cheapest. User-replaceable when worn. Tactile and instantly understandable.
  2. **Printed clamshell cradle, hinged + magnetic latch.** Cylinder lifts out without unwrapping. Higher print cost, captures more cylinder length, no fabric to wear.
  3. **Bottom-cradled, top-tethered.** Printed lower cradle for the cylinder base (the heavy end), plus a soft loop or printed clip at the cylinder shoulder. Splits load: shear at the base, lateral retention at the top.
   Founder Edition aesthetic and the customer-actually-handling-this-monthly UX both bias toward (3) over (1); (2) reads as overdesign for a part that is itself just an aluminum tube. Decide.
- **Cylinder bottom support.** The cylinder sits on a base ring (the standard CGA-320 5 lb cylinder has a printed/spun foot ring, ~5.25" OD, ~0.5" tall). That ring sits on *something* — bare cabinet floor (laminate, hardwood, whatever the customer has), or a printed footprint pad off the front panel, or a separate dropped-in tray. Bare cabinet floor is the simplest spec; a printed pad (with a ~5.5" OD pocket, ~0.5" depth, captured into the cradle structure) is what makes "cylinder goes here" obvious without instructions, which is the README's stated intent. Pad-vs-no-pad is a UX decision, not a structural one — say which.
- **CO2 hose tether path.** The 5/16" red beer line tethers from the cylinder-top primary regulator outlet to the DERPIPE bulkhead on the panel. README says "Inlet stub positioned so the cylinder's CGA-320 outlet aligns naturally when the cylinder sits in the recess, keeping the tether short and out of the way." That implies the inlet is *above* the regulator height — meaning ~17.7" above cabinet floor + the regulator stack (call it 22-24" above the cabinet floor). If the front panel doesn't extend that high, the inlet is on a tab or upper region. If it does, the inlet height needs to be *committed*, not "positioned so the cylinder's CGA-320 outlet aligns naturally" — the tether-out-of-the-way condition requires the inlet to be on the same side as the regulator's outlet (and CGA-320 regulators put the outlet on the side opposite the wrench-flat of the cylinder valve, so cylinder orientation in the cradle is a thing the cradle should index).
- **Coexistence with the pump-cartridge access door.** [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) §3 reference: the cartridge is hosted inside the front face. [`hardware/printed-parts/flavor/pump-case/`](../../hardware/printed-parts/flavor/pump-case/) has a generator (recent commits) but no front-panel-facing dimensions in the front-panel README. How wide is the front panel? If the cabinet width is 24" interior (the standard 36" outer × ~2× ¾" face frame × cabinet box), the cylinder takes ~6" with cradle, the pump cartridge access door is plausibly 5-6" wide, leaves 12" for the rest of the panel (vent grilles? a small status display? nothing — the front face has "no thermal duty" per `future.md`). All of this is layout-on-a-rectangle work that has not been done.
- **WR1110 bracket geometry.** [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) Open item §6: the WR1110 hangs off the inboard NPT stub via threads alone. The bracket captures the regulator body to take transport vibration off the NPT joint. The bracket lives against the inner face of the front panel directly behind the DERPIPE bulkhead. Bracket geometry, mounting hardware (M3 SHCS into heat-set inserts), and the printed-part split between the panel and the bracket: not specified.
- **Double-shutoff QD direction of travel.** README Open item §4 names this as "Separate fork working that detail; lands here when committed." A flush-face / double-shutoff QD (Parker FF or CEJN 116 series, in 1/4" tube line) at the front-panel inlet means **the cylinder can be disconnected without venting the in-appliance side and without venting the cylinder-side hose**. That's the difference between "monthly swap involves a hiss of CO2 in the cabinet" and "monthly swap is silent and clean." Customer-touched, monthly. This is the highest-leverage UX upgrade on the appliance and it's currently a fork.

---

## What changes in the repo if this is executed

Per the third sibling's "what would this change" test, the honest answer:

- **New [`hardware/printed-parts/enclosure/front-panel/generate_step_cadquery.py`](../../hardware/printed-parts/enclosure/front-panel/) CadQuery generator.** First-pass geometry: outer rectangle (matched to the enclosure shell's front aperture), DERPIPE bulkhead through-hole at committed (x, z), red-ring boss around it, cylinder cradle features per the picks above, WR1110 bracket as a separate sub-part or printed-in feature, pump-cartridge access door cutout matched to [`pump-case/generate_step_cadquery.py`](../../hardware/printed-parts/flavor/pump-case/generate_step_cadquery.py)'s outboard face.
- **[`hardware/printed-parts/enclosure/front-panel/README.md`](../../hardware/printed-parts/enclosure/front-panel/README.md) status moves from "Design-in-progress. No CAD generator yet." to "Design committed; see `generate_step_cadquery.py`."** Open items 1, 2, 3 close. Open item 4 (double-shutoff QD) stays open as a future enhancement with the panel geometry pre-provisioned to accept it (i.e., the DERPIPE bulkhead hole is dimensioned so a Parker FF QD can be a drop-in replacement on a future revision).
- **[`hardware/printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md) "red ring / blue ring mechanism" open item closes** via the same multi-material decision applied to both panels.
- **[`hardware/assembly/internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) Open items §1 + §6 close** — pump-cartridge install mechanism is implied by the access-door geometry, and the WR1110 bracket has a part to reference.
- **[`hardware/assembly/enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md)** gains the front-panel pre-install step that today's text explicitly defers ("CO2-inlet bulkhead — not pre-installed on the back panel; lives on the front panel … Front-panel pre-install step is a separate procedure (not yet broken out in this doc)"). One new sub-procedure parallel to the existing back-panel one.
- **[`hardware/bom.md`](../../hardware/bom.md)** gains the cradle hardware (one strap, or hinge-pin + magnet for option 2, or a 6 mm strap + 2× M3 captive nuts for option 3), plus the WR1110 bracket's heat-set inserts.

Six files change minimum: one new CadQuery generator, one README status flip, three doc-clarifications, one BOM update. Every one of them was held back by the front-panel geometry being "TBD" — committing the geometry unblocks all of them at once.

---

## Recommendation

Four picks, in order. Each is reversible — the first CadQuery pass is a sketch, not a tooling commitment.

### R1 — Commit the cylinder envelope, in writing, before drawing any panel geometry

Measure or canonically cite the dimensions of the actual cylinders Derek owns (the two Airgas-pickup 5 lb aluminum cylinders from Feb 13 and Apr 13 invoices). Add a `cylinder-envelope.md` (or a section in `front-panel/README.md`) committing:

- Cylinder body OD, body height (collar-to-collar), foot-ring OD + height
- Valve overall height above the cylinder collar (with the TAPRITE primary regulator installed in service orientation)
- Regulator outlet position relative to the cylinder centerline (radial offset + height above collar)
- Cylinder weight (full + empty) — both informative for the cradle load case

Take a tape measure to the cylinder Derek already has in the kitchen. Photograph it next to a ruler. Number-of-significant-figures shouldn't fight the spec; mm precision is more than enough.

This costs ~20 minutes and makes every downstream decision objective rather than approximate.

### R2 — Pick the restraint mechanism, with a stated rationale

Three plausible families above. Default recommendation: **option 3 (bottom-cradled + top-tethered)**, on these grounds:

1. The cylinder is heavy. A bottom cradle takes the static weight off the strap and onto a printed feature, eliminating long-term strap creep.
2. The customer interacts monthly. A top strap (vs. a clamshell) is single-handed, instantly visible, and doesn't require a hinge that can age.
3. The aesthetic intent is "honest hand-built kitchen appliance," not "industrial cylinder cage." A bottom cradle blending into the panel face reads as bespoke; a full clamshell reads as cage.
4. Failure mode under tipping force (someone bumps the cabinet hard): a base cradle wedges the cylinder against the panel even if the top strap fails. A top-only strap fails open if the strap fails.

The strap itself: black 1" nylon webbing + cam-buckle (printed cam, ~2 hours, or off-the-shelf cam buckle ~$3) anchored at two M3 captive nuts on the panel. Replaceable when the webbing visibly fades.

### R3 — Lay out the panel rectangle, in mm, before drawing curved features

Sketch on paper or in a CadQuery scratch pass:

- Cabinet interior width (assume 22"/559 mm working space for a 24" standard base cabinet — confirm against the actual enclosure outer width from [`hardware/assembly/enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md) or the enclosure shell's CAD generator if it exists).
- Cylinder column on one side (~5.5" / 140 mm wide for cylinder + cradle clearance).
- Pump-cartridge access door alongside (width from [`hardware/printed-parts/flavor/pump-case/`](../../hardware/printed-parts/flavor/pump-case/) — read the generator's outer dimensions, don't guess).
- Remaining real estate on the third zone — likely empty per `future.md` "the front face carries no thermal duty," but committing it as labelled-empty is better than leaving it unstated.

Decide which side the cylinder sits on (left or right of the panel). The pump cartridge is more frequently accessed than the cylinder during initial life (peristaltic tubing wears out faster than CO2 runs out in the first year, per [`hardware/future.md`](../../hardware/future.md)). Customer reaches with their dominant hand — assume right-handed and put the cylinder on the right (toward the right cabinet wall, leaving the pump cartridge on the left where it has elbow room).

This is one paragraph of decision-making. The CAD pass that follows is mechanical.

### R4 — Draft `generate_step_cadquery.py` against R1-R3 and iterate against print

Build the first CadQuery pass with:

- Outer rectangle matching the enclosure shell's front aperture.
- DERPIPE bulkhead through-hole at committed (x, z), with the red-ring boss formed in PET-CF (multi-material is not strictly required if the boss is a separate snap-on TPU collar — see back-panel's pending decision on the same question).
- Cylinder cradle on the chosen side: a contoured pocket matching the cylinder body OD (with 0.5-1 mm clearance for slip-in), 30-50 mm deep, with the pocket bottom doubling as the foot-ring rest if the panel extends to the cabinet floor. Two M3 captive-nut pockets at the strap anchor points.
- Pump-cartridge access door cutout on the opposite side, matched to the cartridge generator's outboard rectangle.
- WR1110 bracket as a back-of-panel printed feature: two M3 SHCS captures clamping the regulator body, with the regulator long axis vertical against the panel inner face. Bracket height + bracket-to-NPT-stub offset land per the WR1110's body geometry (32 mm × 32 mm × 84 mm aluminum-block envelope per its data sheet).
- A `print-log.md` in the same directory tracking iteration history, same convention as `foam-shell/print-log.md` and `touch-flo-shell/print-log.md`.

First print: print just the cradle column at scale (not the full panel) on the H2C — ~3-4 hour print at 0.4 mm nozzle — and fit-test the cradle against the actual cylinder before printing the full panel.

---

## What this doc is *not* asking for

- Not asking to commit the double-shutoff QD (Open item §4). That fork stays open. The recommendation above is to **pre-provision** the inlet bulkhead so a future swap to a QD is mechanically possible without re-printing the panel. The current DERPIPE PTC stays in service for unit 001.
- Not asking to redesign the cylinder. Airgas 5 lb aluminum CGA-320 is committed in `purchases.md`. The panel adapts to the cylinder, not the other way around.
- Not asking to relocate the pump-cartridge access door. Its position on the front face is committed at the [`pump-case/`](../../hardware/printed-parts/flavor/pump-case/) level. The panel adapts to the cartridge.
- Not asking to commit to PET-CF for the cradle features. The cradle is a load path; PETG (or PET-CF, the panel's material) both work for a 9 lb static load and a short-duration impact from a bumped cylinder. Match the panel material.
- Not asking to add a status display, indicator LED, or any front-face electronics. The thermal-duty argument in `future.md` and the user-element location in `future.md` "User-facing elements, by location" both put status / displays *above counter* (RP2040 round display) rather than on the under-counter front face. The front face stays connection-management + cylinder cradle + pump cartridge.

---

## The single thing

If this collapses to one sentence:

> The customer's hands live on the front face every month for the life of the appliance — commit the cylinder envelope, pick the restraint mechanism, lay out the rectangle, and draft `generate_step_cadquery.py` for the front panel **before** the next enclosure print cycle, so the most-touched physical surface on the product gets the same multi-iteration print convergence that the cold-core shell and the faucet shell are already getting.

Everything else is implementation detail.
