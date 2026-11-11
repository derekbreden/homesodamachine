# Complete white Sculpted faucet

The [selected process](finish-selection.json) starts from the recorded
Industrial printing settings and applies the Sculpted finish and supports. The
complete PET-GF plate contains the Sculpted base, tip, display cover,
matching above-counter plate and side-down lever replica. TPU pieces and the
umbilical organizer are separate prints.

The [editable project](../faucet-petgf.3mf)
targets Mark2's abrasive left nozzle and white PET-GF on Textured PEI. It
uses Mark2's [recorded trim](../../z-trim.md), with the left external spool
assigned manually at project and plate scope.

## Layer schedule and finish

The first bed layer is 0.20 mm. Every subsequent nominal course is 0.24 mm
on all five parts. There are no Industrial shoulder fine-layer bands and no
separate eight-layer starting override. Bridge and overhang bead-height
annotations describe their extrusion cross-sections, not additional fine
courses.

| Parts | Seam position | Ordinary gap | Scarf |
| --- | --- | --- | --- |
| Base, shared tip, mounting plate | Back | 150% | A2: 60 mm, 0% scarf gap |
| Cover, lever | Aligned | 15% | Off |

Rear seam enforcement follows the entire base silhouette in its build pose
and the shared tip's curved outer meridian. Wipe is off. The base uses
Arachne with an infill-only solid foot; its reinforcement modifier inherits
ordinary wall settings. The other rigid parts use Classic.

The process retains two ordinary walls, 15% gyroid infill, 15% infill/wall
overlap, 265°C first-layer and 280°C subsequent nozzle temperatures, and an
80°C bed. The [localized PET-GF cooling policy](../../cooling/README.md) keeps ordinary
part cooling off. After three fan-off bed courses, bridges and wall paths
meeting the 50% overhang threshold receive 70%; fan-always-on, fan pre-start
and auxiliary part cooling are off. Bridge flow is 125%, bridges
are 15 mm/s, and overhang limits retain the selected 10/15 mm/s values.
Ordinary supported-wall and infill speeds retain the black print's settings.

## Supports and poses

| Part | CAD X rotation | Support treatment |
| --- | ---: | --- |
| Sculpted base | −15° | Slim trees and segmented outer fins carry a shared dense interface under the rim ellipse. A local nonplanar band follows the inclined seat and the first perimeter follows its contour. Each mounting insert recess bridges its shoulder and pilot roof. |
| Shared tip | −105° | Slim trees and segmented outer fins carry a shared dense interface at the mating lip. The first outer perimeter follows the tilted rim. The inner dispense face has its own contact band and an outlet keepout. A removable disc anchors the hidden root. |
| Sculpted cover | −50° | Saved automatic supports |
| Matching plate | 0° | Bridge the screw counterbore shoulders and keep the shank passages open. |
| Side-down lever | 0° of print-oriented STL | Saved automatic supports |

The [shared PET-GF interface](../../petgf.3mf) joins the fins and trees under
the mating edges. The base prints without a brim. The cover prints on its flat lower lands with support
accessible through its open underside. The side-down lever bridges its
channel and uses accessible support at the attachment relief.
Ordinary sparse infill follows the shared PET-GF profile.

## Preparation and evidence

[prepare_print_project.rs](prepare_print_project.rs), the `sculpted-faucet-print-project`
program, prepares the complete plate from current STLs. Pass
`--slice-output DIRECTORY` for the executable offline slice with the base
and tip nonplanar contact paths. The editable project carries the actual part meshes
and support aids. Pass `--printer Mark1` and `--filament-colour` with the loaded
spool's colour to prepare a Mark1 plate.

[review_print.py](https://github.com/derekbreden/homesodamachine/blob/306268f870/hardware/printed-parts/faucet/sculpted/review_print.py) (in Git at `306268f870`) reads the native G-code's nominal courses,
filament assignment, cooling, speed commands, complete bead footprint and
whole-height seam paths. It packages a separate print-only archive with
unchanged G-code bytes. It is a manual reader, not a build step.

The [native review](prints/2026-10-17-localized-cooling-display-clearance-mark2/native-review.json)
and per-part seam CSVs bind the submitted commands. Physical white Sculpted
finish, cleanup and fit remain a result of this complete print.

The [current print report](../faucet-petgf.print.json) binds the meshes and
recipes for the complete plate. The [contact review](production/contact-review.json)
binds the production motion and the local executable at
`production/faucet-petgf.gcode.3mf`. Physical removal and fit for this
complete plate remain pending.

The display seat, bearing pads and cover bezel use their shared mounted datums.
The [October 17 clearance reading](prints/2026-10-17-localized-cooling-display-clearance-mark2/display-clearance.json)
binds that print's geometry. Current 4 mm tubing and passage evidence are in
[flavor dispense lines](../flavor-lines/README.md); physical assembly of the current preparation remains unmeasured.
