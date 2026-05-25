# Enclosure Mechanical Assembly

The production procedure for taking the integrated cold-core + refrigerant-loop assembly, the bench-built electronics shelf, and the printed enclosure shell to a complete mechanical chassis: cold core seated at the rear, compressor on the floor under its shroud, condenser + fan mounted on the chosen side wall on a straight-through side-to-side airflow path, back panel mounted with all bulkheads pre-installed, hopper installed, electronics shelf seated unpowered behind the C14 inlet. No internal plumbing runs, no AC/DC wiring runs — those are downstream in [`internal-plumbing.md`](internal-plumbing.md) and [`wiring.md`](wiring.md). The output is the mechanical canvas everything else lands on.

Design intent and enclosure layout rationale live in [`../future.md`](../future.md) "Enclosure layout", "Compressor compartment shroud", "User-facing elements by location", "Rear-panel AC inlet", and "Rear-panel nameplate". Part-level READMEs are the source of truth for every component this procedure handles; this document is the build-cadence wrapper.

## Scope

In: the integrated refrigerant-loop assembly (output of [`refrigerant-loop.md`](refrigerant-loop.md) — cold core with wound coil + plumbed compressor + condenser/fan, charged and run-up-verified); the printed enclosure shell + back panel + top hopper feature + nameplate plaque blank (printing per [`../printed-parts/enclosure/`](../printed-parts/enclosure/)); the compressor shroud ([`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md)); all back-panel bulkheads (C14 inlet, water-inlet bulkhead, BiB adapter, the three umbilical PP1208E bulkheads with the blue accent ring on the carbonated-water bulkhead) per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md), plus the front-panel CO2-inlet bulkhead (DERPIPE 5/16"-tube PTC × 1/4" NPT — see [`../future.md`](../future.md) §"Enclosure layout"); the internal drip pan + moisture sensor for the backflow vent; the bench-built unpowered electronics shelf (output of [`electronics-shelf.md`](electronics-shelf.md)).

Out: a complete mechanical chassis — cold core seated at the rear on its support ring, compressor bolted to the enclosure floor with the sheet-metal shroud installed over the terminal block + PTC relay/overload module, condenser + fan mounted on the chosen side wall with intake grille on one side face and exhaust grille on the opposite side face (straight-through, no redirection), back panel mounted with all bulkheads installed (no internal plumbing runs yet, no AC/DC wiring runs yet), hopper installed at the top-front, electronics shelf mechanically seated at the top-back behind the C14 inlet (unpowered). Ready for [`internal-plumbing.md`](internal-plumbing.md) and [`wiring.md`](wiring.md).

Not in scope: internal plumbing runs through the cabinet (warm-side check valves, regulator, pump-to-manifold lines, BiB tee, water-inlet path) — see [`internal-plumbing.md`](internal-plumbing.md); AC + DC + signal wiring runs between the shelf, the compressor, the fan, the manifold, the moisture sensor, and the umbilical — see [`wiring.md`](wiring.md); installing the wound coil onto the vessel (already done in [`cold-core.md`](cold-core.md) step 1); refrigerant-loop integration (already done in [`refrigerant-loop.md`](refrigerant-loop.md)); nameplate plaque serialization, signing, and final application — that happens at [`finish-pack-ship.md`](finish-pack-ship.md), not here.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §7 (printed enclosure parts), §8 (back-panel bulkheads — PP1208E ×3, DERPIPE CO2 PTC, FFL38BARB38 water inlet, BiB connector), §11 (C14 inlet + chassis hardware), §13 (mechanical attach hardware), and the compressor-shroud line in §5 (refrigeration). Status (ACQUIRED / ON-ORDER) lives in [`../purchases.md`](../purchases.md) §6 + §11. The table below is the procedure-level summary.

| Item | Source / spec | Notes |
|---|---|---|
| Integrated refrigerant-loop assembly | Output of [`refrigerant-loop.md`](refrigerant-loop.md) | Cold core + plumbed compressor + condenser/fan, charged, run-up-verified, leak-checked |
| Enclosure shell + back panel + top hopper feature | [`../printed-parts/enclosure/`](../printed-parts/enclosure/) | Bambu PET-CF per back-panel README "Panel material"; printed in the configuration captured at order time |
| Nameplate plaque (blank) | [`../printed-parts/enclosure/nameplate/`](../printed-parts/enclosure/nameplate/) | Pre-printed blank; serialized + signed + applied at [`finish-pack-ship.md`](finish-pack-ship.md), not here |
| Compressor shroud | [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) | SendCutSend [0.059"](WALL_IN) G90 galvanized steel, 5-sided open-bottom box (or U-channel + back wall pending the open item) |
| C14 panel-mount inlet | MXR B07DCXKNXQ ([`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) §1) | Recessed [3–5 mm](AC_RECESS_DEPTH) into panel face with the printed shroud |
| Water-inlet bulkhead | brewhardware FFL38BARB38 ([back-panel §2](../printed-parts/enclosure/back-panel/README.md)) | 3/8" FFL swivel × 3/8" SS hose barb |
| CO2-inlet bulkhead | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect ([front-panel §1](../printed-parts/enclosure/front-panel/README.md)) | Red accent ring at panel opening; mounts on the front panel, not the back panel |
| BiB adapter | Supply Depot B0DMFK9B6P ([back-panel §4](../printed-parts/enclosure/back-panel/README.md)) | 3/8" red BiB connector, single panel-side connector feeding both flavors downstream |
| Umbilical PP1208E bulkheads × 3 | John Guest B00JYFU8MM ([back-panel §6](../printed-parts/enclosure/back-panel/README.md)) | Triangular cluster; blue accent ring on the carbonated-water bulkhead at the top vertex |
| Drip pan + moisture sensor | TBD — see Open items | Backflow-vent observation per [`../future.md`](../future.md) "Backflow vent monitoring"; sensor wires to SIG-9 in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md), terminated at the shelf during [`wiring.md`](wiring.md) |
| Heyco SB-500-6 snap bushing | B01LPBST9G ([compressor-shroud §Penetrations](../cut-parts/compressor-shroud/README.md)) | AC pass-through grommet in the shroud sidewall |
| Bench-built electronics shelf | Output of [`electronics-shelf.md`](electronics-shelf.md) | Unpowered; AC pigtails hang free, terminated at the C14 inlet in [`wiring.md`](wiring.md) |
| ruthex M3 heat-set inserts + M3 fasteners | ruthex B0D39W228K + BNUOK B0DJQGF665 / B0DJQGVK8S | Per the enclosure-shell screw schedule (TBD until enclosure CAD lands — see Open items) |
| Chassis bonding lead — compressor shroud | Green 18 AWG, ring terminal × M3 stud | Bonded to the PEM stud on the shroud per [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) Penetrations §3; landed at the ground bus in [`wiring.md`](wiring.md) |

