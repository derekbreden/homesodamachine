# Single-valve tray

One Beduan solenoid on one printed plate — the valve-manifold family's smallest
member.

| | |
|---|---|
| plate | [38.25](PLATE_X) × [40](PLATE_Y) × [9](PLATE_Z) mm |
| collet span | [59](PORT_SPAN) mm across the two port tips |
| plate top | [6](TRAY_TOP_Z) mm |
| mount ears | 2, on the centreline, [49.5](EAR_PITCH) mm apart |

## Why it exists

`../two-valve-tray/` is two of `../single-tray/`'s cells sharing one floor and
`../three-valve-tray/` is three. This is one, and the plate is that cell's own
reach and nothing more.

The reason it is a part rather than a two-valve plate with a seat left empty:
the assembly scripts seat a valve in every seat they are given. `build_assembly`
is a comprehension over `seats`, with no subset and no variant STEP. So an
unused seat does not render an empty cell — it renders a **valve that is not in
the machine and not in the BOM**, and it shows up in every elevation. A row that
carries one valve gets this part instead.

## Where it goes

The aft stand's middle row, carrying V-K — the tap-water fill/shutoff solenoid
between the water split and the SeaFlo's suction.

The enclosure's aft stand carries three of these — V-K on the middle row and
the two nozzle gates — each placed by its own two runs. Flat, the plate spends
its saving over a two-valve in **X** and its collets face ±Y, which is how all
three stand: `_contents.VK_TRAY_COLLETS`, `NOZZLE_B_TRAY_COLLETS` and
`NOZZLE_TRAY_COLLETS` each name one seat's pair on the `xc` seat. A row turned a
quarter turn about Z spends the saving in **Y** instead, its collets on ±X.

`xc` is the same key the three-valve plate's middle seat carries, so a valve
moved between the two keeps its collet names.

## The ears

The family's, unchanged — one tongue off each port face on the plate's own
centreline, at `two_valve_tray.ear_y`, which is struck off `half_y` and
`port_half`. This plate shares both, so the ears stand where they do on every
other tray and a carrier's boss pitch is the same part to part. The foam cap's
deck-mount table holds the aft stand's stations
(`_cold_core_interface.deck_mounts`).

## Files

| | |
|---|---|
| `single_valve_tray.py` | the bare plate → `single-valve-tray.step` |
| `single_valve_assembly.py` | plate + its valve → `single-valve-assembly.step` |

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/single-valve-tray/single_valve_tray.py`
