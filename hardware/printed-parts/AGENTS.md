# Printed parts

## Mass first

A printed part is **simple continuous mass**. Where a span needs closing, close it with material:
carry the wall through, fill the volume, let one solid do what several features were about to do.
A part reads as one shape, or it reads as an assembly of ideas — and the one shape prints.

A void, a rib, a step, a lip, a labyrinth, a retainer is a **cut against that mass, and it earns
the cut by function**. Name the function where the geometry is made. Clearance already met needs
no ramp; retention the surrounding shape already gives needs no retainer; a condition Derek has
said he accepts is not a problem, and geometry added to close it is added for nothing. Extra
stuff is a defect, and being clever about it does not make it one less.

A feature that solves its own problem and opens another has solved nothing — a gap into the
interior, a rake on a face that was flat, a section too thin to stand as the base of its own
print. Find every side effect and fix it, or take the complexity back out. Those are the two
endings; a half-finished flourish is not a third.

**Degenerate geometry is the same rule in thousandths.** Two faces a fraction of a millimetre
apart where one face belongs, a sliver between solids that nearly agree, a wall carried on a tab
thinner than the wall. These come from constructions never aligned to each other, and they are
fixed at the construction. A fillet laid over the top leaves the sliver underneath it.

Thoroughness is on the same side as simplicity. A corbel that needs to reach further gets
extended; a wall that needs to be thicker gets thickened. What is cut back is decoration, never
the material a function asked for.

## The drawn surface is the part

`<piece>.step.mesh` is what `/3d` draws, and it is the frame Derek clicks and quotes coordinates
from. It carries surface the STEP does not. A change read off the source, the comments or the
solid alone is a change nobody has looked at: recut the payload and look at the drawn part. A
defect named by coordinate is answered in the frame it was named in, and one named on one piece
is a pattern to carry across every piece it fits — the named instance is an example, not the
work order.

## Supports

Down-facing geometry follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy). That
section is canonical for every printable part here, not only the enclosure's.
