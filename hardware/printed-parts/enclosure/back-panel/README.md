# Rear face

**There is no separate back panel.** The rear face is a wall of the printed
`enclosure-back-top` piece, and every connection the appliance makes to the world
is a hole in it — cut by
[`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py)
from the pack's own `back_ports`
([`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py)). This file is that
face's connection inventory.

Everything lands in the band above the cold core: the umbilical port that accepts
the three tubes coming down from the under-cabinet faucet through the countertop,
the tap-water inlet, the AC inlet, and the **CO2 inlet**. The connector bodies
reach forward into the band's open rear half — the power column stands against the
+X wall, clear of them — so every body hangs in open air. The piece prints in
**PETG** — see §"Material" below.

The face has no fluid-pressure duty. It is a connection-management face:
hole patterns sized for off-the-shelf bulkheads and panel-mount receptacles,
with printed bezels, recesses, and labels where the user-facing fit-and-feel
benefits.

## Connections inventory

| # | Connection | Face | Hardware | Hole | Notes |
|---|---|---|---|---|---|
| 1 | AC inlet | Rear | IEC 60320 C14 panel-mount receptacle ([MXR B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ)) | rounded rectangular cutout per C14 spec, its flange landing on two printed bosses of its own | Easternmost station, below the umbilical row, at the end of the wall the power column stands against — its cordage drops the rear wall and runs forward to the AC distribution on that column. It lands from **inside**: flange on the wall's inner face, shroud out through the cutout, recessed [3–5 mm](AC_RECESS_DEPTH) with a printed shroud around the perimeter so the C13 cord housing nests flush. Cord housing is the strain relief — no separate grommet here, and no cable gland anywhere on this wall. Recess detail in §"AC inlet recess" below. |
| 2 | Water inlet | Rear | John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead union ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) — customer pushes the install-kit 1/4" LLDPE into this bulkhead, no tools | ø[18.0 mm](PANEL_HOLE_D) hole (identical SKU and hole to the 3 umbilical PP1208E ports) | **Customer-facing 1/4" JG QC**, on its own storey below the umbilical row's west end, its nut riding just above the rear seam-lip band. The install-kit Waterdrop 15UC-UF filter mounts customer-side, inline upstream of this bulkhead (`bom.md §3`). Inboard, the feed runs forward across the band above the cold core and down the foam-face slab: through the PP010822E 1/4" PTC × 1/4" NPT M → GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling → ASSE 1022's 3/8" MPT inlet, then the ASSE 1022's 3/8" MFL outlet → PI4512F6S + PP061208W → 1/4" LLDPE → water-split PP0208E tee → V-K → a clamped 3/8" stub onto the SeaFlo's molded suction barb. The internal ASSE 1022 chain sits *inside* the cabinet (downstream of the ASSE 1022's MFL outlet), not on this wall. Install kit ships **two** under-sink tee options + extra 1/4" LLDPE: a JG PP0208E 1/4" PTC × 1/4" PTC × 1/4" PTC union tee (black NSF-cert PP) for homes with 1/4" LLDPE already under the sink, and an HAOCHEN 3/8"×3/8"×1/4" angle-stop add-a-tee for homes with a 3/8" angle stop + braided compression supply. |
| 4 | CO2 inlet | Rear | DERPIPE 5/16" tube × 1/4" NPT push-to-connect ([B09LXVGPG7](https://www.amazon.com/dp/B09LXVGPG7)) | Ø[15.42](CO2_HOLE_D) round, east of centre and below the umbilical row | **On the rear face** — the customer's 5/16" supply tether from the CGA-320 regulator on their own cylinder pushes into this PTC. Red accent ring at the opening. Inboard, the GASHER 1/4" NPT SS check threads onto its own stub with the arrow pointing away from the wall, then the WR1110 secondary regulator, then the cold core's `co2-in` cap conduit (`bom.md §4`, [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §1). |
| 5 | Backflow-vent observation | — | Moisture sensor in the internal drip pan under the Multiplex 19-0897's atmospheric vent | n/a for the vent — no hole in this face; the basin withdraws through the −X side wall, not this one | The vent does not exit through this face. It terminates inside the cabinet over a printed drip pan; the ESP32-monitored moisture sensor in the pan is the telltale. Detail: [`/hardware/future.md`](/hardware/future.md) §"Backflow vent monitoring". The basin itself draws WEST on rails, out through a slot in the −X side wall (`enclosure_assembly.west_wall_ports`) — this face carries no part of it. |
| 6 | Umbilical port | Rear | 3× John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead unions ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) | 3× ø[18.0 mm](PANEL_HOLE_D) holes (identical to the water-inlet station's; cut by [`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) from the pack's `back_ports`, which each union's own panel footprint strikes) | Mid-panel, in the band above the cold core the foam and the rear seam lip leave open. Accepts the 3-tube umbilical bundle that runs from the under-cabinet Westbrass faucet down through the countertop to the rear of the appliance: 1× carbonated water + 2× flavor. User pushes each tube into its matching bulkhead — no tools. Same JG black-PP / NSF 51 + NSF 61 / 150 psi @ 70 °F bulkhead family already used inside the cold core, so the SKU is shared and the bulk 10-pack already in stock covers both uses. `bom.md §8`. |

## Umbilical port — tube identification

The 3-tube umbilical bundle leaves the faucet body, runs through the countertop into the cabinet, sleeved in a braided cover with foam insulation on the cold (carbonated-water) line for thermal protection on the most temperature-critical run in the system. At the rear face the user must connect each tube to the matching bulkhead — three identical-looking bulkheads in a black wall is a failure mode, so the carbonated-water tube and bulkhead are color-coded:

- **Carbonated water — blue.** Separate small spool of 1/4" OD blue LLDPE (sourcing in flight; not yet in `bom.md`). The bulkhead receiving it on the rear face is marked with a **blue accent ring** around its opening.
- **Flavor A / Flavor B — black.** Standard 1/4" OD black LLDPE from the existing FWS bulk spool (`bom.md §3` and elsewhere). The two flavor bulkheads have no accent ring — flavor A vs flavor B routing is handled by the manifold and is not user-visible at the face.

User rule at install: **blue tube into the blue-ringed bulkhead**, which stands at the [east](CARB_END) end of the row. Black-into-either-black is unambiguous from there because both flavor tubes route through the same wall-side bundle and the user does not need to distinguish them at the face.

Mechanism for the blue ring is TBD — candidates include multi-material printing of the piece itself, a separately printed TPU collar that snaps over the bulkhead's exterior flange, or a paint touch on the printed bezel surrounding the bulkhead. The selection is downstream of the multi-material capability of the printer running `enclosure-back-top`.

Net identification scheme on the rear face: **blue = carbonated water** [#1f6feb](CARB_COLOR), **black / plain = flavor lines**, **white = tap water** [#ffffff](WATER_COLOR) (the water bulkhead body itself is the white-marked station), **red = CO2** [#d63a3a](CO2_COLOR) (the DERPIPE PTC's own accent ring, below the C14 — station 4 above).

Blue naming carbonated water is what makes the other two fall out: the umbilical riser is bought as blue tube ([`bom.md`](/hardware/ledger/bom.md) §3) and the union that receives it is bought to wear a blue ring (§8), so blue is spent, and the customer's teed-in tap-water station is the white-marked one. The three colors are the customer-wayfinding system committed in [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md) "Color system"; the printed quick-start sheet paints its arrows and the iso line-art paints these rings from the one table in [`_back_panel_dimensions.py`](/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py), so the customer's eye moves from sheet to face without translation. Any change to a ring here (color shade, ring mechanism, placement on the face) needs to round-trip through the unboxing brief because the printed sheet must match.

## Umbilical bundle construction

The 3-tube umbilical from the faucet down to the rear face is bundled into a single sleeved run, wound in 1" nominal spiral wrap after both ends are terminated, per [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) §4.

**Foam insulation on the carbonated-water tube only.** The two flavor tubes carry ambient-temperature syrup at low duty cycle (a few mL per dispense) — warm-in, warm-out, no thermal benefit from insulation. The carbonated-water tube is the temperature-critical run: a multi-meter cold-line carrying chilled CO2-saturated water from the cold-core reservoir up to the faucet, where every degree of warm-up costs dissolved-CO2 retention. Insulating that one tube (and leaving the flavor tubes bare inside the sleeve) is the right thermal allocation.

- **Foam:** CARGEN nitrile rubber pipe insulation, 1/4" ID × 3/8" wall (`B0D2XFK337`, `bom.md §9`). Sized to slip over 1/4" OD LLDPE with a snug interference fit.
- **Foam ships as 1-ft segments.** Install procedure: slide five segments onto the carbonated-water tube and butt them together along the run. The spiral wrap over the bundle holds segments butted.
- **Tube cutting:** the three LLDPE tubes are cut once each, to length, using the kit's Mudder PEX/PE tube cutter (`bom.md §14`), then pushed into the rear wall's PP1208E bulkheads.
- **Foam segment count and total length:** five 1-ft CARGEN segments, 1425 mm total, per [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) §1.

## AC inlet recess

The C14 receptacle is recessed [3–5 mm](AC_RECESS_DEPTH) into the rear face with a printed shroud around the inlet perimeter. On insertion, the C13 cord housing nests into the recess and ends flush with that surface, masking the gap between cord and inlet bezel. IEC 60320 specifies the male-blade insertion region only, not face-to-face mating distance.

## References

- [`/hardware/future.md`](/hardware/future.md) — broader enclosure context, backflow-vent monitoring, layout.
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §8 — PP1208E umbilical line (3 on this wall); with the §3 water inlet the SKU is 4/build.
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3 — water-inlet path (Waterdrop filter, Multiplex 19-0897 backflow, the PI4512F6S + PP061208W outlet stack, water-split PP0208E tee, PP1208E wall bulkhead, HAOCHEN install-kit tee).
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 and [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) — AC runs C14 inward.
- [`../nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) — sister rear-face artifact (separately printed plaque).

## Bulkhead array arrangement

The 3× PP1208E umbilical-port bulkheads stand across the top of the field on one pitch (`enclosure_assembly.PANEL_X`). The order across it is the inboard runs': the two flavor gates take the west of the row, each on the side its run arrives from, and the carb union takes the [east](CARB_END) end with its DIGITEN meter lying inline ahead of it. The **blue-ringed (carbonated-water) bulkhead is the end one** — the user reads it by position in the row, not by a vertex.

The two flavor unions stand side by side at the [west](FLAVOR_B_END) end on a storey of their own, the lane their runs cruise in (`enclosure_assembly.PANEL_ON_GATE_LANE`), below the carb union's, under the tap-water bulkhead that takes its place on the row's own storey. East of centre is the C14 cutout, at the end of the wall the power column stands against, and below the C14 the CO2 PTC. Every station's Z is the pack's, and the wall takes its ceiling from the field's own top edge ([`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) `port_top`).

## Material

The rear face is a wall of `enclosure-back-top`, so it is that piece's material: **PETG** ($11.20/kg), the same as the rest of the enclosure ([`bom.md`](/hardware/ledger/bom.md) §7). Service temperature is above the ~30–40 °C cabinet ambient. There is no separate panel row in §7 because there is no separate panel.

## Open items

- **Blue ring identification mechanism**: multi-material print on the wall itself, snap-on TPU collar, or paint touch on a printed bezel. With PETG committed, multi-material on the wall itself requires a second compatible filament loaded in the AMS; snap-on TPU is the lowest-risk fallback.
- **Bezels, recesses and labels** have no CAD. The through-holes are cut; nothing around them is drawn yet. (The wall is not a moisture or vapor barrier — the appliance is not hermetic. The PP1208E bulkheads seal the pressurized fluid path *around the tube* via their internal EPDM O-rings; the wall interface is purely mechanical capture, flange + nut sandwiching the wall through its Ø[18](PANEL_HOLE_D_SHORT) hole, so no wall-side bulkhead gasket is required.)

## Status

Design-in-progress. The through-holes are cut into the back-top enclosure piece by `enclosure.py`; the recess, bezels, and labels have no CAD yet. This README is the source-of-truth for the rear face's connection inventory; see `../nameplate/README.md` for the equivalent state on the sister rear-face artifact.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py`
