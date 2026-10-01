# Enclosure support work

Before changing an enclosure part, its placed component, or any down-facing enclosure
geometry, read **Support-removal strategy** in
[`enclosure/README.md`](enclosure/README.md#support-removal-strategy). Feature comments
describe their exact geometry; the README carries the policy.

Enclosure parts and their receiver coupons use the shared `../petgf.3mf` tree
supports and their production print orientation. Do not generalize a part-specific
support trial to other parts. The flat-wing nameplate prints without supports,
with its back and both horizontal wings directly on the bed.

Use a 0.20 mm first bed layer, 0.24 mm on expanding print-down chamfer/tapers,
and 0.08 mm on inward/top show rounds. The additive transition in
`../cadlib/overhang_round.py` follows the accepted tee-carrier profile: 0.12 mm
outward per 0.24 mm layer. Use six walls only in the relevant transition band,
normal speeds, saved wall order and 15% overlap. See
`tee-carrier/low-force-trial/README.md` for the physical reference.

Check emitted first-to-second-layer bead overlap and keep supports off the exterior
chamfer/taper and fine show rounds. Retain supports for separate functional faces
such as flat lifting ceilings and mounting seats. Inspect short support bodies too.
Each new part needs its own native slice review; one accepted carrier is not physical
qualification of every grip or roof edge.

Ordinary enclosure walls, webs and joint ends use the nominal 3 mm wall section.
Remove cut remnants and tapered tips that leave thin fins. Apply thinner-section
exceptions only to the specific flexure, cover or other feature that requires them.
