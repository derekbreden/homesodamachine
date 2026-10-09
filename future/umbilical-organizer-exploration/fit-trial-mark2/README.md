# Three PET-GF organizer fit samples — Mark2

The plate contains three Ø32 × 10 mm pucks with smooth vertical passages. The
middle sample is the current best estimate for a fit that stays put during
handling but lets a user push or pull an individual tube through with two hands.
The other samples change each tube bore by ±0.10 mm in **diameter** (±0.05 mm in
radius). The Ø5 mm loose signal-cable passage is identical in all three.

| Bed position, viewed from the front | Sample | Quarter-inch bores | 4 mm drain bore | Bed center X/Y |
|---|---|---|---|---|
| Left | Tight | Ø6.45 mm | Ø4.00 mm | 119.5 / 160 mm |
| Middle | Best estimate | Ø6.55 mm | Ø4.10 mm | 162.5 / 160 mm |
| Right | Loose | Ø6.65 mm | Ø4.20 mm | 205.5 / 160 mm |

Mark the parts T/B/L before removing them, or keep them in bed order. The parts
have no added identification geometry. All three share 0.4 mm bore entrance
chamfers and 0.6 mm outer-rim chamfers; their smooth tube contact is 9.2 mm long.

## Print settings and files

The editable project is
[`2026-10-09-organizer-three-fits-petgf-left04-z004-mark2.3mf`](2026-10-09-organizer-three-fits-petgf-left04-z004-mark2.3mf).
The submitted native archive is
[`2026-10-09-organizer-three-fits-petgf-left04-z004-mark2.gcode.3mf`](2026-10-09-organizer-three-fits-petgf-left04-z004-mark2.gcode.3mf).
Source meshes are in [`parts/`](parts/). Manual preparation is
[`../prepare_print.py`](../prepare_print.py); it does not submit a print.

- Printer: **Mark2**, fixed **left 0.4 mm hardened nozzle**, left external
  slot 254, physical PET-GF. The printer reports PET-CF/GFT01, color `161616`.
- Settings source: [`hardware/printed-parts/petgf.3mf`](../../../hardware/printed-parts/petgf.3mf),
  matching the recent Mark2 faucet job's ordinary layer settings.
- Textured PEI; 0.20 mm first layer and 0.24 mm layers above it; 42 layers,
  final commanded Z 10.04 mm for the 10 mm CAD body.
- Two walls; 15% grid infill; profile flow ratio 0.9555. No XY hole or contour
  compensation; 0.15 mm elephant-foot compensation.
- Nozzle 265 °C first layer / 280 °C subsequent layers; bed 80 °C.
- Requested Mark2 Z trim **+0.04 mm**; native textured-plate startup clears to
  `G29.1 Z0` and applies `G29.1 Z0.02` including that trim.
- No supports, brim or pause; clumping detection disabled. Send options:
  timelapse on, automatic bed leveling on, flow calibration automatic,
  nozzle-offset calibration automatic.
- Native estimate: **33 min 50 sec**, **12.22 g** for the complete plate.

The [`preparation report`](2026-10-09-organizer-three-fits-petgf-left04-z004-mark2.print.json)
binds each source mesh to its native object, records the profile changes, archive
and G-code hashes, emitted layer heights and complete bead envelope. The minimum
usable bed margin is 103.286 mm. The
[`first/second-layer review`](first-second-layer-review.json) compares emitted
bead footprints: every second-layer wall segment overlaps the first-layer model
beads. No support paths are emitted. This is slice evidence, not a physical fit
or adhesion result.

## Launch

Mark2 accepted task **1323252957** at **2026-10-09 08:56:37 CDT**
(`2026-10-09T13:56:37.385732Z`), reporting `RUNNING`, 42 total layers, print
error 0 and no HMS faults. The matching submitted archive SHA-256 is
`394bd9b9d1d6f1fccccd17a7f411095f7e91a2500ab6abab40e4c2974e192afc`.
[`launch.json`](launch.json) holds the sender receipt and authorization;
[`preflight.json`](preflight.json) records both printers and startup spacing.

Mark1's existing back-top task 1320974719 was running in both observations
before this send. Its acceptance time is not present in the local sender
records; the earlier running observation establishes that its startup preceded
this launch by more than three minutes. Mark1 remains on that task.

## What the samples decide

Use the actual blue and both black quarter-inch tubes and the white 4 mm drain
tube. Thread each puck onto free tube ends. Hold the puck in one hand and each
tube in the other; deliberately push and pull each tube through. Select a fit
that moves by hand without a tool, counter bracing, visible kinking, flattening
or scoring. Check each tube separately: the three quarter-inch lines can differ
in actual diameter. No plug unions or magnets are needed.

For a candidate that feels adjustable, mark the tubes at its faces and place it
below the plate, washer and nut working area in the actual sleeved bundle. Let
the bundle hang, bend and reposition it, and perform the mounting sequence.
The marks should remain at the faces without deliberate tube adjustment, and
the mounting area should stay clear. Choose quarter-inch and drain fits
separately if different samples suit them. If none gives both hand adjustment
and retained formation, the next geometry depends on the observed failure;
these prints alone establish no force, wear or lifetime specification.
