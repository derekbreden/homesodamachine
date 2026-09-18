# Industrial faucet PET-GF print project

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains the Industrial
base, relaxed display cover and above-counter plate, with the shared faucet tip.
The four PET-GF parts occupy separate spaces on one plate for their brims and
automatic tree supports. Black and white use the same geometry.

| Position | Part | Rotation about the CAD X axis |
|---|---|---:|
| Left | Industrial shell base | −15° |
| Right rear | Shared faucet shell tip | +40° |
| Far right rear | Industrial display cover | +40° |
| Right front | Industrial above-counter plate | 0° |

The tip stands on its dispense face and the cover on its front wall. Their
groove and lip bearing faces print vertically. The plate rests on its gasket
face, with its locating pedestals up. The base's long straight neck is 15°
from vertical. The Industrial gasket is a separate TPU print.

The project copies the complete project and filament settings from the saved
[Sculpted PET-GF project](../faucet-petgf.3mf): Bambu Lab H2C with 0.4 mm nozzles,
the `0.24mm PET-GF faucet` process and `Polymaker PET-GF @BBL H2C` filament.
The copied settings include two wall loops, 15% grid infill, a 0.45 mm support
top gap, 0–70% part cooling, 265/280 °C nozzle temperatures and an 80 °C textured
plate. The writer preserves the source project and its print, support and
readiness reports byte-for-byte.

After generating the Industrial STLs:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/industrial/prepare_print_project.py
```

The wrapper uses the shared faucet project writer. It checks each source STL
is one closed, consistently oriented volume, embeds its exact mesh, and verifies
bed placement and printer height. [`faucet-industrial-petgf.print.json`](faucet-industrial-petgf.print.json)
records the source, settings and project hashes, bed transforms and agreement
between the embedded meshes and source STLs.

For a local Bambu Studio slice, provide an empty output directory:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/industrial/prepare_print_project.py \
  --slice-output /tmp/faucet-industrial-petgf-slice
```

This runs the installed Bambu Studio CLI without a printer connection. The
resulting [`faucet-industrial-petgf.support-audit.json`](faucet-industrial-petgf.support-audit.json)
records connected support bodies, separate labelled interface islands, bed or
model roots and build-up heights. It also checks actual extrusion bounds,
including supports and brims, for at least 15 mm of shared-bed border and 10 mm
between parts. Unlabelled support contacts remain explicitly unknown.
Slicer time and grams are estimates; grams use the preserved profile's
1.29 g/cm³ density, not a measured PET-GF part mass.

The current four-part project is prepared but has not been sliced. Its
[readiness record](faucet-industrial-petgf.readiness.json) identifies that state.
The retained support audit belongs to project SHA256
`b4d55193f1fb2852c2f15e7b61f66bd000e3eb16a0b8b3526710e8cef7c508be`;
its tip and cover readings do not apply to the current geometry and poses.
The preparation tool does not submit a print. Support removal, contact finish,
display fit and retention are checked on the physical print.
