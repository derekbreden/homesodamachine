# Centered ASSE vent print files

The production set contains the two PET-GF faucet shell pieces, display cover,
above-counter plate, TPU countertop gasket, two TPU vent bungs and their PET-GF
perimeter insertion tool.
The customer receives the assembled faucet. The bungs isolate the shared vent
discharge cavity from the dry tube passages and display.
The [plate manifest](manifest.json) binds all five finalized projects, native
archives, reviews and estimates to their current sources and geometry approvals.

Regenerate the reviewed source STLs before preparing the plates:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/prepare_vent_prints.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_vent_prints.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_faucet_inserts.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_gasket_beads.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_lower_supports.py
```

Inspect the lower-support images for each rigid plate before finalization.
Record the open lower passage and fragment-removal route in its
`geometry_access_review`, following the current
[Sculpted](../faucet-petgf.lower-supports.json) and
[Industrial](../industrial/faucet-industrial-petgf.lower-supports.json) records.
The lower-support reviewer writes an unapproved location report; finalization
requires that access review.

```sh
tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/asse-vent-seals/check_tool_bearing.py \
  --last-model-layer-z 80.84
tools/cad-venv/bin/python hardware/printed-parts/faucet/finalize_vent_prints.py
```

Preparation uses the installed Bambu Studio locally. It exports native G-code
archives and records their checksums, source meshes, exact placements, emitted
process settings and support paths. It never connects to a printer.
Finalization verifies the current 159-reading whole-faucet report and all of its
source bindings. Industrial plates also require the current 26-reading geometry
and 43-reading display-cover reports, including their saved artifact bindings.
Finalizing all five plates writes the manifest.

| Plate | Editable project | Native print archive |
| --- | --- | --- |
| Rigid faucet; H2C left 0.4 mm | [`faucet-petgf.3mf`](../faucet-petgf.3mf) | [`faucet-black-z018-h2c.gcode.3mf`](faucet-black-z018-h2c/faucet-black-z018-h2c.gcode.3mf) |
| Industrial rigid faucet; H2C left 0.4 mm | [`faucet-industrial-petgf.3mf`](../industrial/faucet-industrial-petgf.3mf) | [`faucet-industrial-black-z018-h2c.gcode.3mf`](faucet-industrial-black-z018-h2c/faucet-industrial-black-z018-h2c.gcode.3mf) |
| Two vent bungs and counter gasket; H2C right standard 0.6 mm | [`vent-bungs-tpu85a.3mf`](../asse-vent-seals/vent-bungs-tpu85a.3mf) | [`vent-bungs-tpu85a-h2c.gcode.3mf`](vent-bungs-tpu85a-h2c/vent-bungs-tpu85a-h2c.gcode.3mf) |
| Two vent bungs and Industrial counter gasket; H2C right standard 0.6 mm | [`vent-bungs-industrial-tpu85a.3mf`](../asse-vent-seals/vent-bungs-industrial-tpu85a.3mf) | [`vent-bungs-industrial-tpu85a-h2c.gcode.3mf`](vent-bungs-industrial-tpu85a-h2c/vent-bungs-industrial-tpu85a-h2c.gcode.3mf) |
| Perimeter insertion tool; H2C left 0.4 mm | [`vent-seal-tool-petgf.3mf`](../asse-vent-seals/vent-seal-tool-petgf.3mf) | [`vent-seal-tool-petgf-z018-h2c.gcode.3mf`](vent-seal-tool-petgf-z018-h2c/vent-seal-tool-petgf-z018-h2c.gcode.3mf) |

| Plate | Native time estimate | Saved-density mass estimate | Complete emitted bead margin |
| --- | ---: | ---: | ---: |
| Sculpted rigid | 4 h 42 min 43 s | 127.54 g | 26.30 mm |
| Industrial rigid | 4 h 56 min 18 s | 132.67 g | 25.17 mm |
| Sculpted bungs/gasket | 1 h 3 min 14 s | 8.37 g | 85.23 mm |
| Industrial bungs/gasket | 1 h 3 min 54 s | 8.47 g | 85.22 mm |
| Insertion tool | 24 min 29 s | 7.85 g | 124.40 mm |

PET-GF uses the saved Polymaker material profile, 0.24 mm layers and a 0.20 mm
first layer. The H2C 0.4 mm plates use its +0.18 mm user trim, emitted as
`G29.1 Z0.16` with Textured PEI compensation. Supports use the saved mature
PET-GF process. Sealing seats and supported internal faces print at the normal
layer height. Accepted display-cover fit and retention remain scoped to the
[identified physical article](../faucet-display-cover/physical-acceptance.json).
Each base has three local six-wall, 100% zigzag regions around its insert hosts
and roots. The actual emitted host/cap stock must have at least 98% nominal
bead coverage and at least 2 mm of supporting outer stock from the installed
Ø4.6 mm brass. The records retain enclosed pores and thin edge-slab readings;
their geometry does not measure insert pullout or lifetime.

The bungs print flange-down with Bambu TPU85A, 100% infill, Arachne walls and no
supports. They use 0.24 mm layers and a 0.20 mm first layer. The 0.6 mm profile
keeps its stock plate compensation; the 0.4 mm trim does not transfer to it.
[Bambu's material table](https://us.store.bambulab.com/products/tpu-85a-tpu-90a/)
supports standard 0.6 and 0.8 mm nozzles for TPU85A. The
[H2C manual](https://csm.bblcdn.com/hub/eff78da43720461787dc8bbe5fa0372d.pdf),
pages 122 and 125–126, specifies right-hotend printing and direct toolhead feeding
for this soft material. Prepare the printer with the matching nozzle, dried
filament and feed path before starting that archive.

The native records check complete layer model, support and brim bead bounds,
with at least 20 mm of usable-bed margin. Small bung and tool plates retain an
80 mm margin. Their files are prepared without a printer launch.

Every bung model layer has separate closed bore contours and connected local
inter-bore material paths. The wire contact-core clear diameters are
0.953–0.994 mm; the largest circumscribed wire void is 1.045 mm. Native beads
contain enclosed inter-road pores, including a 0.160 mm straight-span gap in
one upstream web. The [bead review](../asse-vent-seals/vent-bungs-tpu85a.bead-review.json)
records their size and remaining material paths; this is not measured liquid
containment. Both style TPU plates print without supports.
The gasket review checks every native model layer against its source section:
functional openings remain enclosed and separate, and one connected material
pad retains at least 98% nominal coverage of the compensated broad core.
It records enclosed pores and material islands; assembled spill containment
depends on the deposited gasket and clamp compression.

Before assembly, release the tip's tree through the open joint, bottom port
and display pocket; clear both flange grooves, gland lips, body seats and
all tube/wire guides. Remove base supports through the counter-end, donor bay
and lever opening, cover supports through the underside, and each plate
counterbore body through its screw-head opening. The retained lower-support
views locate native trees around the cable route and pedestal sockets; they
receive a geometry/access review before finalization, with its removal route
bound into the plate record. The
[factory sequence](../asse-vent-seals/README.md) follows cleanup.
The insertion tool has a 19 mm side opening for support removal. Its native
slice retains 99.04% of the exact annular bearing area, with the tiny omitted
slot tips outside the necessary load path. Preserve that bearing and the
curved outer sleeve during cleanup.

The existing [accepted lever](../lever-replica/physical-acceptance.json) uses
its [black H2C print archive](../lever-replica/lever-black-petgf-z018-h2c.gcode.3mf).

Native toolpaths establish commanded geometry. Support removal, deposited
surface quality, bung seating/compression and liquid containment belong to the
finished physical assembly. The assembly instructions retain those factory
inspection steps. The print records do not establish ASSE vent capacity,
pressure qualification or consumer certification.
