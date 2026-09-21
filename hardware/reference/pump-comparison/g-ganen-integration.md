# G Ganen enclosure integration map

The selected received pump is **G Ganen B07F35PTFR**. Its three native scans,
measured rigid housing and independent ports are in
[the reference](../g-ganen-pump/README.md). Derek confirms that its four removable
sliding rubber feet are identical and their pads are approximately 7 mm thick.
The shared foot geometry and raw observed poses remain separate.

Installed flow is **enclosure −X**: suction faces east and discharge faces west.
A +90° Z rotation maps reference +Y discharge to world −X. Electrical demand and
hydraulic performance have separate physical qualification; the geometric model
does not supply those ratings.

## Reference and installation

`hardware/reference/g-ganen-pump/installation/g_ganen_installation.py` is the
production API. It supplies the conservative native components, selected foot
poses, screw axes, bearing datum and separately measured ports. The production
scene key is `g-ganen-pump`.

The common foot's selected slot stations are X=9.5 and 67.5 mm, Y=±38.5 mm.
Each clip is fully engaged at the corresponding end of the visible rail; these
are chosen full-engagement positions, not claimed hard stops. The M3 × 20 screw
axes sit 1.5 mm outward inside the slots, with Ø9 × 0.8 mm washers on the nominal
7 mm pads. The [installation record](../g-ganen-pump/installation/README.md)
contains the cap-frame mounting axes and current native checks.

## Consumers

| Consumer | Current contract |
| --- | --- |
| `enclosure_assembly.build_water_pump` | Places the explicit bearing datum on the cap lid; uses the rigid motor rear and installed rear clearance for fore/aft position, then checks pan and rear-fitting lanes. |
| `enclosure_assembly.pump_mount_rows` | Transforms every selected screw axis into the cap frame and compares it with the printed column. |
| `_cold_core_interface.deck_mounts['g-ganen-pump']` | Four explicit cap stations, nominal pad/washer stack, M3 × 20 screw and blind-bore reserve; `_foam_cap` produces columns and lid passages. |
| `build_suction_chain`, `build_discharge_chain`, `build_vk` | Retain the chains' cap anchor seats and the V-K connection. They are independent of the movable feet. |
| `pan_front_y`, `build_pan`, `pump_west_face` | Use the actual placed discharge/casting envelope and the pan's own clearance span; preserve pan landing and withdrawal. |
| `_lines._water_6`, `_lines._water_7` | Connect the measured discharge/suction tips to their chains with reinforced-PVC hoses, axial leads and R15.9 bends. |
| `_lines` other routes and `_scorecard` | Use the current `g-ganen-pump` body/ports, native neighbor clearance, port leads, bend limits and exact cap contact classification. |
| `_tube_export` | Uses per-port exterior profile lengths as geometric insertion allowances; actual hose insertion and retention remain assembly observations. |
| `_bom_sync`, assembly instructions and cards | Carry the selected pump identity and four current mount screws consistently. |

The casing envelope intentionally fills its reentrant rail/cradle cavities.
Native internal overlap at those classified regions does not describe the
hidden rubber grip or material compression. External neighbor clearance uses
the complete placed pump, including all four common feet.

## Generation and print status

The dependency order is cap, foam assembly, cold-core assembly, Box, shell
pieces and complete enclosure assembly. The resulting native geometry, current
assembly gates and exact slice/support evidence determine the print inputs.
[Print readiness](../../printed-parts/enclosure/print-readiness.md) records the
current build and queue. The full enclosure is the intended assembly trial;
physical spring feel, rubber tightening and plumbing commissioning follow on
that complete printed assembly.

The Kamoer cartridge and cap have a separate materializer and their own accepted
local fit evidence. Pump-foot changes do not establish a need to alter those
local bearing surfaces.
