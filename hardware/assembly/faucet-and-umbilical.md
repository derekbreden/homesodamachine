# Faucet and Umbilical

The production procedure for the above-counter fixture stack and the 3-tube umbilical that connects it to the rear panel — the visible half of the appliance from the user's perspective. The faucet body and the umbilical ship as **one permanently-attached unit**: the three LLDPE tubes are connected to the Westbrass body at this bench and never separated again. The customer (or their installer) drills the 1-3/8" countertop hole, drops the faucet+umbilical through it from above, **clips the two halves of the split under-counter plate around the already-dangling umbilical from below**, slides the TPU gasket up the shank, and tightens one nut — no threading of tubes through any pill slot at install time. At the rear-panel end, the three tube tails push into the PP1208E bulkheads on the appliance back panel.

This bench runs in parallel with the main appliance chain. Its inputs are upstream of [`pressure-vessel.md`](pressure-vessel.md) (no dependency on the vessel build) and its output ships in the carton alongside the finished enclosure produced by [`finish-pack-ship.md`](finish-pack-ship.md). Design intent for the user-facing surface lives in [`../future.md`](../future.md) "User-facing elements, by location" and the dispense-head geometry rationale lives in [`../bom.md`](../bom.md) §9 (Dispensing). The under-counter plate's split design specifically exists so that the customer can install the plate around an already-attached umbilical, rather than having to thread tubes through a pill slot from below.

## Scope

