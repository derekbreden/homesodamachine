# Godot

The assemblies move to a Godot project. Python derives the poses and writes the
scene, Godot renders and collides and settles it, CadQuery draws the parts.

## The division

| | |
|---|---|
| Godot | the render, the collision world, multi-body settling, selection |
| Python | the derivation — `enclosure_assembly.py`, `_routing`, the 66 stated bounds |
| CadQuery | printed parts, the walls, the exact readings the card carries |

`web/public/js/viewer` is 9,719 lines and draws without ambient occlusion,
temporal antialiasing or global illumination.

`fit.search` moves one body against 108 frozen ones and `arrange.rank` turns a
kinematic chain. What that leaves is in `arrange.py`'s own words — a question
about how a SET of parts goes together comes back as a column of clearances
that never adds up to a design.

## A pose is a transform

`seat_body` places a body with `Shape.rotate` and `Shape.translate`, and both go
through `BRepBuilderAPI_Transform`, which rebuilds the geometry with the pose
folded into its coordinates. 76 of the enclosure's 137 solids carry an identity
transform, and every `cq.Assembly` node location in the pack is identity.

`_meshes` keys its kept triangles on the shape's own BREP text:

| a body moved by | local-mesh key | tessellation |
|---|---|---|
| `moved()` — a hung `TopLoc_Location` | unchanged | reused |
| `translate()` | new | redrawn |

## Phases

**1 — `seat_body` hangs the pose.** The card reads byte-identical, checked the
way `_realized` and `_meshes` are checked: one process, cache defeated against
cold against warm.

**2 — `_scene.py`.** One node per body, carrying its name, its 4×4, its color,
and the local-frame mesh it references, addressed on the BREP the way
`_meshes._named` addresses it. A `.glb` per distinct shape, a `.tscn` per
assembly. Runs with no engine installed.

**3 — the viewer.** A Godot project loads the scene and web-exports. Held
against `web/public/js/viewer` on the same assembly: the same 145 parts, the
same selection, the same card.

**4 — settling.** Bodies enter a Jolt world as hulls of the meshes phase 2
bakes, and several move at once. What comes back is an arrangement; the
derivation takes it as the target a rule is seated on, so `placed` still reads
a rule off the geometry.

**5 — the audit in the engine.** Selection, drill-down and the scorecard as
editor panels.

## The walls

The enclosure's size is three constants, and every hole in it is derived from
where bodies sit — port cutouts, heat-set stations, Wago wells, the funnel
throat. A wall the engine punches is not the wall that goes to the printer. A
wall from the kernel is 4.30 s cold and 0.02 s warm through `_realized`.
