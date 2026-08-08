# PCBA tray (controller-board mount)

**This tray does not ship.** In the appliance the controller PCBA bolts straight
to four printed bosses on the enclosure's +X wall — the same mount, one part
earlier, with no floor between the board and the wall. The stations are struck off
the board's own MH1–MH4 pattern and carried through its placement
([`enclosure_assembly.wall_mounts`](/hardware/manifold-layout/enclosure_assembly.py)), and
`pcba-board.step` is the body the machine carries. What lives here is the board
datum every one of those mounts is derived from — the outline, the MH1–MH4
rectangle, the thickness, and the component heights read off the fab model — plus
the tray itself as bench geometry.

Built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine:
a **single convex-outline floor**, **no walls**, **heat-set M3 bosses**.

## What mounts here

- **[Controller PCBA](/hardware/pcb/pcba/)** — the one board: ESP32-WROOM-32E,
  both MCP23017s, DS3231, both TBD62083 sink drivers, both DRV8870 pump
  H-bridges, RS485, the 5 V buck + 3.3 V LDO, and every field connector
  (J1–J14).

Off this tray: AC lives across the strip aft of the board — the PSU, relay #1 and
the ground ring-stack each on their own cap columns, the Wago AC distribution in
the [AC hub](/hardware/printed-parts/electronics/ac-hub/); the looms land on the
board's edge connectors per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

## Layout & retention

Four M3 heat-set standoff bosses (⌀7, ruthex insert, 5 mm standoff) under the
board's four **electrically isolated plated mounting holes** — MH1–MH4 in
[`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), 3.2 mm hole / 4.0 mm pad on a
**78.0 × 66.3 mm** rectangle, each hole ~3.5 mm inside its board corner. M3
SHCS drive down through the board into the inserts; the board's bottom face
seats on the boss tops (5 mm clears the THT tails — XH wafers, the J10 screw
block, U10, BT1, J14's shield legs), and the screw head + washer seat on the
top-face pad, which the board's pours keep clear (`fastenerAnnulus`).

The tray frame **is the board's pcb frame** (pcbX/pcbY as in `pcba.tsx`), so
every boss centre is its MH coordinate verbatim. Board footprint
**85 × 72.8 mm** as fabbed; the floor is that outline grown 0.5 mm on the
south edge, where MH3/MH4 sit 3.0 mm from the edge against the M3 boss's
3.5 mm radius (MH1/MH2, 3.5 mm from the north edge, are flush with no
growth). Keep the west and east edges unobstructed on the shelf: the USB-C
programming port (J14) is flush on the west edge, and the J10 12 V screw
throats face east.

`pcba_tray.py` → `pcba-tray.step`; `pcba_assembly.py` → `pcba-assembly.step`
(the board as a simplified populated model — the outline slab + one box per
component at its placed footprint and an approximate height, read from
`hardware/pcb/pcba/out/pcba.circuit.json`; the full component 3D is
[`/hardware/pcb/pcba/out/pcba.glb`](/hardware/pcb/pcba/)). Regenerate with
`tools/cad-venv/bin/python <script>`.
