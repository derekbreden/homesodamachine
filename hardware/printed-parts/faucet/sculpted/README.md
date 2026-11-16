# Complete Sculpted faucet

The [faucet plate's selections](../../../../tools/hsm/print-prep/faucet-plate.json) start from
the recorded Industrial printing settings and apply the Sculpted finish and supports. The
complete PET-GF plate contains the Sculpted base, tip, display cover,
matching above-counter plate and side-down lever replica. TPU pieces and the
umbilical organizer are separate prints.

The [editable project](../faucet-petgf.3mf)
targets Mark2's abrasive left nozzle and black PET-GF on the glued Engineering
Plate the [plate's selections](../../../../tools/hsm/print-prep/faucet-plate.json) name.
Its first layer stands the selections' bed trim above Bambu's own plate compensation, in
place of the [PET-GF trim](../../z-trim.md) that belongs to textured PEI, with the left
external spool assigned manually at project and plate scope.

## Layer schedule and finish

The first bed layer is 0.20 mm. Every subsequent nominal course is 0.24 mm
on the base, cover, mounting plate and lever; the tip's mating courses come from a donor
sliced alone in finer bands. There are no Industrial shoulder fine-layer bands and no
separate eight-layer starting override. Bridge and overhang bead-height
annotations describe their extrusion cross-sections, not additional fine
courses.

| Parts | Seam position | Ordinary gap | Scarf |
| --- | --- | --- | --- |
| Base, shared tip | Back | [Shell gap](../../../../tools/hsm/print-prep/faucet-plate.json) | A2 |
| Mounting plate | Back | [Mounting plate gap](../../../../tools/hsm/print-prep/faucet-plate.json) | A2 |
| Cover, lever | Aligned | 15% | Off |

Rear seam enforcement follows the entire base silhouette in its build pose
and the shared tip's curved outer meridian. The preparer paints the cover seam
on the same lateral center plane wherever its rear wall crosses it. Wipe is off.
The base uses Arachne with an infill-only solid foot; its reinforcement modifier
inherits ordinary wall settings. The other rigid parts use Classic.

The process retains two ordinary walls, 15% gyroid infill, 15% infill/wall
overlap, 265°C first-layer and 280°C subsequent nozzle temperatures, and an
80°C bed. The [localized PET-GF cooling policy](../../cooling/README.md) keeps ordinary
part cooling off. After three fan-off bed courses, bridges and wall paths
meeting the 50% overhang threshold receive 70%; fan-always-on, fan pre-start
and auxiliary part cooling are off. Bridge flow is 125%, bridges
are 15 mm/s, and overhang limits retain the selected 10/15 mm/s values.
Ordinary supported-wall and infill speeds retain the black print's settings.
The tip's model paths by its dispense face take the same part cooling, from the
face back to just short of the lip grooves on both sides. The
[tip-end surface record](https://github.com/derekbreden/homesodamachine/blob/ffe670b3c4a83a970d2e52dd81c75eddb7f12522/hardware/printed-parts/faucet/sculpted/prints/2026-11-12-wing-end-relief-mark1/physical-result/tip-end-surface.json)
shows the band and reads the photographed plate's motion over it.

## Supports and poses

| Part | CAD X rotation | Support treatment |
| --- | ---: | --- |
| Sculpted base | −15° | Its foundation prints first: a removable scaffold and roof under the inclined mounting face, then the foot's courses cut from the base's own sections, with a plug rising in each insert socket and a deck in the bore. The level base courses start on the foot. Each mounting insert recess keeps tree support out. |
| Shared tip | −90° | Its mating courses come from a donor warped to flatten the shoulder, sliced alone with the support regions its warp gives and laid back onto the real shoulder. The inner dispense face's support is painted without a contact band, with an outlet keepout. A removable disc anchors the hidden root. |
| Sculpted cover | −50° | Saved automatic supports |
| Matching plate | 0° | Removable screw-seat rings stand under the counterbores. Bridge the screw counterbore shoulders and keep the shank passages open. |
| Side-down lever | 0° of print-oriented STL | Saved automatic supports |

The base's foundation prints before the rest of the plate, as on the
[restored short-foundation plate](prints/2026-11-14-seven-courses-restored-mark2/README.md).
The base prints without a brim. The cover prints on its flat lower lands with support
accessible through its open underside. The side-down lever bridges its
channel and uses accessible support at the attachment relief.
Ordinary sparse infill follows the shared PET-GF profile.

## Preparation and evidence

[`faucet-plate`](../../../../tools/hsm/print-prep/src/bin/faucet_plate.rs) prepares each style's
plate from current STLs; `faucet-plate sculpted OUT_DIR --production` makes the Sculpted product
plate, with its editable project at [faucet-petgf.3mf](../faucet-petgf.3mf). It runs
[prepare_print_project.rs](../prepare_print_project.rs), the `faucet-print-project` program, for
the plate's projects: the editable plate with the actual base, the slicer's plate with the base
filled under its mounting face, and the warped donor tip, sliced alone. The
[foundation stage](../../../../tools/hsm/print-prep/faucet-underside/README.md) lays the filled
space and the foot in the plate's own paths. Pass `--printer Mark1` and `--filament-colour`
with the loaded spool's colour to prepare a Mark1 plate.

The [Mark1 support and fit trial](https://github.com/derekbreden/homesodamachine/blob/7ebe4a45b0fd8064118e95f2cc1445c5ee643722/hardware/printed-parts/faucet/sculpted/prints/2026-11-11-support-and-fit-mark1/physical-result/physical-result.json)
records the base section's one-piece support release, the tip cleanup and the
cover seating on one wing. Its
[slice review](https://github.com/derekbreden/homesodamachine/blob/7ebe4a45b0fd8064118e95f2cc1445c5ee643722/hardware/printed-parts/faucet/sculpted/prints/2026-11-11-support-and-fit-mark1/support-review.json)
binds the seam gaps, exterior wall paths, shoulder support and nose clearance
to the submitted toolpath.

The Sculpted tip's two lip grooves are its only relief for the display cover. Their aft ends
stand closer to the lips than their fore ends, so the snapped cover rests toward the tube exit.
The cover's sides
bear on the groove roots and clear the rest of the neck when seated, as the
[cover's geometry](../faucet-display-cover/README.md#geometry) describes. The
[wing contact record](https://github.com/derekbreden/homesodamachine/blob/2ac8b452d916cb323d39cce42306069da7a25f91/hardware/printed-parts/faucet/sculpted/prints/2026-11-12-wing-end-relief-mark1/physical-result/physical-result.json)
locates where a rigidly leaned cover's wing ends bore on the tip instead. The
[bowed cover's fit record](https://github.com/derekbreden/homesodamachine/blob/2ec8379a49dab4833c363c0129f5298c7435f70f/hardware/printed-parts/faucet/sculpted/prints/2026-11-12-bowed-cover-tip-end-cooling-mark2/physical-result/physical-result.json)
holds Derek's approval of the bowed cover on this tip, with its aft tips touching the neck and
its front edge lying on the tip for part of its run. The cover's ends are bowed by what they
spring back for both; its fit remains a print result.

[review_print.py](https://github.com/derekbreden/homesodamachine/blob/306268f870/hardware/printed-parts/faucet/sculpted/review_print.py) (in Git at `306268f870`) reads the native G-code's nominal courses,
filament assignment, cooling, speed commands, complete bead footprint and
whole-height seam paths. It packages a separate print-only archive with
unchanged G-code bytes. It is a manual reader, not a build step.

The [native review](prints/2026-10-17-localized-cooling-display-clearance-mark2/native-review.json)
and per-part seam CSVs bind the submitted commands. Physical white Sculpted
finish, cleanup and fit remain a result of this complete print.

The [current print report](../faucet-petgf.print.json) binds the meshes and
recipe for the product plate, and [its record](../faucet-petgf.plate.json) its print-only
archive, kept on this Mac at `production/faucet-petgf.gcode.3mf`. The
[Mark2 matched shoulder trial](prints/2026-11-14-matched-shoulder-mark2/README.md) interleaves
the five parts and carries the foot's slope into the shaft. The base's exterior
walls follow continuous laps with their seam on the rear meridian. The tip builds
from its male plug into whole courses that match the mating angle and the
support interface, then eases to level below the dispense nose. The plate
includes the flat dispense-face seam with rounded
ends and removable mounting-plate counterbore rings.
The [Mark2 steady base wall plate](https://github.com/derekbreden/homesodamachine/blob/04468f9f27ddfa60e45037fc90ff2d98aa3a159a/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-steady-base-wall-mark2/README.md)
carries the matched shoulder and caps the Sculpted base's ordinary exterior
speed across whole laps for an even rear-wall finish.
The [Mark2 extended cover plate](https://github.com/derekbredensteiner/homesodamachine/blob/77742d1058fd2b9c92287fa8edf0dbb3c4737fc9/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-aft-cover-mark2/README.md)
pairs that base finish with the longer rear cover over both cavity corners.
The [Mark2 restored short-foundation plate](prints/2026-11-14-seven-courses-restored-mark2/README.md)
prints the mounting face and visible shoulder on inclined interfaces, then
uses the archived level wall and rear scarf recipe above each foundation.

`faucet-plate sculpted OUT_DIR` prepares that plate, the product plate, from the checkout: its meshes
and the plate's selections in [`faucet-plate.json`](../../../../tools/hsm/print-prep/faucet-plate.json). The base is filled
under its mounting face for the slice and laid on its sloped foundation from its own mesh; the
tip's mating courses come from a warped donor tip, sliced alone and laid back onto the real
shoulder. The plate's slice runs the standing slice path's
bridge-foundation and tip-end cooling stages. Its sequence moves between course groups as the
slicer's layer changes do, and its layer, progress and time-left lines come from the
acceleration planner that `hsm-gcode`'s playback uses. The `sculpted-trial` stage commands lay
one stage at a time for investigation.

These commands run the builds last installed, so after an edit to their source, build them as
[`faucet-plate`'s header](../../../../tools/hsm/print-prep/src/bin/faucet_plate.rs) shows and
install them again:

```sh
hsm-run --install-tools "$PWD" tools/hsm/target/release/faucet-plate tools/hsm/target/release/sculpted-trial \
  tools/hsm/target/release/faucet-print-project
```

`faucet-plate` runs from inside the checkout, through `tools/run` for its slices.

These checks read a prepared plate before it is sent. Each runs by hand on the plate's G-code or
archive:

- `sculpted-trial replay PLATE.gcode OUT.json` plays the plate's moves against the material laid
  before each one, with the modeled toolhead over them. For each phase it gives the closest head
  body, nozzle flank and travelling tip. `sculpted-trial approaches PLATE.gcode REPLAY.json
  OUT.json` reads the replay's dry nozzle approaches again at their exact positions over the
  earlier beads.
- `sculpted-trial audit-tip TIP.stl WARP.json ARCHIVE.gcode.3mf OUT.json` measures the tip's tilted
  courses, their support contacts and its clear waterways against the tip's mesh.
- `hsm-gcode laying`, `recipe` and `harm` read a part's speed, fan and plastic by height, what two
  plates command differently, and the travels that could touch earlier plastic, as the
  [G-code tools](../../../../tools/gcode/README.md) describe.

The replay's toolhead is the committed whole-head map, which `sculpted-trial head-map` folds
from the H2C toolhead model's export.

The display seat, foot recesses and cover bezel use their shared mounted datums.
The [October 17 clearance reading](prints/2026-10-17-localized-cooling-display-clearance-mark2/display-clearance.json)
binds that print's geometry. Current 4 mm tubing and passage evidence are in
[flavor dispense lines](../flavor-lines/README.md); physical assembly of the current preparation remains unmeasured.
