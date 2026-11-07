# Main board

The main board bolts straight to four printed bosses on the +X wall of back-top, with no
floor between the board and the wall. The stations are struck off the board's own MH1–MH4
pattern and carried through its placement, and `pcba-board.step` is the body the machine
carries. What lives here is the board datum every one of those mounts is derived from — the
outline, the MH1–MH4 rectangle, the thickness, the **2 mm THT-tail envelope below the PCB
underside**, and the component heights read off the fab model.

## The board

- **[Main board](/hardware/pcb/pcba/)** — the one board: ESP32-WROOM-32E,
  both MCP23017s, DS3231, both TBD62083 sink drivers, both DRV8870 pump
  H-bridges, RS485, the 5 V buck + 3.3 V LDO, and every field connector
  (J1–J14).

Beside it: AC lives across the strip aft of the main board — the PSU and relay #1
each on their own cap columns, the Wago AC distribution and its PE block in
the wall's own Wago wells; the looms land on the
board's edge connectors per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

## Mounting

The board's four **electrically isolated plated mounting holes** — MH1–MH4 in
[`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), 3.2 mm hole / 4.0 mm pad on a
**78.0 × 66.3 mm** rectangle, each hole ~3.5 mm inside its board corner — take M3
SHCS down through the board into heat-set inserts; the screw head + washer seat on the
top-face pad, which the board's pours keep clear (`fastenerAnnulus`).

The PCB underside and every mounting hole are at Z = 0 in `pcba-board.step`.
Every part on the board is top-side, so the underside presents only through-hole
solder joints and flush copper. The through-hole component footprints continue to
Z = −2 as a conservative tail envelope, except within 8 mm of each mounting hole,
where the model carries the board's own joints instead (`JOINTS` in
[`numbers.rs`](numbers.rs)): J1 pin 1 stands 6.2 mm from MH2 to its pad edge, J7 pin 1
6.3 mm from MH3 and J11 pin 1 5.5 mm from MH4, and MH1's nearest, a J14 shield leg, is
11.3 mm off. In the appliance that envelope is seated nearest the +X wall, so the four wall
bosses reach 2 mm farther inboard to the actual board underside; the wall is not allowed
to occupy the solder-tail clearance simply because the fab visualization omits
detailed clipped leads.

The appliance's mounting sleeves at MH1, MH2 and MH4 are sized off those joints:
3 mm round the knurl entry at MH1, 2.25 mm at MH4 beside J11 pin 1, and 2 mm at
MH2, where the sleeve meets relay #2's lower bar flush. MH3 seats on the
rectangular pad it shares with the upper bar of relay #2, which the enclosure
assembly reads clear of the whole envelope; its fore face stands 0.5 mm off J7
pin 1, 2.6 mm from the knurl entry. Each short M3 insert starts 2.25 mm wallward
of the board's mounting
face, behind the tail zone and its 0.25 mm supported-face allowance. The complete
Ø8 mm insert host starts at that recessed seat; a Ø5 mm entry admits the whole
knurl. M3×8 through the 1.6 mm PCB reaches 4.15 mm into the 4 mm insert, with
at least 0.85 mm reserve before the blind end. The
[enclosure audit](../../enclosure/enclosure/heat-set-review/geometry-check.json)
checks those complete native seats and installed screw stacks.

The board's frame **is its pcb frame** (pcbX/pcbY as in `pcba.tsx`), so every mounting
station is its MH coordinate verbatim. Board footprint **85 × 72.8 mm** as fabbed.
Keep the west and east edges unobstructed on the wall: the USB-C
programming port (J14) is flush on the west edge, and the J10 12 V screw
throats face east.

## Files

[`numbers.rs`](numbers.rs) holds the board datum. [`pcba_assembly.rs`](pcba_assembly.rs)
cuts `pcba-board.step` and its payload and model — the board as a simplified populated
model: the outline slab with MH1–MH4, one box per component at its placed footprint and
height, and the clipped 2 mm wall-facing part of each through-hole box — from
[`board-stock.json`](board-stock.json), the component boxes read off the
[PCB build's](/hardware/pcb/pcba/) fab model `hardware/pcb/pcba/out/pcba.glb`, which holds
the full component 3D. It also writes `pcba-assembly.numbers.json`, the board's slab and
outline centre that the installed machine's wiring reads.

Regenerate from the repository root:

```sh
python3 tools/run.py -- cargo run --release --manifest-path tools/hsm/pcba-assembly/Cargo.toml
```

When the board's design changes, export the fab model again and then write its component
stock down:

```sh
python3 tools/run.py -- cargo run --release --manifest-path tools/hsm/pcba-assembly/Cargo.toml -- --read-fab-model
```
