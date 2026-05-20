# Install-envelope spec gap — the appliance commits to "under-sink" but never defines the envelope, the tap-in, the cylinder size, or the cabinet it has to fit in

*Recommendation for follow-up — written 2026-05-20, hourly-todo-filler agent (fourth of the day).*

**Audience:** future agents, Derek
**Status:** recommendation only — not for direct execution

## Distinct from siblings

- [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md) audits production labor on the bench. This gap is about the *kitchen*, not the bench.
- [`first-pour-commissioning-gap.md`](first-pour-commissioning-gap.md) is about the *time-axis* state machine between plug-in and first cold soda. This gap is about the *space-axis* prerequisites the appliance has not yet specified.
- [`unit-000-founder-kitchen-gap.md`](unit-000-founder-kitchen-gap.md) is about the founder's own install as a *full-stack rehearsal*. This gap is about the *canonical dimensional spec* — the contract — that Unit 000's kitchen will either confirm or break.
- [`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) is the *conversation script* for the Phase-A survey. This gap is the *answer key* that script silently assumes exists but does not — what numbers does the founder actually compare the customer's measurements against?
- [`2026-05-19/electrical-safety-acceptance-gap.md`](../2026-05-19/electrical-safety-acceptance-gap.md) covers the *electrical* side of customer-side preconditions (outlet, GFCI, LCDI cord). This gap covers the orthogonal *mechanical/fluidic* side: cabinet volume, water tap-in, drain proximity, CO2 cylinder placement.
- [`2026-05-19/co2-cylinder-restraint-gap.md`](../2026-05-19/co2-cylinder-restraint-gap.md) is about *how the cylinder is held in place* once it's there. This gap is upstream — *which cylinder*, *what size*, *does it fit*.
- [`2026-05-19/enclosure-exterior-doc-gap.md`](../2026-05-19/enclosure-exterior-doc-gap.md) is about the missing exterior-surface design document (where labels and bottle affordances live). This gap is about the missing *dimensional* spec for the box those surfaces wrap around.

The shape of this gap is unique: it sits at the boundary where the appliance meets the kitchen, and that boundary is currently undefined in both directions.

---

## The actual problem

[`hardware/future.md:1`](../../hardware/future.md) opens with: "This integrated build packs everything into one enclosure under the kitchen sink." [`hardware/future.md:95`](../../hardware/future.md) elaborates: "The enclosure is an under-counter appliance, installed inside the kitchen cabinet beneath the sink. Its front face points toward the kitchen cabinet door; its back sits near the kitchen cabinet's rear wall. All rear-face connections … assume the typical 2–4" working gap between the appliance back and the cabinet rear wall, consistent with under-sink plumbing convention."

That is the *only* dimensional commitment to the cabinet in the entire repo. There is no number for:

1. **The appliance's external W × D × H.** [`hardware/printed-parts/cold-core/foam-shell/README.md:127`](../../hardware/printed-parts/cold-core/foam-shell/README.md) commits the cold-core outer-shell footprint at **283 × 181 mm** (~11.1" × 7.1"), and [`hardware/assembly/enclosure-mechanical.md:87`](../../hardware/assembly/enclosure-mechanical.md) names a "support ring at the back of the enclosure floor" that captures **251 × 181 mm** for the foam-cap. Both are the cold-core footprint, not the whole appliance. The compressor, condenser+fan, electronics shelf, valve manifold, diaphragm pump, and peristaltic pump cartridge live forward and beside the cold core. The enclosure CAD does not exist (`enclosure-mechanical.md` Open item #1: "Enclosure shell + back-panel screw schedule … pending enclosure CAD"). The appliance's overall dimensions are therefore not just unstated — they are not yet *knowable* from any document in the repo.

2. **The target under-sink cabinet.** The phrase "the typical 2–4" working gap" defers to "under-sink plumbing convention" without naming a cabinet width, depth, interior clear height, or door swing. American kitchen sink-base cabinets are 30" / 33" / 36" wide and 24" deep (face frame; interior ~22–23"), and interior clear height under the sink basin runs ~17–22" depending on basin depth, but this is never written in the repo.

3. **The water tap-in method.** [`hardware/assembly/finish-pack-ship.md:85`](../../hardware/assembly/finish-pack-ship.md) names "the upstream-of-backflow-preventer thread that the customer's filtered tap supply lands on" and the rear panel commits to a 3/8" FFL inlet ([`hardware/printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md) connection #2). But how the customer's cold-water supply *gets* to that FFL is unspecified. The candidates are mutually exclusive and have different install footprints: (a) replace the existing 1/2"–3/8" angle stop with a dual-outlet "tee" angle stop (~$25, requires shutting off the cold riser), (b) saddle-valve clamp onto the cold riser (cheap and bad — leaks long-term, prohibited by code in many jurisdictions, the standard "what we *don't* do"), (c) install a 3/8" tee on the existing dishwasher / faucet supply line (~$10, no water shutoff), (d) ship a flex line with a 1/2" FNPT × 3/8" FFL inline tee that mounts between the angle stop and the existing faucet supply. The install consult cannot prescribe any of these because no document picks one.

