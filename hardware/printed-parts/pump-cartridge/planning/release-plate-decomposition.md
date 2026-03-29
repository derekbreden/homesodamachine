# Release Plate — Sub-Component Decomposition

## Decision: Pass Through

This part is a single geometric paradigm. No decomposition needed.

## Rationale

The release plate is a compact prismatic part (~50mm x 50mm x 5mm) whose every feature is an extrude-and-cut operation:

- **Plate body:** A rectangular box. CadQuery `box()`.
- **4 stepped bores (6.5mm / 9.8mm / 15.4mm stepped profile):** Revolved profiles cut from the plate. These are 2D axial cross-sections revolved around each bore's center axis — this is standard CadQuery `polyline().close().revolve()` cut from the box. Revolved profiles used purely as subtractive bore cuts in a prismatic body do not constitute a separate "rotational" paradigm; they are the standard technique for stepped holes in a plate (see Step 6 generation standards, Section 5: "Stepped bores with chamfers — use revolved profiles").
- **2 pin sockets (3.1mm) on lateral edges:** Cylindrical cuts into the plate edges. CadQuery `hole()` or `circle().cutThruAll()`.
- **2 spring boss receivers:** Cylindrical pockets matching the 2mm bosses on the rear wall. Simple circular cuts or counterbores.
- **Guide pin pads (if present):** Cylindrical bosses unioned to the plate body. CadQuery `circle().extrude()`.

All features are either prismatic (the plate body, any pads) or revolved-profile cuts (bores, sockets, receivers) applied to that prismatic body. No sweeps, no lofts, no helical geometry, no complex surfaces. A single CadQuery agent handles this as one script: create box, union any bosses, then cut all bores and sockets.

The features are also tightly interdependent — the bore positions and pin socket positions are all defined relative to the same small plate body. Splitting them would create interface complexity with no benefit.

Decomposition would add pipeline overhead (two sub-component passes through 4s/4b/5/6g plus a composition step) for a part that a single generation agent can produce in one straightforward script. This fails quality gate criterion 5: simple parts must pass through.

## Pipeline path

The release plate proceeds as a single unit through: 4s (spatial resolution) -> 4b (parts specification) -> 5 (engineering drawing) -> 6g (CadQuery generation). No composition step (6c) is needed.
