# Tube insertion tool prints

The tool uses seven printed pieces: five PET-GF pieces and two identical
TPU 85A grip liners. Two complete BESSEY GSCC2.506 screw clamps supply its
actuation and metal reaction frames. The
[assembly and use guide](../../../tube-insertion-guide/tube-insertion-guide.pdf)
identifies each piece and shows the sleeve-first faucet sequence.

The liners are solid blocks with their half-round gripping channels already
formed. Each seats directly in a rigid jaw pocket. Print the tube axis
**vertically**, giving the circular contact profile the same XY perimeter on
every layer. The print is 28 mm tall, with an 8 × 20 mm end footprint,
4.125 mm minimum backing and a Ø7.75 mm contact channel. Assembly requires
no bending or wrapping of TPU.

## Native projects

| Plate | Pieces | Project | Prepared slice |
| --- | --- | --- | --- |
| Mark1 / H2C, rigid base | A base | [Base project](ready/tube-insertion-rigid-base-h2c.3mf) | [Base G-code archive](ready/tube-insertion-rigid-base-h2c.gcode.3mf) |
| Mark1 / H2C, rigid parts | B guided carrier, D lower jaw, E upper jaw, G cap-support puck | [Rigid parts project](ready/tube-insertion-rigid-parts-h2c.3mf) | [Rigid parts G-code archive](ready/tube-insertion-rigid-parts-h2c.gcode.3mf) |
| Mark1 / H2C, soft grip | F liner × 2 | [TPU project](ready/tube-insertion-tpu-85a-mark1.3mf) | [TPU G-code archive](ready/tube-insertion-tpu-85a-mark1.gcode.3mf) |

Projects retain the part poses and bed positions in [print-layout.json](print-layout.json).
The base has its own plate; the smaller rigid pieces share a centered plate.
The two TPU pieces sit near the center of their plate, with a 2 mm model gap. The matching
`.print.json` files bind each project to its source meshes and settings;
`.readiness.json` files record the actual slice, bead envelope, supports and
emitted Z trim. The [Mark1 liner launch](prints/2026-10-12-liners-d775-mark1/launch.json)
records accepted task 1334257829; its physical grip result is pending.

## Slice review

| Plate | Estimated time | Estimated filament | Layers | Minimum bead margin |
| --- | ---: | ---: | ---: | ---: |
| Rigid base | 11 h 55 min | 829.2 g | 225 | 26.02 mm |
| Rigid parts | 4 h 19 min | 241.6 g | 63 | 46.21 mm |
| TPU liners | 1 h 09 min | 9.4 g | 155 | 143.29 mm |

These are Bambu Studio 02.08.02.61 estimates using the saved material densities.
The margins include emitted model, support and brim beads. All three archives
have matching embedded G-code digests and the intended nozzle and Z-trim mapping.

The native first and second layers retain overlapping perimeter beads,
including the carrier's broad countersunk mounting toes. The TPU channel
remains an open semicircle through its upright layers, with solid backing
and no support. The base generates
[no support](ready/tube-insertion-rigid-base-h2c.support-audit.json).

The rigid-parts plate generates
[four bed-rooted support bodies](ready/tube-insertion-rigid-parts-h2c.support-audit.json),
all in lower jaw D. Two occupy its underside locator-key pockets, with
interfaces at print Z=2.12-2.60 mm beneath the 3.1 mm pocket roofs. Two occupy
the side-entry carrier nut pockets, with interfaces at Z=12.44-12.68 mm
beneath the 13.2 mm roofs. Automatic Tree/default settings remain enabled.
Remove these supports through the underside pockets and lateral nut entries
before joining D to B or installing the nuts. Native deposition and access
are reviewed; physical removal effort is unmeasured.

## Material and machine mapping

Rigid pieces use black Polymaker PET-GF on **Mark1 / H2C's left hardened
0.4 mm nozzle**. The [shared PET-GF profile](../../petgf.3mf) supplies the
temperature, flow, speed and machine settings. This tool uses six walls,
100% zigzag infill, a 0.20 mm first layer and 0.24 mm normal layers.
Automatic Tree support with Bambu's default style remains enabled. Requested
user Z trim is +0.18 mm; textured PEI emits `G29.1 Z0.16` after its reset.

The liners use **TPU 85A on Mark1's right fixed 0.6 mm nozzle**, external
spool 255. The [compact Mark1 profile](prints/2026-10-12-tpu-liners-close-z000-mark1/2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.3mf)
supplies the complete TPU recipe: 225 °C nozzle, 35 °C bed, 2.2 mm³/s
maximum flow, two Arachne walls, 100% zigzag infill, three top/bottom layers,
0.30 mm first layer and 0.18 mm normal layers. Supports are disabled for
the constant upright profile; automatic brim remains enabled. Requested
user Z trim is 0.00 mm; textured PEI emits `G29.1 Z-0.02` after its reset.

The thin wet-path thimble is a separate, unchanged faucet part. Use its
[current print project](../../prototype-gaskets-2026-10-08/projects/2026-10-08-touch-flo-tube-gasket-tpu85a-right06-mark2.3mf)
when a new sealing sleeve is needed; its process is independent of the tool's
thick solid liners.

At submission, use the corresponding printer and resolve its actual filament
mapping. [Printer startup spacing](../../../../tools/bambu-printers.md#printer-startup-spacing)
requires three minutes between accepted starts on the shared circuit.

## Manual preparation

Generate the geometry, then prepare and slice the three plates into an empty
scratch directory:

```sh
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/tube_insertion.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/prepare_print.py \
  --slice-output .cache/tube-insertion-native
```

The script runs only when invoked by hand. It does not launch a printer or
add a check to the machine build, edit or commit path. Native slice review
establishes the prepared toolpaths; first physical printing and tube grip
performance remain unqualified.
