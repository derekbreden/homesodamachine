# Rear panel

The external-connection face of the enclosure. Every connection the appliance
makes to the world except CO2 lands on the rear face, in the band above the
cold core: the umbilical port that accepts the three tubes coming down from
the under-cabinet faucet through the countertop, the tap-water inlet, and the
AC inlet. The connector bodies reach forward into the band's open rear half —
the electronics shelf lying on the foam-cap top stays ahead of them, so every
body hangs in open air. The CO2 inlet lives on
the front panel — see [`/hardware/future.md`](/hardware/future.md)
§"Enclosure layout". The face is a wall of the printed back-top enclosure
piece (the holes are cut by
[`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py)
from `_contents.py`'s port layout), printed in **PETG** — see §"Panel
material" below.

The panel has no fluid-pressure duty. It is a connection-management face:
hole patterns sized for off-the-shelf bulkheads and panel-mount receptacles,
with printed bezels, recesses, and labels where the user-facing fit-and-feel
benefits.

## Connections inventory

| # | Connection | Face | Hardware | Panel hole | Notes |
|---|---|---|---|---|---|
| 1 | AC inlet | Rear | IEC 60320 C14 panel-mount receptacle ([MXR B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ)) | rectangular cutout per C14 spec | Leftmost station, on the power assembly's column — its cordage drops the rear wall and runs forward over the foam-cap top to the AC distribution on the shelf. Recessed [3–5 mm](AC_RECESS_DEPTH) into the panel face with a printed shroud around the perimeter so the C13 cord housing nests flush. Cord housing is the strain relief — no separate grommet on this panel. (The cable gland in `bom.md §11` is the cord strain relief on the compressor shroud, a different sheet-metal part.) Recess detail in §"AC inlet recess" below. |
| 2 | Water inlet | Rear | John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead union ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) — customer pushes the install-kit 1/4" LLDPE into this bulkhead, no tools | ø[18.0 mm](PANEL_HOLE_D) panel hole (identical SKU and hole to the 3 umbilical PP1208E ports) | **Customer-facing 1/4" JG QC**, between the AC inlet and the umbilical cluster, its nut riding just above the rear seam-lip band. The install-kit Waterdrop 15UC-UF filter mounts customer-side, inline upstream of this bulkhead (`bom.md §3`). Inboard, the feed runs forward across the band above the cold core and down the foam-face slab: through the PP010822E 1/4" PTC × 1/4" NPT M → GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling → ASSE 1022's 3/8" MPT inlet, then the ASSE 1022's 3/8" MFL outlet → flare38-14ptc → 1/4" LLDPE → water-split PP0208E tee → V-K → SeaFlo suction. The internal ASSE 1022 chain sits *inside* the cabinet (downstream of the ASSE 1022's MFL outlet), not on this panel. Install kit ships **two** under-sink tee options + extra 1/4" LLDPE: a JG PP0208E 1/4" PTC × 1/4" PTC × 1/4" PTC union tee (black NSF-cert PP) for homes with 1/4" LLDPE already under the sink, and an HAOCHEN 3/8"×3/8"×1/4" angle-stop add-a-tee for homes with a 3/8" angle stop + braided compression supply. |
| 5 | Backflow-vent observation | — | Moisture sensor in the internal drip pan under the Multiplex 19-0897's atmospheric vent | n/a — drip pan + sensor mount inboard of the panel, no panel hole | The vent does not exit through the panel. It terminates inside the cabinet over a printed drip pan; the ESP32-monitored moisture sensor in the pan is the telltale. Detail: `../../../future.md` §"Backflow vent monitoring". |
| 6 | Umbilical port | Rear | 3× John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead unions ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) | 3× ø[18.0 mm](PANEL_HOLE_D) panel holes (identical to the water-inlet station's hole; cut by [`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) from `_contents.py` `PORT_BULKHEAD_D`) | Mid-panel, in the band above the cold core the foam and the rear seam lip leave open. Accepts the 3-tube umbilical bundle that runs from the under-cabinet Westbrass faucet down through the countertop to the rear of the appliance: 1× carbonated water + 2× flavor. User pushes each tube into its matching bulkhead — no tools. Same JG black-PP / NSF 51 + NSF 61 / 150 psi @ 70 °F bulkhead family already used inside the cold core, so the SKU is shared and the bulk 10-pack already in stock covers both uses. `bom.md §8`. |

## Umbilical port — tube identification

The 3-tube umbilical bundle leaves the faucet body, runs through the countertop into the cabinet, sleeved in a braided cover with foam insulation on the cold (carbonated-water) line for thermal protection on the most temperature-critical run in the system. At the rear panel the user must connect each tube to the matching bulkhead — three identical-looking bulkheads in a black panel is a failure mode, so the carbonated-water tube and bulkhead are color-coded:

- **Carbonated water — blue.** Separate small spool of 1/4" OD blue LLDPE (sourcing in flight; not yet in `bom.md`). The bulkhead receiving it on the rear panel is marked with a **blue accent ring** around its opening.
- **Flavor A / Flavor B — black.** Standard 1/4" OD black LLDPE from the existing FWS bulk spool (`bom.md §3` and elsewhere). The two flavor bulkheads have no accent ring — flavor A vs flavor B routing is handled by the manifold and is not user-visible at the panel.

User rule at install: **blue tube into the blue-ringed bulkhead**. Black-into-either-black is unambiguous from there because both flavor tubes route through the same panel-side bundle and the user does not need to distinguish them at the panel.

