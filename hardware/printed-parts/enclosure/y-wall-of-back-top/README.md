# +Y wall of back-top

**It is not a part of its own.** The face every connection crosses is a wall of the printed
`enclosure-back-top` piece, and every connection the appliance makes to the world
is a hole in it — cut by
[`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py)
from the pack's own `back_ports`
([`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py)). This file is that
face's connection inventory.

Everything lands in the band above the cold core: the umbilical port that accepts
the three tubes coming down from the under-cabinet faucet through the countertop
and the keystone jack its signal ribbon plugs into, the tap-water inlet, the AC
inlet, and the **CO2 inlet**. The connector bodies
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
| 1 | AC inlet | Rear | IEC 60320 C14 panel-mount receptacle ([MXR B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ)) | rounded rectangular cutout per C14 spec, bored through a printed tunnel standing round it on the inner face | Easternmost station, below the umbilical row, at the end of the wall the power column stands against — its cordage drops the wall and runs forward to the AC distribution on that column. It lands from **inside**: flange on that tunnel's fore face with an M3 heat-set either side of the bore, shroud back up the tunnel toward the cutout. Nothing stands proud of the wall. The C13 cord housing nests [3–5 mm](AC_RECESS_DEPTH) down the same bore on insertion. Cord housing is the strain relief — no separate grommet here, and no cable gland anywhere on this wall. Recess detail in §"AC inlet recess" below. |
| 2 | Water inlet | Rear | John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead union ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) — customer pushes the install-kit 1/4" LLDPE into this bulkhead, no tools | ø[18.0 mm](PANEL_HOLE_D) hole (identical SKU and hole to the 3 umbilical PP1208E ports) | **Customer-facing 1/4" JG QC**, on its own storey below the umbilical row's west end, its nut riding just above the rear seam-lip band. The install-kit Waterdrop 15UC-UF filter mounts customer-side, inline upstream of this bulkhead (`bom.md §3`). Inboard, the feed runs forward across the band above the cold core and down the foam-face slab: through the PP010822E 1/4" PTC × 1/4" NPT M → GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling → ASSE 1022's 3/8" MPT inlet, then the ASSE 1022's 3/8" MFL outlet → PI4512F6S + PP061208W → 1/4" LLDPE → water-split PP0208E tee → V-K → a clamped 3/8" stub onto the SeaFlo's molded suction barb. The internal ASSE 1022 chain sits *inside* the cabinet (downstream of the ASSE 1022's MFL outlet), not on this wall. Install kit ships **two** under-sink tee options + extra 1/4" LLDPE: a JG PP0208E 1/4" PTC × 1/4" PTC × 1/4" PTC union tee (black NSF-cert PP) for homes with 1/4" LLDPE already under the sink, and an HAOCHEN 3/8"×3/8"×1/4" angle-stop add-a-tee for homes with a 3/8" angle stop + braided compression supply. |
| 4 | CO2 inlet | Rear | neoFit ABU44 acetal black bulkhead connector, 1/4" tube ([FWS](https://www.freshwatersystems.com/products/neofit-acetal-black-bulkhead-connector-1-4-tube)) | Ø[17.86](CO2_HOLE_D) round, one column east of the carb union on the umbilical row's own storey | **On this wall** — the customer's red 1/4" LLDPE tether from the CGA-320 regulator on their own cylinder pushes into this collet, and the regulator end lands on that regulator's own 7/16"-20 male flare through a brass MI4508F4SLF. Acetal, rated for CO2 and inert gases where the black polypropylene range is not, and black like the four unions beside it. Red bulkhead ring under its flange. Inboard, a stub of tube reaches a PI010822S in the GASHER 1/4" NPT SS check's inlet with the arrow pointing away from the wall, then the WR1110 secondary regulator, then the cold core's `co2-in` cap conduit (`bom.md §4`, [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §1). |
| 5 | Backflow-vent observation | — | Moisture sensor in the ASSE drip pan under the Multiplex 19-0897's atmospheric vent | n/a for the vent — no hole in this wall; the pan withdraws through the −X side wall, not this one | The vent does not exit through this wall. It terminates inside the cabinet over the ASSE drip pan; the ESP32-monitored moisture sensor in the pan is the telltale. Detail: [`/hardware/future.md`](/hardware/future.md) §"Backflow vent monitoring". The pan itself draws WEST out of its sleeve, through a slot in the −X side wall (`enclosure_assembly.west_wall_ports`) — this wall carries no part of it. |
| 6 | Umbilical port | Rear | 3× John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead unions ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) | 3× ø[18.0 mm](PANEL_HOLE_D) holes (identical to the water-inlet station's; cut by [`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) from the pack's `back_ports`, which each union's own panel footprint strikes) | Mid-wall, in the band above the cold core the foam and the rear seam lip leave open. Accepts the 3-tube umbilical bundle that runs from the faucet under the counter down through the countertop to the rear of the appliance: 1× carbonated water + 2× flavor. User pushes each tube into its matching bulkhead — no tools. Same JG black-PP / NSF 51 + NSF 61 / 150 psi @ 70 °F bulkhead family already used inside the cold core, so the SKU is shared and the bulk 10-pack already in stock covers both uses. `bom.md §8`. |
| 7 | Umbilical signal | Rear | [RiteAV RJ11 6P4C black punchdown keystone jack](https://www.riteav.com/products/riteav-rj11-phone-black-punchdown-type-keystone-jack-10-pack) — customer pushes the umbilical's plug in until it clicks, no tools | [14.5](KEYSTONE_W) × [16](KEYSTONE_H) mm rectangular opening, R[0.6](KEYSTONE_R) corners (cut by [`../enclosure/enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) from the pack's `back_ports`, struck by `enclosure_assembly.keystone_cutout`) | **SIG-6**, the faucet display's TTL UART and its 5 V. On `deck_storey`, in the span between the CO2 pocket and the C14's cutout — [8.00 mm](KEYSTONE_WEST_CLEAR) of wall to the one and [8.00 mm](KEYSTONE_EAST_CLEAR) to the other, which `keystone-span` reads. That span is the wall's only free one: the gate lane's east end is the nameplate's, whose pocket runs x [-14.1, 90.4] over z [226.9, 292.9]. Standing here puts all five mating axes the customer meets on one line. The jack's moulded latch is the whole of its fastening — no nut, no insert, no screw, and the only station on this wall clamped by nothing. It reaches [26 mm](KEYSTONE_DEPTH) inboard, where the J3 loom is punched onto its 110 IDC terminals at [`wiring.md`](/hardware/assembly/wiring.md). Black through, including the dust cover it ships with. Latch band [1.5–3.2 mm](KEYSTONE_PANEL) against a 3 mm wall — `keystone-panel`. 6P4C takes SIG-6's four conductors and an RJ45 plug does not enter it. `bom.md §11`. |

## Umbilical port — tube identification

The 3-tube umbilical bundle leaves the faucet shell, runs through the countertop into the cabinet, sleeved in a braided cover with foam insulation on the cold (carbonated-water) line for thermal protection on the most temperature-critical run in the system. At this wall the user must connect each tube to the matching bulkhead — three identical-looking bulkheads in a black wall is a failure mode, so the carbonated-water tube and bulkhead are color-coded:

- **Carbonated water — blue.** Separate spool of 1/4" OD blue LLDPE ([`bom.md`](/hardware/ledger/bom.md) §3). The bulkhead receiving it on this wall is marked with a **blue accent ring** around its opening.
- **Flavor A / Flavor B — black.** Standard 1/4" OD black LLDPE from the existing FWS bulk spool (`bom.md §3` and elsewhere). Both flavor bulkheads wear a black chip lettered FLAVOR — black is the flavour colour, the colour of the tube that goes in. Neither tells A from B: that routing is handled by the manifold and is not user-visible at the face.

User rule at install: **blue tube into the blue-ringed bulkhead**. The four unions stand as a rectangle on two columns and two storeys, so the blue one is read by its ring rather than by its place in a line — it takes the [east](CARB_END) column of the upper storey, with the white-ringed tap-water union across from it and the two black-ringed flavor unions below. Black-into-either-black is unambiguous because both flavor tubes route through the same wall-side bundle and the user does not need to distinguish them at the face.

**And the tube carries the same word out.** A chip stays on the wall; a tube does not. The tap-water run ends at the customer's angle stop and the CO2 tether at their cylinder's regulator, and neither of those ends wears a ring. So each tube threads through a printed collar — [`../../faucet/tube-collar/`](../../faucet/tube-collar/README.md), this chip's outline bored for the tube and run along it, in the same colour and lettered in the same word. Five stations, five chips, five collars: the three on the umbilical go on at [`assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) §4 and the two on the customer's own cuts ride in the install kit.

The ring is a **separately printed chip inset into the wall** — [`../bulkhead-ring/`](../bulkhead-ring/README.md). The wall cuts one pocket per station, the chip's own thickness deep, with a boss of the same outline one rim larger standing that far inboard behind it, and the fitting's own nut draws flange, chip and wall together. Nothing else fastens it, and colour and wall come out one plane. Each chip carries its own word in a second colour, so a chip is a two-colour print; the piece running `enclosure-back-top` still needs one filament.

Net identification scheme on this wall: **blue = carbonated water** [#1f6feb](CARB_COLOR), **black = flavor lines** [#262629](FLAVOR_COLOR), **white = tap water** [#ffffff](WATER_COLOR) (the water bulkhead body itself is the white-marked station), **red = CO2** [#d63a3a](CO2_COLOR) (the CO2 bulkhead's own ring, east of the blue one on the same storey — station 4 above).

The scheme is the five tube crossings'. The signal station wears no ring: it is the one rectangle among them, it takes a plug and not a tube, and its own opening is the shape a customer reads it by.

**The scheme does not stop at the wall.** Every line inside the cabinet is cut off the spool of what it carries — [`_routing.SPOOLS`](/hardware/scripts/_routing.py), which reads `port_colors` above — so a tube outboard of a ring, the ring, and the tube inboard of it are one colour: white through the water station, blue through the carb union, red through the CO2 bulkhead, black through the two flavour unions. [`assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) names the spool at each cut, and the enclosure and cold-core assemblies draw every run in it.

Blue naming carbonated water is what makes the other two fall out: the umbilical riser is bought as blue tube ([`bom.md`](/hardware/ledger/bom.md) §3) and the union that receives it is bought to wear a blue ring (§8), so blue is spent, and the customer's teed-in tap-water station is the white-marked one. The four colors are the customer-wayfinding system committed in [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md) "Color system"; the quick start ([`/hardware/quickstart/`](/hardware/quickstart/README.md)) reads this same table into its stylesheet and the iso line-art paints its rings from it, so the customer's eye moves from sheet to face without translation. Any change to a ring here (color shade, ring mechanism, placement on the face) needs to round-trip through the unboxing brief because the printed sheet must match.

## Umbilical bundle construction

The 3-tube umbilical from the faucet down to this wall is bundled into a single sleeved run, in PET braid segments laid over the foam's own, per [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) §3.

**Foam insulation on the soda umbilical tube only.** The two flavor tubes carry ambient-temperature syrup at low duty cycle (a few mL per dispense) — warm-in, warm-out, no thermal benefit from insulation. The soda umbilical tube is the temperature-critical run: a multi-meter cold-line carrying chilled CO2-saturated water from the cold-core reservoir up to the faucet, where every degree of warm-up costs dissolved-CO2 retention. Insulating that one tube (and leaving the flavor tubes bare inside the sleeve) is the right thermal allocation.

- **Foam:** CARGEN nitrile rubber pipe insulation, 1/4" ID × 3/8" wall (`B0D2XFK337`, `bom.md §9`). Sized to slip over 1/4" OD LLDPE with a snug interference fit.
- **Foam ships as 1-ft segments.** Install procedure: slide five segments onto the soda umbilical tube and butt them together along the run, laying a braid segment over each as it seats.
- **Tube cutting:** the three LLDPE tubes are cut once each, to length, using the kit's Mudder PEX/PE tube cutter (`bom.md §14`), then pushed into the wall's PP1208E bulkheads.
- **Foam segment count and total length:** five 1-ft CARGEN segments, 1425 mm total, per [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) §1.

## AC inlet recess

The recess is the cutout itself, carried inboard. A printed tunnel stands round the hole on the wall's inner face (`enclosure._c14_tunnel`) and the receptacle is screwed to that tunnel's fore face, so the bore the C13 cord housing enters runs the whole depth of wall and tunnel together and nothing on this station stands proud of the wall. On insertion the housing nests [3–5 mm](AC_RECESS_DEPTH) down that bore, masking the gap between cord and inlet bezel. IEC 60320 specifies the male-blade insertion region only, not face-to-face mating distance.

## References

- [`/hardware/future.md`](/hardware/future.md) — broader enclosure context, backflow-vent monitoring, layout.
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §8 — PP1208E umbilical line (3 on this wall); with the §3 water inlet the SKU is 4/build.
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3 — water-inlet path (Waterdrop filter, Multiplex 19-0897 backflow, the PI4512F6S + PP061208W outlet stack, water-split PP0208E tee, PP1208E wall bulkhead, HAOCHEN install-kit tee).
- [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 and [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) — AC runs C14 inward.
- [`../nameplate/README.md`](/hardware/printed-parts/enclosure/nameplate/README.md) — the plate that fills the field east of the flavour chips, and the two screw bosses the wall stands for it.

## Bulkhead array arrangement

The 3× PP1208E umbilical-port bulkheads stand across the top of the field on one pitch (`enclosure_assembly.PANEL_X`). The order across it is the inboard runs': the two flavor gates take the west of the row, each on the side its run arrives from, and the carb union takes the [east](CARB_END) end with its DIGITEN meter lying inline ahead of it. The **blue-ringed (carbonated-water) bulkhead is the end one** — the user reads it by position in the row, not by a vertex.

The two flavor unions stand side by side at the [west](FLAVOR_B_END) end on a storey of their own, the lane their runs cruise in (`enclosure_assembly.PANEL_ON_GATE_LANE`), below the carb union's, under the tap-water bulkhead that takes its place on the row's own storey. The CO2 PTC stands one column east of the carb union on that same storey, and east of it again is the C14 cutout, at the end of the wall the power column stands against. Every station's Z is the pack's, and the wall takes its ceiling from the field's own top edge ([`enclosure.py`](/hardware/printed-parts/enclosure/enclosure/enclosure.py) `port_top`).

## Material

This wall is `enclosure-back-top`'s own, so it is that piece's material: **PETG** ($11.20/kg), the same as the rest of the enclosure ([`bom.md`](/hardware/ledger/bom.md) §7). Service temperature is above the ~30–40 °C cabinet ambient. There is no row of its own in §7 because there is no separate part.

## Open items

- **The CO2 station's ring** waits on its own bulkhead. `co2-inlet`'s ABU44 is on WEBFWS100697928; until it is placed, the field spans the four unions and stops west of that column.

The wall is not a moisture or vapor barrier — the appliance is not hermetic. Each bulkhead seals the pressurized fluid path *around the tube* via its internal O-ring; the wall interface is purely mechanical capture, flange + ring + nut sandwiching the wall through its Ø[18](PANEL_HOLE_D_SHORT) hole, so no wall-side bulkhead gasket is required.

## Status

Design-in-progress. The through-holes, the chips' pockets and the nameplate's pocket and bosses are all cut into the back-top enclosure piece by `enclosure.py`; the AC inlet's recess has no CAD yet. This README is the source-of-truth for this wall's connection inventory; `../nameplate/README.md` carries the plate standing beside them.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py`
