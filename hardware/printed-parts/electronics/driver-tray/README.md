# Driver tray (12 V switching / distribution group)

The 12 V block of the Zone-B electronics shelf — the drivers that take the PSU's
12 V and switch it to the loads. Built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine, same
idioms as the [power tray](/hardware/printed-parts/electronics/power-tray/):
boards pack **flush**, a **single convex-outline floor**, **no walls**, **heat-set
M3 bosses**.

## What mounts here

- **[L298N](/hardware/reference/l298n/)** — dual H-bridge for the two Kamoer peristaltic pumps; also makes the 5 V logic rail
- **2× [ULN2803A](/hardware/reference/uln2803a/)** — sink the 12 solenoid coils + the condenser fan to GND
- **[Teyleten relay #2](/hardware/reference/teyleten-relay/)** — gates 12 V to the SeaFlo diaphragm pump
- **[DC distribution block](/hardware/reference/dc-dist-block/)** — 12 V + / GND rails off the PSU secondary *(placeholder — hardware TBD)*

Off this tray: the 12 V feed comes from the [power tray](/hardware/printed-parts/electronics/power-tray/) PSU;
the control inputs come from the [controller tray](/hardware/printed-parts/electronics/controller-tray/).

## Layout & retention

L298N at the lower-left; the two ULN2803As stacked just to its right; relay #2 +
DC distribution block in the next column. Footprint ≈ **181 × 68 mm**. Every board
screws onto heat-set M3 standoff bosses.

> Reference geometries here are **estimated stand-ins — verify by caliper** (the
> ULN2803A module footprint especially), and the **DC distribution block is a
> placeholder** until that hardware is chosen.

`driver_tray.py` → `driver-tray.step`; `driver_assembly.py` →
`driver-assembly.step`. Regenerate with `tools/cad-venv/bin/python <script>`.
