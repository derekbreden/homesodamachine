# Finish, Pack, Ship

The production procedure for the final stage of the appliance chain — the bench between a unit that passed [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) and a tracked carton sitting on a carrier's truck. Cosmetic inspection, identity-marking with the per-unit signed nameplate, fluid-drain confirmation for transit, install-kit pack-out, customer documentation, outer label, and carrier handoff. This document is the repeatable last-touch procedure; everything downstream is the customer's countertop install, supported by the printed install guide in the box.

Design intent for the Founder Edition shipping experience lives in [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md), [`/hardware/future.md`](/hardware/future.md) "Rear-panel nameplate", and [`/marketing/target-market.md`](/marketing/target-market.md) "Founder Edition". The dev-phase task list for the very first unit ships lives in [`/hardware/handwork.md`](/hardware/assembly/handwork.md); this doc is the per-unit repeatable bench across the [50](FOUNDER_EDITION_COUNT)-unit Founder Edition run.

## Scope

In: one appliance that has passed acceptance + burn-in per [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) with its per-serial log archive intact under `logs/<serial>/`; the pre-generated per-unit nameplate plaque (printed per [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) with serial + QR baked in, signature still to be applied at this bench); the bagged faucet-and-umbilical sub-assembly (output of [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)); the install kit components per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14 (Mudder PTFE tubing cutter, CARGEN nitrile foam segments for the cold dispense line, NEMA 5-15P → C13 line cord from §5, and the customer documentation packet); the appliance carton with molded foam end-caps; tracking + labeling supplies.

Out: a sealed appliance carton sitting on the loading-out shelf, ready for carrier pickup: cosmetic wipe-down complete; every exposed surface visually inspected and passed; the per-unit serialized nameplate applied to the rear panel with signature in place; the system fluid-drained and air-purged dry (no water in any line, no flavor in any reservoir) and the rear-panel inlets capped for transit; install kit packed; printed customer documentation included; outer shipping label affixed; shipping weight + dimensions recorded against the order; carrier tracking number assigned and emailed to the customer.

