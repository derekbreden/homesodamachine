# Shell Bottom — Decomposition Decision

## Decision: Pass Through

This part is a single geometric paradigm. No decomposition needed.

## Rationale

Every feature of the Shell Bottom is prismatic extrude-and-cut geometry:

- **Main body:** Open-top box (bottom wall + lower side walls + lower front/rear walls) — a single box extrusion with material removed from the interior.
- **T-rail profiles:** Linear extrusions running along the outer side walls in the depth direction. The T cross-section (stem + crossbar with 45-degree underside chamfers) is a 2D profile extruded along a straight path.
- **Link rod channels:** U-shaped grooves cut into the bottom interior surface, running front-to-back. Linear cuts.
- **Slide bushings:** Six cylindrical bores (3.2mm ID) in boss features along the channel walls. Simple cylinder subtractions from cylindrical bosses.
- **Inset panel recess (lower half):** A rectangular pocket in the front wall interior face. Box cut.
- **Snap-fit hooks:** Small prismatic tabs along the top rim with hook lips. Box extrusions with chamfered lead-ins.
- **Mounting plate locating slots:** Rectangular cuts in the inner faces of the side walls. Box cuts.

No feature requires a sweep, loft, revolve, or helix. No feature interacts with a different geometric paradigm. The part is large and has many features, but they are all the same kind of CadQuery work — `box()`, `rect()`, `circle()`, `extrude()`, `cut()`, `chamfer()`. A single generation agent handles this without needing multiple advanced techniques.

Decomposing would create interface boundaries (e.g., splitting the body from the T-rails, or the channels from the body) that serve no purpose — the features are tightly integrated into the same prismatic shell. The T-rails are part of the side walls. The channels are part of the bottom wall. The bushings sit in the channels. Splitting any of these apart would require re-joining them at flush surfaces, adding composition complexity for zero geometric simplification.
