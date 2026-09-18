# Sculpted faucet PET-GF print project

[`faucet-petgf.3mf`](faucet-petgf.3mf) contains the shell base, shell tip,
display cover and above-counter plate on one plate. The current Mark2 job
uses white Polymaker PET-GF with a left 0.4 mm nozzle.

| Position | Part | CAD X rotation |
|---|---|---:|
| Left | Faucet shell base | −15° |
| Right rear | Faucet shell tip | −105° |
| Far right rear | Faucet display cover | −50° |
| Right front | Above-counter plate | 0° |

The tip rests toward its hidden neck-joint end. The cover's visible bezel
faces upward; its open underside provides access for support removal before
installing the display. The above-counter plate rests on its gasket face,
with its locating pedestals up. The base's long straight neck is 15° from
vertical. The cover retains 1.25 mm inward preload per wing and the mating
groove and lip geometry recorded in the successful complete-part print.

## Settings

The process uses **0.24 mm layers**, a **0.20 mm first layer**, two walls and
15% grid infill. Nozzle temperatures are 265 °C for the first layer and
280 °C thereafter, with an 80 °C Textured PEI plate. Part cooling is 0–70%,
off for the first three layers. Automatic tree supports use a 0.45 mm top
gap, 0.30 mm bottom gap, 0.40 mm XY gap, two top interface layers and 0.50 mm
interface spacing. The external white PET-GF uses the printer's existing
PET-CF material mapping; the right nozzle is unused.

**+0.18 mm Z trim** is added to the stock plate compensation. On Textured
PEI with this 0.4 mm nozzle, the startup code clears the trim with
`G29.1 Z0`, then applies `G29.1 Z0.16`. The printer profile is
`Bambu Lab H2C 0.4 Standard +0.18 Z trim`.

Refresh the four meshes while retaining the saved project settings:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/refresh_print_project.py \
  --settings-from hardware/printed-parts/faucet/faucet-petgf.3mf --z-trim 0.18
```

The project opens in Bambu Studio for slicing. The writer also accepts
`--slice-output /tmp/faucet-petgf-slice` for an offline toolpath/support
reading; it does not contact a printer.

## Slice and support removal

The native slice estimates **4 h 30 min 50 s and 126.31 g** at the saved
profile density. Toolpaths have 23.12 mm minimum bed margin and 27.17 mm
minimum separation between parts.

| Part | Support contact and removal access |
|---|---|
| Base | One bed-rooted body and three small model-rooted patches; 23 labelled interface islands. Remove through the counter-end and donor/lever openings. |
| Tip | One bed-rooted body, with unlabelled interfaces at the joint, internal passages and display pocket. Sampled outer-skin proximity is confined to 1.36 mm from the joint seam. Remove through the joint and display opening. |
| Cover | One bed-rooted body and two labelled interface islands under the inner bezel, bridge and opening edges. The sampled visible outer bezel and lip bearing faces are clear. Remove through the open underside. |
| Above-counter plate | Three bed-rooted bodies inside the screw counterbores, reaching the screw seats. Remove through each counterbore. |

The [contact reading](faucet-petgf.support-faces.json) includes support paths
without explicit interface labels. Its bounded samples locate surfaces near
the supports; physical removal and finish are established by the print.

## Records

The [print report](faucet-petgf.print.json) records the exact source STL
hashes, embedded-mesh agreement, bed transforms and intentional profile
changes. The [native validation](faucet-petgf.native-validation.json) records
the exported archive and G-code hashes, emitted settings and Z-trim commands.
The [readiness record](faucet-petgf.readiness.json) identifies the matching
slice, support reading and printer submission.

Support bodies, their roots, build-up and contact islands are in the
[support audit](faucet-petgf.support-audit.json). Physical support removal,
finish and fit observations are recorded in the [print log](faucet-shell/print-log.md).