In: one shell + plate + Touch-Flo body sub-assembly (output of [`../printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](../printed-parts/faucet/touch-flo-shell/ASSEMBLY.md)); the TPU mounting gasket — slid onto the shank during this bench, sits permanently between the printed mounting plate's underside and where the countertop top surface will be at install; the 3-tube dispense head (1/4" SS center tube + 2× 1/8" SS flanking tubes + decorative ferrules + PE liner); two halves of the split SendCutSend 0.060" SS under-counter plate (ships loose in the install bag, halves clip around the umbilical at install — pending DXF update, see Open items); 3× 1/4" OD LLDPE tubes cut to length (1× blue carbonated-water + 2× black flavor); CARGEN nitrile foam pipe-insulation segments; cable sleeve; the RP2040 round display; the KRAUS air switch; one Cat6 cable carrying both signals through a single countertop pass.

Out: a complete above-counter fixture stack permanently attached to its umbilical — faucet body with dispense head installed, RP2040 round display nested into the printed shell, KRAUS air switch tail emerging from the body, three LLDPE tubes connected at the body's compression ports and routed up through the upper mounting plate's pill slot, three sleeved tubes terminated bare and push-to-connect-ready at the rear-panel end, foam insulation only on the cold (carbonated-water) tube, Cat6 + tube bundle co-sleeved through the countertop. Bagged together with the install kit (TPU gasket, two split under-counter plate halves, factory shank nut, Mudder tube cutter, installer instruction sheet), drop-shipped inside the appliance carton.

Not in scope: countertop drilling itself; the customer-side install steps — drop-through, gasket + split-plate-halves + nut tighten from below, push-into-PP1208E at the rear panel — covered in the install guide (placeholder: `install-above-counter.md`, see Open items). Cat6 termination at the electronics shelf — that's `wiring.md`.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §9 (Dispensing — faucet body, dispense head, under-counter plate, foam insulation), §8 (Flavor subsystem — Pysrych reducing compression unions + Siptenk stiffeners + 1/8" SS flanking tubes + PE liner), §10 (UI — KRAUS air switch), and §1 (RP2040 round display). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

| Item | Source | Notes |
|---|---|---|
| Touch-Flo shell + plate + body sub-assembly | Output of [`../printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](../printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) | Shell printed in PET-CF with M3 heat-set inserts, factory shank nut clamping the harvested Westbrass R2031-NL body to the printed mounting plate |
| 1/4" OD × 12" 304 SS center tube | B0F87DJDZW (4-pk) | Carbonated-water spout; carries chilled CO2-saturated water from the Westbrass body's outlet ferrule to the visible faucet tip |
| 1/8" OD × 12" 304 SS flanking tubes × 2 | B0F87V8XCB (4-pk) | Flavor spouts; downstream of the Pysrych 1/4" × 1/8" reducing compression unions |
| Eoiips 1/16" ID × 1/8" OD food-grade PE liner | B0BWJ3S5NM | ~6" per flanking tube; lines the 1/8" SS so the syrup wetted path is food-grade PE, not bare SS |
| Pysrych 1/4" OD × 1/8" OD 304 SS reducing compression union × 2 | B0BM4394Z4 (2-pk) | Joins the soft 1/4" LLDPE flavor supply to the rigid 1/8" SS flanking tube at the dispense-head transition; one per flavor line |
| Siptenk 1/4" OD brass tube stiffener × 2 | B0FM77LLM1 (100-pk) | Inside the LLDPE side of each Pysrych ferrule so the soft tube doesn't crush under the nut |
| Beduan 1/4" OD compression ferrule sleeve (decorative) | B07V4K2KKH (5-pk) | Slides over the visible tip of the 1/4" SS center tube — cosmetic, not load-bearing |
| Beduan 1/8" OD compression ferrule sleeves (decorative) × 2 | B07V8RJJYJ (5-pk) | Slides over the visible tips of the two 1/8" SS flanking tubes — cosmetic |
| TPU mounting gasket (printed) | [`../printed-parts/faucet/touch-flo-mounting-gasket/`](../printed-parts/faucet/touch-flo-mounting-gasket/) | Above-counter gasket between the printed mounting plate's underside and the countertop top surface. **Installed at this bench**, slid up the shank from below the plate during step 2 — the body has already been clamped to the plate at the touch-flo-shell sub-assembly bench, but the shank stub remains accessible from below for the gasket to slide onto. Stays permanently on the shank from this point forward. Customer never touches it. |
| SendCutSend 0.060" 304 SS under-counter plate — two-half split design | `touch_flo_under_counter_plate.dxf` | Distributes the under-counter nut's clamping load. **Ships as two identical D-shaped halves** that the installer clips around the umbilical from below at install time, removing the "thread tubes through a pill slot" step that a solid disc would require with an already-attached umbilical. Per-half SCS unit cost is roughly half the prior one-piece cost; both halves come on a single SCS order. |
| 1/4" OD LLDPE, blue (carbonated water) | New small-spool SKU, sourcing in flight per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification" | Cut to length once; color-coded blue to match the blue-ringed PP1208E bulkhead on the rear panel |
| 1/4" OD LLDPE, black (flavor lines) × 2 | FWS bulk spool ([`../bom.md`](../bom.md) §3) | Cut to length once each; bare black, matches the two unmarked PP1208E bulkheads on the rear panel |
| CARGEN nitrile foam pipe insulation, 1/4" ID × 3/8" wall, 1-ft segments | B0D2XFK337 ([`../bom.md`](../bom.md) §9) | **Cold tube only.** Foam ships as 1-ft segments and is installed segment-at-a-time; no field foam-cutting. Segment count per umbilical TBD pending cabinet-routing-length spec |
| Cable sleeve (braided polyester or spiral wrap) | TBD per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical bundle construction" | Single sleeve over all three tubes + Cat6 from just above the under-counter plate down to ~3" above the rear-panel bulkheads |
| Waveshare RP2040 round LCD 0.99" | B0CTSPYND2 ([`../bom.md`](../bom.md) §1) | Sits inside the printed shell's display recess; UART + 5 V via Cat6 conductors per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) SIG-6 |
| KRAUS air switch, matte black | B096319GMV ([`../bom.md`](../bom.md) §10) | Above-counter flavor-select button; signal pair via Cat6 per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) SIG-5 |
| Cat6 cable | TBD spec | Single shared run from above-counter fixture stack to the electronics shelf, carrying both SIG-5 (KRAUS air-switch contacts) and SIG-6 (RP2040 power + UART). Cuts the countertop pass-through count from two to one |

