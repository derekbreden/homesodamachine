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

`../two-valve-tray/` is two of `../single-tray/`'s cells sharing one floor. This
is one, and the plate is that cell's own reach and nothing more.

The reason it is a part rather than a two-valve plate with a seat left empty:
the assembly scripts seat a valve in every seat they are given. `build_assembly`
is a comprehension over `seats`, with no subset and no variant STEP. So an
unused seat does not render an empty cell — it renders a **valve that is not in
the machine and not in the BOM**, and it shows up in every elevation. A row that
carries one valve gets this part instead.

## Where it goes

Nowhere in the machine. This plate is bench geometry: the appliance seats no
tray at all, because the three valves that stand on a printed face stand in
cradles the cold core's own top lid carries — [`single-tray`](/hardware/printed-parts/valve-manifold/single-tray/README.md)'s
cell cut straight into that face at each station in
`_cold_core_interface.cap_cradles` — and every other valve is butted collet to
collet down a limb of the flavour pack, which carries its own. So the part has
no row in [`bom.md`](/hardware/ledger/bom.md) §7 and nothing bolts to the cap.

What it is FOR is the cell on a floor: one seat's own reach and nothing more, so
a carrier that cannot print a cradle into itself can bolt one on instead. Flat,
the plate spends its saving over a two-valve in **X** and its collets face ±Y; a
plate turned a quarter turn about Z spends the saving in **Y** instead, its
collets on ±X.

`xc` is the seat's own key, and the family keys every collet the same way — the
seat's name, then the end by sign.

## The ears

The family's, unchanged — one tongue off each port face on the plate's own
centreline, at `two_valve_tray.ear_y`, which is struck off `half_y` and
`port_half`. This plate shares both, so the ears stand where they do on every
other tray and a carrier's boss pitch is the same part to part. No carrier in
this machine presents that pitch: `_cold_core_interface.deck_mounts` is empty,
and the cap prints the cell rather than bolting the plate.

## Files

| | |
|---|---|
| `single_valve_tray.py` | the bare plate → `single-valve-tray.step` |
| `single_valve_assembly.py` | plate + its valve → `single-valve-assembly.step` |

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-manifold/single-valve-tray/single_valve_tray.py`
