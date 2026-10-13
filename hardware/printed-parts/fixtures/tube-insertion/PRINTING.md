# Centred tube-grip prints

Print replacement D and E jaws and two F liners. Reuse the existing base,
carrier, support puck and stocked metal hardware. The base and carrier
STLs match the identified existing geometry. The
[assembly guide](../../../tube-insertion-guide/tube-insertion-guide.pdf)
shows their assembly and the sleeve-first sequence.

The two closure screws, liner length and crossbar share X22. Each liner
retains its Ø7.75 mm half-round channel and adds 1 mm to the flat backing.
Its 9 mm thickness stands 1 mm proud of the 8 mm pocket. Print the tube
axis vertically, giving a 9×20 mm end footprint and 28 mm height. Minimum
TPU backing is 5.125 mm.

## Native projects

| Plate | Pieces | Project | Exact slice |
| --- | --- | --- | --- |
| Mark1, PET-GF | D lower jaw, E upper jaw | [Jaw project](ready/tube-insertion-centered-grip-petgf-left04-z018-mark1.3mf) | [Jaw slice](ready/tube-insertion-centered-grip-petgf-left04-z018-mark1.gcode.3mf) |
| Mark2, PET-GF | D lower jaw, E upper jaw | [Jaw project](ready/tube-insertion-centered-grip-petgf-left04-z004-mark2.3mf) | [Jaw slice](ready/tube-insertion-centered-grip-petgf-left04-z004-mark2.gcode.3mf) |
| Mark1, TPU 85A | F liner × 2 | [Liner project](ready/tube-insertion-centered-liners-tpu85a-right06-z018-mark1.3mf) | [Liner slice](ready/tube-insertion-centered-liners-tpu85a-right06-z018-mark1.gcode.3mf) |

The jaw plate contains only the two replacement halves. The TPU pieces
have a 2 mm model gap. The corresponding `.print.json` and `.readiness.json`
files bind the meshes, settings, native material process and emitted trim.
The [Mark1 jaw launch](prints/2026-10-13-centered-grip-mark1/README.md)
records task 1335878319 with software completion at 63/63 layers. The
[Mark1 insert launch](prints/2026-10-13-centered-liners-mark1/README.md)
records accepted task 1336534713 and preserves its exact slice. The Mark2
jaw plate has no printer submission. The
[physical acceptance record](physical-acceptance.json) identifies successful
insertion with the Mark1 jaws and inserts: the handle starts insertion well,
and the full fixture makes the final press very easy.

| Plate | Estimated time | Estimated filament | Layers | Minimum full-bead margin |
| --- | ---: | ---: | ---: | ---: |
| PET-GF jaws | 2 h 33 min | 126.7 g | 63 | 100.25 mm |
| TPU liners | 1 h 18 min | 10.7 g | 155 | 142.22 mm |

The estimates use Bambu Studio 02.08.02.61 and the saved material densities.
The emitted G-code and archive checksums match their reviews. Native
slicing establishes the toolpaths, not printed strength or tube grip.

## Material and supports

The jaws use black Polymaker PET-GF on either printer's left hardened
0.4 mm nozzle, external spool 254. The shared PET-GF recipe supplies temperature and flow;
the grip uses six walls, 100% zig-zag infill, a 0.20 mm first layer and
0.24 mm normal layers. Automatic Tree/default support is retained.
Standard Mark2 +0.04 mm user trim emits `G29.1 Z0.02` after the reset.
Standard Mark1 +0.18 mm user trim emits `G29.1 Z0.16` after the reset.
The Mark1 and Mark2 slices have identical executable paths apart from
those trim commands, with each archive matching its external spool colour.

The [Mark1 native support review](ready/tube-insertion-centered-grip-petgf-left04-z018-mark1.support-audit.json)
records the emitted supports. Clear D's underside key pockets and side-entry
nut pockets before assembling the carrier joint. Physical support-removal
effort remains unmeasured.

The liners use black TPU 85A on Mark1's right fixed 0.6 mm nozzle and
external spool 255: 225 °C nozzle, 35 °C bed, 2.2 mm³/s maximum flow, two
Arachne walls, 100% zig-zag infill, three top/bottom layers, a 0.30 mm first
layer and 0.18 mm normal layers. The upright profile needs no supports.
Automatic brim is retained. Standard Mark1 +0.18 mm user trim emits
`G29.1 Z0.16` after the reset. The liner restart amount uses the saved
recipe; the separately prepared restart experiment has no grip qualification.

The [physical failure record](prints/2026-10-12-liners-d775-mark1/grip-failure.json)
identifies grip failure at rigid closure and the 8.5 mm CAD screw offset
for that trial. The [centred grip review](centered-grip-review.json)
establishes alignment and the added 2 mm total closure reserve. The
[physical acceptance](physical-acceptance.json) records functional grip and
successful insertion with these identified replacement parts. Numerical
forces and endurance are unmeasured.

## Manual preparation

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/tube_insertion.py
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/prepare_print.py --plate centered-grip-mark1 --slice-output .cache/centered-grip-next
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/prepare_print.py --plate centered-grip-mark2 --slice-output .cache/centered-grip-next
tools/cad-venv/bin/python hardware/printed-parts/fixtures/tube-insertion/prepare_print.py --plate centered-liners-mark1 --slice-output .cache/centered-grip-next
```

Use empty slice directories. These manual operations submit no print and
join no build, hook or watcher. At submission, use each printer's own
filament mapping and the three-minute shared-circuit startup separation.
