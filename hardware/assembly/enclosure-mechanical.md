# Enclosure Mechanical Assembly

The production procedure for taking the integrated cold-core + refrigerant-loop assembly, the bench-built electronics shelf, and the printed enclosure shell to a complete mechanical chassis: cold core seated at the rear, compressor on the floor under its shroud, condenser + fan mounted on the chosen side wall on a straight-through side-to-side airflow path, back panel mounted with all bulkheads pre-installed, hopper installed, electronics seated unpowered on the foam-cap top (power tray, PCBA tray, and DC distribution lying flat in the band above the cold core). No internal plumbing runs, no AC/DC wiring runs — those are downstream in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md). The output is the mechanical canvas everything else lands on.

Design intent and enclosure layout rationale live in [`/hardware/future.md`](/hardware/future.md) "Enclosure layout", "Compressor compartment shroud", "User-facing elements by location", "Rear-panel AC inlet", and "Rear-panel nameplate". Part-level READMEs are the source of truth for every component this procedure handles; this document is the build-cadence wrapper.

## Scope

In: the integrated refrigerant-loop assembly (output of [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) — cold core with wound coil + plumbed compressor + condenser/fan, charged and run-up-verified); the printed enclosure shell + back panel + top hopper feature + nameplate plaque blank (printing per [`/hardware/printed-parts/enclosure/`](/hardware/printed-parts/enclosure/)); the compressor shroud ([`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md)); all panel bulkheads (the three umbilical PP1208E bulkheads with the blue accent ring on the carbonated-water bulkhead, the water-inlet PP1208E, and the C14 inlet, all on the back panel) per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md), plus the front-panel CO2-inlet bulkhead (DERPIPE 5/16"-tube PTC × 1/4" NPT — see [`/hardware/future.md`](/hardware/future.md) §"Enclosure layout"); the internal drip pan + moisture sensor for the backflow vent; the bench-built unpowered electronics shelf (output of [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md)).

Out: a complete mechanical chassis — cold core seated at the rear on its support ring, compressor bolted to the enclosure floor with the sheet-metal shroud installed over the terminal block + PTC relay/overload module, condenser + fan mounted on the chosen side wall with intake grille on one side face and exhaust grille on the opposite side face (straight-through, no redirection), back panel mounted with all bulkheads installed (no internal plumbing runs yet, no AC/DC wiring runs yet), hopper installed at the top-front, electronics mechanically seated on the foam-cap top (unpowered). Ready for [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md).

Not in scope: internal plumbing runs through the cabinet (warm-side check valves, regulator, pump-to-manifold lines, water-inlet path) — see [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md); AC + DC + signal wiring runs between the shelf, the compressor, the fan, the manifold, the moisture sensor, and the umbilical — see [`wiring.md`](/hardware/assembly/wiring.md); installing the wound coil onto the vessel (already done in [`cold-core.md`](/hardware/assembly/cold-core.md) step 1); refrigerant-loop integration (already done in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)); nameplate plaque serialization, signing, and final application — that happens at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md), not here.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7 (printed enclosure parts), §8 (back-panel bulkheads — PP1208E ×3, PP1208E water inlet), §3 (the §3 PP1208E water inlet), §4 (the DERPIPE front-panel CO2 PTC), §5 (the C14 inlet + the compressor shroud + its SS cable gland), and §13 (mechanical attach hardware). **The chassis fastener schedule at Open items 1 — the four compressor-foot screws, the two shroud screws + washer, and the four condenser-ear screws — has no §13 rows yet**; §13's M3 × 8 count is spent on the electronics shelf and there is no M3 × 10 or M3 × 18 line at all. Status (ACQUIRED / ON-ORDER) lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11. The table below is the procedure-level summary.

| Item | Source / spec | Notes |
|---|---|---|
| Integrated refrigerant-loop assembly | Output of [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) | Cold core + plumbed compressor + condenser/fan, charged, run-up-verified, leak-checked |
| Enclosure shell + back panel + top hopper feature | [`/hardware/printed-parts/enclosure/`](/hardware/printed-parts/enclosure/) | PETG per back-panel README "Panel material"; printed in the configuration captured at order time |
| Cold-core support ring | [`/hardware/printed-parts/enclosure/cold-core-ring/`](/hardware/printed-parts/enclosure/cold-core-ring/) | Printed PETG, unfastened; the seat the cold core lands on, with wells for the bottom foam cap's cap-screw heads. BOM row still missing — see Open items |
| Nameplate plaque (blank) | [`/hardware/printed-parts/enclosure/nameplate/`](/hardware/printed-parts/enclosure/nameplate/) | Pre-printed blank; serialized + signed + applied at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md), not here |
| Compressor shroud | [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) | SendCutSend [0.059"](WALL_IN) G90 galvanized steel, 5-sided open-bottom box |
| C14 panel-mount inlet | MXR B07DCXKNXQ ([`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) §1) | Recessed [3–5 mm](AC_RECESS_DEPTH) into panel face with the printed shroud |
| Water-inlet bulkhead | John Guest PP1208E B00JYFU8MM ([back-panel §2](/hardware/printed-parts/enclosure/back-panel/README.md)) | Customer-facing 1/4" JG QC on the rear panel; the internal ASSE 1022 chain it feeds sits inside the cabinet |
| CO2-inlet bulkhead | DERPIPE 5/16"-tube × 1/4" NPT push-to-connect ([front-panel §1](/hardware/printed-parts/enclosure/front-panel/README.md)) | Red accent ring at panel opening; mounts on the front panel, not the back panel |
| Umbilical PP1208E bulkheads × 3 | John Guest B00JYFU8MM ([back-panel §6](/hardware/printed-parts/enclosure/back-panel/README.md)) | Triangular cluster; blue accent ring on the carbonated-water bulkhead at the top vertex |
| Drip pan + moisture sensor | Pan: [`/hardware/printed-parts/enclosure/drip-pan/`](/hardware/printed-parts/enclosure/drip-pan/) (printed PETG); sensor: Shutao LM393 water-sensor module (B0B2W76MB1, [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md)) | Backflow-vent observation per [`/hardware/future.md`](/hardware/future.md) "Backflow vent monitoring"; sensor wires to SIG-9 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md), terminated at the shelf during [`wiring.md`](/hardware/assembly/wiring.md); the basin rides a VHB'd printed rail pair on the foam-cap top and draws aft to be emptied |
| SS 1/2" NPT cable gland | B0F2HP5FWB ([compressor-shroud §Penetrations](/hardware/cut-parts/compressor-shroud/README.md)) | AC pass-through strain relief in the shroud sidewall |
| Bench-built electronics shelf | Output of [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md) | Unpowered; AC pigtails hang free, terminated at the C14 inlet in [`wiring.md`](/hardware/assembly/wiring.md) |
| ruthex M3 heat-set inserts + M3 fasteners | ruthex B0D39W228K + BNUOK B0DJQGF665 / B0DJQGVK8S | Per the enclosure-shell screw schedule (TBD until enclosure CAD lands — see Open items) |
| Chassis bonding lead — compressor shroud | Green 18 AWG, ring terminal | Bonded to the shroud's earth-bond hole on the back face (see [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Grounding & mounting"); landed at the ground bus in [`wiring.md`](/hardware/assembly/wiring.md) |

