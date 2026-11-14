# Sculpted faucet matched shoulder on Mark2

The [complete print plate](sculpted-faucet-matched-shoulder-black-mark2-review.gcode.3mf)
contains the Sculpted base, tip, display cover, mounting plate and lever in black PET-GF.
The [editable project](sculpted-faucet-matched-shoulder-black-mark2.3mf) holds the
physical tip in the trial pose.

The tip's small breakaway pad seats the hidden plug on the bed. The courses
begin to tilt above the pad, hold the mating angle across the bearing face and
its interface, and ease to level where the tube's axis is vertical. The
[warp receipt](tip-warp.json) describes the field and the
[deposition audit](tip-geometry.json) measures it in the packaged commands.
The [base's rear seam](../2026-11-14-rear-seam-mark2/seam-evidence.json)
and the other companions' deposited paths come from the rear seam plate.

The shoulder uses the donor's dense Slim tree interface on the matching
course planes. The [support reading](shoulder-support.json) measures projected
coverage and gap under the first wall and bridge paths. The face keeps its
scoped internal paint, beverage outlet keepout and localized part cooling.
The [nose support reading](nose-support.json) locates the resolved interface
roads on the inside of the dispense face. Clean release, surface finish and
assembled fit remain checks on the printed part.

The [head replay](head-replay.json) models the nominal roads against the
[H2C head](../../../../../reference/h2c-toolhead/README.md), including the
trees, nozzle flank and cross-plate transfers. [Motion timing](chronology.json)
uses the acceleration planner. [Package metadata](package.json) describes the
handed-off archive.

[Run inputs](run-inputs.zip) retain the printable tip and cover, support
modifiers, native donor and full-plate template, and sequenced commands.
The working run is `.cache/runs/faucet-pose20-mark2-20261114/fixed24`.
[Reproduce the plate](REPRODUCE.md) from the retained inputs and Rust stages.
