# Touch-Flo TPU O-ring

Printed-TPU O-ring that seals the 3/8" OD LLDPE water tube into the
faucet body's 9.75 mm internal port. Sits between the supply tube's
outer wall and the bore of the harvested Westbrass R2031-NL-62 valve
body's bottom threaded metal rod, *inside* the faucet head, below the
`touch-flo-shell` cutout for the same tube. Compresses radially when
the user pushes the tube into the body port; that compression is the
seal.

**Status: placeholder — awaiting CAD.** No
`generate_step_cadquery.py` or `.step` yet. Directory exists so the
part is visible in the tree and referenceable from sibling docs.

## Where it's referenced today

[`../touch-flo-shell/generate_step_cadquery.py`](../touch-flo-shell/generate_step_cadquery.py)
around line 261–267 calls out the 0.225 mm radial gap this O-ring is
expected to take up:

```
WATER_TUBE_OD       = 0.375 * 25.4   # 9.525 — 3/8" LLDPE
                                      # (sealed in body's
                                      #  9.75 mm port via
                                      #  a TPU O-ring —
                                      #  0.225 mm radial gap)
```

The `touch-flo-shell` itself does not model the O-ring; it only
documents that one exists in the assembly stack below.

## Material

Bambu TPU 90A — same stock and hardness as the other printed gaskets
in this project (foam-cap gasket, reservoir face seals and retaining
ring, touch-flo-mounting-gasket). 90A is soft enough to compress and
seal against the tube OD without crushing the LLDPE, firm enough to
resist cold-flow over years. See
[`../../cold-core/foam-shell/README.md`](../../cold-core/foam-shell/README.md)
("foam_cap_gasket" section) and
[`../touch-flo-mounting-gasket/generate_step_cadquery.py`](../touch-flo-mounting-gasket/generate_step_cadquery.py)
docstring for the existing TPU-90A treatment in this repo.

## Geometry placeholder

All dimensions TBD — the values below are the constraints any future
CAD must satisfy, not committed numbers.

- **ID:** ~9.525 mm (= 3/8" = water tube OD). Likely slightly under,
  to grip the tube before compression.
- **OD:** slightly under 9.75 mm (= body port diameter). Likely close
  to flush, with the seal coming from radial squish into the
  0.225 mm port-to-tube gap.
- **Height (axial):** TBD. Long enough for a confident seal and to
  resist roll-out during tube insertion; short enough to not eat into
  the port's usable depth or interfere with the metal-rod thread
  start.
- **Cross-section:** TBD — square / rectangular is the natural choice
  for an FDM-printed ring; round-cross-section O-rings are awkward in
  FDM and not necessary here.

## Function

The 0.225 mm radial gap between the 9.525 mm tube OD and the 9.75 mm
port ID is the design seal interface. Without an elastomeric element
the gap leaks under any pressure. With this O-ring seated in the
gap, pushing the tube in compresses TPU radially against both the
tube OD and the port ID — same sealing mechanism as a standard
elastomer O-ring in a face/bore application, but printed in TPU 90A
from existing project stock instead of sourced as a separate
elastomer SKU.

The water side of this seal is potable cold carbonated water at
dispensing pressure (low — gravity / line pressure from the
carbonator, no pump). No food-contact regulatory framing applies to
this project at the Founder Edition scale (see
[`../../enclosure/nameplate/README.md`](../../enclosure/nameplate/README.md)
on the broader listing posture).

## When to design this

Defer until either:
- A tube-into-port pressure test on the assembled faucet head leaks
  without it, *or*
- The `touch-flo-shell` and the body-port internal geometry are
  otherwise stable enough that the O-ring's axial space and ID/OD
  tolerances stop drifting.

Until then, this README is the placeholder.
