# Front panel

3D-printed front face of the under-counter enclosure. Carries the CO2 inlet (the customer's hose lands here) and the visual cylinder cradle that organizes where the customer places their CO2 bottle inside the cabinet. Also hosts the pump-cartridge access door — its geometry and operation live with the cartridge itself at [`../../flavor/pump-case/`](../../flavor/pump-case/), not here. Printed in **Bambu PET-CF**, matching the rest of the enclosure exterior; material rationale per the back-panel doc's "Panel material" section.

The panel has no fluid-pressure duty. It is a connection-management plate with one fluid bulkhead and one mechanical aperture, plus the cradle affordance that makes "cylinder goes here" obvious without instructions.

## Connections inventory

| # | Connection | Hardware | Notes |
|---|---|---|---|
| 1 | CO2 line inlet | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect | Customer's CGA-320 primary regulator hose (~12" short tether per [`../../../bom.md`](../../../bom.md) §4) lands here. Downstream of this panel: GASHER 1/4" NPT SS check valve + WR1110 fixed-90 PSI secondary regulator before the cold core. Red accent ring at panel opening per §"CO2 inlet — red color-coding" below. |

## Cylinder placement

The CO2 cylinder sits beside the appliance on the cabinet floor — not inside the appliance, not strapped to the panel. The panel's job is to make "cylinder goes here" obvious without the customer reading the install guide:

- A cylinder-shaped recess (shallow vertical notch) sculpted into the floor-side of the front face beside the inlet stub
- A retention strap or printed cradle holding the cylinder upright against vibration, one-handed to release at refill time
- Inlet stub positioned so the cylinder's CGA-320 outlet aligns naturally when the cylinder sits in the recess, keeping the tether short and out of the way

The intent is fit-and-feel: the customer reads "cylinder goes here" before they read any instructions. Geometric specifics (recess depth, inlet height, strap mechanism) are panel-CAD decisions and are flagged in Open items below.

## CO2 inlet — red color-coding

The CO2 inlet is **red** by industry-standard convention across beverage, brewing, and draft-equipment practice. Stock is already supplied red by the existing BOM SKUs:

- **5/16" ID beer CO2 line** ([`../../../bom.md`](../../../bom.md) §4, `B0D1RB3TF6`) — standard red beer-line PVC, runs from the customer's CGA-320 regulator to this panel.
- **Imaictuu 5/16" ID red PVC** (Feb 13, 2026 Amazon order) — backup / second-source for the same line.

The front-panel CO2 bulkhead gets a **red accent ring** at its panel opening. The ring mechanism (multi-material print, snap-on TPU collar, or paint touch) is the same open question as the blue ring on the back-panel doc; both colors should share whatever solution is committed.

The internal 1/4" LLDPE between the front-panel CO2 PTC and the vessel-side TAISHER elbow is **black** (standard FWS stock). A red 1/4" LLDPE for service-technician visibility on the internal run is a future enhancement, not a TBD requiring action.

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

- **Cradle / strap / inlet-height geometry.** Panel-CAD decision. Sized against a 5 lb aluminum CGA-320 cylinder (~12" tall × ~5" OD) sitting beside the appliance on the cabinet floor; coexisting with the pump-cartridge access door already on this face.
- **Red accent ring mechanism.** Multi-material print, snap-on TPU collar, or paint touch — shares the decision pattern with the back-panel blue ring; both should land on the same approach.
- **WR1110 mounting bracket geometry.** Printed bracket against the front-panel inner face capturing the regulator body.
- **Double-shutoff QD on the inlet.** A flush-face / double-shutoff quick-disconnect at this inlet would close the "hose isn't seated when the cylinder valve opens" failure mode — no gas vents when the hose isn't connected to the panel. Separate fork working that detail; lands here when committed.

## Status

Design-in-progress. No CAD generator yet. This README is the source-of-truth for the panel's connection inventory and design intent until the geometry reaches `generate_step_cadquery.py`; see [`../back-panel/README.md`](../back-panel/README.md) "Status" for the equivalent state on the sister panel.
