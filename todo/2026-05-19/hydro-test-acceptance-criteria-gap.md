# Hydro test pass/fail criteria + failure handling are undefined for the carbonator vessel

**Author:** hourly agent, 2026-05-19 (fifth of the day)
**Status:** prototype-blocker — recommendation only, not for direct execution
**Audience:** Derek, future agents
**Distinct from siblings:**
- Morning sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — post-sale brand-name legal exposure.
- Midday sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — post-sale SKU stockout policy.
- Earlier today [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md) — meta doc; this routine should bias toward the appliance.
- Earlier today [`integrated-firmware-gap.md`](integrated-firmware-gap.md) — firmware-side prototype-blocker (no integrated controller code exists).

This doc takes the appliance bias seriously. If executed, it changes [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) — the procedure that gates unit 001's vessel from "welded" to "shippable." It is the bench-side prototype-blocker that pairs with the firmware-side prototype-blocker.

---

## TL;DR

[`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) step 6 commits the hydro test rig (BEAMNOVA pump + SENCTRL gauge + ChillWaves plugs, all ACQUIRED), commits the test pressure (180 PSI ≈ 2× the 90 PSI working pressure), and commits the hold duration (30 min). It does not commit:

1. **A PSI-drop tolerance over the 30-min hold.** Working position is "no visible drop." The SENCTRL is a 2.5" 0–200 PSI glycerin gauge — eyeball-readable to ~1–2 PSI on a good day. "No visible drop" is operationally undefined at this gauge resolution.
2. **A failure-handling decision tree.** The Open item enumerates three failure modes (re-weldable bead weep, scrap-grade HAZ weep, threaded-port leak) but does not commit which mode triggers which action, how many repair iterations are allowed, or what failure case sends a vessel to investigation vs. the recycle bin.
3. **Post-hydro visual inspection.** Step 6 says "no visible weep at welds or threads." It does not commit *with what inspection aid* (naked eye? loupe? soap-bubble solution?), *at what timing intervals*, and *against what observation rubric*.

These three gaps gate unit 001's vessel from "welded" to "shippable." Without them, the procedure passes whichever vessel the operator (Derek) feels good about that day, and a marginal vessel that should have been re-welded ships into the cold-core pour where it becomes unrepairable.

The procedure-of-record problem is small and tractable. Brewery bright-tank and ASME B31 hydro-test practice gives well-rehearsed answers; the specific values for this geometry (~6 L total internal volume, 0.065" 316L wall, four 1/4" NPT ports, single circumferential plate-to-tube weld at each end + one internal tack on the float rod) follow from standard practice once the standards are picked.

---

## Why this matters now

The hydro test is the *only* destructive-or-decisive test the vessel sees before it enters the cold-core foam pour ([`cold-core.md`](../../hardware/assembly/cold-core.md)). After the pour, the vessel is bonded to the evaporator coil under aluminum foil tape and surrounded by two-part closed-cell polyurethane. A weep discovered after that point requires destroying the cold core to access the vessel — *and* the foam pour is a one-time wet operation that re-binds when you try to re-cast it. Hydro is the last point at which a marginal vessel is cheaper to re-weld than to scrap-and-restart.

Sibling [`integrated-firmware-gap.md`](integrated-firmware-gap.md) covers what the controller needs to know to actually run on the integrated build. This doc covers what the *vessel itself* needs to satisfy to be allowed onto an integrated build at all. Both gate unit 001 from a different direction.

Founder Edition cadence (~12 units/year, [`marketing/target-market.md`](../../marketing/target-market.md)) means that one bad vessel decision compounds into a month of build time lost. The procedure cost of catching it at hydro is ~$1 of citric acid and ~$5 of wire-fill repair, vs. ~$60 of vessel stock + 4 weld hours + 1 hr cold-core teardown if it's caught after foam.

---

## Evidence the gap is real and unaddressed elsewhere

`grep -rn "PSI drop\|psi drop\|pressure decay\|pressure decrease" hardware/` returns nothing in any committed doc. `grep -rn "soap.bubble\|Snoop\|leak.detector solution" hardware/` likewise. The decision-tree language ("re-weld vs. scrap," "investigation cell," "rework limit") doesn't appear either. There is no policy document, no inherited brewery SOP, no upstream reference.

The closest relevant doc is [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) §163, which explicitly cross-references the same gap:

> *"This mirrors the same gap in [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) 'Open items' §2 at hydro-test — the same decision tree should apply across both gates and ideally lives in one place once committed."*

Two gates blocked on the same missing policy.

The post-hydro pneumatic check is mentioned in step 6 (Milton 727 air-plug rig) but the procedure isn't expanded — "post-validation rig" is the entire spec.

---

## Recommendation

Four committed values + one decision tree + one inspection rubric. All written into [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) step 6. None of this requires new hardware purchases.

### R1 — Commit a PSI-drop tolerance, with thermal-stability gating

Add to step 6:

> **Pass criterion 1 (pressure):** SENCTRL gauge reads ≥ 175 PSI at t=30 min, having started at 180 PSI at t=0. Maximum allowable drop is **5 PSI** (one minor division on the 0–200 PSI dial, the practical limit of unaided eye resolution on this gauge). Bench ambient must hold within ±2 °F across the 30-min window; record bench thermometer at t=0, t=15, t=30. If ambient drifted more than 2 °F, the test is inconclusive — re-run after thermal stabilization, do not pass or fail on the gauge reading alone.

The 5 PSI / 30 min number (~2.8 % / 30 min, ~5.5 % / hour extrapolated) is consistent with brewery bright-tank practice on 15–60 PSI design vessels and well inside ASME B31.9 hydrotest convention ("no observable drop" interpreted against gauge resolution, typically <1 %/10 min). It is also tight enough that a real leak (a single weld pinhole at ~0.1 mm equivalent diameter at 180 PSI) drops the gauge well below 5 PSI in 30 min, so the criterion has positive discrimination.

The thermal-stability clause exists because pure water with a well-bled rig has very low compressibility: in a perfectly rigid steel vessel with zero entrained air, ΔP ≈ 36 PSI per °F of water temperature change. Real rigs have ~0.5–1 % trapped air that buffers the swing down to ~5–10 PSI/°F, but the test is *still* dominated by thermal drift unless ambient is stable. The fix is to test indoors at a stabilized bench temperature, not in the garage in May.

Implementation note: a $4 indoor thermometer at the bench (Derek likely owns one) is the entire incremental hardware cost.

### R2 — Add a pneumatic + soap-bubble follow-on at low pressure

After hydro passes, add a separate sub-step:

> **Pass criterion 2 (pneumatic leak check, follow-on):** Drain the vessel. Re-plug ports with three ChillWaves and the Milton 727 air-plug rig in one port. Apply 30 PSI shop air for 10 minutes. Apply commercial leak-detector solution (Snoop B0009H5310 or 1:5 dish-soap:water) to every NPT thread, every weld bead surface (top + bottom plate circumferential welds), and the float-rod tack on the bottom plate viewed through the now-empty interior. **Pass:** no bubble formation at any location across the 10-min window. **Fail:** any sustained bubble at any joint or weld.

Rationale: hydro at 180 PSI catches macro leaks but water surface tension self-seals pinholes ≤ ~10 µm under quiescent conditions. Gas at 30 PSI flows through what water won't, and soap bubbles amplify the volumetric flow into visual evidence. This is the standard brewery + HVAC follow-on after a hydro pass and the reason the Milton 727 rig is already on the BOM. The doc just needs to commit when and how it's used.

Stored pneumatic energy at 30 PSI in a 6 L vessel is ~3 ft-lb — orders of magnitude below the hydro test's residual stored energy, well inside "if a plug shoots out you bruise your hand" rather than the kinetic-energy concern that's correctly elsewhere flagged for full-pressure pneumatic testing.

### R3 — Commit a failure-handling decision tree

Replace the current "Failure handling — open" sentence in step 6 with:

> **Failure handling.** The leak's location dictates the response:
>
> 1. **Threaded-port leak (NPT joint):** Drain, depressurize, remove the plug, clean the threads (no chase — that loses metal), re-apply Millrose PTFE tape (2.5 wraps clockwise as seen looking into the female port), reinstall, re-test. **Maximum 3 thread re-tapes per port across a vessel's lifetime.** A port that needs a 4th wrap is suspect for cross-threading or a tap-engagement-depth problem; vessel goes to investigation, not back into the queue.
>
> 2. **Weld bead surface weep (visible at bead, drip-dry then re-wet pattern):** Drain, dry, mark the leak location with a fine-tip Sharpie. Re-fire the X1 Pro at the marked spot with the [`welding-progress-2026-05-09.md`](../../hardware/welding-progress-2026-05-09.md) recipe (60 % power, 12 mm/s wire, Bushing delay 2000 ms, ER316L .030). Re-test. **Maximum 2 bead-repair iterations on the same weld arc.** A bead that won't seal after two repairs is treated as a HAZ defect — go to step 3.
>
> 3. **HAZ or parent-metal weep (gap-from-bead, base material, sensitized region):** Vessel is scrap. Do not attempt field repair; HAZ remediation requires solution annealing (1010–1100 °C water quench) which is out of scope. Document the failure location, recipe in use, and prior repair history into a new dated entry of [`welding-progress-YYYY-MM-DD.md`](../../hardware/) so the process learning compounds. Cut the failure region out of the scrap vessel and retain as a teaching artifact.
>
> 4. **No-visible-weep PSI drop, thermally explained (ambient drift >2 °F during the 30-min hold):** Inconclusive. Re-test after thermal stabilization.
>
> 5. **No-visible-weep PSI drop, thermally unexplained (ambient stable, gauge still dropping):** The leak is at a location that wasn't inspected. Run R2's soap-bubble check at 30 PSI air on every joint + weld; identify the leak; treat per 1/2/3 above.
>
> 6. **Catastrophic failure (sudden gauge crash, water expulsion, audible report):** Stop. Vessel scrap. Pressure-source isolated, vessel drained, failure point inspected with welder off. If at HAZ or parent metal → log and scrap. If at thread → review the tap depth and the plug torque on the failing port; tap-fixture issue probable. Document the failure mode in [`welding-progress-YYYY-MM-DD.md`](../../hardware/).

The repair-iteration caps (3 thread re-tapes, 2 bead repairs) exist because beyond those counts the failure shape stops being "tape inadequacy" or "bead inclusion" and starts being a tooling or process problem that needs the operator off the bench and back at the design level.

The same tree applies to the post-hydro pneumatic check in R2 (any bubble = leak per its location). Acceptance failures at [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) §163's analogous gap can cross-reference this tree directly once it lands.

### R4 — Commit a post-hydro visual inspection rubric

Add to step 6:

> **Visual inspection at t=0, t=15, t=30 of the 30-min hold.** Bring a 10× loupe (Bausch & Lomb 81-41-72 or equivalent — the $15 jeweler's loupe Derek likely owns) and a raking-angle flashlight to the bench. Wipe vessel dry before pressurization. At each inspection point, inspect under raking light:
>
> - **Top plate circumferential weld** (one 360° pass, ~15 cm of bead).
> - **Bottom plate circumferential weld** (same).
> - **All four NPT plugged ports** (raking light at the thread crown for bead-up-out-of-the-thread pattern, finger-touch to the threads for moisture).
> - **Float-rod tack weld** (visible by tipping the vessel and looking through the open port — only if the test is being run with one port unplugged for the SENCTRL gauge, which is the recommended config).
>
> Record any observation (dry / damp / drip / wet) per location per timing point on a paper inspection sheet. A vessel that is dry at all 8 locations across 3 inspection points has passed R4. Any drip or wet observation triggers R3.

The loupe + raking-light pattern is the standard hand-inspection rubric for shielded-gas welded SS at the bench. It catches surface porosity (visual, no drip required) and bead crater cracks (visible at end-of-bead transitions) in addition to active weeps.

### R5 — Move the criteria + tree to a shared module if a second gate appears

Step 6 should reference a single failure-handling tree applied across both hydro (here) and acceptance (post-build at [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) §163). If the doc gets long, factor it into a `hardware/assembly/leak-test-policy.md` and reference from both. Cheap factoring; defer until the second gate (acceptance) actually documents what *its* version of the tree looks like.

---

## What changes in the repo if this is executed

- **[`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) step 6** gains the four committed criteria above and the decision tree, replacing the three "Open items" lines.
- **[`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "Open items" §1–3** become closed (or move to a new short list of *follow-on* questions like "should the loupe be ESD-safe at the bench").
- **[`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) §163** cross-reference can point to the now-committed tree rather than an open item.
- **Possibly new [`hardware/assembly/leak-test-policy.md`](../../hardware/assembly/leak-test-policy.md)** if R5 is followed and the second gate documents its tree.

