# Sculpted faucet tip shoulder trial for Mark2

The [sliced review archive](sculpted-faucet-tip-shoulder-black-mark2-review.gcode.3mf)
contains the complete Mark2 trial. Open it in Bambu Studio Preview. The
[editable five-part project](sculpted-faucet-tip-shoulder-black-mark2.3mf) holds the
Sculpted base, tip, display cover, mounting plate and lever in their print poses.
The sliced archive carries the inclined regions, scheduling and local supports.

The material is black Polymaker PET-GF on the left hardened nozzle and textured PEI.
The saved spool profile uses Bambu's PET-CF identifier. The ordered print paths use
manual support and part milestones. Keep smooth timelapse off. Native power-loss
recovery and per-layer camera calls are disabled in the executable.

## Tip and cover

The tip's curved plug seats into the base. The bearing shoulder is the face picked
in the yellow screenshot. Its support interface and first model roads follow that
plane. The inclined courses advance uphill in narrow height bands to clear the
cooling duct. Layer angle eases back to level below the dispense nose. The base
deposition comes from the
[shaft trial](https://github.com/derekbreden/homesodamachine/blob/ddd391f3d32bd8397f08b517ee58614fcd3e93ba/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-shaft-tilted-mark2/README.md).

The [shoulder support reading](tip-shoulder-support.json) checks the first model
roads and the interface's clearance from the plug and bore. The native interface
joins around the plug. Free the tree below it, then sever the exposed rim from the
outside at both sides if needed to release it in pieces.

On the dispense face, the cover fills the rounded cut across the tip's crown.
The [mesh and support reading](dispense-face.json) locates the photographed mark
in the outlet section and measures the seam, the clearances through assembly and the
native interface supporting the first extended cover roads. The
[opening and clearance reading](cover-clearance.json) checks the direction the
cover seats along.

## Mounting plate

Each screw-head counterbore under a base insert has a short removable ring under its
shoulder. The ring gap leaves room for the first overhang road to sag before it
reaches the support. Catch the split from the bed face with a pick, flex the ring
inward and pull it out through the counterbore. The [ring support record](ring-supports.json)
shows the gap from the emitted roads and the clearance around the pick opening.

## Verification

The [plate receipt](plate.json) binds the archive, editable project and timeline
to the same motion. The estimate includes acceleration, with warmup and firmware
waits outside the playback clock. The [head replay](head-replay.json) uses the
photo-derived [H2C head envelope](../../../../../reference/h2c-toolhead/README.md)
and nominal deposited beads.

The replay clears the modeled head body. It predicts more nozzle contact with
prior beads on the inclined outer wall than at the same height on the printed
tip. The archive is staged for review. Shoulder finish, support release and
the cover's snap remain physical fit questions.

[Reproduce the trial](stage/REPRODUCE.md) from the recorded native inputs.
