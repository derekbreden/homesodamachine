# Industrial faucet PET-GF print project

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains the Industrial
base, relaxed display cover and above-counter plate, with the shared faucet tip.
The four PET-GF parts occupy separate spaces on one plate for their brims and
automatic tree supports. Black and white use the same geometry.

| Position | Part | Rotation about the CAD X axis |
|---|---|---:|
| Left | Industrial shell base | −15° |
| Right rear | Shared faucet shell tip | −105° |
| Far right rear | Industrial display cover | −50° |
| Right front | Industrial above-counter plate | 0° |

The tip rests toward its hidden neck-joint end. The cover's visible bezel
faces upward; supports are accessible through its open underside before
installing the display. The plate rests on its gasket face, with its locating
pedestals up. The base's long straight neck is 15° from vertical. The Industrial
gasket is a separate TPU print.

The shared tip and Industrial cover use 1.25 mm inward preload per wing,
1.20 mm groove engagement, 3.00 mm lips, 0.48 mm roof clearance, 0.30 mm
end clearance and 0.25 mm inner-edge relief. The [display-cover reading](display-cover-check.json)
checks the Industrial cover against the shared tip, display and tubes.

The project copies the complete project and filament settings from the saved
[Sculpted PET-GF project](../faucet-petgf.3mf): Bambu Lab H2C with 0.4 mm nozzles,
the `0.24mm PET-GF faucet` process and `Polymaker PET-GF @BBL H2C` filament.
The copied settings include two wall loops, 15% grid infill, a 0.45 mm support
top gap, 0–70% part cooling, 265/280 °C nozzle temperatures and an 80 °C textured
plate. Layers are 0.24 mm with a 0.20 mm first layer. The requested
**+0.18 mm Z trim** gives `G29.1 Z0.16` with the stock Textured PEI correction.
Black PET-GF uses the left external spool's existing PET-CF mapping; the right
nozzle is unused. The writer preserves the source project and its print,
support and readiness reports byte-for-byte.

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

The current native slice estimates **4 h 45 min 12 s and 131.23 g**. Its
toolpaths have 22.38 mm minimum bed margin and 26.24 mm separation.

| Part | Support contact and removal access |
|---|---|
| Industrial base | One bed-rooted body with nine labelled interface islands at the counter-end and fastener pockets, donor arches, lever roof and internal tube transition. Remove through the counter-end and donor/lever openings. |
| Shared tip | One bed-rooted body with unlabelled interfaces at the joint, internal passages and display pocket. Sampled outer-skin proximity lies within 1.36 mm of the joint seam. Remove through the joint and display opening. |
| Industrial cover | One bed-rooted body with two labelled islands under the hidden inner bezel and front/rear neck-clearance surfaces. No sampled visible outer-bezel or lip-bearing contact. Remove through the open underside. |
| Industrial plate | Three bed-rooted bodies inside the screw counterbores, reaching the screw seats. Remove through each counterbore. |

The [contact reading](faucet-industrial-petgf.support-faces.json) includes
unlabelled support paths. Its bounded samples locate surfaces near the
supports; physical removal and finish are established by the print.

The [readiness record](faucet-industrial-petgf.readiness.json) identifies the
matching project, native slice, support reading and printer submission.
The [native validation](faucet-industrial-petgf.native-validation.json)
records the emitted settings and Z trim against the successful Sculpted job.
The preparation tool does not submit a print. Support removal, contact finish,
display fit and retention are recorded in the [print log](print-log.md).
