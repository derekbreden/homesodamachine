# Sculpted faucet PET-GF print project

[`faucet-petgf.3mf`](faucet-petgf.3mf) contains the Sculpted shell base, shared
shell tip, display cover and above-counter plate on one H2C plate. The matching
[native print archive](vent-print-readiness/faucet-black-z018-h2c/faucet-black-z018-h2c.gcode.3mf)
is prepared for Polymaker PET-GF and the left 0.4 mm nozzle.

| Position | Part | CAD X rotation |
| --- | --- | ---: |
| Left | Faucet shell base | −15° |
| Right rear | Faucet shell tip | −95° |
| Far right rear | Faucet display cover | −50° |
| Right front | Above-counter plate | 0° |

The tip's open 50° neck joint, bottom drain port and display pocket provide
support-removal access before tube and seal installation. The cover's visible
bezel faces up and its underside remains open. The plate rests on its gasket
face, with its locating pedestals up. The base's straight neck is 15° from
vertical. Display-cover acceptance remains scoped to the
[identified physical article](faucet-display-cover/physical-acceptance.json).

The saved process uses 0.24 mm layers, a 0.20 mm first layer, two walls and
15% grid infill. Three host/root modifiers retain six walls and 100% zigzag
infill around the M3 heat-set insert pilots. The
[emitted-deposition review](faucet-petgf.insert-beads.json) reads every complete
slab through those regions and retains pore and edge-slab diagnostics.
Installed brass is Ø4.6 mm; its supporting outer stock must extend at least
2 mm beyond that envelope. Native deposition establishes nominal geometry;
insert pullout and lifetime remain physical properties.

Nozzle temperatures are 265 °C first layer and 280 °C thereafter; the Textured
PEI plate is 80 °C. Cooling is 0–70%, off for the first three layers. Automatic
tree supports retain a 0.45 mm top gap, 0.30 mm bottom gap, 0.40 mm XY gap,
two top interface layers and 0.50 mm interface spacing. The H2C's +0.18 mm
0.4 mm trim emits `G29.1 Z0.16` after stock Textured PEI compensation.

After generating and reviewing the source meshes, prepare and review locally:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/prepare_vent_prints.py rigid
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_vent_prints.py supports
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_faucet_inserts.py sculpted
tools/cad-venv/bin/python hardware/printed-parts/faucet/review_lower_supports.py sculpted
```

Review the lower-support images and record their cleanup access as described in
the [print workflow](vent-print-readiness/README.md), then finalize:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/finalize_vent_prints.py rigid
```

The native slice estimates 4 h 37 min 27 s and 127.29 g using the saved profile
density. Its complete emitted model/support/brim envelope has 26.30 mm minimum
usable-bed clearance; separate part toolpaths have 37.67 mm minimum clearance.
The [readiness record](faucet-petgf.readiness.json) binds the current source,
project, native payload, reviews and cleanup procedure. Preparation never
connects to a printer.

| Part | Support removal |
| --- | --- |
| Base | Cut the tree into short fragments and remove through the counter-end, common rear tube opening, donor bay and lever opening. Clear all insert pilots and locating sockets; the flat ribbon must pass freely behind the F1-D-F2 bundle. |
| Tip | Release the tree through the joint, 12 × 22 mm bottom port and display pocket. Clear both gland grooves, seats and lips, then all dry tube/wire guides before inserting bungs. |
| Cover | Remove through the underside before fitting the display. Retain the broad wings and their lip-bearing surfaces. |
| Plate | Remove each counterbore support through its screw-head opening while retaining the screw seat. |

The [support audit](faucet-petgf.support-audit.json) counts connected support
bodies, including those without interface labels. The
[contact reading](faucet-petgf.support-faces.json) and
[cavity image](vent-print-readiness/faucet-black-z018-h2c/native-cavity-supports.png)
locate the emitted support paths. The
[lower-guide review](faucet-petgf.lower-supports.json) retains
[base sections](vent-print-readiness/faucet-black-z018-h2c/native-lower-support-sections.png)
for cleanup around the shared rear passage and pedestal sockets. Accessible geometry
does not establish physical release or deposited sealing finish. The
[factory seal sequence](asse-vent-seals/README.md) follows support cleanup.

The [complete print set](vent-print-readiness/README.md) also includes the
TPU bungs, counter gasket and insertion tool. Physical support removal, finish,
fit and retention observations belong in the [print log](faucet-shell/print-log.md).
