# Printed parts

## Begin with the whole job

A printed part is the **simplest continuous printable shape that completely does its work**.
Start from the current assembly: what the part holds, clears, guides, seals or presents; how it
is installed and removed; which piece owns each surface or closed span; and which face is on the
bed. Geometry left over from an obsolete insertion direction or an earlier arrangement has no
function in the current part.

Simple does not mean sparse, featureless or made with the least material. A corbel that needs to
reach farther is extended, a wall that needs to be thicker is thickened, and a volume that the
part owns is filled with one sound body. Voids, ribs, steps, lips and retainers are ordinary
functional geometry when the assembly needs them. What does not belong is a separate patch for
a condition already accepted, a second retainer where the surrounding body already locates the
object, or a feature which exists only to repair a side effect of another unnecessary feature.

Put material on the piece that owns the function. An opening in one member can be correctly
closed by its mating member in the assembled state; filling the first member instead can block
insertion or service. Inspect the isolated pieces and their assembled relationship before
deciding that an apparent gap needs material.

When complexity is necessary, follow all of its consequences. Check the print orientation, the
faces it changes, the clearances and motions around it, and the neighboring and mating pieces.
Fix every side effect in the same coherent construction or choose a simpler construction. Do not
leave a thin base, a new sightline, a displaced flat, or another local defect behind a feature
which solves only its own immediate problem.

Two faces a fraction of a millimetre apart where one face belongs, nearly coincident solids that
leave a sliver, and a wall carried on a sub-layer tab are construction defects. Align the datums
or booleans which make them; a cosmetic fillet over the result does not fix the construction. A
reported instance is also a search pattern: inspect its mirror, every repetition of the same
helper, adjacent transitions, and the other pieces where the construction occurs.

## Agents own visual review

An agent shaping a part is also one of its visual reviewers. For every coherent iteration, derive
the smallest affected outputs: the piece's own generator cuts its STEP, STL and payload (the pump
cartridge has a dedicated materializer, `hardware/scripts/materialize_pump_cartridge.py`), and
`tools/publish_now.py` grafts the changed piece payload into the enclosure and appliance payloads
and tells the site — no appliance stood, no Bazel waited on. Inspect the isolated printable shape
and the served assembled context, and look beyond the coordinates Derek supplied for repetitions
and related defects. Publish that coherent iteration while the review is active, inspect the
served result, route findings to the agents whose work they touch, fix them, and look again.
`enclosure_assembly.py` stands the whole appliance and is the reconciliation path: it answers a
body moved in the pack, and it does not gate a look at a surface. A selected edge is an example
of what to learn to see, not the boundary of the work.

## Know what each representation shows

The physical print is the part. The files answer different questions about it:

- The CadQuery source and exported STEP carry the exact B-rep construction, dimensions and
  analytic faces. On pieces with a mesh-only show skin, the STEP is intentionally a smooth body
  and does not contain the complete printed surface.
- The STL is the tessellated geometry handed to the slicer. Of the STEP, STL and viewer payload,
  it is the closest representation of the geometry that will be printed. Slicer settings and
  toolpaths still intervene between the STL and the physical result.
- `<piece>.step.mesh` is the payload `/3d` draws and the coordinate frame Derek clicks. For the
  pieces whose printable surface is in an STL, the payload is cut from that STL and simplified
  to the viewer's tolerance; it is the fast, pickable visual proxy for the printed surface, not a
  replacement for the STL.

When Derek names a defect on a `.step.mesh`, begin in that exact visual frame, find the same
surface in the current STL, and trace it through the STEP and source to the construction that
makes it. Then regenerate the affected STEP, STL and payload and inspect both the piece and the
assembly. A clean STEP does not dismiss a defect present in the printable STL. A payload-only
artifact calls for a payload fix, not a speculative change to sound print geometry.

## Supports

Every printable piece in the enclosure assembly follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy). That
section is canonical for the whole enclosure assembly, not only its back-top quadrant.
