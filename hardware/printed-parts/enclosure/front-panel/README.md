# Front panel

3D-printed front face of the under-counter enclosure. Carries the CO2 inlet (the customer's hose lands here), hosts the pump-cartridge access door, and mounts the Legrand GFCI behind a small cutout that exposes only the device's central button band — the door's geometry and operation live with the cartridge itself at [`../../flavor/pump-case/`](../../flavor/pump-case/), not here. Printed in **Bambu PET-CF**, matching the rest of the enclosure exterior; material rationale per the back-panel doc's "Panel material" section.

The panel has no fluid-pressure duty. It is a connection-management plate with one fluid bulkhead, one mechanical aperture (the pump-cartridge door), and one electrical aperture (the GFCI cutout). The bottle-placement affordance that lands the CO2 cylinder in the right spot is **not** owned by this front face — see "Cylinder placement — out of scope here" below.

## Connections inventory

| # | Connection | Hardware | Notes |
|---|---|---|---|
| 1 | CO2 line inlet | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect | Customer's CGA-320 primary regulator hose (~12" short tether per [`../../../bom.md`](../../../bom.md) §4) lands here. Downstream of this panel: GASHER 1/4" NPT SS check valve + WR1110 fixed-90 PSI secondary regulator before the cold core. Red accent ring at panel opening per §"CO2 inlet — red color-coding" below. |
| 2 | GFCI cutout | Rectangular cutout matching the Legrand Radiant 1597BKCCD12 central button band (per [`../../../bom.md`](../../../bom.md) §5) | Exposes only the device's TEST/RESET buttons + status LED; the device's two 5-15R receptacle outlets sit behind the printed material and are not customer-accessible. Device mounts face-flush with the back of the printed panel via standard single-gang yoke screws (~83 mm / 3.28" on center). See [`../../../../business/regulatory.md`](../../../../business/regulatory.md) "UL 943 — ground-fault protection" and §"GFCI cutout — geometry TBD" below. |

## Cylinder placement — out of scope here

The CO2 cylinder sits **beside** the appliance on the cabinet floor, in the working air gap between one side of the appliance and the cabinet sidewall — **not** in front of the front face. Putting the cylinder in front would block the cabinet door from opening and put a ~9 lb pressurized aluminum bottle in the customer's shins every time they reach in. That's not the layout.

The bottle-shaped visual affordance that lands the cylinder in the right place (a curve matched to the cylinder body OD, no restraint, just "feels right when you set it down") belongs to whichever exterior surface the cylinder neighbors in the side gap — almost certainly one of the side faces, possibly with a contribution from the floor edge. That surface is **not** this front face, and its design document does not yet exist. See Open items below.

The front-panel scope, as it relates to the cylinder, reduces to a single decision: **position the DERPIPE inlet stub at a height matched to the customer's primary regulator outlet height**, so the short red tether takes the obvious path from the cylinder (sitting in the side gap, regulator on top) around the front-side corner to the inlet on the front face. Inlet height is a panel-CAD decision and lives here. Cylinder geometry does not.

## CO2 inlet — red color-coding

The CO2 inlet is **red** by industry-standard convention across beverage, brewing, and draft-equipment practice. Stock is already supplied red by the existing BOM SKUs:

- **5/16" ID beer CO2 line** ([`../../../bom.md`](../../../bom.md) §4, `B0D1RB3TF6`) — standard red beer-line PVC, runs from the customer's CGA-320 regulator to this panel.
- **Imaictuu 5/16" ID red PVC** (Feb 13, 2026 Amazon order) — backup / second-source for the same line.

The front-panel CO2 bulkhead gets a **red accent ring** at its panel opening. The ring mechanism (multi-material print, snap-on TPU collar, or paint touch) is the same open question as the blue ring on the back-panel doc; both colors should share whatever solution is committed.

Red on this panel is part of the broader three-color customer-wayfinding system committed in [`../../../../marketing/unboxing-and-quickstart.md`](../../../../marketing/unboxing-and-quickstart.md) "The color discipline" — **blue = carbonated water, red = CO2, third color TBD = install action**. The same red appears on the matching line drawing in the printed quick-start sheet, so the customer's eye moves from sheet to panel without translation. Any change to the red accent here (color shade, mechanism, placement) needs to round-trip through the unboxing brief because the printed sheet must match.

The internal 1/4" LLDPE between the front-panel CO2 PTC and the vessel-side TAISHER elbow is **black** (standard FWS stock). A red 1/4" LLDPE for service-technician visibility on the internal run is a future enhancement, not a TBD requiring action.

## GFCI cutout — geometry TBD

The Legrand Radiant 1597BKCCD12 mounts face-flush behind the printed front panel. A rectangular cutout exposes only the central TEST/RESET/LED band — the two 5-15R receptacle outlets above and below the buttons sit behind the printed material and are not customer-accessible. Exact cutout dimensions need to be measured off a physical device sample before the CAD is locked (2 units on order per [`../../../purchases.md`](../../../purchases.md) §9).

Material thickness at the cutout area should be thinned from the panel's nominal ~3 mm down to ~1–1.5 mm so a finger pressing through the cutout reaches and operates the TEST/RESET buttons cleanly. PET-CF prints reliably at 1.5 mm; 1 mm to be validated empirically.

Mounting bosses on the inner face of the panel capture the device's standard single-gang yoke screws (~83 mm / 3.28" on center, top and bottom).

AC wiring (runs AC-1a and AC-1b per [`../../../wiring/ac-wiring-schedule.md`](../../../wiring/ac-wiring-schedule.md)) lands at the device's LINE and LOAD terminals on the back of the device. The wires cross the enclosure depth from the rear-panel C14 inlet (LINE side) and back to the electronics-shelf AC distribution block (LOAD side). Routing follows the existing pre-printed channels in the enclosure shell; strain-relief grommets at any panel pass-through TBD.

The labels "TEST" and "RESET" should be printed/etched on the front panel adjacent to each button cutout, since the device's own embossed labels will be partially covered by the printed material. Adjacent placement, font, and color discipline are open.

## Internal routing — WR1110 placement

Downstream of the front-panel inlet stack: GASHER check → WR1110 secondary regulator → first PP010822E PTC × NPT M adapter → 1/4" OD LLDPE up over the manifold → cold-core CO2 input at the foam-cap top. Procedure detail in [`../../../assembly/internal-plumbing.md`](../../../assembly/internal-plumbing.md) §1.

The WR1110 mounts on a printed bracket against the front-panel inner face so transport vibration doesn't stress the NPT stub. Bracket geometry is TBD with the panel CAD.

The 1/4" LLDPE run from the front-panel stack to the cold-core CO2 input is longer than the prior back-panel-CO2 version — front-to-back across or around the manifold instead of landing directly behind the cold core. Tube routing follows the existing pre-printed channels in the enclosure shell.

## References

- [`../../../future.md`](../../../future.md) — broader enclosure context, cylinder-beside-appliance layout, user-facing elements by location.
- [`../../../bom.md`](../../../bom.md) §4 — CO2 path (DERPIPE bulkhead, GASHER check, WR1110, 5/16" short tether).
- [`../back-panel/README.md`](../back-panel/README.md) — sister exterior panel; identification-ring pattern, PET-CF material rationale.
- [`../../flavor/pump-case/`](../../flavor/pump-case/) — pump-cartridge access door geometry (lives on this same face).
- [`../../../assembly/internal-plumbing.md`](../../../assembly/internal-plumbing.md) §1 — CO2 path install procedure.

## Open items

- **Inlet-stub height on the panel.** The DERPIPE bulkhead height must match the customer's regulator-outlet height with the cylinder seated in its side-gap placement, so the short red tether takes the obvious path. Decision is downstream of the regulator stack measurement and the enclosure-exterior cylinder-placement decision (which side gap).
- **Red accent ring mechanism.** Multi-material print, snap-on TPU collar, or paint touch — shares the decision pattern with the back-panel blue ring; both should land on the same approach.
- **WR1110 mounting bracket geometry.** Printed bracket against the front-panel inner face capturing the regulator body, downstream of the DERPIPE bulkhead position.
- **Pump-cartridge door cutout coordination.** Cutout rectangle matched to the [`pump-case/`](../../flavor/pump-case/) generator's outboard footprint.
- **GFCI cutout dimensions.** Cutout rectangle matched to the Legrand 1597BKCCD12 central button band, measured off the physical device once on hand (2 units on order). Working estimate ~38 × 38 mm; verify before CAD lock.
- **Panel thickness at the GFCI cutout.** Test 1 mm vs 1.5 mm PET-CF at the cutout region for button operability through the printed material; both protrudes through the device face and finger reach through the cutout depth matter.
- **TEST / RESET labels on the front panel.** Embossed-into-panel vs printed paint vs accent-color decal; same decision pattern as the red/blue accent rings, both should land on a consistent approach.
- **AC wire pass-throughs on the front panel.** Strain-relief grommets where AC-1a (from C14 inlet) and AC-1b (to AC distribution block) land at the device's LINE/LOAD terminals on the inside face of the panel.
- **Double-shutoff QD on the inlet.** A flush-face / double-shutoff quick-disconnect at this inlet would close the "hose isn't seated when the cylinder valve opens" failure mode — no gas vents when the hose isn't connected to the panel. Separate fork working that detail; lands here when committed.
- **Bottle-placement affordance (out of scope for this doc; flagged here for the cross-reference).** Lives on the as-yet-unwritten enclosure-exterior surface document. The front-panel inlet height depends on the cylinder side-gap decision made there.

## Status

Design-in-progress. No CAD generator yet. This README is the source-of-truth for the panel's connection inventory and design intent until the geometry reaches `generate_step_cadquery.py`; see [`../back-panel/README.md`](../back-panel/README.md) "Status" for the equivalent state on the sister panel.
