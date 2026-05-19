# Foam-pour procedure for the cold core is undefined, and the pour is single-shot, irreversible, and scraps a fully-built welded vessel + coil + reservoirs if it fails

**Author:** hourly agent, 2026-05-19 (seventh of the day)
**Status:** prototype-blocker — recommendation only, not for direct execution
**Audience:** Derek, future agents
**Distinct from siblings:**
- [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — marketing/legal exposure (no physical bench impact).
- [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — post-sale SKU stockout policy.
- [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md) — meta doc: **"bias toward the appliance."** This doc takes that bias.
- [`integrated-firmware-gap.md`](integrated-firmware-gap.md) — firmware-side prototype-blocker (electronics).
- [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md) — vessel-side prototype-blocker (wet bench, vessel pressure).
- [`front-panel-cad-gap.md`](front-panel-cad-gap.md) — enclosure-front-CAD prototype-blocker.

This doc is the **cold-core-side** prototype-blocker that pairs with the firmware-side, the vessel-side, and the front-panel-side. It commits changes to [`hardware/assembly/cold-core.md`](../../hardware/assembly/cold-core.md) — the procedure that turns a hydro-tested vessel + wound coil + two reservoirs into a foam-poured cold core ready for refrigerant integration. Unit 001's cold core is gated on it.

It is also the only step in the integrated-build procedure whose **failure mode is destruction of every upstream input at once**. Hydro fails → reweld and re-test the vessel. Firmware bug → reflash. Front-panel print fails → reprint the panel. Foam pour fails into a populated cold-core body → scrap the welded passivated 316L vessel + the wound 22-ft 0.031" wall coil + both food-contact PETG reservoirs + the printed shell stack, because the foam has cured around them and the assembly is monolithic. The economic and schedule asymmetry here is larger than any other single step in the build.

---

## TL;DR

[`hardware/assembly/cold-core.md`](../../hardware/assembly/cold-core.md) step 5 commits the body pour as **"Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Y top — all at once, no cap on, no down-channels."** Step 2 commits the cap pours as 16 mm cups with a Ø10 mm pour hole and two Ø6 mm vents in the foam_cap_lid. Step 6 commits the M3 × 25 SHCS cap close-out.

That is the entire procedural commitment. Everything below is undefined:

1. **Per-pour batch volume.** No mL target for any of the three pours. The graduated mixing cups (Pouring Masters 5 oz / 150 mL, ACQUIRED, [`bom.md`](../../hardware/bom.md) §6) and stir sticks (JMU 6", ACQUIRED) are committed, but the procedure does not say how many cups to pour per pour, how much Part A and Part B per cup, or what fraction of the 1 qt kit gets consumed per appliance.
2. **Mix-ratio precision tolerance.** "Mix 1:1" is committed. The Fiberglass Supply Depot 2 lb kit instructions (which the project has not yet read — see open item #1 in [`cold-core.md`](../../hardware/assembly/cold-core.md)) will state a tolerance window. Two-part PU foams typically tolerate ±5–10% on volumetric ratio before mechanical properties degrade noticeably; gross off-ratio (>15%) gives brittle iso-heavy foam (Part A excess) or tacky never-cures (Part B excess). The procedure does not commit either the spec tolerance or a measurement protocol that achieves it.
3. **Pot life / rise time / cure time.** Not in the procedure. For 2 lb density marine pour foam these numbers are typically 30–60 s cream time, 90–120 s rise time, 5–10 min tack-free, 24 h full cure — but the actual Fiberglass Supply Depot datasheet is the source of truth and it has not yet been transcribed into the procedure. **Pot life is the binding constraint on whether the body pour can be made as a single 150 mL batch or has to be split.**
4. **Pour-temperature window.** Both parts and the substrate (the assembled shell stack) need to be in the manufacturer's specified temperature range for the cure to proceed correctly. The procedure does not commit a target, does not commit a measurement, and does not commit a wait-state if the kitchen/garage is out of window.
5. **Exotherm management.** 2 lb closed-cell PU foam reaches ~70–90 °C peak exotherm in free-rise pours, and confined or large-section pours can run hotter (~100–110 °C in the worst quartile). PETG glass transition is ~80 °C; PET-CF is higher. The body pour's foam zone has thick sections (the 16 mm outer foam gap × 213.4 mm height × ~700 mm developed perimeter ≈ 2.4 L of foam, mostly in 16 mm thickness, plus larger reservoir-pocket cavity volume) where the exotherm peak could approach or exceed PETG Tg. **There is no documented thermal verification of the printed PETG shells' tolerance to the actual pour exotherm.** A shell that softens at the exotherm peak deforms permanently around the vessel/reservoirs and the cold core is scrap.
6. **Pre-pour readiness gate.** Step 4 enumerates the installs (vessel, coil, reservoirs, three copper plugs, seven penetrations) but does not enumerate a verification checklist before the pour starts. Are all tube exits seated? Is the CO2 PP0308E elbow seated correctly under the −Z support arch (step 4 calls out the install-order trap but step 5 doesn't gate on its outcome)? Are the M3 ruthex inserts pressed (step 3) before the body assembly (step 4), or is that re-checked at step 5?
7. **Pour-completion verification.** The procedure says foam falls in and reaches all cavities "in parallel." It does not say how to verify the pour actually filled. Visual inspection from the +Y top sees only the surface; voids at the bottom of the 0.5 mm coil-to-wall radial gap or in the reservoir-pocket cavity floors are invisible. The procedure does not commit a verification method (mass-balance check from the cup residue? post-cure tap test? destructive section on the first build only?).
8. **Failure-handling decision tree.** Open item #2 names "trim method after cure" but the procedure has no decision tree for *what counts as scrap*. If the body pour visibly under-fills, can a top-up pour be added through the +Y opening before the cap goes on? If the exotherm warps a shell wall, can the wall be reflowed or is the core scrap? If the foam ratio was off, is the resulting brittle/tacky foam usable or scrap?
9. **Mock pour / dry run.** No practice pour is committed before Unit 001. The foam kit arrived 3 days ago (Sat May 16, [`purchases.md`](../../hardware/purchases.md) §11). The procedure as written sends a $200+ welded-vessel + $40 wound coil + $40 of food-contact PETG reservoirs into the irreversible step **on the first attempt the operator (Derek) has ever made with this specific foam kit, into this specific shell geometry**. Two-part PU foam is operator-skill-sensitive — the difference between a good pour and a void-laden pour is in the first 60 seconds of handling, and that skill is not transferable from reading a procedure.
10. **PPE and safety scope.** Step 4 of the table commits nitrile gloves (ACQUIRED) as a foam-pour consumable, on a "1 pair per build" basis, because the isocyanate component is a skin sensitizer. The procedure does not commit respiratory protection. PU foam mixing releases isocyanate vapor (volatile MDI), and the cure exotherm aerosolizes additional vapor through the +Y opening for several minutes. ACGIH TLV for MDI is 0.005 ppm (8-hr TWA) and 0.02 ppm (STEL). The procedure does not commit ventilation (open-air? fume hood? respirator?), and a kitchen counter or garage workshop pour without ventilation is over the STEL on a typical-volume pour. The procedure also does not commit trim PPE for cured-foam dust (a respirable nuisance dust; cured PU is not toxic but the dust is sensitizing on prolonged exposure).

These ten gaps gate Unit 001's cold core from "every input ready" to "shippable foam-poured core." The procedure of record, as written, will pour Unit 001 on whatever process Derek improvises in the moment, against a kit he has not yet bench-tested. **It will probably work on the first try anyway** — millions of marine pour-foam jobs are completed by amateurs every year against thinner instructions. The question is the *expected value* of pour #1 versus pour #2 versus pour #3, given that pour #1 carries roughly $300 of consumed inputs above the foam itself and ~12 hours of build labor (vessel weld + hydro + passivation + coil wind + shell prints + reservoir prints + body-side assembly), and pour #2 carries the same plus the cost and lead time of a second batch of every upstream input.

The single highest-EV change is to *do a mock pour first*, against a stand-in shell stack that does not contain the vessel/coil/reservoirs, and lock the per-pour batch volume, mix protocol, pot-life budget, and exotherm-vs-PETG-Tg behavior before pour #1 of Unit 001.

---

## Why this matters now

The foam kit ([Fiberglass Supply Depot 2 lb 2-part closed-cell PU foam, 1 qt kit, B08R7TX8QJ](../../hardware/purchases.md), $42.89 delivered) arrived Sat May 16. The Bambu H2C print of the foam-shell is on its 4th attempt per [`foam-shell/README.md`](../../hardware/printed-parts/cold-core/foam-shell/README.md) "Print history" — once that prints clean, every upstream input is ready and the build cadence stops blocking on parts and starts blocking on procedure. The cap pours (steps 2) can run in parallel as soon as the foam-cap and foam-cap-lid prints are off the bed; the body pour (step 5) runs as soon as the body assembly (step 4) is complete.

In other words: this gap is the *next* thing that blocks Unit 001, and it blocks it within days, not weeks. None of the other six siblings today gate the build on this timeline.

The foam kit is also the input where the project has the lowest practical experience. The hydro test (sibling [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md)) covers a procedure Derek has approximated on the touch-flo-shell weld bench multiple times. The firmware (sibling [`integrated-firmware-gap.md`](integrated-firmware-gap.md)) is a port of a 3,781-line working prototype codebase. The front-panel CAD (sibling [`front-panel-cad-gap.md`](front-panel-cad-gap.md)) is a new generator of the same kind already written for the back panel. The foam pour, by contrast, has zero prior bench experience in this repo — no welding-log-style attempt-by-attempt record, no calibration photos, no scrap pours.

The asymmetry between "5 minutes to pour" and "12 hours and ~$300 of consumed inputs upstream of the pour" is what makes this the single highest-leverage place to *not* trust the first attempt.

---

## What the repo commits today

### 1. Materials

[`hardware/bom.md`](../../hardware/bom.md) §6 and [`hardware/purchases.md`](../../hardware/purchases.md) §11:

| Item | Source | Status |
|---|---|---|
| Fiberglass Supply Depot 2 lb 2-part closed-cell PU foam, 1 qt kit | [B08R7TX8QJ](https://www.amazon.com/dp/B08R7TX8QJ) | ON-ORDER → delivered Sat May 16 |
| Pouring Masters 5 oz / 150 mL graduated mixing cups (50-pk) | [B08JHH1DBF](https://www.amazon.com/dp/B08JHH1DBF) | ACQUIRED |
| JMU 6" tongue depressors, individually wrapped (100-pk) | [B09H6ZP447](https://www.amazon.com/dp/B09H6ZP447) | ACQUIRED |
| SUP 4 mil nitrile exam gloves, XL (50 pairs) | [B0G8SSMVKW](https://www.amazon.com/dp/B0G8SSMVKW) | ACQUIRED |

The kit yield claim from [`bom.md`](../../hardware/bom.md) §6: *"1.25 ft³ yield covers inner + outer shells with margin"* — i.e. ~35 L of cured foam from one $42.89 kit. Per-appliance consumption (see math below) is ~5–6 L. **One kit covers ~6 appliances of foam** at the spec ratio, and the spec ratio is what the procedure has to hit.

### 2. Geometry

[`hardware/printed-parts/cold-core/foam-shell/README.md`](../../hardware/printed-parts/cold-core/foam-shell/README.md):

- Total cold-core envelope: ~251 × 181 × 213.4 mm = ~9.7 L geometric volume.
- Pressure vessel occupied volume: Ø127 mm × 152.4 mm tall = ~1.93 L.
- Two reservoirs occupied volume: ~1.18 L each × 2 = ~2.36 L.
- PETG shell wall material: ~996 mL of foam-shell solid per README §"volume" line 524.
- Net foam zone (body pour): ~9.7 − 1.93 − 2.36 − 1.0 = **~4.4 L** of foam-fill volume in the body.
- Cap pour zones: 16 mm tall × ~footprint of ~245 × 175 mm (minus boss + lid pour-hole pillar) ≈ **~600 mL each cap**, ~1.2 L total across both caps.
- **Per-appliance foam consumption: ~5.6 L cured foam ≈ 187 mL mixed liquid at 30:1 free-rise expansion ratio** (typical for 2 lb density).
- One pour-cup batch (mixing 75 mL Part A + 75 mL Part B in a 150 mL Pouring Masters cup) yields ~150 mL mixed → ~4.5 L cured foam — **fits the body pour in one batch**.
- Each cap pour needs ~600 mL cured ÷ 30 = **~20 mL mixed = 10 mL Part A + 10 mL Part B per cap**, well below a single 150 mL cup.

These numbers are first-principles estimates from the geometry README, not the kit datasheet. The kit datasheet free-rise number could be 25:1 or 35:1; the actual rise inside the constrained body cavity is lower than free-rise. **A 1.5× safety factor on batch volume is the minimum responsible margin until the kit's actual rise is measured.**

### 3. Three-pour cadence

[`cold-core.md`](../../hardware/assembly/cold-core.md) step 5 commits "single top-down body pour, all at once, no cap on, no down-channels." [`foam-shell/README.md`](../../hardware/printed-parts/cold-core/foam-shell/README.md) §"Assembly and foam pour" commits the same with explicit named foam paths (the ±Z gaps at x ∈ [−39.7, +39.7] where the pockets' ±Z walls end, the centerward-wall transition arcs, and the 0.5 mm radial gap behind the coil).

The two cap pours are independent of the body pour (step 2 in [`cold-core.md`](../../hardware/assembly/cold-core.md), can run in parallel, before the body assembly). Cap pour-and-vent geometry: Ø10 mm pour hole + 2× Ø6 mm vents in the `foam_cap_lid` ([`foam-shell/README.md`](../../hardware/printed-parts/cold-core/foam-shell/README.md) line 157).

### 4. Open items

[`cold-core.md`](../../hardware/assembly/cold-core.md) "Open items":

1. *"Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window). Vendor is committed... still needs to be read and the numbers locked into this doc once the kit is in hand."* — **The kit is now in hand**, 3 days ago. The data-sheet read has not happened.
2. *"Trim method after foam cure. What gets flush-cut, with what — knife, oscillating tool, both depending on location."*
3. (Reservoir-internal assembly, unrelated to this doc.)
4. (Reservoir final qualification, unrelated.)

That is the complete documented gap surface. The ten-item TL;DR above expands the implicit gaps that the open-item list does not name.

---

## What's missing, in execution order

### A. Read the datasheet, transcribe the binding numbers

The Fiberglass Supply Depot 2 lb pour foam comes with a single-sheet instruction insert and an MSDS / SDS. The binding numbers to extract and commit into [`cold-core.md`](../../hardware/assembly/cold-core.md) Open Items §1 closure:

1. **Mix ratio.** 1:1 by volume? 1:1 by weight? (Volume-equal is most common for 2 lb density; weight-equal is occasionally specified.)
2. **Mix tolerance.** ±5%? ±10%? Failure modes off-spec (brittle vs. tacky vs. shrinkage).
3. **Pot life (cream time).** Time from mix-start to first visible expansion. Typically 30–60 s for 2 lb density.
4. **Rise time.** Time from pour to fully-risen. Typically 90–180 s.
5. **Tack-free time.** When the surface no longer transfers material to a glove. Typically 5–10 min.
6. **Full cure time.** When mechanical properties stabilize. Typically 24 h.
7. **Pour-temperature window.** Substrate + components. Typically 70–85 °F (21–29 °C).
8. **Exotherm peak.** Datasheet may or may not state. If not, an instrumented mock pour (a single thermocouple at the midpoint of a 16 mm × 200 mm × 200 mm test pour) measures it.
9. **Free-rise expansion ratio.** Typically 25–35× for 2 lb density. Sets the safety-factor floor on batch volume.
10. **PPE / ventilation.** Vapor inhalation hazard, isocyanate skin sensitization, dust hazard during trim. Specifies what respirator type (if any) and what ventilation rate.

Transcribe these into a new subsection of [`cold-core.md`](../../hardware/assembly/cold-core.md) between Step 4 and Step 5, titled **"Foam material spec (Fiberglass Supply Depot 2 lb, B08R7TX8QJ)"**. One short paragraph per binding number.

### B. Mock pour #1 — free-rise calibration

Mix 10 mL Part A + 10 mL Part B in one Pouring Masters cup, on a cardboard surface, in PPE, outdoors or in a well-ventilated garage. The goal is *measurement*, not output:

1. **Mark the cup at 10 mL pre-mix.** Confirm the volume scale on the cup matches the spec ratio.
2. **Mix for 15 s with a tongue depressor, watching a stopwatch.** Note cream-onset time.
3. **Pour onto the cardboard immediately after mix stops.** Watch rise. Note rise-end time.
4. **Measure final cured-puck volume against the 20 mL mixed-liquid input.** Expansion ratio is the actual one for this kit and operator.
5. **Discard.** Mock #1 is for calibration only, not for production.

Expected outputs: actual cream time (binding constraint #1 on body-pour batch strategy), actual expansion ratio (binding constraint #2 on batch volume), actual exotherm warmth-to-touch (gross check on whether PETG Tg is at risk).

### C. Mock pour #2 — geometry-bounded fill, scrap shell

Print a **mock outer_shell + tank_support_ring** in cheap PLA (or use the first attempt of the H2C foam-shell that's already a scrap from one of the four print attempts in [`foam-shell/README.md`](../../hardware/printed-parts/cold-core/foam-shell/README.md) "Print history"). Skip the reservoirs and the vessel — drop in stand-ins (a 5" OD PVC cap + two cardboard rectangles in the reservoir pockets) to represent the displaced volume.

Mix 75 mL + 75 mL = 150 mL of mixed liquid in a single Pouring Masters cup. Pour through the +Y opening as the procedure specifies. Observe:

1. **Does the pour visibly traverse the centerward-wall transition arcs and reach the back of the coil envelope before gel?** If not, the geometry-vs-pot-life budget is too tight and the procedure must change (e.g., split into two cups, or pre-warm the shell to slow cream onset, or use a different foam with longer pot life).
2. **Does foam exit through the 0.5 mm tube clearances in the +Z slot at a rate that drains headspace before fill completes?** If yes, the slot needs pre-taping (kapton or aluminum) before the pour.
3. **Does the PLA stand-in shell deform from exotherm?** Both PLA (Tg ~60 °C) and PETG (Tg ~80 °C) have margin issues at 70–90 °C exotherm. A PLA mock-shell deformation is informative — it sets a lower bound on the PETG shell's risk. If the PLA mock-shell doesn't deform, the PETG shell is almost certainly safe. If it deforms severely, the PETG shell is in the danger zone and the body pour needs to be split or a longer-pot-life foam should be sourced.
4. **Section the mock after 24 h cure.** Cut with a hacksaw or bandsaw through the cured assembly to inspect for voids — particularly behind the coil, in the reservoir-pocket cavity floors, and at the bottom of the 16 mm outer foam gap.

This is the single pour that has the highest information-per-dollar in this entire program. It costs one cup, ~150 mL of foam (~3% of the kit), and a couple hours. It de-risks the irreversible step on Unit 001.

### D. Mock pour #3 — cap pours

Same protocol, on a scrap foam-cap + foam-cap-lid print. 10 mL + 10 mL into one cup, poured through the Ø10 mm pour hole, watch the rise come out the two Ø6 mm vents. Confirm that the cap fills before gel, that the vents pass the bypass air, and that the cap surface trims flush after cure.

This is the easiest of the three pours and the lowest-risk; mock it last, because if A/B/C succeed, this almost certainly works on first attempt. But running it as a third mock generates the *handling experience* Derek needs before pour #1 of Unit 001, on the same kit's chemistry, at the same workshop temperature.

### E. Lock the procedure into [`cold-core.md`](../../hardware/assembly/cold-core.md)

After mocks A–D, [`cold-core.md`](../../hardware/assembly/cold-core.md) gets a 4-section rewrite of Step 2 + Step 5:

1. **Pre-pour readiness checklist** (10 items): all tube exits seated, three copper plugs slid in, M3 ruthex inserts pressed top + bottom, PP0308E elbow seated in the −Z support arch, both reservoirs seated in pockets, vessel seated on tank_support_ring, +Z slot tube-clearance bands taped (kapton, per mock C result), workshop temperature in window, PPE on (gloves + respirator + ventilation confirmed), stopwatch on bench.
2. **Per-pour mix protocol** for each of cap × 2 and body × 1: cup count, Part A mL per cup, Part B mL per cup, mix-stick stir count (e.g., 30 s with 60 stirs), cream-onset stopwatch target, pour start time relative to mix end.
3. **Pour execution** for each: pour location (cap pour hole / body +Y open top), pour rate (e.g., "decant in one continuous stream over 5 s"), what to watch for during rise.
4. **Pour pass/fail criteria** (10 items): visible fill at vents (caps), no shell deformation observed, no leakage past taped slot bands, exotherm-peak surface temp ≤ 70 °C measured at the outer_shell OD with an IR thermometer, surface trimmable flat after cure, no voids visible at trim, …
5. **Failure-mode triage**: under-fill (top-up before tack-free? scrap?), over-exotherm shell deformation (scrap), off-ratio brittle/tacky (scrap or salvage based on extent), foam in the wrong cavity (scrap), …

Step 6's open item #2 ("trim method after foam cure") gets resolved by the mock-D experience: oscillating tool for outer trim, hobby knife for tight corners around tube exits, sanding sponge for the surface-finish on visible top edge.

### F. Commit a one-shot exotherm-Tg verification

Independently of the pour procedure: print a 16 mm × 200 mm × 200 mm slab of the same H2C PETG used in [`foam-shell/README.md`](../../hardware/printed-parts/cold-core/foam-shell/README.md). Pour 150 mL of mixed 2-part foam into a cardboard mold on top of it. After 30 min, measure permanent deformation against a flat reference. This is the gold-standard answer to "does the body-pour exotherm warp the PETG shell?" — pass = the pour procedure is safe; fail = the body pour must be split into smaller batches with cooldowns between, or the foam-shell must be reprinted in a higher-Tg material (PET-CF, ASA, or PC), or the foam vendor must change.

The H2C PETG shell on the cold core represents ~$50 of print time + filament (per [`bom.md`](../../hardware/bom.md) §7) and a multi-day print queue. Sacrificing one 200×200×16 mm slab to verify its exotherm tolerance is trivially worth it.

---

## What good looks like — closing this gap

When this recommendation is fully landed, the following is true:

1. [`cold-core.md`](../../hardware/assembly/cold-core.md) Open Items §1 is closed: the data-sheet binding numbers (mix ratio + tolerance, pot life, rise, cure, exotherm, expansion ratio, temperature window, PPE) are transcribed into the procedure.
2. [`cold-core.md`](../../hardware/assembly/cold-core.md) §2 (cap pours) is rewritten with explicit per-cup volumes, mix protocol, pour execution, and pass/fail criteria.
3. [`cold-core.md`](../../hardware/assembly/cold-core.md) §5 (body pour) is rewritten the same way, with the additional pre-pour readiness checklist and explicit failure-mode triage.
4. [`cold-core.md`](../../hardware/assembly/cold-core.md) §6 Open Items §2 is closed: trim method is committed per surface.
5. A new doc — perhaps [`hardware/foam-pour-log.md`](../../hardware/foam-pour-log.md) — captures the four mock pours' actual results (cream time, expansion ratio, exotherm temp, fill traverse observation, scrap-shell deformation) the same way [`welding-progress-2026-05-01.md`](../../hardware/welding-progress-2026-05-01.md) and [`welding-progress-2026-05-09.md`](../../hardware/welding-progress-2026-05-09.md) capture the weld attempts. Calibration evidence on the workbench.
6. The first appliance ([Unit 001](../../hardware/build-readiness-2026-04-26.md)) body pour is the *fifth* pour Derek has made with this kit, not the first.

---

## What this is not

This doc is not a substitute for the procedure itself. It is the list of gaps and the order to close them. The actual procedure rewrites belong in [`cold-core.md`](../../hardware/assembly/cold-core.md), the calibration data belongs in a new pour-log file, and the failure-handling decisions belong to Derek with the cured foam in front of him.

This doc is not pushing for an ASME or NSF-level qualified pour procedure. The cold core is a sealed dry-foam interior — there is no food-contact, no pressure containment, no regulated process. The bar is "the foam fills the cavity and the shell doesn't warp," and that bar is reachable in four mock pours of one cup each.

This doc is not in conflict with sibling [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md). The routine-meta sibling argues the hourly routine should bias toward the appliance and away from post-sale operations docs. This doc takes that bias seriously: every recommendation here lands a change in [`hardware/`](../../hardware/) and moves the integrated build forward in days, not the four-year Founder Edition arc. This is the appliance bias making contact with the next unrepairable step.

---

## R1 — Will this recommendation, if executed, change the appliance?

Yes. Closing this gap commits:

- A re-read of one purchased kit's instruction sheet and the transcription of ~10 numbers into [`cold-core.md`](../../hardware/assembly/cold-core.md).
- Four mock pours consuming ~200 mL of foam total (~4% of one $42.89 kit) and producing one calibration document.
- A rewrite of [`cold-core.md`](../../hardware/assembly/cold-core.md) §2, §5, §6 to include per-pour batch volumes, pre-pour readiness, pour execution, and failure-mode triage.
- One thermal verification slab pour confirming the H2C PETG shell tolerates the exotherm.

The unblocked downstream is: Unit 001's cold core can be foam-poured with the *expected outcome* being that pour #1 of Unit 001 is the fifth confident pour Derek has made with this kit, not the first one ever. The asymmetric-downside step in the integrated build becomes a routine step.

---

## R2 — Why the appliance fails without this

If pour #1 of Unit 001 goes badly — voids, exotherm-warped shell, off-ratio brittle foam, leakage past the +Z slot before fill completes — the recovery path is:

1. Re-weld and re-hydro a fresh vessel ([`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md), ~$30 of stock + a day of bench time).
2. Re-wind 22 ft of fresh GOORY ACR copper coil ([`bom.md`](../../hardware/bom.md) §5, ~$10 of consumed tubing + 30 min).
3. Reprint two reservoirs and the foam-shell stack ([`bom.md`](../../hardware/bom.md) §7, ~$50 of filament + multi-day print queue).
4. Repeat steps 1–4 of [`cold-core.md`](../../hardware/assembly/cold-core.md) (vessel install, foil tape, coil install, ruthex insert press, full body-side install — ~6–8 hours).
5. Re-pour.

That recovery path costs ~$100 of consumed inputs and 3–7 days of calendar time, against ~$8 of consumed foam (4% of the kit) for the four-mock-pour calibration. The recommendation is to spend the $8.

If pour #1 of Unit 001 goes well anyway — which is the most likely single outcome — the four mocks were not wasted: they produced a pour log that the next 49 Founder Edition units will draw on, and they produced the calibration data that the future Standard Edition production batch needs. Mock-pour skill is a per-operator asset, not a per-unit cost.

---

## Out-of-scope for this doc

- The reservoir-internal assembly procedure ([`cold-core.md`](../../hardware/assembly/cold-core.md) open item #3) is upstream of the cold-core foam pour and out of scope here.
- The refrigerant-loop integration ([`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md)) is downstream of the cold-core pour and out of scope here.
- The hydro test acceptance criteria for the vessel that feeds into this procedure are covered by sibling [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md).

---

## One-paragraph close

The cold-core foam pour is the single step in the integrated build whose failure mode destroys every upstream input simultaneously and whose procedure has the least bench experience anywhere in the repo. The kit is in hand, the geometry is committed, the math is straightforward, and the irreversibility is total. Four mock pours and one thermal verification slab — consuming ~4% of one $42.89 kit and a Saturday — turn pour #1 of Unit 001 from a coin flip into a routine step. Do them.
