# Mounting Partition -- Decomposition Decision

## Decision: Pass Through (No Decomposition)

This part is a single geometric paradigm. No decomposition needed.

## Rationale

The mounting partition is entirely prismatic: a flat rectangular plate with cylindrical through-holes and rectangular notches/tabs. Every feature is an extrude-and-cut operation on the same base body:

- Base plate: rectangular box extrusion
- Motor bores (x2): cylindrical cuts through the plate thickness
- M3 through-holes (x8): cylindrical cuts through the plate thickness
- Bottom edge registration tabs (x2): rectangular extrusions from the bottom edge
- Top edge registration tabs (x2): rectangular extrusions from the top edge
- Linkage arm notches (x2): rectangular cuts at the bottom corners

No sweeps, no lofts, no revolved profiles, no rotational features. All holes are circular and their axes are parallel (all run through the plate thickness). All notches and tabs are rectangular prisms aligned with the plate axes. A single CadQuery agent handles this as a straightforward box-plus-cuts-plus-unions problem.

Decomposing this part would add pipeline complexity (two sub-components, a composition step) with no benefit -- there is no geometric boundary where a split would simplify the CadQuery work. The entire part fits in one script using `box()`, `hole()`, and rectangular `cut()` operations.

The part is also small (approximately 128 mm x 5 mm x 63 mm) and fits on the build plate with large margins. No build-volume concern motivates a split.
