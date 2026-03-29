# Top Shell -- Decomposition Decision

This part is a single geometric paradigm. No decomposition needed.

## Rationale

Every feature of the top shell is an extrude-and-cut operation from a prismatic body. The shell body is a rectangular box with walls. All internal and external features are either:

- **Box extrusions:** side walls, rear bulkhead, pump mounting shelf, snap-fit ledges, over-center detent cantilever arm
- **Cylindrical cuts:** motor bores (36.4 mm), screw holes (3.4 mm), bulkhead fitting holes (17.0 mm), lever pivot boss holes (3.1 mm), spring pockets, alignment pin holes (4.2 mm)
- **Cylindrical unions:** lever pivot bosses, spring pocket walls (if raised from a wall face)
- **Rectangular profile cuts:** T-slot rail groove halves along side walls

No feature requires revolve, sweep, loft, or helix. The 36.4 mm motor bores are standard hole operations through a flat shelf, not rotational geometry. The cylindrical pockets and bosses are simple primitives placed on planar faces. The T-slot groove is a rectangular profile extruded along a straight edge.

The features are also tightly interdependent. The pump mounting shelf ties into both side walls and the rear bulkhead. The lever pivot bosses, spring pockets, detent arm, and snap-fit ledges all attach to the shell walls. Decomposing would create interface boundaries through the walls themselves, adding composition complexity with no geometric benefit.

A single CadQuery agent can handle this part as one box body with sequential unions (shelf, bosses, ledges, cantilever) and cuts (bores, holes, pockets, grooves). No advanced techniques are required.
