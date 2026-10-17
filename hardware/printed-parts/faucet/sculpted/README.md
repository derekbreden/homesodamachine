# Complete white Sculpted faucet

The [selected process](finish-selection.json) carries the latest black
Industrial faucet printing settings to the Sculpted geometry. The complete
PET-GF plate contains the Sculpted base, shared tip, Sculpted display cover,
matching above-counter plate and side-down lever replica. TPU pieces and the
umbilical organizer are separate prints.

The [editable project](prints/2026-10-17-localized-cooling-display-clearance-mark2/2026-10-17-sculpted-white-localcool-clearance150-right04-z004-mark2.3mf)
targets Mark2's right hardened standard-flow 0.4 mm hotend and white PET-GF in
external slot 255. Its normal +0.04 mm requested Z trim emits +0.02 mm on
Textured PEI. The right nozzle retains its recorded native XY registration.
Filament assignment is Manual at project and plate scope, with filament 1
assigned to extruder 2. The PET-GF availability metadata includes both of
Mark2's installed hardened 0.4 mm hotends.

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

The process retains two ordinary walls, 15% grid infill, 15% infill/wall
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
| Sculpted base | −15° | Seven segmented edge-following arcs fitted to the 58 × 59 mm foot ellipse; local contact-strip blockers; Tree(auto)/Default elsewhere |
| Shared tip | −105° | Accepted eight fins, seam-side lip tree enforcers and removable disc on the hidden male root; Tree(auto)/Default elsewhere |
| Sculpted cover | −50° | Saved automatic supports |
| Matching plate | 0° | Saved automatic supports |
| Side-down lever | 0° of print-oriented STL | Saved automatic supports |

The base arc arrangement comes from the physically accepted Industrial rim,
with CAD X scaled by 58/59 to follow the Sculpted ellipse. Release angles,
build Z and the requested 0.24 mm gap are retained. The shared tip aids retain
their source geometry and contact scope. Automatic support decisions,
including normal sections, are retained elsewhere.

## Preparation and evidence

[prepare_print_project.py](prepare_print_project.py) rebuilds the five parts
from current STLs, transfers settings by part role, fits the base rim aids
and applies the right-nozzle filament mapping. It runs manually and never
starts a printer.

[review_print.py](review_print.py) reads the native G-code's nominal courses,
filament assignment, cooling, speed commands, complete bead footprint and
whole-height seam paths. It packages a separate print-only archive with
unchanged G-code bytes. It is a manual reader, not a build step.

The [native review](prints/2026-10-17-localized-cooling-display-clearance-mark2/native-review.json)
and per-part seam CSVs bind the submitted commands. Physical white Sculpted
finish, cleanup and fit remain a result of this complete print.

The [selected print](selected-print.json) and [launch record](prints/2026-10-17-localized-cooling-display-clearance-mark2/launch.json)
identify the current complete project and its submitted archive.

The display seat and cover bezel have 1.50 mm additional clearance along the
display normal, giving 1.80064 mm nominal clearance to either flavor tube.
Four bearing pads extend by 1.50 mm. Their 3.25 × 3.00 mm footprint
has inner faces flush with the open channel. The neck opening,
tube paths, snap datums and lower cover shoulder remain fixed. The
[clearance reading](prints/2026-10-17-localized-cooling-display-clearance-mark2/display-clearance.json)
binds the geometry; physical assembly of this revision remains to be evaluated.