Tooling (per-build-amortized only; single-asset tools live in [`../purchases.md`](../purchases.md), not here): Mudder PEX/PE tube cutter (also in the installer's install kit, [`../bom.md`](../bom.md) §14 — same cutter SKU lives in both places); small adjustable wrench for the Pysrych compression nuts; the Hakko FX-888D station from the upstream sub-assembly step is not used at this bench.

## Procedure

### 1. Cut the three LLDPE tubes to length

Cut all three tubes — 1× blue carbonated-water + 2× black flavor — to the umbilical's design length (TBD pending cabinet-routing-length spec; see Open items). One cut per tube with the Mudder cutter, square-end, no burr. All three tubes are the same length: the umbilical bundles them together inside one sleeve and they terminate at the same end face, so length differences would just create extra slack at one end of the sleeve.

The installer makes a *second* cut on each tube at field install — trimming the rear-panel end to fit the customer's actual cabinet depth before pushing each tube into its PP1208E bulkhead. The factory length is sized long with that installer-trim allowance baked in; do not cut tight here.

### 2. Build the 3-tube dispense head

Reference the dispense-head geometry rationale in [`../bom.md`](../bom.md) §9 + §8 and the touch-flo body's outlet geometry in [`../harvested/touch-flo-faucet/`](../harvested/touch-flo-faucet/).

- **Center spout (carbonated water).** Take one 12" 1/4" OD 304 SS center tube. Slide the decorative Beduan 1/4" OD ferrule over the visible end. Insert the un-decorated end into the Westbrass body's downstream compression port (factory ferrule + nut on the body's outlet side). Hand-snug + 1/4 turn with a wrench — the connection sees CO2-saturated water at ~90 PSI when the faucet is open, so the joint matters; not over-torqued, as the body is brass and the tube is SS.
- **Flanking spouts (flavor A + flavor B).** Each flavor leg is: blue carbonated-water (already done above) is not part of this leg — this is flavor only. For each of the two flanking spouts: line the inside of one 12" 1/8" OD 304 SS tube with a ~6" section of Eoiips 1/16" ID × 1/8" OD PE liner (push it in by hand; friction-fit, no adhesive). Slide the decorative Beduan 1/8" OD ferrule over the visible end of the SS tube. The other end of the SS tube gets fed into a Pysrych 1/4" × 1/8" reducing compression union on the 1/8" side. Snug the 1/8" ferrule onto the SS tube. The 1/4" side of the Pysrych union accepts the LLDPE flavor tube in step 3.

The three spouts emerge from the body in the factory triangular arrangement (center = water, two outboard = flavors) — same geometry the printed shell's dispense-head boss is designed around.

### 3. Connect the LLDPE umbilical tubes to the dispense head

- **Carbonated water (blue tube).** The blue LLDPE tube push-connects to the Westbrass body's upstream compression port (the supply side that takes carbonated water *in* — opposite end of the body from the center spout assembled in step 2). The body's factory ferrule + nut clamp the LLDPE; insert a Siptenk 1/4" stiffener into the LLDPE end first so the ferrule doesn't crush the tube under torque. Hand-snug + 1/4 turn.
- **Flavor lines (black tubes × 2).** Each black LLDPE tube push-connects to the 1/4" side of one Pysrych reducing union assembled in step 2. Same drill: Siptenk stiffener inside the LLDPE first, then the LLDPE into the 1/4" Pysrych ferrule, hand-snug + 1/4 turn.

At the rear-panel end of all three tubes: **leave them bare and square-cut.** No fittings, no stiffeners. The installer pushes each tube directly into the matching PP1208E bulkhead's collet at field install; PP1208E's internal grab-ring + EPDM O-ring make the seal around the tube OD, no separate ferrule needed (same seal mechanism already in use on the reservoir-cap bulkhead per [`../printed-parts/cold-core/reservoir/generate_step_cadquery.py`](../printed-parts/cold-core/reservoir/generate_step_cadquery.py)).

### 4. Slide foam segments onto the carbonated-water tube only

Per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical bundle construction": **foam goes on the blue tube only.** The two flavor reservoirs sit between the inner and outer foam shells of the cold core and pre-chill passively to 8–15 °C, but the syrup throughput is a few mL per dispense at low duty cycle — warm-in, warm-out, no thermal benefit from insulating the flavor lines. The carbonated-water tube is the only temperature-critical run: it carries the chilled CO2-saturated water up through the countertop to the faucet, where every degree of warm-up costs dissolved-CO2 retention.

Slide CARGEN 1-ft segments onto the blue tube end-to-end. The segments are sized as a snug interference fit over 1/4" OD LLDPE; lubricate with a wipe of water if friction is high (no solvents — nitrile is solvent-sensitive). Butt the segments together along the run with no gap; the braided sleeve installed in step 5 holds the butts compressed.

Segment count for the standard build is **TBD pending cabinet-routing-length spec** (see Open items). The 1-ft granularity is sized so the installer at field install can pull off whole segments to shorten the foamed run to actual cabinet length without needing to cut foam.

### 5. Sleeve the three tubes + Cat6 into one bundle

Bundle the three LLDPE tubes (one foamed blue + two bare black) into the natural triangular dense-pack arrangement — same pattern the rear-panel PP1208E cluster is laid out for, so the bundle's three tubes already align with the three bulkheads when the installer presents the bundle to the panel. The blue (foamed) tube sits at the top vertex of the triangle for orientation matching with the blue-ringed bulkhead at the top of the panel cluster.

Run the Cat6 cable alongside the three-tube triangle. The Cat6 is the *fourth* element inside the sleeve, sitting in the void between the three triangle-packed tubes and the sleeve's inner wall. It carries both above-counter electrical signals through one countertop pass:

- **SIG-5 (KRAUS air switch contacts)** — 2 conductors, switch + GND, per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md).
- **SIG-6 (RP2040 round display)** — 4 conductors, UART TX + RX + 5 V + GND, per the same schedule.