No new BOM lines. No new purchases. The Milton 727 + ChillWaves + SENCTRL are all ACQUIRED ([`hardware/purchases.md`](../../hardware/purchases.md) §1). A leak-detector solution (Snoop or homemade 1:5 dish soap) and a $4 bench thermometer are the only incremental consumables and both are below the purchases.md threshold.

The change is a procedure-document edit, executable in roughly an hour.

---

## What this doc is *not* asking for

- Not asking to re-purchase or re-spec any hydro rig hardware — everything needed is in hand.
- Not asking to commit to ASME-stamped hydro testing or independent third-party witness. [`business/regulatory.md`](../../business/regulatory.md) already establishes the appliance is not pursuing UL/ETL listing at this stage; ASME UV stamping correspondingly out of scope. The criteria above are *founder-edition self-witness* criteria, calibrated to the same rigor a brewery bright-tank fabricator runs against, adapted to one builder with consumer tools.
- Not asking to relax or skip hydro testing in favor of pneumatic-only. R2 is a follow-on to R1, not a substitute. Hydro is the primary safety gate; pneumatic catches what hydro misses; both run on every vessel.
- Not asking to write the firmware-side spec called out in [`integrated-firmware-gap.md`](integrated-firmware-gap.md). The two are independent prototype-blockers; either can land first without the other.

---

## The single thing

If this collapses to one sentence:

> Commit "≤ 5 PSI drop over 30 min at stable ambient, plus a 10-min 30 PSI soap-bubble follow-on, plus a six-mode repair-or-scrap tree" into [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) step 6, before the first 316L production vessel is welded — so that "weld it, plug it, pump it, walk away, come back" returns either *ship* or *fix that specific way*, not the operator's intuition.

Everything else is implementation detail.