Not in scope: the customer-side countertop install at the kitchen — that's the customer's (or their installer's) job, supported by the printed install guide that lives in the install kit. International shipping is out of scope for Founder Edition; the run ships to lower 48 US states only (see Open items).

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14 (install kit) + §5 (line cord) + §9 (CARGEN foam — extra segments beyond the umbilical bench's allocation, for the install-kit's cold-dispense-line extension at field install). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Carton + foam end-cap + shipping consumable line items are pending and tracked under Open items below.

| Item | Source | Notes |
|---|---|---|
| Per-unit nameplate plaque, pre-printed with serial + QR | [`/hardware/printed-parts/enclosure/nameplate/`](/hardware/printed-parts/enclosure/nameplate/) | One per appliance, generated ahead of time per the unit's serial. Signature applied at step 3 below — not pre-applied at print time. |
| Bagged faucet-and-umbilical sub-assembly | Output of [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) | One permanently-attached faucet + umbilical unit, drops into the carton alongside the appliance. The bag also contains the install-kit parts the customer needs at countertop install: keyhole under-counter plate, factory shank nut + washer, Mudder cutter. (TPU gasket is already on the shank from the factory; not in the install kit.) |
| Mudder PTFE plastic tubing cutter | B08VW15TK8, 1 of 3 pk per appliance | [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14. Installer trims the umbilical's rear-panel end to actual cabinet depth before pushing into the rear-panel PP1208E bulkheads. |
| CARGEN nitrile foam pipe-insulation segments | B0D2XFK337 ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9) | Loose 1-ft segments in the install kit so the installer can extend the foamed cold-dispense run to actual cabinet length. **These are on top of the 84"/build §9 already allocates** — 60" to the umbilical's five segments and ~24" to the cabinet-internal riser. The umbilical length itself is settled (1540 mm blue tube, five segments); what is still open is how many spare segments a far-end install needs, which the first real install answers. |
| Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed | B08VS8D4WC, 1 of 6 pk per appliance | [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5. Standard US wall outlet to C14 inlet. |
| Customer documentation packet | Printed in-house | (a) Printed quick-start install guide; (b) Printed safety + UL/regulatory inserts per [`/business/regulatory.md`](/business/regulatory.md) (flame symbol marking, flammable-refrigerant marking, R-600a charge mass note, 120 V 60 Hz only warning); (c) Founder Edition welcome letter, personally signed. |
| Transit inlet caps | TBD per Open items | Two caps for transit — one over the water inlet barb (rear panel), one over the CO2 inlet PTC (front panel). Keeps debris out of the wetted path and signals to the installer "remove these before connecting." |
| Appliance carton + molded foam end-caps | TBD per Open items | Outer carton sized for the appliance + install kit + faucet-and-umbilical bag, with foam end-caps cradling the enclosure to absorb drop loads at corners. |
| Archival pen (signature application) | TBD per Open items | Pigment-ink, fade-resistant, kitchen-wipe-resistant. Used if the signature is applied handwritten rather than laser-engraved (decision pending per [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) "Signature fidelity"). |
| Outer shipping label + tracking | Carrier's label format | Generated at carrier-handoff step 9. |

Tooling (per-appliance-amortized only — single-asset tools live in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md), not here): microfiber wipe-down rag, isopropyl + lint-free wipes for fingerprint removal on stainless and printed surfaces, foam-tip swab for hopper/funnel interior, the laser-engraver (if the signature path lands on engrave) or the archival pen (if it lands on handwritten), kitchen scale or platform scale for the shipping-weight measurement.

## Procedure

### 1. Cosmetic wipe-down + final visual inspection

Take the appliance fresh off the [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) bench. Wipe every exposed surface with the microfiber + isopropyl: rear panel and its inlets, the Zone C top door + its surround, condenser intake/exhaust grilles, both side faces, the front face, and the bottom. Foam-tip swab the funnel cavity to clear any settled dust. Lift out the dishwasher-safe silicone funnel, wipe it down separately, and seat it back in after the unit is dry. The unit has been on the burn-in bench for the acceptance soak — fingerprints, dust drift from shop air, and the residue of fingers from prior assembly steps all land here.

Inspect every exposed surface against the following pass criteria:

- Every visible printed surface clean of layer-line debris and stringing — particular attention to the Zone C top door and the rear-panel cutouts where small printed features land near user sightlines.
- No scuffs, scratches, or print-bed adhesion marks that telegraph through the Founder Edition framing.
- No exposed wiring at any panel cutout; cable-gland grommets seated flush.
- The compressor shroud (see [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md)) seated flush with no daylight at its grommeted AC pass-through; the single AC pass-through cleanly bonded at its chassis ground tab.
- The foam-shell pour ports (see [`cold-core.md`](/hardware/assembly/cold-core.md)) trimmed flush with no overspray bloom protruding past the shell's outer surface.
- The rear-panel C14 inlet recessed cleanly into its printed shroud per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md); the recess shroud's seam against the rear-panel face shows no gap.
- The umbilical-port PP1208E bulkhead cluster on the rear panel — three bulkheads, blue accent ring on the carbonated-water bulkhead at the top — all three bulkheads finger-tight against the rear panel with no rotation play.
- Condenser intake + exhaust grilles clear of any print-process debris that could shed into the airflow path on first run.

Failures at this step: cosmetic blemishes are repaired in place where possible (light scuff buff with the lint-free wipe, reseat a loose grommet, swap a marked panel screw, reflow a heat-set insert if a panel screw is reading proud). A unit with a defect that can't be repaired in place returns upstream to the relevant subsystem bench for re-fabrication or part swap; do not ship a Founder Edition unit with a known cosmetic defect that the customer will see at unboxing.

### 2. Confirm system fluid-drain dry

The appliance ships **DRY**. Carbonator vessel and both flavor reservoirs are emptied at [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 13, after the burn-in refill defined in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) "Air Purge In/Out" — pump air through each reservoir into the nozzle until the discharge runs dry, with the carbonator drained through the dispense path under residual CO2 pressure first.

Carton-weight references: ~[20 kg](SLOSH_CARTON_W) full carton; emptied reservoirs save ~[~1.5 kg](WATER_DRAINED) water + ~[~1 kg](FLAVOR_DRAINED) flavor.

