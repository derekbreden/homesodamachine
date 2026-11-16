# Sculpted faucet with the tip's shoulder on a scaffold and roof, Mark2

The [print plate](sculpted-faucet-tip-scaffold-black-mark2.gcode.3mf) and
[editable project](sculpted-faucet-tip-scaffold-black-mark2.3mf) hold the complete black PET-GF
faucet: the Sculpted base, the tip, the display cover, the mounting plate and the lever.
`faucet-plate sculpted --production` prepared them from the checkout at
[`6b77eba36`](https://github.com/derekbreden/homesodamachine/tree/6b77eba364d6ff4c80d3e115af3ca3a7493f8dd1),
so the plate is also the Sculpted product plate of that commit. The [package record](package.json)
binds the archive's G-code and the acceleration planner's estimate of its motion. The
[launch receipt](launch.json) identifies the job Mark2 accepted, and the
[startup spacing](startup-spacing.json) record gives Mark 1's last start before it.

The plate goes on Mark2's glued Engineering Plate with the PET-GF trim the print setup gives it
there, as the [plate Derek stopped](../2026-11-15-machine-z-engineering-mark2/README.md) did.

Beside that plate, this one stands the tip's mating shoulder on its own foundation, the way the
base's foot stands on its scaffold and roof:

- A scaffold of level wall layers rises from the bed under the shoulder's ring, outlined inside
  and out, walled across at the base's wall spacing and tied across at its tie spacing. It keeps
  the base's plug clearance from the mating plug and from every other bead the plate lays beside
  it, and on the shoulder's high side, where the plug's flare runs under the ring, it leans out
  with the plug from the bed. Its first layer meets the tip's brim and its second stands on it.
- The roof's courses lie parallel to the shoulder over the scaffold: the first in level lines,
  each standing on the scaffold layer beneath it, then up the slope, then across it at an angle.
  The roof reaches past the shoulder's rim as the base's roof reaches past its rim, and on the
  high side its lip steps around the slicer's tree for the tip's high side.
- A course of air separates the roof from the shoulder's first course, as before.
- The slicer lays no support under the mating lip; the plate's scaffold and roof stand where its
  trees and the donor's interface stood. The shoulder's own tilted courses are the donor's, as
  before.

The [tip foundation record](tip-foundation.json) gives the ring the plate measured, the scaffold's
layers and the roof's lines. The [verification](verification.json) records the checks the plate
passed before it was sent: the scaffold's and roof's clearance from the tip's other beads, the
roof's lines on the scaffold beneath them, the shoulder's first course over the roof, the head
replay and the travel reading. The [foundation record](foundation.json), [tip courses
report](tip-courses.json), [warp](tip-warp.json), [cooling receipts](cooling.json) and
[flow cap](flow-cap.json) are the run's own.

No print has tested the tip's scaffold and roof: how the scaffold stands, how the shoulder's
first course lies on the roof, or how the scaffold and roof come off.

[Reproduce the plate](REPRODUCE.md).