Tooling: standard hand tools — Phillips + hex (2.5 mm for M3), soldering iron + ruthex insert tip for any inserts not pre-installed at the printed-part stage, a level, and the build-fixture cradle that holds the chassis upright while the cold core is seated (printed bench fixture, not yet specified — see Open items).

## Procedure

The chassis is built from the floor up: enclosure shell on the bench, compressor on the floor under its shroud, condenser/fan against the chosen side wall, cold core dropped in at the rear, drip-pan rails onto the foam-cap top behind it with the basin slid in aft-to-forward, hopper at the top-front, back panel (bulkheads pre-installed) mounted last, electronics stack seated on the pump-2 column beside the rear-panel C14 inlet. The cold core drops in as a single pre-assembled unit — it is not built up in place. See [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Output condition" for the state the cold core arrives in.

### 1. Stage the enclosure shell + back panel on the bench

Print-inspect the enclosure shell, back panel, top hopper feature, and nameplate blank. Wipe down the interior; remove brim residue and any stray support material at the bulkhead bores, the grille slats, the compressor-mounting bosses on the floor, and the cold-core support-ring landing at the rear. Set the nameplate plaque aside in the unit's build folder — it does not get applied at this step (see [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md)). The pre-printed blank attachment points on the rear panel are confirmed clean and unobstructed.

Install ruthex M3 heat-set inserts wherever the enclosure-shell screw schedule calls for them (insert positions are defined per the enclosure CAD — see Open items). Standard heat-set procedure: soldering iron on the insert, press straight down until flush. All inserts go in *before* anything else is in the cabinet, while there is bench access from every face.

Pre-install all bulkheads on the back panel on the bench, ahead of mounting it to the shell. This is the easier work surface, and pre-installation lets the bulkhead torque load react against a panel that is unconstrained from inside-the-cabinet interference:

- **C14 inlet** seats into the rectangular cutout from the outside face, retained by its panel-mount screws per the MXR spec, drawn flush against the printed shroud's recess so the C13 cord housing will nest into the [3–5 mm](AC_RECESS_DEPTH) recess on insertion. Inlet solder-tab pins face into the cabinet.
- **Water-inlet bulkhead** (John Guest PP1208E, same SKU and panel hole as the umbilical trio): customer-facing 1/4" JG push-to-connect facing out — the install-kit 1/4" LLDPE pushes in, no tools — retained by its flange + nut sandwich like the umbilical cluster below. The ASSE 1022 chain it feeds sits inside the cabinet, not on this panel ([back-panel §2](/hardware/printed-parts/enclosure/back-panel/README.md)).
- **CO2-inlet bulkhead** — *not* pre-installed on the back panel; lives on the front panel per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md). Front-panel pre-install step is a separate procedure (not yet broken out in this doc).
- **Umbilical PP1208E bulkheads × 3** in the triangular cluster: the blue-accent-ring bulkhead at the top vertex (carbonated water), the other two at the bottom corners (flavor A + flavor B). All three retained against the panel via their flange + nut sandwich on the EPDM O-ring per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Open items" — mechanical capture only, no panel-side gasket.