Confirm dry at this bench by: (a) listening at the nozzle while gently tilting the appliance [~15°](TILT_ANGLE) side-to-side and front-to-back — no liquid splash, no pooled-water "thunk"; (b) opening each reservoir cap and visually inspecting the sump for residual flavor (must be zero — the air-purge sequence pumps the reservoirs dry, so any residual flavor at this bench means the purge cycle didn't complete); (c) opening the faucet lever with the system de-pressurized and the rear CO2 line disconnected — no liquid discharge at the spout, no audible CO2 vent (the system should already be at atmospheric pressure off the burn-in bench). Any wet finding sends the unit back to the burn-in bench for a re-purge cycle, not corrected at this bench.

### 3. Apply the per-unit nameplate plaque with signature

Confirm the plaque pulled for this unit matches the serial assigned to the order. The plaque was pre-printed per [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) with the unit's serial baked into the contrast inlay (model `SFI-1`, serial `SFI1-FE-NNN`, input rating `120V AC 60Hz 5A 600W`, the prominent 120 V 60 Hz ONLY warning, and the QR code rendered against `homesodamachine.com/u/NNN`). The serial on the plaque must match the serial in the per-unit log archive at `logs/<serial>/`; if the QR scans to a different unit number than the plaque text, escalate — do not apply a mismatched plaque.

The signature is **not** baked in at print time — it lands here, at the final-stage bench, on the actual plaque about to ship with the actual machine. Apply by the path committed in [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) "Signature fidelity":

- **Handwritten path (working default until first plaque prints):** sign the plaque's recessed signature field with the archival pigment-ink pen, inside the recess so the signature sits below the surrounding surface plane (protects the signature from kitchen wipe-down wear). Let the ink set for the manufacturer's specified dry time before mounting — typical pigment ink is touch-dry inside 30 seconds and abrasion-resistant after a few minutes.
- **Laser-engrave path (alternative pending the test-print review):** load the plaque into the engraver's fixture, register against the plaque's print-aligned datum, run the per-unit pen-trace vector. Vacuum any engrave dust off the plaque face before mounting.

Whichever path is in service, the signature is applied to *this* plaque for *this* unit — the builder is signing this specific machine, not pre-signing a batch of blank plaques. The signature is the physical proof per [`/marketing/target-market.md`](/marketing/target-market.md) "At Founder Edition, the brand is a person" that a specific person built this specific machine.

Mount the signed plaque to the rear panel per the mounting interface defined in [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) "Mounting" — likely candidates per that doc are M3 countersunk screws through corner bosses, magnetic attachment over a recessed pocket, or an interference-fit dovetail; the per-unit procedure picks up whichever path the enclosure design lands on. Once mounted, the plaque is permanent — do not pre-mount and then attempt to sign in place; apply signature first, mount second.

### 4. Cap rear-panel inlets for transit

Cap the two fluid inlets — water inlet (rear panel), CO2 inlet PTC (front panel) — with the transit caps. The caps do two jobs: keep dust and packing-foam fragments out of the wetted path during transit and warehouse handling, and signal to the installer at unboxing "remove these before connecting."

Inlet-by-inlet:

- **Water inlet** — caps the upstream-of-backflow-preventer thread that the customer's filtered tap supply lands on. Once installed at the customer site, the cap comes off and the installer threads the supply line on; the cap never goes back on.
- **CO2 inlet PTC** — caps the 5/16" DERPIPE push-to-connect on the front panel that the customer's CO2 regulator line plugs into. Cap is a press-on rubber plug sized to the 5/16" PTC's outer collar.

The umbilical-port PP1208E bulkhead cluster on the rear panel is *not* capped — those bulkheads land on the customer-supplied umbilical tubes from the bagged faucet sub-assembly, and a cap there would be removed and discarded by the installer in any case. The PP1208E's grab-ring collet keeps debris out of the bulkhead's bore well enough for the transit-only window.

Cap specifications and source are TBD (see Open items); working assumption is a press-on rubber cap sized to each inlet OD, sourced as a small assortment kit from McMaster.

### 5. Photograph the finished unit + archive to the per-serial log

Two photos minimum:

- **Rear panel.** Full panel framing, the signed plaque centered in frame, serial number and QR readable from the photo. Good light at the plaque face so the contrast-inlay text reads cleanly; the signature must be legible.
- **3/4 front.** User-facing surfaces — front face, top funnel, and one side. Establishes that the user-facing aesthetic is what the customer's photo at unboxing will compare against.

Both go into the unit's archive at `logs/<serial>/finish/` — the burn-in bench's archive directory already has the test logs under `logs/<serial>/burn-in/`, and the finish photos sit alongside as the visual confirmation of the unit's ship-state. The photos exist for two reasons: customer-support reference if the unit arrives with damage and a "what it looked like leaving the shop" comparison shot is needed for the claim, and a record of the as-shipped state for the run that the founder can look back on.

Whether the per-serial archive ships with the appliance (USB stick in the box, QR-linked cloud archive at `homesodamachine.com/u/NNN`, both), stays at the factory only, or some split is an Open item.

### 6. Pack the install kit

Into the install kit box, in this order (bottom-up so the customer encounters them top-down):

- **NEMA 5-15P → C13 line cord** ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5): 6 ft, UL-listed Monoprice B08VS8D4WC. Laid flat at the bottom of the kit box.
- **CARGEN nitrile foam segments** ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9): loose 1-ft segments for the installer to extend the foamed cold-dispense run to the customer's actual cabinet length, over and above the 84"/build §9 allocates to the two factory runs; spare-segment count per appliance open until the first real install. Bundled with a single zip-tie so the segments stay packed together until the installer needs them.
- **Mudder PTFE tubing cutter** ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14): used at install to trim the umbilical's rear-panel end before pushing into the PP1208E bulkheads. Sits above the foam and cord so the installer pulls it out first when they get to the umbilical-trim step.
- **Customer documentation packet on top** (so the customer hits it first when they open the kit): printed quick-start install guide, printed safety + regulatory inserts per [`/business/regulatory.md`](/business/regulatory.md) (flame symbol ISO 7010 W021, flammable-refrigerant text marking, R-600a charge mass note, 120 V 60 Hz only warning), and the Founder Edition welcome letter on letterhead, hand-signed.