Six conductors used of Cat6's 8. Specific pair-to-conductor allocation within the Cat6 is **TBD** (see Open items — `ac-wiring-schedule.md` doesn't yet pin a conductor pinout).

Slide the chosen sleeve (braided polyester or spiral wrap, TBD per the back-panel README) over the full length of the bundle. Sleeve runs from just above the under-counter plate (top end, where the bundle emerges out the bottom of the faucet body's pill slot) to ~3" above the rear-panel end (bottom end, where the installer trims to fit). Leaving the last 3" un-sleeved at the rear-panel end is so the installer can flex the three tubes apart by a few inches for the three-bulkhead push-connect — a hard-sleeved bundle would force the bulkheads to be perfectly tangent to the bundle's sleeved diameter.

### 6. Drop in the RP2040 round display and route the KRAUS air switch

The printed Touch-Flo shell from the upstream sub-assembly already has a recess for the RP2040 round display on its top face (geometry per the shell's `generate_step_cadquery.py`). Nest the display into the recess; the Cat6's 4 RP2040 conductors (UART TX, UART RX, 5 V, GND) terminate at the display's pin header. Termination format at the display end is the display's native header (TBD — depends on whether we solder leads or use Dupont female ends).

Route the KRAUS air switch through the shell's pill slot alongside the two flavor tubes. The KRAUS lives entirely above the countertop in the user's normal sightline — it's the flavor-select button — and its signal pair terminates at the Cat6 (SIG-5).

The above-counter fixture stack is now complete: shell, plate, body, three spouts, three umbilical tubes, foam on the cold one, sleeve, RP2040 display nested in the shell, KRAUS air switch wired to the Cat6 trunk.

### 7. Bag the sub-assembly with installer kit

Lay the bundled umbilical down with the faucet body at one end and the three bare tube tails + Cat6 unterminated end at the other. Coil the umbilical loosely (8–12" loop diameter — tighter than that risks kinking the LLDPE).

The TPU gasket is already on the shank from step 2 and is not in the install kit. Into the bag with the umbilical, add the install-kit parts the customer needs at countertop install:

- **Two halves of the split SendCutSend 0.060" 304 SS under-counter plate** — the two D-shaped halves that clip around the umbilical from below at install.
- Factory shank nut + washer (loose — to be installed below the under-counter plate halves)
- One Mudder PEX/PE tube cutter (the per-appliance install-kit tool from [`../bom.md`](../bom.md) §14, same SKU as the bench-side cutter)
- One installer-facing instruction sheet covering the above-counter install — countertop drill template, drop-through-from-above sequence (gasket already in place on the shank from the factory; compresses against countertop top surface as the assembly seats), **clip-the-two-plate-halves-around-the-umbilical-from-below** step, washer + shank-nut tighten sequence, rear-panel push-to-connect rule "blue tube into the blue-ringed bulkhead, black-into-either-black", Cat6 termination at the rear-panel access (TBD which side terminates Cat6). Doc placeholder: `install-above-counter.md` (see Open items).

Bag, seal, label with build number and the part identifier `FAUCET-UMBILICAL-SUBASSEMBLY`, set aside for [`finish-pack-ship.md`](finish-pack-ship.md) (TBD).

## Output condition

A bagged sub-assembly that is:

- One above-counter fixture stack with the dispense head's three SS spouts installed, the RP2040 display nested in the printed shell, and the KRAUS air switch routed
- The umbilical is **permanently attached** to the faucet body — three LLDPE tubes (1× blue carbonated-water + 2× black flavor) connected at the body's compression ports, routed up through the upper mounting plate's pill slot, inside a single sleeve with foam insulation on the cold tube only, Cat6 alongside the three tubes inside the same sleeve
- Three tubes terminated bare and square-cut at the rear-panel end, ready for push-into-PP1208E at install
- Cat6 unterminated at the above-counter end (gets cut to length at the customer's countertop position during install); Cat6 rear-panel end terminated at the electronics shelf during `wiring.md` at appliance final assembly (the bagged sub-assembly is brought to the wiring bench, Cat6 conductors broken out, terminated, and the bag re-closed for shipping)
- TPU mounting gasket already in place on the shank between the printed mounting plate's underside and where the countertop top surface will be (installed at this bench, not in the install kit; customer never touches it)
- Loose install-kit parts bagged together: **two halves of the split SS under-counter plate**, factory shank nut + washer, Mudder tube cutter, installer instruction sheet
- Labeled, sealed, ready to drop into the appliance carton at [`finish-pack-ship.md`](finish-pack-ship.md)

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Cat6 conductor pinout for SIG-5 + SIG-6.** [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) defines the runs at the schedule level (SIG-5 = air-switch contacts, SIG-6 = RP2040 UART + 5 V) but does not pin specific Cat6 pair-to-conductor assignments. Needed for the RP2040-end pin-header build and for the rear-panel termination in `wiring.md`.
2. **Umbilical design length.** Cabinet-routing length depends on countertop thickness, faucet-to-back-of-cabinet horizontal offset, and rear-panel position inside the enclosure. Three numbers are unresolved and the umbilical length sums them all. Once spec'd, this also fixes the CARGEN foam segment count for step 4.
3. **Cable sleeve selection.** Braided polyester vs spiral wrap, per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md). The cleaner one for the customer-visible sleeve segment between countertop and rear-panel cluster is whichever installs with the bundle and Cat6 already inside; spiral wrap allows post-bundle install (wrapping around an assembled bundle), braided requires pre-thread.
4. **Blue LLDPE small-spool sourcing.** A small spool of 1/4" OD blue LLDPE is in flight per the back-panel README. SKU + supplier not yet in `bom.md` or `purchases.md`.
5. **Installer instruction sheet — `install-above-counter.md`.** Customer-facing install guide covering countertop drilling, drop-through-from-above sequence (the TPU gasket is already on the shank from the factory and compresses against the countertop top surface as the assembly seats — customer does not install the gasket), clip-the-split-plate-halves-around-the-umbilical step, washer + shank-nut tighten sequence, blue-tube-into-blue-bulkhead rule at the rear panel, and the umbilical trim step at the rear-panel end. Scope + doc name placeholder pending dedicated installer-docs branch.
6. **RP2040 display termination at the above-counter end.** Whether the Cat6's 4 display conductors land at the display via soldered leads, Dupont female header, or a JST-XH 4-pin connector. Affects both the rework-friendliness of the display and the BOM (JST headers already in [`../bom.md`](../bom.md) §11; soldered leads are zero-BOM but make field-swap of a failed RP2040 harder).
7. **Cat6 strain relief through the countertop.** The 1-3/8" countertop hole that takes the faucet shank is sized for the shank + gasket + plate stack; the Cat6 piggybacks through the same hole alongside the tubes. Whether the Cat6 needs a separate grommet, a printed strain-relief collar, or just rides loose through the gasket's pill-slot region is undefined.
