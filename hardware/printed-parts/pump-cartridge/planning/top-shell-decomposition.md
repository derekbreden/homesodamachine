# Top Shell — Sub-Component Decomposition

## Decision: Pass Through

This part is a single geometric paradigm. No decomposition needed.

## Rationale

The top shell is an open-bottom half-box whose every feature is a prismatic extrude-and-cut operation:

- **Half-box body (ceiling, upper side walls, front wall, rear wall upper portion):** A rectangular box with a pocket cut from the bottom face, leaving ceiling and walls. CadQuery `box()` minus interior `box()` cut, or built up from individual wall extrusions. All orthogonal planar surfaces.
- **Palm surface on front wall:** The front wall's exterior face is flat by default. The crosshatch grip texture (0.2mm deep, 1mm pitch) is a grid of shallow rectangular grooves cut into a planar face — repetitive linear cuts on a single workplane.
- **Finger plate rectangular slot:** A rectangular cutout through the front wall. CadQuery `rect().cutThruAll()` on the front wall face.
- **Snap-fit cantilever hooks on inner side walls:** Rectangular cantilever beams extruded from the inner edges of the side walls. Each hook is a rectangular profile sketch extruded inward, with a 30-degree entry ramp (chamfer cut) at the tip and a fillet at the root. These are prismatic features — extruded rectangular cross-sections with simple chamfer and fillet treatments. No sweeps or complex curves.
- **Partition capture slots in side walls:** Rectangular slot cuts into the inner faces of both side walls at the partition Y-position. CadQuery `rect().cutBlind()` on each side wall interior face. Identical geometry to the matching slots in the bottom shell.
- **0.3mm inset step at parting line perimeter:** The bottom edge of the shell body is inset 0.3mm on all four sides relative to the bottom shell. This is a rectangular step — either built into the base box dimensions or cut as a perimeter ledge. Purely prismatic.
- **1mm exterior fillets on all exterior edges:** Standard CadQuery `fillet()` edge treatment applied after the body and cuts are complete.
- **2x M3 development screw clearance holes through ceiling:** Cylindrical through-holes. CadQuery `hole()` at two positions on the top face.

Every feature is either a box, a rectangular cutout, a rectangular extrusion (hooks), a cylindrical hole, or an edge treatment (fillet, chamfer). No sweeps, no lofts, no revolves, no rotational features beyond simple cylindrical holes. The snap-fit hooks — the most complex features — are extruded rectangular profiles with chamfered tips, well within a single CadQuery agent's capability using workplane sketches and extrudes.

The features are also spatially interdependent. The snap-fit hooks are positioned relative to the side walls. The partition slots are cut into those same side walls. The finger plate slot is cut into the front wall that also carries the palm surface. The 0.3mm inset step runs around the same perimeter as the hooks. Splitting any of these into separate sub-components would create interface boundaries through shared wall geometry, adding composition complexity with no benefit.

Decomposition would add pipeline overhead (multiple sub-component passes through 4s/4b/5/6g plus a composition step) for a part that a single generation agent can produce in one script: create the half-box body, cut the finger plate slot, extrude the snap-fit hooks, cut the partition slots, cut the screw holes, apply fillets and the perimeter step. This fails quality gate criterion 5: simple parts must pass through.

## Pipeline path

The top shell proceeds as a single unit through: 4s (spatial resolution) -> 4b (parts specification) -> 5 (engineering drawing) -> 6g (CadQuery generation). No composition step (6c) is needed.