Whether a starter SodaStream concentrate pair + a primed CO2 tank also ride in the install kit is an Open item — the BOM currently calls both user-supplied, but the Founder Edition framing might justify a starter pack to make the first pour happen the day the appliance arrives, rather than asking the customer to source CO2 from a local welding-gas supplier (per [`/marketing/target-market.md`](/marketing/target-market.md) "The CO2 pain point needs honesty") before they get their first soda.

### 7. Pack the carton

Stand the empty carton up on its bottom face with the TOP arrow on the interior facing up. Drop one molded foam end-cap into the bottom of the carton, recess facing up. Lift the appliance with the umbilical-port cluster facing the carton's interior-marked REAR wall (so the customer at unboxing pulls the appliance out and sees the user-facing front face first, not the rear panel). Lower the appliance into the bottom end-cap; the end-cap's molded recess cradles the appliance's lower corners and bottom face. Drop the second molded foam end-cap onto the appliance from the top, mating with the appliance's upper corners and the funnel surround.

Side voids — the carton is sized so the appliance + foam end-caps leave two flanking voids on the long sides of the carton, sized for the two satellite items:

- **Faucet-and-umbilical bag** (output of [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)) lays into one side void, coiled to its 8–12" loop diameter per that bench's bagging step. Orient the bag so the faucet body sits at the carton's TOP end — keeps the heavier faucet body away from the carton's bottom drop zone, which the foam end-caps already cover for the appliance itself.
- **Install kit box** lays into the other side void, customer-documentation face up so the printed quick-start install guide is the first thing the customer sees when they open the kit.

Wedge both items with foam corner-blocks so they don't shift during transit. Close the carton's top flaps in the standard short-flap-first / long-flap-second order. Seal with kraft tape across all three top seams (long center + both short ends), then the same on the bottom. The Founder Edition unit is a [$7,500](FOUNDER_EDITION_PRICE) D2C ship — the seal isn't load-bearing, but it telegraphs care to the customer at unboxing.

### 8. Weigh, measure, and record against the order

Place the sealed carton on the platform scale, level surface, zero the scale empty first. Record actual weight to [0.1 kg](SCALE_PRECISION) precision. Measure length × width × height with a tape measure across the carton's longest dimension on each axis (not the foam end-cap recess — the carrier dim-weight algorithm uses external dimensions, not internal void). Record both against the order in the run log (`logs/<serial>/finish/ship-dims.txt` is the working format, containing: serial, gross weight in kg, length × width × height in cm, and the run-log entry's timestamp).

Expected envelope: appliance at ~[10](APPLIANCE_W_LOW)–[15 kg](APPLIANCE_W_HIGH) + packaging + install kit + faucet-and-umbilical bag lands the carton at **[15](CARTON_W_LOW)–[20 kg](CARTON_W_HIGH)** and roughly [60](CARTON_L) × [50](CARTON_W_DIM) × [50 cm](CARTON_H_DIM) — both numbers are working assumptions, not precision specs, and the first-unit measurement is what calibrates the carrier-cost model for the run. The exact target weight is flagged as an Open item.

If the weight exceeds the carrier's ground threshold (typically [70 lb](CARRIER_LIMIT_LB) / [~32 kg](CARRIER_LIMIT_KG) for UPS Ground / FedEx Ground residential), escalate to LTL freight; see Open items for the carrier-selection commit. At the Founder Edition unit's expected [15](CARTON_W_LOW)–[20 kg](CARTON_W_HIGH), no escalation is anticipated, but the measurement is the gate.

### 9. Generate the shipping label, hand off to carrier, email tracking

Carrier selection — UPS Ground vs FedEx Ground vs LTL freight, per package weight and customer ZIP — is an Open item; working default for the [50](FOUNDER_EDITION_COUNT)-unit Founder run is ground freight to lower 48 US states. International is out of scope.

