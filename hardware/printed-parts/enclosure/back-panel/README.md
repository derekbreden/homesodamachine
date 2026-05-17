# Rear panel

3D-printed rear face of the under-counter enclosure. Carries every external connection on the appliance: AC inlet, tap-water inlet, CO2 line inlet, bag-in-box (BiB) syrup inlet, the moisture-sensor drip-pan vent that observes the §3 backflow preventer, and (new) the umbilical port that accepts the three tubes coming down from the under-cabinet faucet through the countertop. Printed in the same stock as the rest of the enclosure shell — PETG or PETG-CF, panel material TBD pending the enclosure-wide print-stock decision.

The panel itself has no fluid-pressure duty. It is a connection-management plate: hole patterns sized for off-the-shelf bulkheads and panel-mount receptacles, with printed bezels, recesses, and labels where the user-facing fit-and-feel benefits.

## Connections inventory

| # | Connection | Hardware | Panel hole | Notes |
|---|---|---|---|---|
| 1 | AC inlet | IEC 60320 C14 panel-mount receptacle ([MXR B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ)) | rectangular cutout per C14 spec | Recessed 3–5 mm into the panel face with a printed shroud around the perimeter so the C13 cord housing nests flush. Cord housing is the strain relief — no separate grommet on this panel. (The Heyco SB-500-6 in `bom.md §11` is the cord grommet on the compressor shroud, a different sheet-metal part.) Recess detail in §"AC inlet recess" below. |
| 2 | Water inlet | brewhardware FFL38BARB38 3/8" FFL swivel × 3/8" SS hose barb → JoyTube 3/8" ID food-grade silicone hose downstream to the SeaFlo pump | mounting follows the FFL38BARB38's panel-thread profile (TBD as the panel reaches CAD) | Suction side of the SeaFlo pump. Full upstream path (tap → ASSE 1022 backflow → FFL38BARB38 → silicone hose → pump): `../../../future.md` line 33 / `bom.md §3`. The customer-supplied 3/8" supply line lands at this fitting. |
| 3 | CO2 line inlet | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect through-panel | ø follows DERPIPE bulkhead spec | Customer feed comes from their CGA-320 primary regulator. Downstream of this panel, the line passes a GASHER 1/4" NPT SS check valve and the Interstate Pneumatics WR1110 fixed-90 PSI secondary regulator before reaching the cold core. Detail: `../../../future.md` §"Carbonation subsystem" + `bom.md §4`. |
| 4 | BiB syrup adapter | Supply Depot 3/8" red BiB connector ([B0DMFK9B6P](https://www.amazon.com/dp/B0DMFK9B6P)) — one connector on the panel feeding both flavors via the §8 PP010822E + PP2308E Y-divider tree downstream | TBD (follows Supply Depot connector spec) | Secondary input path for users who source commercial syrup. The primary path is the top-face hopper — see `../../../future.md` §"Flavor subsystem". `bom.md §8`. |
| 5 | Backflow-vent observation | Moisture sensor in the internal drip pan under the Multiplex 19-0897's atmospheric vent | n/a — drip pan + sensor mount inboard of the panel, no panel hole | The vent does not exit through the rear panel. It terminates inside the cabinet over a printed drip pan; the ESP32-monitored moisture sensor in the pan is the telltale. Detail: `../../../future.md` §"Backflow vent monitoring". |
| 6 | Umbilical port (NEW) | 3× John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead unions ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) | 3× ø17.0 mm panel holes (same hole the §8 reservoir-cap PP1208E uses; see `printed-parts/cold-core/reservoir/generate_step_cadquery.py` lines 251–310 for the pocket / panel-hole geometry that ports here) | Accepts the 3-tube umbilical bundle that runs from the under-cabinet Westbrass faucet down through the countertop to the rear of the appliance: 1× carbonated water + 2× flavor. User pushes each tube into its matching bulkhead — no tools. Same JG black-PP / NSF 51 + NSF 61 / 150 psi @ 70 °F bulkhead family already used inside the cold core, so the SKU is shared and the bulk 10-pack already in stock covers both uses. `bom.md §8`. |

## Umbilical port — tube identification

The 3-tube umbilical bundle leaves the faucet body, runs through the countertop into the cabinet, sleeved in a braided cover with foam insulation on the cold (carbonated-water) line for thermal protection on the most temperature-critical run in the system. At the rear panel the user must connect each tube to the matching bulkhead — three identical-looking bulkheads in a black panel is a failure mode, so the carbonated-water tube and bulkhead are color-coded:

- **Carbonated water — blue.** Separate small spool of 1/4" OD blue LLDPE (sourcing in flight; not yet in `bom.md`). The bulkhead receiving it on the rear panel is marked with a **blue accent ring** around its opening.
- **Flavor A / Flavor B — black.** Standard 1/4" OD black LLDPE from the existing FWS bulk spool (`bom.md §3` and elsewhere). The two flavor bulkheads have no accent ring — flavor A vs flavor B routing is handled by the manifold and is not user-visible at the panel.

User rule at install: **blue tube into the blue-ringed bulkhead**. Black-into-either-black is unambiguous from there because both flavor tubes route through the same panel-side bundle and the user does not need to distinguish them at the panel.

Mechanism for the blue ring is TBD — candidates include multi-material printing of the panel itself, a separately printed TPU collar that snaps over the bulkhead's exterior flange, or a paint touch on the printed bezel surrounding the bulkhead. The selection is downstream of the panel-material decision and the multi-material capability of the printer running the panel.

## AC inlet recess

The C14 receptacle is recessed 3–5 mm into the panel face with a printed shroud around the inlet perimeter. On insertion, the C13 cord housing nests into the recess and ends flush with the panel surface, visually masking the IEC-mandated gap between cord and inlet bezel.

This is purely a fit-and-feel improvement; no electrical or mechanical change to the connector. The visible gap between cord housing and inlet face is by design under IEC 60320, which specifies only the male-blade insertion region — not face-to-face mating distance. The C13/C14 cross-test pair (uxcell inlet B07PXSLBF4 + Tripp Lite cord B0000511C0, ordered Apr 24, 2026) confirmed all four parts in the MXR × Monoprice / MXR × TrippLite / uxcell × Monoprice / uxcell × TrippLite matrix mate to spec — the gap is the standard, not the parts. For a hand-built Founder Edition appliance the printed shroud is the cheapest path to a "fully seated" user-facing appearance.

Locking C13 cords (Tripp Lite P-Lock series and similar) were considered and rejected: the design concern is fit/feel feedback at insertion, not mechanical retention, and friction-only retention is sufficient for an under-counter install. A hardwired-cord alternative (KitchenAid / Vitamix pattern, no detachable connector at all) is held under separate consideration and would obviate the bezel-recess solution if pursued.

## References

- `../../../future.md` — broader enclosure context, original AC-inlet recess rationale, backflow-vent monitoring, layout.
- `../../../bom.md §8` — PP1208E line (qty 5/build: 2 reservoir + 3 rear-panel).
- `../../../bom.md §3` — water-inlet path (Multiplex 19-0897 backflow, FFL38BARB38, JoyTube).
- `../../../bom.md §4` — CO2 path (WR1110, GASHER check, DERPIPE bulkhead).
- `../../../bom.md §11` and `../../../wiring/ac-wiring-schedule.md` — AC runs C14 inward.
- `../nameplate/README.md` — sister rear-face artifact (separately printed plaque).

## Open items

- **Bulkhead array arrangement** for the 3× PP1208E umbilical-port bulkheads: triangular cluster, in-line vertical row, or in-line horizontal row. Driven by faucet-side bundle routing through the countertop hole, panel-side fingertip clearance for the PTC collet release, and visual ordering relative to the blue-ringed bulkhead.
- **Blue ring identification mechanism**: multi-material print on the panel itself, snap-on TPU collar, or paint touch on a printed bezel. Driven by the panel-material decision and the printer's multi-material capability.
- **Final panel material**: PETG vs PETG-CF. The rear panel sees no thermal load but does carry threaded inserts and bulkhead clamp loads where stiffness matters; PETG-CF is the stiffer candidate at higher cost.
- **Panel mounting** to the enclosure shell: screw pattern, heat-set insert plan, gasket-or-no-gasket. To be decided alongside the enclosure-wall design.
- **Bulkhead-to-panel sealing**: the PP1208E ships with an EPDM O-ring on the panel-side flange; whether that O-ring is sufficient against a printed PETG/PETG-CF panel surface or whether a TPU gasket washer is added is TBD pending the first dry-fit.

## Status

Design-in-progress. No CAD generator yet. This README is the source-of-truth for the panel's connection inventory until the geometry reaches `generate_step_cadquery.py`; see `../nameplate/README.md` for the equivalent state on the sister rear-face artifact.