Tooling: standard hand tools — Phillips + hex (2.5 mm for M3), soldering iron + ruthex insert tip for any inserts not pre-installed at the printed-part stage, torque-limiting screwdriver for the shroud-to-compressor M5→M3 step-down anchors (don't crush the compressor's M5 grommet feet), a level, and the build-fixture cradle that holds the chassis upright while the cold core is seated (printed bench fixture, not yet specified — see Open items).

## Procedure

The chassis is built from the floor up: enclosure shell on the bench, drip pan in, compressor on the floor under its shroud, condenser/fan against the chosen side wall, cold core dropped in at the rear, hopper at the top-front, back panel (bulkheads pre-installed) mounted last, electronics shelf seated behind the C14 inlet. The cold core drops in as a single pre-assembled unit — it is not built up in place. See [`refrigerant-loop.md`](refrigerant-loop.md) "Output condition" for the state the cold core arrives in.

### 1. Stage the enclosure shell + back panel on the bench

Print-inspect the enclosure shell, back panel, top hopper feature, and nameplate blank. Wipe down the interior; remove brim residue and any stray support material at the bulkhead bores, the grille slats, the compressor-mounting bosses on the floor, and the cold-core support-ring landing at the rear. Set the nameplate plaque aside in the unit's build folder — it does not get applied at this step (see [`finish-pack-ship.md`](finish-pack-ship.md)). The pre-printed blank attachment points on the rear panel are confirmed clean and unobstructed.

Install ruthex M3 heat-set inserts wherever the enclosure-shell screw schedule calls for them (insert positions are defined per the enclosure CAD — see Open items). Standard heat-set procedure: soldering iron on the insert, press straight down until flush. All inserts go in *before* anything else is in the cabinet, while there is bench access from every face.

Pre-install all bulkheads on the back panel on the bench, ahead of mounting it to the shell. This is the easier work surface, and pre-installation lets the bulkhead torque load react against a panel that is unconstrained from inside-the-cabinet interference:

