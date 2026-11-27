---
title: Smooth 2.38 mm cold-core casing
lede: Plain walls preserve the printed reservoirs’ mating cavities. The casing leaves room for foil seals inside the enclosure envelope.
date: 2026-10-25T16:30:19-05:00
commit: 30b4a0ebb0fd
model: manifold-layout/enclosure-assembly.step
---

The shell and cap walls use a smooth 2.38 mm section. The 282.4 × 180.4 mm casing has R11.7 corners and leaves 0.30 mm per face for exterior foil tape, without recessed seal bands. Floors remain 2 mm, the equipment lid remains 5.4 mm, and the nominal stack remains 253.4 mm tall.

Reservoir-facing cavity profiles, reed slots, clamp axes, copper-cover seats, conduit positions and equipment datums stay fixed. Pocket walls grow toward the foam. The radial cylinder-to-pocket foam blanket is 14.62 mm; the straight front/back pour bands are 14.94 mm. The assembly uses its fixed copper-port reference so changing the casing does not translate the equipment.

The [native integration receipt](/hardware/printed-parts/cold-core/casing-integration-review.json) records an exact zero difference between the reservoir mating cavities, clearance for both reservoir bodies and caps, and clear assembled screw and tube paths. These are geometry checks, not physical fit or lifetime acceptance.

The shell’s 0.4 mm slice uses Classic with three loops from each boundary, giving six perimeter beads in all 30 sampled ordinary wall sections. Its [Mark2 job record](https://github.com/derekbreden/homesodamachine/blob/eca139d1b8d5b45c1e6e73a818144b5683fae003/hardware/printed-parts/cold-core/foam-shell/prints/2026-10-25-mark2-left04-smooth238-z004/README.md) binds the reviewed slice and accepted task 1375153599.
