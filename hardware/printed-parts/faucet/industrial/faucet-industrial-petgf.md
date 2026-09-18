# Industrial faucet PET-GF print project

[`faucet-industrial-petgf.3mf`](faucet-industrial-petgf.3mf) contains the Industrial
base, relaxed display cover and above-counter plate, with the shared faucet tip.
The four PET-GF parts occupy separate spaces on one plate for their brims and
automatic tree supports. Black and white use the same geometry.

| Position | Part | Rotation about the CAD X axis |
|---|---|---:|
| Left | Industrial shell base | −15° |
| Right rear | Shared faucet shell tip | −105° |
| Far right rear | Industrial display cover | +130° |
| Right front | Industrial above-counter plate | 0° |

The cover's broad planar bezel face lies on the bed. The plate rests on its
gasket face, with its locating pedestals up. The base's long straight neck is
15° from vertical. The shared tip retains its established print direction.
The Industrial gasket is a separate TPU part and is not included in this project.

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

The current Bambu Studio 02.08.02.61 slice completes without warnings. It
estimates **4 h 39 min 38 s and 130.51 g**. Actual extrusion bounds, including
supports and brims, leave at least **24.90 mm of shared-bed border** and
**26.99 mm between parts**.

## Support reading

The base has one bed-rooted support body and ten explicitly labelled
interface islands. The tip has one bed-rooted body, the cover has two and the
plate has three. No model-rooted bodies occur in this slice. Unlabelled contacts
on the tip and plate have unknown interface-island counts and unknown build-up
to first contact; an empty interface list does not mean they print unsupported.

| Piece / body | Root and build-up | Supported region and retained function |
|---|---|---|
| Base / tree-1 | Bed; first labelled interface at print Z2.60 mm after 2.40 mm build-up; body ends at Z62.60 mm | Seven labelled islands lie under the tilted counter-end face. Two reach the donor-arch cheeks, and one reaches the rear lever/tube transition. The mounting face, donor clearance and lever opening retain their working geometry. Remove through the bottom and donor/lever openings before installing hardware; inspect the small interior passages and rear contact. The exposed long neck has no support. |
| Shared tip / tree-1 | Bed; ends at print Z134.60 mm; contacts unlabelled | The tree spans the neck-joint end and open display-chassis interior. Exact contact boundaries require a physical reading. Preserve the joint engagement, tube and ribbon passages, retaining grooves and metal-foot supports during removal. |
| Cover / trees 1–2 | Bed; labelled interfaces begin at print Z14.84 mm after 14.64 mm build-up; bodies end at Z15.08 mm | One body reaches the underside of each broad retaining lip. The bezel lies on the bed. Remove supports through the open underside before loading the display, preserving both lip bearing faces. |
| Plate / trees 1–3 | Bed; end at print Z2.84 mm; contacts unlabelled | The three underside screw counterbores retain their flat factory-screw seats. Remove each support through its counterbore opening before assembly. |

These are measurements of this slice. Removal effort, trapped branches and
contact finish are observations from the physical print.

[`faucet-industrial-petgf.readiness.json`](faucet-industrial-petgf.readiness.json)
distinguishes a prepared project from a completed offline slice and support
audit. The preparation tool does not submit a print. Support removal, contact
finish, display fit and retention are checked on the physical test print.