4. **The CO2 cylinder size.** [`hardware/future.md:31`](../../hardware/future.md) describes the customer-side CGA-320 primary regulator feeding the in-appliance WR1110 secondary, and [`hardware/future.md:95`](../../hardware/future.md) names "the side air-gap between the appliance and one cabinet sidewall" as the cylinder's home. [`hardware/assembly/acceptance-and-burn-in.md:22`](../../hardware/assembly/acceptance-and-burn-in.md) names "5 lb or 10 lb CO2 cylinder" as the bench-test source. But the *customer*-side cylinder is never sized. Physical sizes (with valve):
   - **5 lb:** ~5.25" diameter × 18" tall — fits the side air-gap of any reasonable under-sink cabinet, runs out faster
   - **10 lb:** ~6.9" diameter × 20" tall — comfortable runtime, needs ~7" of side-gap width
   - **15 lb:** ~7" diameter × 24" tall — tall enough that the upper portion fouls the sink basin or disposal hangdown in many cabinets
   - **20 lb:** ~8" diameter × 28" tall — does not fit under most kitchen sinks; the cylinder *top* hits the basin underside before the bottom reaches the cabinet floor
   The marketing copy at [`marketing/target-market.md:276`](../../marketing/target-market.md) commits to "CO2 lasts months" and [`marketing/target-market.md:271`](../../marketing/target-market.md) names "syrup every few weeks (Amazon). CO2 every few months." Those statements imply a specific minimum cylinder size, and the cabinet implies a maximum. Both bounds are unstated; the implicit answer is **5 lb** or **10 lb** but no document commits.

5. **The drain proximity for the backflow-preventer vent drip pan.** [`hardware/future.md:121`](../../hardware/future.md) describes the Multiplex 19-0897 atmospheric vent dripping into "a small internal drip pan" with a moisture sensor. The pan is finite. If check #1 weeps continuously, the pan eventually fills. The repo currently treats this as "the moisture sensor catches the first drop and the app notifies the customer," but the pan's working capacity vs the customer's response time vs the existing under-sink dishwasher discharge / P-trap proximity is undocumented. This is mechanical-fluidic, parallel to the electrical GFCI question; both are *what the customer's existing kitchen has to provide*.

## Why the gap is real and load-bearing

Five downstream documents already silently depend on this spec:

- [`hardware/assembly/faucet-and-umbilical.md:64`](../../hardware/assembly/faucet-and-umbilical.md): "Segment count for the standard build is **TBD pending cabinet-routing-length spec** (see Open items)."
- [`hardware/assembly/faucet-and-umbilical.md:117`](../../hardware/assembly/faucet-and-umbilical.md): "**Umbilical design length.** Cabinet-routing length depends on countertop thickness, faucet-to-back-of-cabinet horizontal offset, and rear-panel position inside the enclosure. Three numbers are unresolved and the umbilical length sums them all."
- [`hardware/assembly/internal-plumbing.md:145`](../../hardware/assembly/internal-plumbing.md): "**Cabinet-internal carbonated-water insulation segment count.** … Pick once the cabinet-internal run length is pinned by the cold-core position + back-panel position."
- [`hardware/assembly/enclosure-mechanical.md:137`](../../hardware/assembly/enclosure-mechanical.md): "**Condenser-fan side-wall assignment (left vs. right).** … should be confirmed against typical 36"-base-cabinet door-swing geometry in target kitchens, then locked into the printed shell at order time."
- [`hardware/assembly/enclosure-mechanical.md:140`](../../hardware/assembly/enclosure-mechanical.md): "**Build-fixture cradle.** … depends on the shell's external dimensions and on whether the build proceeds on its side or upright."