- **C14 inlet** seats into the rectangular cutout from the outside face, retained by its panel-mount screws per the MXR spec, drawn flush against the printed shroud's recess so the C13 cord housing will nest into the [3–5 mm](AC_RECESS_DEPTH) recess on insertion. Inlet solder-tab pins face into the cabinet.
- **Water-inlet bulkhead** (FFL38BARB38): swivel-nut side outside (customer's 3/8" line lands here), barb side inside.
- **CO2-inlet bulkhead** — *not* pre-installed on the back panel; lives on the front panel per [`../printed-parts/enclosure/front-panel/README.md`](../printed-parts/enclosure/front-panel/README.md). Front-panel pre-install step is a separate procedure (not yet broken out in this doc).
- **BiB adapter** (Supply Depot 3/8" red): connector side outside, downstream barb inside.
- **Umbilical PP1208E bulkheads × 3** in the triangular cluster: the blue-accent-ring bulkhead at the top vertex (carbonated water), the other two at the bottom corners (flavor A + flavor B). All three retained against the panel via their flange + nut sandwich on the EPDM O-ring per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Open items" — mechanical capture only, no panel-side gasket.

Set the populated back panel aside; it mounts in step 7.

### 2. Install the internal drip pan + moisture sensor

Seat the printed drip pan in its location under where the Multiplex 19-0897's atmospheric vent will terminate (the pan + vent location are inside the cabinet, not routed through any panel; see [`../future.md`](../future.md) "Backflow vent monitoring"). Place the moisture sensor in the pan with its leads routed up toward the electronics-shelf landing point. Leave the leads loose for now — termination at the shelf happens in [`wiring.md`](wiring.md) (run SIG-9 in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md)).

Pan + sensor go in early because they sit underneath the compressor + plumbing zone; installing them after the compressor lands forces access from above through the wiring loom.

### 3. Mount the compressor to the floor with the shroud pre-installed

The compressor body comes in as part of the integrated refrigerant-loop assembly with all refrigerant lines already brazed to it; the cold core's coil stubs are connected to the suction line and capillary tube as documented in [`refrigerant-loop.md`](refrigerant-loop.md). The compressor is not separated from this assembly at any point in this procedure.

**Install the compressor shroud over the terminal block + PTC relay/overload module BEFORE bolting the compressor to the enclosure floor.** Bench access to the terminal block is much easier with the compressor still on the build cart; once the compressor is bolted to the floor it sits in the middle-bottom of the enclosure with the cold core landing right next to it, and the shroud's M3 mounting tabs at the M5 compressor feet become significantly harder to fasten. Sequence:

1. Set the compressor on its side or upright on a clean bench, the cold-core assembly steady on its cart with no tension on the refrigerant lines.
2. Route the Heyco SB-500-6 snap bushing into the shroud's [1/2"](PANEL_HOLE) sidewall hole (the side that will face toward the electronics shelf at top-back — best path for the future AC pigtail run to Teyleten relay #1).
3. Lower the shroud down over the terminal block + PTC module. Confirm ≥[10 mm](TB_CLEARANCE) clearance on all sides of the terminal block per [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) "Dimensions".
4. Anchor the shroud's M3 mounting tabs to the compressor's M5 mounting feet via the step-down adapter washers per [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) Penetrations §2. Torque-limited.

With the shroud locked to the compressor, lift the compressor + shroud as a single unit and bolt it to the enclosure floor at the middle-bottom compressor-mounting bosses. The condenser + fan + condenser-side tubing comes along on the same lift (still attached as part of the integrated refrigerant-loop assembly). Mind the condenser orientation — its airflow axis lands in step 4.

### 4. Mount the condenser + fan against the chosen side wall

Position the condenser + fan against the chosen side wall, fan axis crossing the enclosure side-to-side, intake side facing the intake grille and exhaust side facing the exhaust grille on the opposite face. The donor's harvested fan shroud carries the mounting screws into the printed enclosure side wall's condenser bosses (insert pattern defined per the enclosure CAD).

Which side wall (left or right) holds the intake vs. exhaust is not yet locked — see Open items. Working assumption: the side opposite the cabinet door swing per the kitchen install convention, so the condenser exhaust is on the cabinet-rear side and intake on the cabinet-front side (the user opens the door to less-warm air). Either assignment is mechanically equivalent — the fan + condenser are symmetric in the enclosure cavity — but it locks the grille faces of the printed shell at order time.

Confirm: the fan's flow direction matches the donor's native orientation per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md). The fan was already validated in this configuration in the donor ice maker; the only new variable is its anchor surface.

### 5. Seat the cold core at the rear

With the compressor + condenser + fan now anchored, lower the cold core into the rear of the enclosure as a single pre-assembled unit. The cold core lands on the printed support ring at the back of the enclosure floor — the ring captures the foam-shell's outer bottom-cap footprint ([283](FOAM_SHELL_X) × [181 mm](FOAM_SHELL_Z) per [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "outer_shell" + "foam_cap and foam_cap_lid").

The coil stubs are already brazed into the donor loop (suction line + cap-tube join) per [`refrigerant-loop.md`](refrigerant-loop.md) step 4–5 — no brazing work happens here. Confirm no tension is induced on the refrigerant lines as the cold core seats; the compressor + condenser were placed first specifically so the cold core can land on the support ring without dragging the brazed joints. Re-check the BPV31 cap is tight (the appliance's single permanent service-access point per [`refrigerant-loop.md`](refrigerant-loop.md) "Output condition").

Cold-core penetrations on the +Z outer wall (the wall facing forward toward the front of the cabinet, by the cold-core coordinate convention in [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md)) — the shared copper/water-inlet slot, the reservoir-line holes, the water-outlet hole, the reed-cable holes — face into the cabinet interior where [`internal-plumbing.md`](internal-plumbing.md) and [`wiring.md`](wiring.md) will reach them.

### 6. Install the top hopper

Install the flavor hopper at the top-front of the enclosure per [`../future.md`](../future.md) "User-facing elements by location". The hopper is sized to accept a SodaStream concentrate bottle pour without splash and routes downward through solenoid-selected valves to the two flavor reservoirs in the cold core. Whether the hopper is integral to the printed top face or attaches as a separate part is an open item — see Open items.

If the hopper is a separate part, it lands here against its M3-into-ruthex screw pattern on the enclosure top face. If it is integral to the printed top face, this step collapses into the top-face install (which itself may be deferred to after step 7 to keep wiring access — sequencing locked when the open item resolves). Either way, the silicone hopper cover ([`../future.md`](../future.md) "Flavor subsystem") is a user-removable accessory and is not installed at this step; it ships in the accessory bag.

Internal hopper-to-reservoir routing (the hopper outlet hose + tee + solenoid valves) is plumbing work that lives in [`internal-plumbing.md`](internal-plumbing.md), not here. At this step the hopper is mechanically in place and its outlet stub hangs free, accessible from inside the cabinet.

### 7. Mount the populated back panel

Lift the populated back panel (all bulkheads pre-installed per step 1) and seat it against the rear of the enclosure shell. Fasten with the screw pattern specified in the enclosure CAD (TBD — see Open items). With the panel in, confirm the umbilical PP1208E cluster is oriented with the blue-ringed bulkhead at the top vertex of the triangle — orientation matters here because the user-facing rule at install is "blue tube into the blue-ringed bulkhead" per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification", and that rule only works if the blue ring sits where the user expects it (visually dominant top of the triangle).

The panel has no fluid-pressure duty per the back-panel README — the bulkhead O-rings seal the pressurized fluid path around each tube. The panel-to-shell interface is mechanical capture only; no panel-side gasket is required.

The four cabinet-side bulkhead stubs (water inlet barb, CO2 NPT, BiB downstream barb, three umbilical PTC interiors) are now all visible from inside the cabinet. They get plumbed in [`internal-plumbing.md`](internal-plumbing.md). The C14 inlet's solder-tab pins are similarly exposed inside; they get terminated to the electronics shelf's AC pigtails in [`wiring.md`](wiring.md). The compressor shroud's [1/2"](PANEL_HOLE) Heyco-bushed sidewall hole now faces the electronics-shelf landing zone, ready to accept the shelf-side AC run in [`wiring.md`](wiring.md). Confirm: no plumbing or wiring has been routed through any bulkhead or shroud penetration at this point.

### 8. Seat the electronics shelf at the top-back (unpowered)

Mechanically seat the bench-built electronics shelf at the top-back of the enclosure, directly behind the rear panel and the C14 inlet, per [`../future.md`](../future.md) "Enclosure layout". The shelf carries all of: C14 inlet pigtail, AC distribution block, Mean Well IRM-90-12ST PSU, both Teyleten relays, ESP32-DevKitC-32E, MCP23017 GPIO expander, two ULN2803A driver modules, the L298N peristaltic-pump driver, and the 5 V + 3.3 V regulators ([`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) header).

The shelf is **unpowered** at this step. The AC pigtails from the shelf hang free — they get terminated at the C14 inlet's solder-tab pins in [`wiring.md`](wiring.md), not now. Similarly DC and signal runs to the manifold, fan, moisture sensor, reed columns, and faucet umbilical land in [`wiring.md`](wiring.md). The chassis bonding lead from the compressor shroud's PEM ground stud routes toward the shelf's ground bus and waits to be terminated.

Confirm the shelf clears the back-panel bulkheads behind it (the C14 inlet pigtail wants ~50 mm of pigtail length per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) run AC-1) and the cold core directly below it. No wiring runs are made at this step.

## Output condition

A complete mechanical chassis ready for [`internal-plumbing.md`](internal-plumbing.md) and [`wiring.md`](wiring.md):

- Cold core seated at the rear on its support ring, no tension on the refrigerant lines
- Compressor bolted to the enclosure floor, sheet-metal shroud installed and anchored to the M5 compressor feet, Heyco-bushed [1/2"](PANEL_HOLE) AC pass-through facing the electronics shelf
- Condenser + fan mounted on the chosen side wall, airflow axis crossing the enclosure side-to-side, intake grille on one side face and exhaust grille on the opposite side face
- Back panel mounted with all back-panel bulkheads pre-installed: C14 inlet (recessed with printed shroud), FFL38BARB38 water inlet, Supply Depot BiB connector, three PP1208E umbilical bulkheads in triangular cluster (blue ring at top vertex). CO2 inlet lives on the front panel — see [`../printed-parts/enclosure/front-panel/README.md`](../printed-parts/enclosure/front-panel/README.md); separate install step (not yet broken out in this doc).
- Drip pan + moisture sensor installed under the backflow-vent termination point, sensor leads routed toward the electronics shelf (not yet terminated)
- Hopper installed at the top-front, outlet stub hanging free
- Electronics shelf mechanically seated at the top-back behind the C14 inlet, unpowered, AC pigtails hanging free
- Nameplate plaque blank set aside in the unit's build folder, **not** applied (serialization, signature, and application happen at [`finish-pack-ship.md`](finish-pack-ship.md))
- Chassis bonding lead from the compressor shroud's PEM stud routed toward the shelf's ground bus, not yet terminated
- No internal plumbing runs, no AC/DC/signal wiring runs

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Enclosure shell + back-panel screw schedule.** The fastener type/size and ruthex insert positions for panel-to-shell mating, hopper-to-shell mating (if separable), and condenser-fan-shroud-to-side-wall mating are pending enclosure CAD. Working assumption is M3 SHCS into ruthex inserts (matching the pattern already used on cold-core caps and faucet shells per [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Cap-to-outer-shell joinery"), but counts, positions, and exact lengths are not committed.
2. **Condenser-fan side-wall assignment (left vs. right).** [`../future.md`](../future.md) "Enclosure layout" specifies side-to-side airflow with intake on one face and exhaust on the opposite face, but does not lock which side. Working assumption is the side opposite the cabinet-door swing per kitchen install convention; this is unverified and should be confirmed against typical 36"-base-cabinet door-swing geometry in target kitchens, then locked into the printed shell at order time.
3. **Hopper attach mode.** Whether the flavor hopper attaches via the top of the enclosure as a separate printed part, or is integral to the printed top face of the enclosure shell. The BOM lists the hopper as a separate 0.4 kg PET-CF print ([`../bom.md`](../bom.md) §7) but the top face's print orientation may make a single integrated print preferable — pending the enclosure-shell CAD decision.
4. **Drip pan + moisture sensor part selection.** Neither part is in [`../bom.md`](../bom.md) yet. The pan is presumed to be a small printed PET-CF tray sized for the Multiplex vent terminal location; the moisture sensor is presumed to be a generic ESP32-compatible resistive or capacitive board. Specifics need to land before [`wiring.md`](wiring.md) can finalize the SIG-9 pin assignment and cable length.
5. **Build-fixture cradle.** A printed bench fixture that holds the enclosure shell upright (or tilted) during compressor mounting, cold-core lowering, and back-panel installation. Not yet specified; depends on the shell's external dimensions and on whether the build proceeds on its side or upright.
6. **Cold-core support-ring detail at the enclosure floor.** Whether this is an integral feature of the enclosure-shell floor print, a separate printed ring that drops in, or a set of cleats — pending enclosure-shell CAD.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_enclosure_mechanical_sync.py`
