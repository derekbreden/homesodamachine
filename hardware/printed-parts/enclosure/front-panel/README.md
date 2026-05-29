# Front panel

3D-printed front face of the under-counter enclosure. Carries the ESP32-S3 detachable rotary display, the front-dispense spout, and the CO2 line inlet. Printed in **Bambu PET-CF**, matching the rest of the enclosure exterior.

Opening the cabinet door and looking at the front of the appliance shows the customer the display (rotate to toggle flavor, three-dot affordance for advanced settings), the dispense spout, and the CO2 connection. Pump cartridge access is on top in Zone C, beneath the removable funnel under the single top door ([`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md)); the GFCI lives on the electronics shelf. See [`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md) "What is on the front face" for the architectural framing.

## Front face features

| # | Feature | Hardware | Notes |
|---|---|---|---|
| 1 | ESP32-S3 rotary display | Meshnology ESP32-S3 1.28" Rotary Display (B0G5Q4LXVJ) | **Detachable.** Sits in a recess on the front face; the customer pulls it out and the [~1 m](DISPLAY_CORD_L) cord behind the panel pays out so they can hold the display or mount it on the cabinet's false-drawer-front above the cabinet door — the obvious empty flat panel just below the counter where a drawer would normally go. Re-seating retracts the cord. Default state shows the selected flavor; the rotary mechanism toggles between flavors; a subtle three-dot affordance reaches advanced settings. Seat, cord, retraction, and connector are all open — see §"S3 detach mechanism" below. |
| 2 | Front-dispense spout | TBD | The customer's drill-trigger moment — a visible thing on the front you press, soda comes out (currently-selected flavor, set on the S3). Internal plumbing taps the carbonator outlet + flavor-pump junction before the umbilical, with its own valve and a front-panel nozzle. Lever vs button vs glass-press TBD. |
| 3 | CO2 line inlet | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect | Customer's CGA-320 primary regulator hose ([~12"](CGA_TETHER_L) short tether per [`/hardware/bom.md`](/hardware/bom.md) §4) lands here. Downstream: GASHER 1/4" NPT SS check valve + WR1110 [fixed-90 PSI](REGULATOR_PRESSURE) secondary regulator before the cold-core CO2 input at the foam-cap top. Red accent ring at the panel opening per §"CO2 inlet — red color-coding" below. Possibly migrated to the furthest-forward edge of a side face — see §"CO2 inlet placement" below. |

## CO2 inlet placement

The inlet lands on the front face. A possible migration to the furthest-forward edge of a side face is open — see Open items.

## Cylinder placement

The CO2 cylinder sits **beside** the appliance on the cabinet floor, in the working air gap between one side of the appliance and the cabinet sidewall. The bottle-shaped visual affordance that lands the cylinder in place belongs to the side-face surface the cylinder neighbors; that surface's design document does not yet exist.

Front-panel scope as it relates to the cylinder: **position the DERPIPE inlet stub at a height matched to the customer's primary regulator outlet height**, so the short red tether takes the obvious path from the cylinder around the front-side corner to the inlet.

## CO2 inlet — red color-coding

The CO2 inlet is **red**. Stock is supplied red by the existing BOM SKUs:

- **5/16" ID beer CO2 line** ([`/hardware/bom.md`](/hardware/bom.md) §4, `B0D1RB3TF6`) — standard red beer-line PVC, runs from the customer's CGA-320 regulator to this panel.

The front-panel CO2 bulkhead gets a **red accent ring** at its panel opening. The ring mechanism (multi-material print, snap-on TPU collar, or paint touch) is the same open question as the blue ring on the back-panel doc; both colors should share whatever solution is committed.

Red on this panel is part of the three-color customer-wayfinding system committed in [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md) "Color system" — **blue = carbonated water, red = CO2, white = tap water**. The same red appears on the matching line drawing in the printed quick-start sheet, so the customer's eye moves from sheet to panel without translation. Any change to the red accent here (color shade, mechanism, placement) needs to round-trip through the unboxing brief because the printed sheet must match.

The internal 1/4" LLDPE between the front-panel CO2 PTC and the vessel-side TAISHER elbow is **black** (standard FWS stock).

## S3 detach mechanism

The S3 is the only detachable element on the front face. Its recess sits flush with the panel surface when undisturbed; a deliberate pull releases it. The cord ([~1 m](DISPLAY_CORD_L)) is coiled behind the panel inside the cabinet, paying out as the customer pulls the display out and retracting when the display is re-seated.

Open candidates:

- **Seat:** magnetic, click-detent, or friction-only.
- **Cord:** Cat6 (carries UART + [5 V](DISPLAY_SIGNAL_V) per the SIG-7 schedule), coiled stretch cable, or a custom flat ribbon.
- **Retraction:** spring-loaded retractor, hand-recoil, or no active retraction (cord hangs limp when extended).
- **Connector at the back of the display:** sized to fit through the recess opening and not obstruct re-seating.

## Internal routing — WR1110 placement

Downstream of the front-panel CO2 inlet stack: GASHER check → WR1110 secondary regulator → first PP010822E PTC × NPT M adapter → 1/4" OD LLDPE routed up through the electronics-shelf zone → cold-core CO2 input at the foam-cap top (+Z). Procedure detail in [`/hardware/assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §1.

The WR1110 mounts on a printed bracket somewhere along the CO2 path between the front-panel inlet and the foam-shell top. Exact bracket location is flexible per [`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md) "What is flexible".

## References

- [`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md) — enclosure architecture (4 zones, firm vs flexible, front-face curation).
- [`/hardware/future.md`](/hardware/future.md) — broader enclosure context, cylinder-beside-appliance layout, user-facing elements by location.
- [`/hardware/requirements.md`](/hardware/requirements.md) §5 — S3 role and detachability (the foundational spec for the S3 as the sole interaction surface).
- [`/hardware/bom.md`](/hardware/bom.md) §1 — ESP32-S3 module source.
- [`/hardware/bom.md`](/hardware/bom.md) §4 — CO2 path (DERPIPE bulkhead, GASHER check, WR1110, 5/16" short tether).
- [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) — sister exterior panel; identification-ring pattern, PET-CF material rationale.
- [`/hardware/assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §1 — CO2 path install procedure.

## Open items

- **Front-dispense spout design.** Lever vs button vs glass-press; internal plumbing tap point + valve choice + nozzle geometry; cleaning + fingerprint visibility. Feature is committed, geometry is not.
- **S3 detach mechanism.** Seat, cord, retraction, connector — all open per §"S3 detach mechanism".
- **CO2 inlet placement (front face vs side-face forward edge).** Resolved by deciding whether the migration to a side face is worth its complications.
- **Inlet-stub height on the front face.** The DERPIPE bulkhead height must match the customer's regulator-outlet height with the cylinder seated in its side-gap placement, so the short red tether takes the obvious path. Decision is downstream of the regulator stack measurement and the enclosure-exterior cylinder-placement decision.
- **Red accent ring mechanism.** Multi-material print, snap-on TPU collar, or paint touch — shares the decision pattern with the back-panel blue ring; both should land on the same approach.
- **WR1110 mounting bracket geometry.** Printed bracket along the CO2 path, downstream of the DERPIPE bulkhead position.
- **Double-shutoff QD on the inlet.** A flush-face / double-shutoff quick-disconnect at this inlet would close the "hose isn't seated when the cylinder valve opens" failure mode — no gas vents when the hose isn't connected to the panel.
- **Bottle-placement affordance (out of scope for this doc; flagged here for the cross-reference).** Lives on the as-yet-unwritten enclosure-exterior surface document. The front-panel inlet height depends on the cylinder side-gap decision made there.

## Status

Design-in-progress. No CAD generator yet. This README is the source-of-truth for the panel's front face contents and design intent until the geometry reaches a CAD generator.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/front-panel/_front_panel_dimensions.py`
