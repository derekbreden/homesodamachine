# Front Bezel — Decomposition Decision

## Decision: Pass Through (No Decomposition)

This part is a single geometric paradigm. No decomposition needed.

### Rationale

Every feature of the front bezel is prismatic (extrude-and-cut):

- **Main body shell:** Extruded rectangular profile with wall thickness, open at the back where it mates to the tray and lid. Pure box-and-shell.
- **Palm contour (1-2 mm crown):** A subtle convex curvature over the outer face. Achievable in CadQuery via a loft between two rectangular profiles offset by 1-2 mm at center, or a spline-based face. This is a shaped extrusion, not a different geometric paradigm.
- **Finger channels:** Rectangular pocket cuts into the left and right edges of the body. Through-cuts along the X axis (side-to-side). Pure prismatic removal.
- **Pull-tab paddles:** Flat paddle surfaces inside the finger channels with horizontal rib texture. These are integral to the channel geometry -- either left standing when the channels are cut, or added as small extrusions within the channel voids. Pure prismatic.
- **Snap tabs:** Small extruded protrusions on the back edges (2 per side wall, 1 on floor, 1 on lid edge). Pure prismatic additions.
- **Step-lap overlap (1.5 mm):** The bezel's back edges extend 1.5 mm past the tray front edges, creating the shadow-line seam. This is just the body's depth dimension -- not a separate feature requiring a different technique.
- **Fillets:** 2 mm on external corners, 3 mm where fingers curl around channel edges. Standard CadQuery fillet operations on selected edges.

No feature requires sweeps, revolves, helical operations, or lofts beyond the shallow palm contour (which is a minor shaping of an otherwise prismatic body). All features are tightly coupled -- the channels are cuts into the body, the paddles exist within those channels, and the snap tabs are on the back edges of the same shell. Splitting any of these into a separate sub-component would create composition boundaries through interdependent geometry, adding complexity without benefit.

A single CadQuery agent can handle this part as one extrude-and-cut problem with a final fillet pass.
