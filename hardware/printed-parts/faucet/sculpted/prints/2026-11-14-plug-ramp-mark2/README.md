# Sculpted faucet plug ramp on Mark2

The [launched plate](sculpted-faucet-plug-ramp-black-mark2-review.gcode.3mf) holds
the Sculpted base, tip, display cover, mounting plate and lever in black PET-GF.
The [launch record](launch.json) identifies the exact job accepted by Mark2.

The small free end of the male plug starts against a removable bed anchor.
The model courses tilt gradually through the plug and reach the base's slope
as the full-diameter mating shoulder starts. They hold that angle as the
whole shoulder comes through, then ease to level as the tube axis reaches
vertical. This leaves the level nose with its existing pose and local cooling.
The [course field](tip-warp.json) gives the ramp and shoulder datums.

The physical bearing face remains steeper than the model courses. Bed-rooted
tree supports carry a stepped interface around its annulus with the plug and
bore kept clear. The [support comparison](support-comparison.json) shows
where the first emerging walls are farther from the interface. Closing the
gap across the whole interface improves backing and places some support roads
inside the bearing surface. This plate uses the wider setting. Check the face
for droop and drag after release, then seat the plug in the base.

The [head replay](head-replay.json) checks the whole plate against the
[photo-derived head envelope](../../../../../reference/h2c-toolhead/README.md).
The flow cap applies to the [mapped tip courses](flow-cap.json). The
[deposition audit](retained-deposition.json) binds the other parts and mounting
plate rings to the flat-face review plate. Its [printable face geometry](https://github.com/derekbreden/homesodamachine/blob/f5dee32108832f6d0e1f5c50dbb8f7fd5c30576e/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-tip-shoulder-mark2/dispense-face.json)
describes the full-width cover and flat seam.

[Run inputs](run-inputs.zip) retain the editable plate, complete native slice,
warped donor and settings, ring paths, and sequenced motion. The
[input manifest](native-sources.json) binds the files to the submitted archive.
The working run folders are `.cache/runs/faucet-plug-ramp-20261114`,
`.cache/runs/faucet-plug-ramp-native-20261114` and
`.cache/runs/faucet-plug-ramp-sequence-20261114`. The
[reproduction commands](stage/REPRODUCE.md) use the saved inputs.