Set the populated back panel aside; it mounts in step 7.

### 2. Mount the compressor to the floor with the shroud pre-installed

The compressor body comes in as part of the integrated refrigerant-loop assembly with all refrigerant lines already brazed to it; the cold core's coil stubs are connected to the suction line and capillary tube as documented in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md). The compressor is not separated from this assembly at any point in this procedure.

**Install the compressor shroud over the terminal block + PTC relay/overload module BEFORE bolting the compressor to the enclosure floor.** Bench access to the terminal block is much easier with the compressor still on the build cart; once the compressor is bolted to the floor it sits in the middle-bottom of the enclosure with the cold core landing right next to it, and seating the shroud over it is much harder. Sequence:

1. Set the compressor on its side or upright on a clean bench, the cold-core assembly steady on its cart with no tension on the refrigerant lines.
2. Fit the SS cable gland into the shroud's [7/8"](PANEL_HOLE) sidewall hole and secure its locknut (the side that will face toward the electronics stack at the front-right — best path for the future AC pigtail run to Teyleten relay #1).
3. Lower the shroud down over the terminal block + PTC module. Confirm ≥[10 mm](TB_CLEARANCE) clearance on all sides of the terminal block per [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Dimensions".
4. Fasten the shroud through its two Ø4.5 mounting holes per [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Grounding & mounting". These are **shear pins, not clamps** — they locate the sheet without distorting it, so torque-limited. Screws and positions are in the schedule at Open items 1: M3 × 10 from the front wall's exterior counterbore, M3 × 8 with a flat washer from the machine corridor. Drive the rear one here. The MQ-6 as placed sits 1.00 mm behind the shroud's rear face on that screw's own axis, so once [`wiring.md`](/hardware/assembly/wiring.md) lands the sensor the shroud does not come off again without pulling it.

Bolt the compressor to the enclosure floor at its four printed pads, the shroud seated over it — M3 SHCS through each donor grommet's steel bushing. **The grommet is the isolation element and is never crushed**; the screw bears on the bushing, not the rubber. Foot pitch and screw length are estimates until a donor is measured — see the schedule at Open items 1. The condenser + fan + condenser-side tubing comes along on the same lift (still attached as part of the integrated refrigerant-loop assembly). Mind the condenser orientation — its airflow axis lands in step 3.

### 3. Mount the condenser + fan against the chosen side wall

Position the condenser + fan against the chosen side wall, fan axis crossing the enclosure side-to-side, intake side facing the intake grille and exhaust side facing the exhaust grille on the opposite face. The donor's harvested fan shroud carries the mounting screws into the printed enclosure side wall's condenser bosses (insert pattern defined per the enclosure CAD).

Which side wall (left or right) holds the intake vs. exhaust is not yet locked — see Open items. Working assumption: the side opposite the cabinet door swing per the kitchen install convention, so the condenser exhaust is on the cabinet-rear side and intake on the cabinet-front side (the user opens the door to less-warm air). Either assignment is mechanically equivalent — the fan + condenser are symmetric in the enclosure cavity — but it locks the grille faces of the printed shell at order time.

Confirm: the fan's flow direction matches the donor's native orientation per [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md). The fan was already validated in this configuration in the donor ice maker; the only new variable is its anchor surface.

### 4. Seat the cold core at the rear

Drop the printed cold-core support ring ([`/hardware/printed-parts/enclosure/cold-core-ring/`](/hardware/printed-parts/enclosure/cold-core-ring/)) onto the back of the enclosure floor first. It is unfastened: its two ears reach the ±X side bands to fix it laterally, and it keys fore-and-aft between the back column's Z-seam pin pods. Confirm its six wells are clear of debris — they are what the bottom foam cap's six M3 cap-screw heads hang in, and those heads, not the cap's lid, are the core's lowest surface.

With the compressor + condenser + fan now anchored, lower the cold core into the rear of the enclosure as a single pre-assembled unit. The cold core lands on that ring — the ring's bearing rail captures the foam-shell's own outer footprint ([283](FOAM_SHELL_X) × [181](FOAM_SHELL_Y) per [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "outer_shell" + "foam_lid"), landing the core one ring height above the floor. Its two front lugs are the core's stop forward; the back Z-seam lip its rear face already seats against is the stop aft.

The coil stubs are already brazed into the donor loop (suction line + cap-tube join) per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) step 4–5 — no brazing work happens here. Confirm no tension is induced on the refrigerant lines as the cold core seats; the compressor + condenser were placed first specifically so the cold core can land on the support ring without dragging the brazed joints. Re-check the BPV31 cap is tight (the appliance's single permanent service-access point per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Output condition").

Cold-core penetrations on the +Z outer wall (the wall facing forward toward the front of the cabinet, by the cold-core coordinate convention in [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md)) — the shared copper/water-inlet slot, the reservoir-line holes, the water-outlet hole, the reed-cable holes — face into the cabinet interior where [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md) will reach them.

### 5. Bond the drip-pan rails, slide the basin in, seat the moisture sensor

Bond the printed rail pair ([`drip-pan/README.md`](/hardware/printed-parts/enclosure/drip-pan/README.md)) to the cold core's foam-cap top with 3M VHB 4941 under foot and web, in the rear strip east of where the controller board lands: rails fore-and-aft, home stops forward, the pair's aft ends on the cap's rear edge. The basin then slides in from the back along the shelves until its front wall butts the home stops, which lands it under the drip off the Multiplex 19-0897's atmospheric vent tip — the tip leans aft over the strip, its fall into the basin verified by the assembly scorecard's `fall` rule (the pan + vent location are inside the cabinet; see [`/hardware/future.md`](/hardware/future.md) "Backflow vent monitoring"). Lay the moisture sensor flat in the basin with its leads routed toward the shelf's landing point on the same deck. Leave the leads loose for now — termination at the shelf happens in [`wiring.md`](/hardware/assembly/wiring.md) (run SIG-9 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md)).

Rails + basin + sensor go in before the back panel and the shelf: both reach into the band over this strip, and the rails bond from above with the bay still open. The basin's own travel is aft, along the rails — the deck it stands `drip_pan.RAIL_LIFT` above stays open for the SIG-9 leads and the C14 cordage.

### 6. Clear the Zone C opening

Nothing installs at this step — the hopper is an **opening**, not a part. [`enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py) cuts `_hopper_hole` in the top wall right of the display facet, sized off the placed funnel's own collar dimensions, so the enclosure-front-top print already carries it and there is no screw pattern to land.

Deburr and wipe the collar seat: the removable silicone funnel's brim underside rests on this face, and brim residue or a stray support nib holds the basin proud and crooked in its frame. Then sight straight down the opening and confirm the fall corridor to the pump row below is clear — the funnel's spout drops through open air to the V-B hopper gate on the source-select tray, and the pumps' keep-outs hold that corridor open. The funnel itself ([`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md)) is fitted at finish-and-pack, after the wipe-down, not here.

The V-B hopper gate and the flavor routing below the opening are plumbing work that lives in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md), not here.