Each of these resolves the moment one canonical install-envelope spec is written. None of them can resolve before then. The gap is not just a missing document — it is a **load-bearing node** in the spec graph, and several other open items are waiting on it.

## The consequence of letting the gap stand

The Founder Edition customer-facing promise at [`marketing/target-market.md:16`](../../marketing/target-market.md) is "Install: plug and play — under an hour, no plumber, no special tools." That promise is unverifiable today because:

- The appliance's external dimensions are unknown, so we cannot say it fits in any specific cabinet size.
- The water tap-in method is unspecified, so we cannot say whether a plumber is needed (replacing the angle stop is the kind of work many homeowners would call one for, even though it is technically DIY).
- The CO2 cylinder size is unspecified, so we cannot tell the customer what to buy from the welding gas supplier *before* the install consult — and the consult itself will be derailed if the customer brought home a 20 lb cylinder that doesn't fit.

The install consult ([`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase A survey) will hit this in the wild. Phase A asks the customer to measure their cabinet; the consult playbook does not yet say *what number it's comparing those measurements against*. The customer will read out "interior 28" wide, 20" deep, 22" clear under the basin," and the founder will say "great" or "we have a problem" based on numbers the repo does not currently contain.

The downstream failure mode is worse than just an awkward consult: it is a unit-001 install that *fails on site*. The 60–90 minute pulldown step on the printed quick-start sheet ([`marketing/unboxing-and-quickstart.md:61`](../../marketing/unboxing-and-quickstart.md), step 8) cannot happen if step 1–7 cannot happen because the appliance does not fit beside the dishwasher tap or the P-trap.

## What this document is recommending

**Not** a CAD-level enclosure design. The enclosure shell does not yet have geometry; the install-envelope spec is the upstream constraint that the shell will satisfy. The spec is what the customer-facing documents and the install-consult playbook cite *now*, before CAD work begins.

The recommended deliverable is a single new file, **`hardware/install-envelope.md`** (or equivalent location), that commits to:

### 1. Target cabinet definition

A primary target ("the cabinet the appliance is designed for") and a secondary target ("the cabinet the appliance is verified-compatible with"):

- **Primary:** 36"-wide single-bowl sink-base cabinet, 24" deep face frame (interior ~22.5" deep), 34.5" tall (interior clear height ~32"), with a centered single-bowl 8–10" deep stainless or composite sink basin, garbage disposal on one side (typically left), dishwasher tap on the other. *This is the founder's own kitchen profile if [`unit-000-founder-kitchen-gap.md`](unit-000-founder-kitchen-gap.md) confirms — verify before committing.*
- **Secondary:** 33"-wide double-bowl sink base, same depth and height, with two ~7" deep basins. Tighter on internal clear-height; CO2 cylinder selection narrows.
- **Out-of-spec but documented:** 30"-wide cabinets, apron-front sinks (basin hangs below cabinet top edge), 27"-deep cabinets (custom-build territory, but feasible).

### 2. Appliance external envelope

A committed maximum W × D × H for the integrated build, derived from the cabinet target above with the documented "2–4" working gap" carved out on the back and on both sides:

- **Width (W):** primary cabinet interior is ~34" (36" cabinet face frame minus stiles); minus 2× ~4" side gap (one side is the airflow plenum + cylinder; other is the disposal hangdown / dishwasher tap clearance) ⇒ appliance ≤ ~24" wide. *Sanity check against the cold core 283 mm (11.1") + compressor (~6") + condenser+fan stack (~5"); leaves 1–2" of internal routing volume, which is plausible.*
- **Depth (D):** primary cabinet interior is ~22.5"; minus 2–4" rear gap (umbilical routing, AC inlet recess, FFL38BARB38 reach) ⇒ appliance ≤ ~19" deep. *Cold core 181 mm (7.1") deep, compressor ~6" deep, condenser+fan ~5" deep arranged front-to-back fit comfortably.*
- **Height (H):** primary cabinet interior clear under basin is ~22"; minus 1" above for the umbilical down-stroke + faucet riser, minus 1" below for foot/level clearance ⇒ appliance ≤ ~20" tall. *Cold core ~10" tall + electronics shelf ~2–3" above + compressor ~7" tall arranged differently, but they don't stack linearly; the layout is L-shaped, with the cold core occupying the rear full height and the compressor + electronics shelf in front and on top.*

These are first-pass numbers; the deliverable should refine them against actual sub-component dimensions and lock the maximum envelope as a constraint that the enclosure CAD work then satisfies.

### 3. Water tap-in method, committed

Recommend committing to: **3/8" compression tee installed between the existing cold-water angle stop and the kitchen faucet supply line, with 3/8" FFL on the branch.** This is:

- 5–10 minute install with no water shutoff (the angle stop closes; the existing faucet still works during install)
- No plumber needed; the consumer-grade compression union is within the documented "plug and play" promise
- Standard product (~$10 at any hardware store, Eastman 60082 or equivalent)
- Compatible with the rear-panel FFL38BARB38 inlet that is already committed
- The customer keeps the option to undo the install by removing the tee and reconnecting the original supply line — the appliance is non-destructive to the kitchen plumbing

Alternative: ship the tee in the install kit. This converts a "go buy a part" step into a "open the box" step on install day. ~$10 BOM-add per unit.

Document the alternatives (replace angle stop with dual-outlet tee stop, saddle valve as explicitly **not recommended** with the code citation) for completeness.

### 4. CO2 cylinder size, committed

Recommend committing to: **5 lb aluminum CGA-320 cylinder as the customer-facing standard, with 10 lb listed as a longer-runtime option for households with cabinet room.**

- 5 lb fits any plausible target cabinet's side air-gap with margin (5.25" diameter < the 7" gap that a 24"-wide appliance leaves in a 36" cabinet).
- 5 lb full cylinder weight is ~12 lb — manageable for the customer to transport to the welding gas supplier for refill.
- 5 lb at typical SodaStream-style serving rate (~10 g CO2 per 12 oz dispense at full carbonation) delivers ~225 servings — call it **2 months at 3 sodas/day**, which matches the marketing copy "every few months."
- 10 lb listed as the option for the household that wants 4 months between trips; 6.9" diameter still fits the standard target side-gap; height (~20") is the binding dimension and is verified against the cabinet target.
- 20 lb explicitly out of spec for the under-sink install (height fouls the basin underside in most cabinets).

The committed size should be cross-referenced from [`marketing/unboxing-and-quickstart.md`](../../marketing/unboxing-and-quickstart.md) (the customer is told what to acquire before the appliance arrives), from the install-consult playbook ([`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase A: "Have you picked up your CO2 cylinder? Here is the size we recommend"), and from the cylinder-restraint design ([`2026-05-19/co2-cylinder-restraint-gap.md`](../2026-05-19/co2-cylinder-restraint-gap.md) — the restraint geometry depends on the cylinder diameter and height).

### 5. Drip-pan capacity floor

A pan capacity vs response-time figure. The Multiplex 19-0897 vent drip rate at first failure of check #1 is probably ~drops/minute initially; a 100 mL pan provides ~6+ hours of buffer. The pan capacity needs to be specified so the printed-pan CAD can target it, and the customer-facing response-time promise (e.g. "the app pings you within 5 minutes of the first drop and you have hours, not minutes, to act") is documented. Plumbing into a drain is explicitly *not* the design choice — that is documented in [`hardware/future.md:121`](../../hardware/future.md) — so the pan is the buffer.

### 6. The downstream-update list

The new install-envelope.md should ship with a checklist of every downstream document that gets edited to cite it:

- [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) "Open items" #2 closes against the new spec → umbilical design length + foam segment count become concrete numbers.
- [`hardware/assembly/internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) "Open items" #7 closes → cabinet-internal carbonated-water insulation segment count is concrete.
- [`hardware/assembly/enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md) "Open items" #2 closes → condenser fan side-wall assignment locks against documented target-cabinet door-swing convention.
- [`hardware/assembly/enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md) "Open items" #5 closes → build-fixture cradle dimensions become specifiable.
- [`hardware/bom.md`](../../hardware/bom.md) acquires a new line: **Eastman 60082 (or equivalent) 3/8" compression tee for cold-water tap-in, 1 per install kit**, and the BOM impact (~$10 / unit) is committed.
- [`marketing/unboxing-and-quickstart.md`](../../marketing/unboxing-and-quickstart.md) acquires: a "before your appliance arrives, pick up a 5 lb CO2 cylinder from a local welding gas supplier" pre-arrival paragraph, plus the install-step drawing showing the compression-tee tap-in.
- [`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase A survey acquires concrete numerical thresholds: "interior cabinet width ≥ X, interior depth ≥ Y, interior height ≥ Z" — the consult goes from open-ended to gated.
- [`2026-05-20/unit-000-founder-kitchen-gap.md`](unit-000-founder-kitchen-gap.md) acquires a "verify the founder's kitchen meets the install-envelope spec, then build to it" precondition — the founder's kitchen becomes a *test* of the spec, not the source of it. (If the founder's kitchen is the primary target, the spec is *measured from* his cabinet *and then committed* — the spec exists; the kitchen is the calibration set.)

## What this gap is *not*

- Not the design of the enclosure shell. That is downstream CAD work that consumes the install-envelope spec as input. (See [`enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md) "Open items" #1.)
- Not the design of the front-panel exterior surface / bottle-affordance graphic. That is [`2026-05-19/enclosure-exterior-doc-gap.md`](../2026-05-19/enclosure-exterior-doc-gap.md).
- Not the customer-side electrical preconditions. That is [`2026-05-19/electrical-safety-acceptance-gap.md`](../2026-05-19/electrical-safety-acceptance-gap.md).
- Not the CO2 cylinder *restraint* in the cabinet. That is [`2026-05-19/co2-cylinder-restraint-gap.md`](../2026-05-19/co2-cylinder-restraint-gap.md). (This gap names *which cylinder*; the sibling gap names *how it stays put*.)
- Not the customer-side CO2 supply ecosystem. That is [`2026-05-18/co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) and [`pie-in-the-sky/co2-service.md`](../../pie-in-the-sky/co2-service.md).
- Not the install-consult playbook itself. That is [`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md). (This gap is the *content* the playbook reads from; the playbook is the *script* that reads it aloud.)

## Suggested next action

The recommended path to closure is *not* "wait for the enclosure CAD." The recommended path is the opposite: **write `hardware/install-envelope.md` first, with first-pass numbers, then constrain the enclosure CAD to satisfy it.** The five "TBD pending cabinet-routing-length spec" open items in the assembly docs are evidence that downstream work is already blocked on this; producing first-pass numbers unblocks them, and the numbers can be refined as the CAD reaches detailed-design fidelity.

The first-pass spec is producible in one focused session by:

1. Measuring the founder's own sink-base cabinet (W, D, H, basin hangdown, disposal envelope, P-trap location, dishwasher tap location, angle-stop position, receptacle location, basin-underside clear height) — 30 minutes with a tape measure.
2. Decomposing the appliance into its known sub-components (cold core 283×181×~200 mm, compressor ~150×150×175 mm per harvested Antarctic Star, condenser+fan ~150×120×80 mm per harvested ice-maker, electronics shelf 150×100×40 mm, valve manifold ~150×100×50 mm) and packing them into a first-pass L-shape.
3. Comparing the resulting envelope to the cabinet target with the documented 2–4" gaps applied. Verify the L-shape fits. If it doesn't, iterate on the sub-component arrangement before iterating on the cabinet target.
4. Picking the water tap-in method and CO2 cylinder size against the resulting side-gap and rear-gap volumes.
5. Writing it down. The document is the deliverable.

The work product is dimensional and committal — exactly the kind of artifact this hourly agent should *not* produce unilaterally, which is why this is a recommendation rather than a draft. The numbers will only be right when they have been physically measured against a real cabinet.

## One-line summary

The integrated appliance commits, in many sentences, to going under the customer's kitchen sink — but never says how big it is, what cabinet it's designed for, how the water gets to it, or how big a CO2 cylinder sits beside it. Until those four numbers exist on one page, the install consult is asking the customer questions for which the appliance does not yet have answers.
