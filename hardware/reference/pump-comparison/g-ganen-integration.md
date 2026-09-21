# G Ganen enclosure integration map

The selected received pump is G Ganen B07F35PTFR. Derek confirmed that no caliper measurements were recorded. The scan-reference agent owns its measured model; this map does not qualify dimensions, inlet/outlet identity, electrical demand or hydraulic performance. All current build results below use the SeaFlo reference.

Three complementary 0.10 mm fused clouds and their native projects are archived in
`~/Documents/3D Scans/2026-09-20-g-ganen-pump/`. Derek identifies the feet as flexible rubber.
Its flow arrow points right with `4002` upright and readable. Derek identifies installed flow toward enclosure −X. With the intended +90° Z rotation,
local +Y is discharge and local −Y is suction. The feet are removable fore/aft sliders on
fixed casing rails. Scan foot poses are individual positions; unloaded poses do not establish
the compressed mounting stack or one mandatory hole pattern.

## Reference interface

Current source: `hardware/reference/seaflo-22-pump/seaflo_22_pump.py`.

- `build()` supplies the actual casing, pressure-switch, feet and barb envelope; assembly currently imports its generated STEP at `enclosure_assembly.SEAFLO_STEP`.
- `suction()` / `discharge()` return port-tip `(position, outward_axis)` in the reference frame. The scan must establish tip station, centerline, usable barb and shoulder separately. IN/OUT needs a visible marking or user evidence.
- `mount_holes()` returns mount-center XY coordinates; `mount_seat_z()` supplies the common bearing plane. The current consumer assumes parallel holes and one underside plane; a nonrectangular pattern or different foot levels requires a real interface change.
- `FOOT_T` supplies pad-top height to casting sections, flavor-port storey and the reservoir-A fill route. It must be a measured mounting envelope, not an inherited SeaFlo number.
- `PORT_D` sets discharge-port radial envelope beside the ASSE tray. `PORT_L` supplies hose engagement in the cut schedule. If ports differ, use per-port values and update these consumers.
- Proposed scan-reference frame is motor/head joint X=0, +X toward motor rear, mounting underside Z=0, shaft centerline Y=0. This is the coordinate convention in the pump-comparison record. Do not mirror a model to force its port identity.

## Placement and manufactured interfaces

`hardware/manifold-layout/enclosure_assembly.py`:

| Consumer | Required reevaluation |
|---|---|
| `SEAFLO_STEP`, `SEAFLO_YAW`, `build_seaflo` | Load the selected reference; resolve bearing plane and pose against the cap, rear plane, tray lane and flavor-port lane. `pump_west_face` intersects the native solid at two real neighboring height bands. |
| `pump_mount_rows` | Inverse-transform every placed mounting hole to cap coordinates and compare with printed columns. |
| `build_suction_chain`, `SUCT_CORNER_ROOM`, `build_vk` | Inlet barb location affects the suction chain Y and the V-K valve/cradle. X/Z currently belong to cap anchor stations. |
| `build_discharge_chain`, `DISCH_CORNER_ROOM`, `anchor_rows` | Outlet barb changes hose turn room and the chain's axial section that bears in its cap anchor. |
| `flavor_storey`, `deck_z` | Pump pad/casting can affect flavor unions and the supported deck, then ASSE/split/regulator/gas-chain heights. Measure resulting propagation rather than moving known fitted Kamoer seats. |
| `pan_front_y`, `build_pan`, `pump_west_face` | Discharge barb bounds ASSE pan/sleeve Y; casting bounds its side clearance. Recheck vent-to-pan landing, wall slot and tray withdrawal. |
| `build_pack`, `CORE_RIDERS`, solids/carry maps and scene IDs | Carry one consistently named diaphragm-pump component through placement, scorecard and viewer; avoid an unlabeled G Ganen model behind a SeaFlo identity. |

`hardware/printed-parts/cold-core/_cold_core_interface.py` owns the printed interfaces:

- `deck_mounts["seaflo-pump"]` is currently a 59 x 79 rectangular pattern centered (-93.20, 2.62) in the cap frame, zero standoff, 8.50 mm clamp stack, 20 mm screw. **None of those dimensions transfers automatically.** A different pattern requires measured positions and a suitable `DeckMount` representation.
- `deck_mount_reach`, insert depth, lid clearance and cap-column spacing must follow the measured foot and actual selected fastener stack. Preserve the cap's pour passages and minimum stock.
- `cap_anchors` for suction/discharge chains and `cap_cradles["vk-solenoid"]` are downstream if those chains move. V-A/V-B cradle bearing shapes are independent and remain applicable; their world stations must still agree with final assembly.
- Consumers: `_foam_cap.py`, `foam-cap/foam_cap.py`, `foam-assembly/foam_assembly.py`, then `hardware/cold-core-layout/cold_core_assembly.py`.

## Tube and plumbing consumers

`hardware/manifold-layout/_lines.py` imports the pump reference and registers its two ports in `STATIONS`.

- `water-6` discharge and `water-7` suction currently use 3/8-inch reinforced PVC (`HOSE_OD`, `HOSE_BEND`, `BARB_SKEW`) into the existing MAACFLOW/JG suction and MAACFLOW/GASHER/JG discharge chains. Compatibility and clamp engagement depend on the scanned barb crest/root diameters and usable length, not pump naming.
- `water-5` leaves the discharge-chain collet; `water-3` reaches V-K. Both need reevaluation if the chains move.
- `_fluid_2` checks an actual tube sweep against the pump and a minimum R14 bend. Its present 1.473 mm native clearance describes SeaFlo only.
- `_gate_a_deck_y` places the `fluid-18` cross-machine turn from pump front. `_fill_a_cap_z` and `_fill_a_turn_y` place `fluid-14` over the pad and behind suction hose. Other routes must pass a complete native neighbor check after the new placement; no manual copying of old route offsets establishes clearance.
- `build_seated_runs` gates `fluid-4` on the pump's scene ID, even though its turn is struck from V-B. Keep that scene mapping consistent and check fluid-2/drain separation in the final enclosure assembly.
- `hardware/scripts/_tube_export.py` imports the pump and uses `PORT_L` for barb engagement and total cut length. `_routing.py` and `_lines.py` own current hose stock/bend assumptions.
- `hardware/manifold-layout/_scorecard.py` names water-6/7 endpoints and pump-to-cap deck-mount contact. Rename/update the selected reference consistently while retaining meaningful mount, port-lead, bend and clearance checks.

## Remaining model and record consumers

- `hardware/scripts/_bom_sync.py` derives pump screws from the deck mount count. Update the current selected pump identity, mounting hardware and tube cut list after the measured design is settled.
- `_materials.py`, model scene labels and parts descriptions carry SeaFlo's identity/color. These are presentation changes, separate from measurement.
- `hardware/wiring/_ac_wiring_schedule_sync.py` currently budgets a 5 A diaphragm peak; firmware documentation cites that figure for the refill/dispense interlock. Geometry does not measure the G Ganen current or justify removing the interlock. Label and powered measurements need their own evidence.
- Readiness/slice/support records for a complete enclosure must bind to the resulting actual meshes. No old SeaFlo print provenance qualifies the replaced-pump enclosure.

## Build handoff

The completed baseline is `hardware/manifold-layout/enclosure-box.json`, SHA256 `a1468381b233f54a07cd491fefe3dabdc56da89bb46fa3bffb6d2181802427c9`. Direct Box, traced Box and traced cold-core assembly passed; all 20 source entries recorded in `hardware/manifold-layout/scan-consumer-checks.json` matched after completion. No complete enclosure piece producer or combined enclosure assembly was run in this sequence. Trace graph updates were sequential and have finished.

For G Ganen: generate the measured reference, resolve native placement/chain interfaces, derive cap columns and any moved chain/V-K seats, regenerate the cap and foam assembly, then rebuild Box, cold-core model, affected enclosure pieces/payload, combined assembly and tube/BOM records. Re-run physical-fit and support-removal checks for affected production parts. The Kamoer cartridge and cap have an independent materializer and depend only on their documented Box subset; their dry-fit print does not require the G Ganen reference.

The full enclosure remains unreleased until the selected reference and its consumers agree.