### 7. Mount the populated back panel

Lift the populated back panel (all bulkheads pre-installed per step 1) and seat it against the rear of the enclosure shell. Fasten with the screw pattern specified in the enclosure CAD (TBD — see Open items). With the panel in, confirm the umbilical PP1208E cluster is oriented with the blue-ringed bulkhead at the top vertex of the triangle — orientation matters here because the user-facing rule at install is "blue tube into the blue-ringed bulkhead" per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification", and that rule only works if the blue ring sits where the user expects it (visually dominant top of the triangle).

The panel has no fluid-pressure duty per the back-panel README — the bulkhead O-rings seal the pressurized fluid path around each tube. The panel-to-shell interface is mechanical capture only; no panel-side gasket is required.

The four cabinet-side bulkhead stubs (the water-inlet PTC interior and the three umbilical PTC interiors) are now all visible from inside the cabinet. They get plumbed in [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md), as is the front panel's CO2 NPT stub once the front panel is on (separate install step per step 1). The C14 inlet's solder-tab pins are similarly exposed inside; they get terminated to the power tray's AC pigtails in [`wiring.md`](/hardware/assembly/wiring.md). The compressor shroud's [7/8"](PANEL_HOLE) gland sidewall hole is ready to accept the AC run arriving from the shelf above the cold core in [`wiring.md`](/hardware/assembly/wiring.md). Confirm: no plumbing or wiring has been routed through any bulkhead or shroud penetration at this point.

### 8. Seat the electronics shelf on the foam-cap top (unpowered)

Bolt the board and the PSU down onto the foam cap's own deck-mount columns. There is no tray under either of them and nothing is bonded: the top cap carries eight boss columns, each with a heat-set insert in its top, and each module lands on four of them with M3 × 8 SHCS. The board's four rise through the lid and stand proud of it, so the board rides the column tops with its through-hole tails clear; the PSU's four stop under the lid, so the PSU lies flat on the lid's own face beside the pump and its screws cross the lid to reach the inserts. The stations are the cap's ([`_cold_core_interface.deck_mounts`](/hardware/printed-parts/cold-core/_cold_core_interface.py)); the assembly reads its poses off them.

The **controller PCBA** takes the west column, a quarter turn from its own frame so the long axis runs down the bay — the USB-C edge (J14) looking south into the open band ahead of the cap, where a hand reaches it with the back panel on, and the J10 12 V throats north up the column. Handle it ESD-safe; the four holes are its electrically isolated MH1–MH4, and the screw heads seat on the top-face pads.

The **Mean Well IRM-90-12ST PSU** takes the aft strip west of the drip basin, laid across it, its AC end toward the rear-panel C14 inlet directly above.

The **AC distribution (three Wagos), both Teyleten relays, the ground bus and the DC distribution block** have no station yet. The power tray still carries them as bench geometry, but the PSU it was laid out around no longer sits on it — see [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md).

The shelf is **unpowered** at this step. The AC pigtails from the power tray hang free — they get terminated at the C14 inlet's solder-tab pins directly above in [`wiring.md`](/hardware/assembly/wiring.md), not now. Similarly the DC and signal runs to the manifold, pumps, fan, moisture sensor, reed columns, and faucet umbilical land in [`wiring.md`](/hardware/assembly/wiring.md). The compressor shroud's earth-bond lead (to the back-face bond hole, run AC-6 per [`wiring.md`](/hardware/assembly/wiring.md)) routes toward the shelf's ground bus and waits to be terminated.

Confirm the board's two X edges are clear to a hand and a plug, and that the panel-port bodies reaching into the band stand above its crown rather than in front of its edges. No wiring runs are made at this step.

## Output condition

A complete mechanical chassis ready for [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) and [`wiring.md`](/hardware/assembly/wiring.md):

- Cold core seated at the rear on its support ring, no tension on the refrigerant lines
- Compressor bolted to the enclosure floor, sheet-metal shroud installed and fastened to the enclosure floor through its two Ø4.5 mm base mounting holes, gland-fitted [7/8"](PANEL_HOLE) AC pass-through facing the electronics stack
- Condenser + fan mounted on the chosen side wall, airflow axis crossing the enclosure side-to-side, intake grille on one side face and exhaust grille on the opposite side face
- Back panel mounted with the three PP1208E umbilical bulkheads pre-installed in their triangular cluster (blue ring at top vertex), the PP1208E water inlet left of them, and the C14 inlet (recessed with printed shroud) at the leftmost station — every station in the band above the cold core, bodies reaching forward into its open rear half. CO2 inlet lives on the front panel — see [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md); separate install step (not yet broken out in this doc).
- Drip pan + moisture sensor seated on the foam-cap top under the backflow vent's fall, in the strip behind the shelf row, sensor leads routed toward the shelf on the same deck (not yet terminated)
- Hopper installed at the top-front, outlet stub hanging free
- Electronics shelf seated on the foam-cap top — power tray, PCBA tray, and DC distribution lying flat in the band above the cold core — unpowered, AC pigtails hanging free
- Nameplate plaque blank set aside in the unit's build folder, **not** applied (serialization, signature, and application happen at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md))
- Chassis bonding lead ring-terminated at the compressor shroud's Ø6 mm earth-bond hole on its back face, routed toward the shelf's ground bus, not yet terminated
- No internal plumbing runs, no AC/DC/signal wiring runs

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Enclosure shell + back-panel screw schedule.** The refrigeration stratum is drawn — the compressor's four floor pads, the shroud's two capture bosses, and the condenser's four ear pads are printed features of the front-bottom piece (`enclosure.py` `_compressor_feet` / `_shroud_seat` / `_condenser_mount`), all M3 SHCS into ruthex M3 heat-sets:

| Station | Qty | Screw | Position (world mm) | Notes |
|---|---|---|---|---|
| Compressor feet | 4 | M3 SHCS, est. M3 × 18 | pads x {43, 143} × y {34, 99}, top z 8.25 | Through the donor grommet's steel bushing — the grommet is the isolation element and is never crushed. Foot pitch 100 × 65 is an **estimate** until the donor is measured |
| Shroud — front | 1 | M3 × 10 | axis x 103, z 18; head counterbored in the front wall exterior | A shear pin through the shroud's Ø4.5 hole, not a clamp — no sheet distortion |
| Shroud — rear | 1 | M3 × 8 + flat washer | axis x 103, z 18, driven from the machine corridor | Washer because Ø4.5 leaves an M3 head 0.5 mm of bearing. **The MQ-6 as placed fouls this screw's driver lane** — 1.00 mm behind the shroud's rear face, on the bore's own x |
| Condenser fan-shroud ears | 4 | M3 × 10 | y {47.75, 130.25} × z {37.25, 119.75}, pad face x 269 | Ear pattern 82.5 × 82.5 is an **estimate** until the donor shroud is separated |

Still open: the panel-to-shell and hopper-to-shell patterns, and the shroud's rear-screw/MQ-6 service conflict above.
2. **Condenser-fan side-wall assignment (left vs. right).** [`/hardware/future.md`](/hardware/future.md) "Enclosure layout" specifies side-to-side airflow with intake on one face and exhaust on the opposite face, but does not lock which side. Working assumption is the side opposite the cabinet-door swing per kitchen install convention; this is unverified and should be confirmed against typical 36"-base-cabinet door-swing geometry in target kitchens, then locked into the printed shell at order time.
3. ~~**Hopper attach mode.**~~ **CLOSED — integral.** The hopper is an opening in the printed top face, not a part: [`enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py) cuts `_hopper_hole` from `enclosure-front-top` off the funnel's own dimensions, and the cast silicone funnel ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §8, BBDINO) seats its brim in it. So the shell print already carries the hopper ( §7 "Enclosure — front bottom + front top", PETG), there is no separate hopper row to add, and EN-06 collapses into the top-face install with no fastener pattern of its own.
4. ~~**Drip-pan landing.**~~ **CLOSED.** The basin is [64 × 76 × 15 mm](/hardware/printed-parts/enclosure/drip-pan/), sized by what its floor carries and by what stands beside it: the Shutao plate lies with its long edge down the withdrawal axis, so the width it asks for comes out of the strip's depth rather than its contested X, and the controller board takes the west end the basin gives back. It stands `drip_pan.RAIL_LIFT` off the foam-cap top on a VHB'd printed rail pair, hung east of the vent column with its back face on the cap's rear edge, and draws aft along the rails to be emptied — rising at no point. §7 row added. Still open: the SIG-9 cable length, and the rear-panel slot the withdrawal wants (see [`back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) Open items) — until it is cut, the basin draws aft off the rails and lifts clear inside the cabinet.
5. **Build-fixture cradle.** A printed bench fixture that holds the enclosure shell upright (or tilted) during compressor mounting, cold-core lowering, and back-panel installation. Not yet specified; depends on the shell's external dimensions and on whether the build proceeds on its side or upright.
6. **Cold-core support ring — its BOM row and its print-flatness check.** The ring is designed and packed ([`/hardware/printed-parts/enclosure/cold-core-ring/`](/hardware/printed-parts/enclosure/cold-core-ring/)): a separate drop-in print, because the shell's Y seam falls inside the core's own footprint and an integral rail would print in two pieces with the core's bearing plane across the joint. Open: its missing [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7 row, and a first-article check that the bearing rail lies flat — it is the core's datum plane and a 283 mm open frame is the shape most likely to lift a corner. The M3 head protrusion the seat height is derived from is the DIN 912 nominal, not a measurement off a seated screw with the cap gasket compressed.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_enclosure_mechanical_sync.py`
