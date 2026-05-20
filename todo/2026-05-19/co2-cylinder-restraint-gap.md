# CO2 cylinder restraint + regulator-drop hazard gap — a 12 lb pressurized cylinder lives on the cabinet floor with no mechanical restraint, no valve-shear protection, and no install-time torque procedure for the CGA-320 nut

*Recommendation for follow-up — written 2026-05-19, hourly-todo-filler agent.*

This is a **mechanical-safety + installation-procedure** gap that is distinct from every other CO2-related doc in the repo:

- [`co2-asphyxiation-and-prv-vent-path-gap.md`](co2-asphyxiation-and-prv-vent-path-gap.md) covers *gas-escape detection* (NDIR sensor, PRV vent path).
- [`co2-runtime-and-depletion-ux-gap.md`](co2-runtime-and-depletion-ux-gap.md) covers *firmware tracking of remaining mass* and the lockout/swap UX.
- [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) covers *refill logistics* — where the customer goes to get a new cylinder.
- [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) names "where the CO2 cylinder will live (under the sink vs. in an adjacent cabinet)" as an install-call topic but does not address *how it is held in place*.

Nothing in the BOM, no printed part, and no step in any assembly or install document addresses the physical question: **how does a free-standing 5–20 lb pressurized cylinder stay upright in a busy under-sink cabinet, and what happens when it doesn't?**

