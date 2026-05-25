# Rear panel

3D-printed rear face of the under-counter enclosure. Carries every external connection on the appliance except the CO2 inlet (which lives on the front panel — see [`../../../future.md`](../../../future.md) §"Enclosure layout"): AC inlet, tap-water inlet, bag-in-box (BiB) syrup inlet, the moisture-sensor drip-pan vent that observes the §3 backflow preventer, and (new) the umbilical port that accepts the three tubes coming down from the under-cabinet faucet through the countertop. Printed in **Bambu PET-CF**, matching the rest of the enclosure exterior — see §"Panel material" below.

The panel itself has no fluid-pressure duty. It is a connection-management plate: hole patterns sized for off-the-shelf bulkheads and panel-mount receptacles, with printed bezels, recesses, and labels where the user-facing fit-and-feel benefits.

## Connections inventory

| # | Connection | Hardware | Panel hole | Notes |
|---|---|---|---|---|
| 1 | AC inlet | IEC 60320 C14 panel-mount receptacle ([MXR B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ)) | rectangular cutout per C14 spec | Recessed [3–5 mm](AC_RECESS_DEPTH) into the panel face with a printed shroud around the perimeter so the C13 cord housing nests flush. Cord housing is the strain relief — no separate grommet on this panel. (The Heyco SB-500-6 in `bom.md §11` is the cord grommet on the compressor shroud, a different sheet-metal part.) Recess detail in §"AC inlet recess" below. |
| 2 | Water inlet | John Guest PI1208S 1/4" QC × 1/4" QC acetal bulkhead union ([B0C1F3QR7N](https://www.amazon.com/dp/B0C1F3QR7N)) — customer pushes the install-kit 1/4" LLDPE into this bulkhead, no tools | ø[17.0 mm](PANEL_HOLE_D) panel hole (matches the umbilical PP1208E hole profile already used on this panel) | **Customer-facing 1/4" JG QC.** Downstream-from-the-customer inside the cabinet the line runs through the Waterdrop 15UC-UF filter (placement internal-vs-external TBD per `bom.md §3` header) → PP010822E 1/4" PTC × 1/4" NPT M → GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling (food-service gold standard, matches the TAISHER 316L SS vessel-port elbows and the 316L pressure-vessel walls themselves) → ASSE 1022's 3/8" MPT inlet, then the ASSE 1022's 3/8" MFL outlet → FFL38BARB38 → JoyTube silicone → SeaFlo. The brewhardware FFL38BARB38 sits *inside* the cabinet (downstream of the ASSE 1022's MFL outlet), not on this panel — earlier drafts of this row had it as the panel-mounted fitting, which is wrong: FFL only mates with MFL, so it can't take the customer's supply directly. Install kit ships **two** under-sink tee options + extra 1/4" LLDPE so the customer doesn't need to source any plumbing: a JG PP0208E 1/4" PTC × 1/4" PTC × 1/4" PTC union tee (black NSF-cert PP) for modern homes with 1/4" LLDPE already under the sink (most newer-construction kitchens and any kitchen with a PEX manifold + ice-maker / RO stub-out), and an HAOCHEN 3/8"×3/8"×1/4" angle-stop add-a-tee for older homes with a 3/8" angle stop + braided compression supply. |
| 4 | BiB syrup adapter | Supply Depot 3/8" red BiB connector ([B0DMFK9B6P](https://www.amazon.com/dp/B0DMFK9B6P)) — one connector on the panel feeding both flavors via the §8 PP010822E + PP2308E Y-divider tree downstream | TBD (follows Supply Depot connector spec) | Secondary input path for users who source commercial syrup. The primary path is the top-face hopper — see `../../../future.md` §"Flavor subsystem". `bom.md §8`. |
| 5 | Backflow-vent observation | Moisture sensor in the internal drip pan under the Multiplex 19-0897's atmospheric vent | n/a — drip pan + sensor mount inboard of the panel, no panel hole | The vent does not exit through the rear panel. It terminates inside the cabinet over a printed drip pan; the ESP32-monitored moisture sensor in the pan is the telltale. Detail: `../../../future.md` §"Backflow vent monitoring". |
| 6 | Umbilical port (NEW) | 3× John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead unions ([B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM)) | 3× ø[17.0 mm](PANEL_HOLE_D) panel holes (same hole the §8 reservoir-cap PP1208E uses; see `printed-parts/cold-core/reservoir/generate_step_cadquery.py` lines 251–310 for the pocket / panel-hole geometry that ports here) | Accepts the 3-tube umbilical bundle that runs from the under-cabinet Westbrass faucet down through the countertop to the rear of the appliance: 1× carbonated water + 2× flavor. User pushes each tube into its matching bulkhead — no tools. Same JG black-PP / NSF 51 + NSF 61 / 150 psi @ 70 °F bulkhead family already used inside the cold core, so the SKU is shared and the bulk 10-pack already in stock covers both uses. `bom.md §8`. |

## Umbilical port — tube identification

The 3-tube umbilical bundle leaves the faucet body, runs through the countertop into the cabinet, sleeved in a braided cover with foam insulation on the cold (carbonated-water) line for thermal protection on the most temperature-critical run in the system. At the rear panel the user must connect each tube to the matching bulkhead — three identical-looking bulkheads in a black panel is a failure mode, so the carbonated-water tube and bulkhead are color-coded:

- **Carbonated water — blue.** Separate small spool of 1/4" OD blue LLDPE (sourcing in flight; not yet in `bom.md`). The bulkhead receiving it on the rear panel is marked with a **blue accent ring** around its opening.
- **Flavor A / Flavor B — black.** Standard 1/4" OD black LLDPE from the existing FWS bulk spool (`bom.md §3` and elsewhere). The two flavor bulkheads have no accent ring — flavor A vs flavor B routing is handled by the manifold and is not user-visible at the panel.

User rule at install: **blue tube into the blue-ringed bulkhead**. Black-into-either-black is unambiguous from there because both flavor tubes route through the same panel-side bundle and the user does not need to distinguish them at the panel.

Mechanism for the blue ring is TBD — candidates include multi-material printing of the panel itself, a separately printed TPU collar that snaps over the bulkhead's exterior flange, or a paint touch on the printed bezel surrounding the bulkhead. The selection is downstream of the panel-material decision and the multi-material capability of the printer running the panel.

Net identification scheme on the rear panel: **blue = carbonated water**, **black / plain = flavor lines**. (The CO2 inlet lives on the front panel — see [`../front-panel/README.md`](../front-panel/README.md); red color-coding for CO2 lines is documented there.)

Blue on this panel is part of the three-color customer-wayfinding system committed in [`../../../../marketing/unboxing-and-quickstart.md`](../../../../marketing/unboxing-and-quickstart.md) "Color system" — **blue = carbonated water, red = CO2, white = tap water**. The same blue appears on the matching line drawing in the printed quick-start sheet, so the customer's eye moves from sheet to panel without translation. Any change to the blue ring here (color shade, ring mechanism, placement on the panel) needs to round-trip through the unboxing brief because the printed sheet must match.

## Umbilical bundle construction

The 3-tube umbilical from the faucet down to the rear panel is bundled into a single sleeved run. Sleeve material — braided polyester sleeve vs. spiral wrap — is TBD pending fit-up against the countertop pass-through.

**Foam insulation on the carbonated-water tube only.** The two flavor tubes carry ambient-temperature syrup at low duty cycle (a few mL per dispense) — warm-in, warm-out, no thermal benefit from insulation. The carbonated-water tube is the temperature-critical run: a multi-meter cold-line carrying chilled CO2-saturated water from the cold-core reservoir up to the faucet, where every degree of warm-up costs dissolved-CO2 retention. Insulating that one tube (and leaving the flavor tubes bare inside the sleeve) is the right thermal allocation.

- **Foam:** CARGEN nitrile rubber pipe insulation, 1/4" ID × 3/8" wall (`B0D2XFK337`, `bom.md §9`). Sized to slip over 1/4" OD LLDPE with a snug interference fit.
- **Foam ships as 1-ft segments, not as a continuous tube.** Install procedure for the end-builder: slide segments onto the carbonated-water tube, discard the segments that don't fit the cabinet-routing length, butt the remaining segments together along the run. **No foam cutting in the field.** The 1-ft segment granularity is the install ergonomics: the user matches cabinet length by removing whole segments, not by measuring and cutting.
- **Tube cutting:** the three LLDPE tubes themselves are cut once each, to length, using the kit's Mudder PEX/PE tube cutter (`bom.md §14`), then pushed into the rear-panel PP1208E bulkheads. One cut per tube, no foam cuts.
- **Thermal cost of segmented vs. continuous foam:** ~1–3% additional heat ingress at the segment butts, assuming tight butting under the sleeve compression. Negligible against the install-ergonomics win of zero in-field foam work. The braided sleeve over the bundle also helps hold segments butted.
- **Foam segment count and total length:** TBD pending the cabinet-routing-length spec (depends on countertop thickness, faucet drop, and rear-panel position within the cabinet).

## AC inlet recess

The C14 receptacle is recessed [3–5 mm](AC_RECESS_DEPTH) into the panel face with a printed shroud around the inlet perimeter. On insertion, the C13 cord housing nests into the recess and ends flush with the panel surface, visually masking the gap between cord and inlet bezel. The gap is intentional under IEC 60320, which specifies the male-blade insertion region only, not face-to-face mating distance.

## References

- `../../../future.md` — broader enclosure context, original AC-inlet recess rationale, backflow-vent monitoring, layout.
- `../../../bom.md §8` — PP1208E line (qty 5/build: 2 reservoir + 3 rear-panel).
- `../../../bom.md §3` — water-inlet path (Waterdrop filter, Multiplex 19-0897 backflow, FFL38BARB38, JoyTube, PI1208S panel bulkhead, HAOCHEN install-kit tee).
- `../../../bom.md §11` and `../../../wiring/ac-wiring-schedule.md` — AC runs C14 inward.
- `../nameplate/README.md` — sister rear-face artifact (separately printed plaque).

## Bulkhead array arrangement

The 3× PP1208E umbilical-port bulkheads are arranged in a **triangular cluster** on the rear panel — three circles tangent in the densest packing. Three 1/4" OD tubes naturally pack the same way inside the umbilical bundle (densest-three-circle triangle), so the panel-side hole pattern mirrors the bundle-side tube pattern: the user presents the bundle to the panel and each tube already sits in front of its matching bulkhead with no re-threading. An in-line row (vertical or horizontal) would require the same number of push-clicks but force a mental re-arrangement step — the user would have to peel the three tubes out of their natural triangular bundle and fan them into a line. Same physical work, more cognitive friction. The triangle also keeps the cluster compact, leaving more panel real estate around the cluster for fingertip clearance on the PTC collet release. The blue-ringed (carbonated-water) bulkhead sits at the top vertex of the triangle so it remains the visually dominant one regardless of panel orientation.

## Panel material

The rear panel — and the rest of the enclosure exterior — is printed in **Bambu PET-CF**. The decision is enclosure-wide, not panel-specific: one material across every visible exterior surface for aesthetic coherence and one-fewer-material to juggle in the print queue.

- **Surface and dimensional quality.** PET-CF prints with no visible layer lines, a consistent matte surface finish, and dimensional stability across cabinet temperature swings. Validated empirically on prior touch-flo faucet parts in `hardware/printed-parts/touch-flo-faucet/` — the surface comes off the bed publication-grade with no post-processing.
- **Heat resistance.** Service temperature well above the ~30–40 °C cabinet ambient (compressor + electronics waste heat). Not a thermal bottleneck.
- **Stiffness and bulkhead capture.** Carbon-fiber reinforcement gives the panel the stiffness needed for threaded inserts and bulkhead clamp loads (3× PP1208E push-to-connect bulkheads on this panel alone) without creep under sustained nut torque.
- **Cost.** $85/kg vs ~$30/kg for PETG-CF or ASA-CF — the premium. Enclosure mass is ~1–2 kg total per build, so the material delta is ~$60–100/build vs. mixing PETG-CF on hidden faces. Manageable at Founder Edition volumes; the aesthetic uniformity win is worth $15–25/build at minimum.
- **Supply.** Bambu PET-CF is more reliably in-stock at Bambu than PETG-CF, which cycles out of stock frequently. Lower stocking risk for production runs.
- **Workflow fit.** Integrates cleanly with the project's existing Bambu workflow: AMS spool compatibility, refill-spool format, tuned print profiles already proven on prior parts.

This closes the prior "PETG vs PETG-CF" TBD on this panel and on the enclosure exterior at large.

## Open items

- **Blue ring identification mechanism**: multi-material print on the panel itself, snap-on TPU collar, or paint touch on a printed bezel. With PET-CF committed, multi-material on the panel itself requires a second compatible filament loaded in the AMS; snap-on TPU is the lowest-risk fallback.
- **Panel mounting** to the enclosure shell: screw pattern, heat-set insert plan, gasket-or-no-gasket. To be decided alongside the enclosure-wall design. (Note: the panel is not a moisture or vapor barrier — the appliance is not hermetic. The PP1208E bulkheads seal the pressurized fluid path *around the tube* via their internal EPDM O-rings; the panel interface is purely mechanical capture, flange + nut sandwiching the panel through its Ø[17](PANEL_HOLE_D_SHORT) hole, so no panel-side bulkhead gasket is required.)

## Status

Design-in-progress. No CAD generator yet. This README is the source-of-truth for the panel's connection inventory until the geometry reaches `generate_step_cadquery.py`; see `../nameplate/README.md` for the equivalent state on the sister rear-face artifact.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py`