Mechanism for the blue ring is TBD — candidates include multi-material printing of the panel itself, a separately printed TPU collar that snaps over the bulkhead's exterior flange, or a paint touch on the printed bezel surrounding the bulkhead. The selection is downstream of the panel-material decision and the multi-material capability of the printer running the panel.

Net identification scheme on the rear panel: **blue = carbonated water**, **black / plain = flavor lines**, **white = tap water** (the water bulkhead body itself is the white-marked station). (The CO2 inlet lives on the front panel — see [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md); red color-coding for CO2 lines is documented there.)

Blue on this panel is part of the three-color customer-wayfinding system committed in [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md) "Color system" — **blue = carbonated water, red = CO2, white = tap water**. The same blue appears on the matching line drawing in the printed quick-start sheet, so the customer's eye moves from sheet to panel without translation. Any change to the blue ring here (color shade, ring mechanism, placement on the panel) needs to round-trip through the unboxing brief because the printed sheet must match.

## Umbilical bundle construction

The 3-tube umbilical from the faucet down to the rear panel is bundled into a single sleeved run. Sleeve material — braided polyester sleeve vs. spiral wrap — is TBD pending fit-up against the countertop pass-through.

**Foam insulation on the carbonated-water tube only.** The two flavor tubes carry ambient-temperature syrup at low duty cycle (a few mL per dispense) — warm-in, warm-out, no thermal benefit from insulation. The carbonated-water tube is the temperature-critical run: a multi-meter cold-line carrying chilled CO2-saturated water from the cold-core reservoir up to the faucet, where every degree of warm-up costs dissolved-CO2 retention. Insulating that one tube (and leaving the flavor tubes bare inside the sleeve) is the right thermal allocation.

- **Foam:** CARGEN nitrile rubber pipe insulation, 1/4" ID × 3/8" wall (`B0D2XFK337`, `bom.md §9`). Sized to slip over 1/4" OD LLDPE with a snug interference fit.
- **Foam ships as 1-ft segments.** Install procedure: slide segments onto the carbonated-water tube, discard the segments that don't fit the cabinet-routing length, butt the remaining segments together along the run. The braided sleeve over the bundle holds segments butted.
- **Tube cutting:** the three LLDPE tubes are cut once each, to length, using the kit's Mudder PEX/PE tube cutter (`bom.md §14`), then pushed into the rear-panel PP1208E bulkheads.
- **Foam segment count and total length:** TBD pending the cabinet-routing-length spec (depends on countertop thickness, faucet drop, and rear-panel position within the cabinet).

## AC inlet recess

The C14 receptacle is recessed [3–5 mm](AC_RECESS_DEPTH) into the rear panel face with a printed shroud around the inlet perimeter. On insertion, the C13 cord housing nests into the recess and ends flush with the panel surface, masking the gap between cord and inlet bezel. IEC 60320 specifies the male-blade insertion region only, not face-to-face mating distance.

## References

- `../../../future.md` — broader enclosure context, backflow-vent monitoring, layout.
- `../../../bom.md §8` — PP1208E umbilical line (3 rear-panel); with the §3 water inlet the SKU is 4/build.
- `../../../bom.md §3` — water-inlet path (Waterdrop filter, Multiplex 19-0897 backflow, flare38-14ptc, water-split PP0208E tee, PP1208E panel bulkhead, HAOCHEN install-kit tee).
- `../../../bom.md §11` and `../../../wiring/ac-wiring-schedule.md` — AC runs C14 inward.
- `../nameplate/README.md` — sister rear-face artifact (separately printed plaque).

## Bulkhead array arrangement

The 3× PP1208E umbilical-port bulkheads are arranged in a **triangular cluster** on the rear panel — three circles tangent in the densest packing. Three 1/4" OD tubes naturally pack the same way inside the umbilical bundle (densest-three-circle triangle), so the panel-side hole pattern mirrors the bundle-side tube pattern: the user presents the bundle to the panel and each tube already sits in front of its matching bulkhead. The blue-ringed (carbonated-water) bulkhead sits at the top vertex of the triangle. The tap-water bulkhead and the C14 inlet sit left of the cluster — the C14 directly above the power assembly its cordage drops to.

## Panel material

The rear panel — and the rest of the enclosure exterior — is printed in **PETG** ($11.20/kg), the same material as the enclosure halves ([`bom.md`](/hardware/ledger/bom.md) §7). Service temperature is above the ~30–40 °C cabinet ambient.

## Open items

- **Blue ring identification mechanism**: multi-material print on the panel itself, snap-on TPU collar, or paint touch on a printed bezel. With PETG committed, multi-material on the panel itself requires a second compatible filament loaded in the AMS; snap-on TPU is the lowest-risk fallback.
- **Panel mounting** to the enclosure shell: screw pattern, heat-set insert plan, gasket-or-no-gasket. To be decided alongside the enclosure-wall design. (Note: the panel is not a moisture or vapor barrier — the appliance is not hermetic. The PP1208E bulkheads seal the pressurized fluid path *around the tube* via their internal EPDM O-rings; the panel interface is purely mechanical capture, flange + nut sandwiching the panel through its Ø[18](PANEL_HOLE_D_SHORT) hole, so no panel-side bulkhead gasket is required.)

## Status

Design-in-progress. The through-holes are cut into the back-top enclosure piece by `enclosure.py`; the recess, bezels, and labels have no CAD yet. This README is the source-of-truth for the panel's connection inventory; see `../nameplate/README.md` for the equivalent state on the sister rear-face artifact.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py`