This is one of those gaps that does not block unit-1 bench work (the bench-test cylinder sits on a workbench under the operator's eye), but it is the kind of thing that produces a phone call, an insurance claim, or — in the bad-tail case — a hospitalized child. It needs a documented mitigation before any unit lives in a customer's kitchen.

## What I think is wrong

The picture, drawn from [`hardware/future.md`](../../hardware/future.md), [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md), and [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md):

- A 5 lb (typical, ~12 lb gross) or 10 lb (typical, ~22 lb gross) or 20 lb (typical, ~42 lb gross) aluminum CGA-320 CO2 cylinder sits on the cabinet floor **beside** the appliance, in the side air-gap between the appliance and the cabinet sidewall. Cabinet dimensions for a 36" base sink cabinet are typically ~33" wide × ~22" deep × ~28" tall internally; the appliance occupies most of one half, the cylinder lives in the other half.
- The customer's own dual-gauge **CGA-320 primary regulator** hangs off the cylinder valve. A typical home-soda primary (Taprite, CO2Doctor, BeverageElements) is ~3 lb of brass + two 2.5" gauges, mounted laterally on a single CGA-320 nut and a fiber/plastic washer.
- A length of 5/16" beer line (~3 ft) runs from the regulator's barbed outlet through the side air-gap to the **front-panel DERPIPE 5/16" PTC bulkhead** on the appliance, where it lands on the in-appliance WR1110 fixed-90 PSI secondary regulator.

That picture has six independent mechanical-failure modes, none of which has a written mitigation:

1. **Tip-over (free-standing cylinder).** A 5 lb aluminum CO2 cylinder is ~14" tall × 5.25" diameter and weighs ~12 lb full — top-heavy enough to tip when knocked, particularly with a 3 lb regulator + gauges hanging off the top extending the moment arm laterally by 4–6". The cabinet floor is the high-traffic interior surface of the kitchen: dish soap, sponges, scrub brushes, garbage bags, drain cleaner, and (in homes with kids) a step-stool for reaching the sink all live within 12" of the cylinder. The probability of an incidental knock per year is not low.

2. **Valve-shear projectile (post-tip-over).** This is the canonical compressed-gas hazard. A CGA-320 valve under a regulator does not have a removable valve-protection cap installed during service (the cap *has* to come off to fit the regulator). If a full cylinder tips with the regulator attached, and the regulator strikes a hard surface (the cabinet sidewall, the disposal, the appliance side face) before the cylinder body does, the lateral impact load on the CGA-320 valve neck can exceed the brass threading's shear strength. The valve breaks off. The cylinder becomes a Class-2.2 thrust-driven projectile capable of penetrating a residential cabinet wall and the drywall behind it. **This is the NIOSH ALERT 96-101 hazard** (*Preventing injuries from compressed gas cylinders*) — uncommon but well-documented across industrial and consumer settings, and the canonical reason OSHA 1910.101(b) requires cylinders to be "secured in an upright position at all times" in occupational settings. The residential analogue is not regulated, but the physics and the liability are identical.

3. **Regulator drop / nut back-out.** Subtler and more common than valve shear. The CGA-320 nut is hand-tightened (or wrench-tightened to ~25–40 ft-lb depending on the source). Under thermal cycling, vibration from a nearby dishwasher or disposal, or even from the customer leaning against the cabinet, a hand-tight nut can back off. The fiber/plastic washer is single-use; reusing one past its first install (which a refill-day customer will do unless told otherwise) is the failure path. A backed-off CGA-320 nut vents the **full cylinder pressure** (~800 PSI for liquid-phase CO2 at room temperature) into the cabinet. Inventory: ~1,230 L of gas at room conditions for a 5 lb cylinder, ~4,900 L for a 20 lb. See the asphyxiation gap doc for the dose-time curve that follows in an unventilated cabinet.

4. **Hose-strain at the front-panel inlet.** The 5/16" beer line from the regulator outlet to the DERPIPE bulkhead is the only mechanical coupling between cylinder + regulator and the appliance. If the cylinder is pulled forward (cleaning, refill day, customer reaching past it), the hose pulls on (a) the regulator barb outlet, (b) the front-panel DERPIPE bulkhead, or (c) both. The DERPIPE bulkhead is a press-to-connect — its retention force on a 5/16" beer line is the tube-OD friction grip, which is rated for the working pressure (90 PSI on the appliance side, ~800 PSI on the regulator side until the regulator's high-side outlet), not for a 12 lb tug. The barb on the regulator outlet is typically a 1/4" or 5/16" hose barb retained by a single screw clamp; a sustained pull rotates the regulator's outlet seat.

5. **Refill-day disconnect/reconnect.** Every 4–8 weeks at typical consumption ([`co2-runtime-and-depletion-ux-gap.md`](co2-runtime-and-depletion-ux-gap.md)), the customer:
   - Closes the cylinder valve.
   - Vents the regulator's low-side.
   - Unscrews the CGA-320 nut from the cylinder.
   - Carries the empty cylinder to the trunk of their car.
   - Drives to a welding-supply store (per [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md)).
   - Returns with a full cylinder.
   - Threads the CGA-320 nut onto the new cylinder valve.
   - Replaces the fiber washer (or doesn't — no documented requirement).
   - Hand-tightens or wrench-tightens (no documented torque or wrench-availability assumption).
   - Opens the cylinder valve.
   - Verifies no leak (no documented soap-bubble or sniffer step).

   That nine-step procedure is the single most failure-prone routine maintenance event in the appliance's life, and it is not written down anywhere a Founder Edition customer can find it. The unit ships with no documented refill procedure, no torque spec, no spare-washer inventory, and no leak-witness step.

6. **Child / pet access.** This is not theoretical. The under-sink cabinet is where children are trained to leave alone (because of the cleaning chemicals) and where some children go specifically *because* they've been told not to. Pets — particularly cats — fit into the side air-gap and may sleep there. A 12 lb cylinder pulled down by a curious toddler or knocked over by a cat is a meaningful event. The current design has zero child-access mitigation (no door lock, no cabinet-floor anchor) and no documentation acknowledging the population of customers who have children at home.

## Why this matters in the Founder Edition context

[`marketing/target-market.md`](../../marketing/target-market.md) names the Founder Edition customer as a homeowner with $200K+ household income. Roughly 40% of that demographic has at least one child under 18 in the home. The "second sale" in [`marketing/target-market.md`](../../marketing/target-market.md) "The coworker model" — visitors seeing a unit in a kitchen and asking about it — explicitly targets a behavior that puts third parties (their children, their guests' children) in proximity to the cylinder.

The Founder Edition price ($7,500) and the personal-install model do two things simultaneously:

- They create the **highest possible liability exposure per unit shipped** — premium price implies premium care of the customer's home, and the founder's name on the plaque means the founder is the named party in any complaint.
- They create the **best possible install-time access to fix this** — the founder is personally in the customer's kitchen (or on Zoom) during install. There is no better moment to verify cylinder restraint than during the install consult.

The current state — no documented restraint, no documented refill procedure, no torque spec, no child-access mitigation — is unforced exposure. Closing it costs ~$30 of hardware per unit and 5 minutes of install time.

## What's already in the repo, what's missing

**Present:**

- The cylinder's *location* is named in [`hardware/future.md`](../../hardware/future.md) ("beside the appliance in the cabinet on the cabinet floor — in the side air-gap").
- The line-of-sight rationale is named in [`hardware/future.md`](../../hardware/future.md) ("on a short tether to a front-panel CO2 inlet, putting the cylinder valve in the customer's line of sight at install and service").
- The setpoint guidance for the primary regulator is named in [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "CO2 supply" ("anywhere in the 70–100 PSI range; the WR1110 takes care of the rest").

**Absent:**

- **No restraint hardware in the BOM.** Grep `purchases.md` for "strap", "chain", "restraint", "cradle", "bracket", "anchor": nothing on the cylinder side. The only thing close is the printed front-panel DERPIPE bulkhead retention, which is for the hose, not the cylinder.
- **No restraint geometry in any printed part.** The `printed-parts/enclosure/` tree has `back-panel`, `front-panel`, and `nameplate` — no side-face exterior surface document and therefore no documented cylinder-side strap mount, cradle, or anchor.
- **No refill-day procedure.** There is no `procedures/cylinder-swap.md`, no equivalent inside [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md), and no end-user-facing maintenance doc that explains the nine-step swap above.
- **No torque spec for the CGA-320 nut.** Even [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) step 1, which has the bench operator open the cylinder valve and set the primary, does not call out a torque or a wrench requirement for the CGA-320 nut.
- **No spare-washer policy.** A fiber CGA-320 washer is a $0.10 single-use item; the appliance has no inventory of spares to ship with the unit and no end-of-life policy for the one installed at the factory.
- **No child-access acknowledgment.** [`marketing/target-market.md`](../../marketing/target-market.md), [`business/regulatory.md`](../../business/regulatory.md), and [`hardware/future.md`](../../hardware/future.md) collectively contain zero mentions of children, pets, or cabinet locks.

## What I'd propose

Five interventions, in order of cost and effect. The first three close 95% of the surface for ~$30 / unit + ~10 min of install time. The fourth is an exterior-surface document. The fifth is a customer-facing maintenance doc.

### 1. Add a cylinder strap to the BOM, anchored to the appliance side face

The standard hardware is a $5–15 nylon-webbing strap with a quick-release buckle, anchored at one end to a fixed point on the appliance side face and wrapping horizontally around the cylinder ~2/3 of the way up. This is the same pattern used on RV propane-tank brackets, paintball cylinder mounts, and laboratory CO2-cylinder brackets.

Candidate parts:

- **Camco 57541 quick-release cylinder bracket** (the RV-propane version, ~$10, Prime). Designed for 20 lb propane but adjustable down to 5 lb. Quick-release pin lets the customer remove the cylinder for refill day without tools.
- **Generic "cylinder retention strap" 2"-wide nylon + cam buckle** (~$8, Prime). Less rigid than the bracket but lower-profile in the side air-gap.
- **Custom printed cradle + strap.** A 3D-printed cradle that bolts to the appliance side face and accepts a generic nylon strap. Allows tuning to the 5/10/20 lb cylinder size mix and integrates with the rest of the printed enclosure aesthetic. The cradle becomes part of the as-yet-unwritten side-face exterior surface document (see item 4 below).

The anchor point is on the appliance side face — the same face that carries the condenser intake or exhaust grille per [`hardware/future.md`](../../hardware/future.md). Use the existing M3 heat-set inserts pattern from [`hardware/purchases.md`](../../hardware/purchases.md) §printed-parts hardware (ruthex RX-M3Sx4.0 brass heat-set, already in stock at 100-pc bag, ~3.8 builds of stock). Two inserts per side, M3 × 25 mm SHCS through the strap mount.

BOM cost per unit: ~$10 (strap or bracket) + ~$0.20 (2× M3 inserts already amortized) = **~$10 / unit**, 1 SKU added.

### 2. Add a 3D-printed cylinder footprint template to the install kit

A flat printed disc, ~7" diameter × 1/8" thick, that the founder lays on the cabinet floor during install to mark where the cylinder sits relative to the appliance. The template carries:

- A central 5.25" circle (5 lb cylinder OD) with concentric 7.25" (10 lb) and 8" (20 lb) rings, so the customer's existing or future cylinder size is visible.
- An arrow indicating the orientation of the regulator outlet (toward the front-panel inlet, i.e., 90° from the appliance side face).
- A small printed-text reminder: "Strap before walking away."

The template ships in the install kit, gets used during the consult, and remains in the cabinet — partly as a documentation artifact, partly so the customer puts the cylinder back in the same place after refill day.

BOM cost per unit: ~$0.50 of PETG/PET-CF, **~$0.50 / unit**, no new SKU.

### 3. Ship a CGA-320 service kit with each unit

A small zip-bag with:

- 5× fiber CGA-320 washers (single-use, ~$0.10 each).
- 1× plastic or printed CGA-320 wrench (~$3, e.g., the "Coast Guard tank wrench" form factor).
- A small printed card with:
  - The torque spec or the hand-tight + 1/4-turn convention.
  - The pre-refill venting sequence.
  - The post-refill leak-witness step (sniff at the CGA-320 nut after opening the valve; if any hiss, close the valve and re-seat).

This kit lives in the same place as the appliance's user-facing service paperwork — most likely zip-tied to the appliance's CO2 inlet hose, so it's discovered the first time the customer disconnects the cylinder.

BOM cost per unit: ~$5 (washers + wrench + printed card + bag), **~$5 / unit**, 3–4 SKUs added.

### 4. Write the side-face exterior surface document

[`hardware/future.md`](../../hardware/future.md) explicitly defers the cylinder-side surface geometry: *"The matching bottle-shaped placement affordance ('cylinder goes here') belongs to whichever side-face exterior surface the cylinder neighbors in the side gap — not the front panel. That surface's design document does not yet exist; geometric specifics deferred to it."*

This is the same gap [`enclosure-exterior-doc-gap.md`](enclosure-exterior-doc-gap.md) flags from a different angle (the unowned exterior surfaces). The cylinder-restraint topic is one of the surfaces that document should own. When that file lands at `hardware/printed-parts/enclosure/side-panel/README.md` (or similar), it should include:

- The condenser intake or exhaust grille geometry (per [`cabinet-heat-rejection-gap.md`](cabinet-heat-rejection-gap.md)).
- The cylinder-bottle placement affordance (per [`hardware/future.md`](../../hardware/future.md)).
- The strap/cradle mount geometry (per item 1 above).
- The cabinet-floor footprint template (per item 2 above).
- The customer-side documentation surface (per item 5 below).

All four of those want to live on the same printed part. Writing the document once, with all four in it, is cheaper than writing four documents.

### 5. Write the customer-facing CO2 swap procedure

A one-page (single sheet of paper, two-sided) printed maintenance card that ships in the unit. Contents:

**Side 1 — refill day:**

1. Close the cylinder valve (turn clockwise until firm; do not overtighten).
2. Press the dispense lever briefly to vent the line.
3. Unscrew the CGA-320 nut (counterclockwise) using the supplied wrench. Catch the fiber washer; it is single-use — discard it.
4. Lift the cylinder from the cradle/strap and take it to your local supplier (see the supplier list in the welcome packet, per [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md)).
5. After return: install a fresh fiber washer (from the service kit) on the CGA-320 mating surface.
6. Thread the CGA-320 nut onto the new cylinder valve. Hand-tight first, then 1/4 turn with the wrench. **Do not overtighten.**
7. Open the cylinder valve slowly (one full turn is sufficient).
8. Listen + sniff at the CGA-320 nut. If you hear or smell anything, close the valve and re-seat.
9. Strap the cylinder back into the cradle/bracket. Verify the bracket pin is fully seated.
10. Confirm app shows >700 PSI on the supply gauge (per [`co2-runtime-and-depletion-ux-gap.md`](co2-runtime-and-depletion-ux-gap.md), which sets that threshold).

**Side 2 — what to do if it doesn't go right:**

- Hiss at the CGA-320 nut: close valve, replace washer.
- Hiss anywhere else: close valve, photograph the location, call the founder (Founder Edition) or open a ticket (Standard Edition).
- Cylinder leans, falls over, or pulls the hose: close valve immediately; do not lift the cylinder by the regulator.
- CO2 alarm on the appliance: per the asphyxiation gap's recommended NDIR sensor, open the cabinet doors, ventilate, do not lean in.

This is the same content that should also live at `homesodamachine.com/u/NNN/co2-swap` per [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md), so the customer can pull it up on their phone during refill day.

## Where this lands in the existing docs

- **[`hardware/bom.md`](../../hardware/bom.md):** add a new §"CO2 cylinder restraint + service kit" with the Camco bracket (or strap of choice), the fiber washers, the CGA-320 wrench, the footprint template print, the maintenance card. ~$15–20 / unit incremental BOM.
- **[`hardware/purchases.md`](../../hardware/purchases.md):** add the Camco 57541 ASIN (or selected equivalent) and the fiber-washer pack ASIN as LIKELY-TO-BUY entries. Place orders before the next Founder Edition build cycle.
- **[`hardware/printed-parts/enclosure/`](../../hardware/printed-parts/enclosure/):** create a new `side-panel/` subdirectory with a README that owns the strap mount, the footprint template, and the customer maintenance card geometry. Cross-references from [`hardware/future.md`](../../hardware/future.md) §"Enclosure layout" and [`enclosure-exterior-doc-gap.md`](enclosure-exterior-doc-gap.md).
- **[`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md):** add a step that places the service kit zip-tied to the appliance's CO2 inlet hose before pack-out, and a step that confirms the strap/bracket is loose-installed (not yet customer-cylinder-specific) before the unit ships.
- **[`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md):** add a CGA-320 torque/leak-witness check to the existing step 1 (currently "Open the CO2 cylinder valve and set the primary CGA-320 regulator to 90 PSI" — no torque, no leak witness).
- **[`todo/2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md):** the install agenda already names "Where the CO2 cylinder will live" as a topic; extend it to "Cylinder placement + strap + footprint template" with a verbatim install-consult script ("strap before walking away").
- **[`marketing/target-market.md`](../../marketing/target-market.md):** the "What's the ongoing hassle?" answer in the purchase-decision section currently says "CO2 every few months (currently a trip to a gas supplier — a known rough edge)." Extend with "the refill procedure is a documented two-page card, and a service kit ships with the appliance." That is a small but visible reassurance for the buyer at $7,500 who is mentally inventorying the things they don't yet know how to do.

## What's intentionally out of scope here

- **Cabinet locks.** A locking cabinet door is the user's home, not our hardware. The maintenance card can recommend a $10 child-safety cabinet latch for households with toddlers, but adding hardware that locks the cabinet is overreach.
- **Earthquake bracing for the appliance itself.** The appliance is heavy (~80–100 lb assembled), short (~24" tall), and centered on the cabinet floor; tip-over physics for the appliance are dominated by the cabinet's own seismic anchoring, not by any restraint we ship. Same scope-boundary applies for hurricanes.
- **Tip-over sensor in the cylinder.** A small accelerometer + radio module that pages the iOS app on cylinder-tip would be a cute feature. It is not the right place to spend the dollar; the cylinder doesn't need a sensor, it needs a strap.
- **DOT-Special-Permit-class cylinder design.** The 5 lb CGA-320 cylinders we use are off-the-shelf 3AL aluminum from Catalina or Norris; their hydro-test cadence is 5 years and is the cylinder supplier's responsibility, not ours.

## Tie-in to the broader safety story

The repo already has the following safety-architecture pieces in flight or done:

- **Hydrocarbon-leak detection** (MQ-6 sensor placement — covered, with corrections, in [`leak-detection-coverage-gap.md`](leak-detection-coverage-gap.md)).
- **CO2 gas-escape detection** (NDIR sensor — covered in [`co2-asphyxiation-and-prv-vent-path-gap.md`](co2-asphyxiation-and-prv-vent-path-gap.md)).
- **PRV vent path** (same doc).
- **Electrical safety** ([`electrical-safety-acceptance-gap.md`](electrical-safety-acceptance-gap.md)).
- **Hydro-test acceptance** ([`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md)).
- **Water-damage containment** ([`water-damage-containment-gap.md`](water-damage-containment-gap.md)).

What's missing from that list is the **largest mechanical-energy reservoir in the system** — a 5–20 lb cylinder of compressed gas, stored on the cabinet floor with no restraint. The carbonator vessel holds maybe ~5 L of free CO2 inventory; the cylinder holds 1,230–4,900 L. Every other safety doc in the list above addresses something either smaller (the carbonator) or further away (refrigerant, water). The cylinder is the biggest, the closest, and the one currently unmanaged.

If a Founder Edition customer's child knocks over the cylinder while reaching for dish soap, and the regulator shears off the valve, and the cylinder penetrates the cabinet sidewall, that is a story whose ending writes the repo's first product-liability claim. The total cost to prevent that ending is ~$15–20 of hardware and ~10 minutes of install time per unit. The math is unforced.

## Effort budget

- Adding the BOM lines + ordering the strap + washer pack: ~30 min, one $30 Amazon order for 10-build stock.
- Writing the side-face exterior README: ~2 hours, drafts off [`enclosure-exterior-doc-gap.md`](enclosure-exterior-doc-gap.md)'s scope.
- Writing the customer maintenance card: ~1 hour. Lives in `marketing/customer-docs/co2-swap.md` (or wherever the customer-facing doc tree is decided to live; the per-unit portal gap is the natural home).
- Updating the install playbook + finish-pack-ship + acceptance-and-burn-in cross-references: ~30 min.
- Adding the strap mount geometry to the side-face print: ~2 hours of CAD work once the part exists. If the part doesn't exist yet, the geometry goes in with the rest of the side-face design.

Total: under one workday of work, ~$30 in parts for 10 builds of stock. Closes the gap end-to-end.

## What I'd want to double-check before committing

1. **Is the cylinder really in the side air-gap, or has it migrated to in front of the cabinet door?** [`hardware/future.md`](../../hardware/future.md) is firm on the side air-gap, but [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) hedges with "under the sink vs. in an adjacent cabinet." If the cylinder is in an adjacent cabinet, the side-face mount story is wrong and the restraint anchor needs to be a freestanding floor anchor (still doable, but different hardware).
2. **What torque is actually correct for CGA-320?** The published numbers vary wildly. The CGA itself (Compressed Gas Association) publishes a recommendation in CGA V-1 / V-9, but the consumer-grade fiber washer changes the answer materially. A bench test against an empty cylinder + a torque wrench would establish the right number for the maintenance card. ~1 hour at the bench.
3. **Is the Camco 57541 the right bracket?** The propane-tank specific geometry may bind awkwardly on a CO2 cylinder. Worth bench-fitting one before committing 50 units worth of stock. The fallback (generic nylon strap + cam buckle) is fine but less rigid.
4. **Does the customer's existing cylinder fit the bracket?** Some customers will have a 10 lb or 20 lb cylinder rather than the 5 lb the documentation assumes. The bracket needs to handle that range, or the install consult needs to ask up front and the founder needs to swap to a different size strap on the day.

None of those four are blocking; they're "answer before the next batch" items.

---

*This gap was identified by inventorying every place a high-energy or high-liability physical surface lives in the appliance system and asking whether it has a written mitigation. Every one had one — except the cylinder sitting beside the appliance on the cabinet floor. That asymmetry is what made this worth surfacing.*
