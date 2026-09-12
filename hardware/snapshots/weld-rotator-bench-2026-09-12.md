# Cap-weld rotator on the welding table — Snapshot 2026-09-12

**This is a point-in-time snapshot, not a living document.** It records the state of the
cap-weld rotation rig the night it moved from the bench to the welding table: wired, turning
under the pedal, and not yet used for a weld. The living description is
[`weld-rotation-rig.md`](/hardware/assembly/weld-rotation-rig.md); the controller is
[`firmware/src_weld_rotator/`](/firmware/src_weld_rotator/README.md).

## What is on the table

The fixture in the guide's built-system table, with the STEPPERONLINE 23HS30-2804S on the
DM542T, the BTF-LIGHTING 24 V adapter, the HimaPro 50122 pedal, and the ESP32-DevKitC-32E
driving the acquired ULN2803A module. The low-voltage harness is Dupont jumpers and WAGO 221
lever nuts, one WAGO per node:

- **Pedal.** GPIO27's WAGO holds the GPIO27 jumper, one leg of the pull-up and the pedal `NO`.
  The other leg meets the 3V3 jumper in its own WAGO. Pedal `COM` sits on an ESP32 GND pin. The
  pull-up is one resistor from the acquired Chanzon 3.3 kΩ pack.
- **Driver signals.** ULN `1B`/`1C` carry GPIO25 to `PUL-`, `2B`/`2C` carry GPIO26 to `DIR-`,
  with `PUL+` and `DIR+` on the ESP32's 5 V. The module's silk names the chip's pins: `nB` is
  input n, `nC` output n.
- **`ENA`.** The guide's table carries it on `3B`/`3C` from GPIO32. That row was added after the
  harness was built; this snapshot does not confirm it landed.

The DM542T switches follow the guide: 3.76 A peak, half current at standstill, 3,200 pulses per
motor revolution. The speed and degrees arithmetic assume that last figure.

## Firmware and stored settings

Commit `0fb3f5b5d` is flashed. `status` reports the reset reason, uptime, how long the pedal has
been in its state, and whether the driver is holding. Stored in flash:

| Setting | Value |
|---|---|
| `speed` | 8.0 mm/s bead travel (1.235 table rpm, 48.6 s per revolution) |
| `direction` | `ccw` |
| `dirinvert` | off |

`direction cw` was seen to turn the table clockwise viewed from above before the switch to
`ccw`, so no inversion is stored.

## Seen on the console

Each pedal press prints `RUN 8.00 mm/s` and each release `STOP pedal released at N deg`, with N
matching the length of the press. The board stays up across presses: no USB drop, no reset.

## Not yet done

- **The first weld** on the rig.
- **The lap check.** One full turn on the `turned` readout should bring the index mark back to
  its start. A mismatch means the microstep switches disagree with 3,200 pulses per revolution.
- **The driver hold, once `ENA` is wired.** Ten seconds after a release the motor should go cold
  and the table turn by hand; `status` says `driver released`. A press that leaves the motor
  loose means the enable sense is the reverse of the driver manual's, a one-line firmware flip.
- **Bench power.** The Micro-USB moves from the host to the acquired 5 V adapter's tip once the
  settings are stored, per the guide.