Generate the carrier label from the carrier's web portal against the customer's shipping address. Declared value at the carrier's insurance level is TBD pending the damage-claim decision (Open item 3); working assumption is full declared value of [$7,500](FOUNDER_EDITION_PRICE). Affix the label to the carton's top face (so the carrier's scanner reads it on the loading dock without rotating the carton) with the label-pouch's adhesive backing, not loose-taped — the carton sees rough handling and a corner-lifted label peels off in transit.

Hand the carton off to the carrier at scheduled pickup. Scan the carton out of the run log at handoff (`logs/<serial>/finish/shipped.txt` records the tracking number, carrier, handoff date/time, and the carrier's pickup-driver acknowledgment).

Email the tracking number to the customer the same day, against the email on file with the order. The Founder Edition framing per [`/marketing/target-market.md`](/marketing/target-market.md) "trust gap" makes the carrier-handoff email a personal touch from the founder — written from `derek@homesodamachine.com`, naming the unit's serial number, attaching the rear-panel photo from step 5 — not a templated drop-ship notification. The customer paid [$7,500](FOUNDER_EDITION_PRICE) to one of the first [50](FOUNDER_EDITION_COUNT) hand-built units; the handoff email reads accordingly.

Damage-claim and warranty-registration workflow at carrier handoff is an Open item.

## Output condition

A finished, ship-ready unit is:

- Cosmetically wiped and visually inspected on every exposed surface, no known cosmetic defects
- Confirmed fluid-drained dry: no water in the carbonator or any line, no flavor in either reservoir, system at atmospheric pressure
- Rear-panel nameplate applied with this unit's serial + QR + this unit's hand-applied (or laser-engraved) signature
- Water (rear panel) + CO2 (front panel) inlets capped for transit
- Carton sealed with appliance + bagged faucet-and-umbilical sub-assembly + install kit + customer documentation packet
- Shipping weight + dimensions recorded against the order in the per-serial run log
- Outer shipping label affixed to the carton's top face; carrier tracking number assigned
- Tracking number emailed to the customer from the founder's address with the rear-panel photo attached
- Per-serial photo set + ship-dims + tracking number archived under `logs/<serial>/finish/`

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Carrier selection — undecided.** UPS Ground, FedEx Ground, or LTL freight for the [50](FOUNDER_EDITION_COUNT)-unit Founder Edition run is not yet committed. Working default is ground to lower 48; decision drives the label-generation tooling at step 9 and the per-shipment cost model.
2. **Starter pack — undecided.** The BOM calls both flavor concentrate and the CO2 tank user-supplied (see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) "External / user-supplied"). The Founder Edition framing arguably justifies a starter SodaStream concentrate pair + a primed CO2 tank in the box so the first pour happens the day the unit arrives. The call hasn't been made.
3. **Damage-claim + warranty-registration workflow.** Carrier handoff with insurance level, customer-facing claim process, and what the founder commits to on a damaged-in-transit unit (replace? repair? refund?) — all unwritten. Founder Edition unit value at [$7,500](FOUNDER_EDITION_PRICE) makes the answer non-trivial.
4. **Per-serial archive disposition.** Whether `logs/<serial>/` exports with the appliance (USB stick in the box, QR-linked cloud archive, both), retains at the factory only, or some split between the two. The per-unit QR on the nameplate could resolve to a customer-portal page that surfaces this unit's log archive — a future customer-portal decision per [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) "Per-unit QR code".
5. **International shipping — scoped out for Founder Edition.** Currently lower-48-only. Flagged here as a future-work item because the Founder Edition demand pipeline already includes inbound interest from outside the US, and the answer needs a separate set of carrier, customs, and regulatory marking workstreams (the regulatory inserts in step 6 are written against US-only markings).
6. **Carton + foam end-cap + transit-cap source.** No SKU committed yet for the outer carton, the molded foam end-caps, or the three rear-panel transit caps. Working assumption is a custom-cut carton + custom-poured foam from a local packaging house; the per-unit cost lands in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) once the source is committed.
7. **Shipping weight — precise number.** The [15](CARTON_W_LOW)–[20 kg](CARTON_W_HIGH) working envelope is an estimate; the first-unit measurement at step 8 calibrates the run, and the cost model for the carrier-selection decision (Open item 1) depends on the precise number landing.
8. **Signature path — handwritten vs laser-engrave.** Per [`/hardware/printed-parts/enclosure/nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) "Signature fidelity", the decision between handwritten archival pen and laser-engraved vector is deferred until the first plaque prints. Step 3 of this procedure runs whichever path lands; the bench's tooling list and the per-unit time both shift with the answer.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_finish_pack_ship_sync.py`
