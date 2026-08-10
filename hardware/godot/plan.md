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

**2 — [`_scene.py`](../scripts/_scene.py).** One glTF node per body, carrying
its name, its 4×4, its colour, and the local-frame triangles it stands over,
named the way `_meshes._named` names kept triangles so two placements of one
drawn body meet at one mesh:

```
tools/cad-venv/bin/python hardware/scripts/_scene.py hardware/manifold-layout/enclosure_assembly.py
```

The enclosure writes 145 nodes over 139 drawn bodies, 5.1 MB against the
STEP's 21 MB. The cold core writes 63 over 63.

**3 — [the viewer](machine.gd).** `GLTFDocument` reads the scene at run time,
so a rebuilt scene is picked up by running again and the project carries no
copy of the machine:

```
godot --path hardware/godot -- --scene <path.glb> --view iso --hide "enclosure*" --shot out.png
```

The enclosure reads back as 145 bodies over 223 × 361 × 500 mm, under SSAO,
SSIL, SDFGI, TAA and an ACES curve. A web export wants the engine's export
templates, which are not installed.

**4 — [settling](settle.gd).** Bodies enter a Jolt world where their rules put
them, several are free at once, and contact opens whatever is inside something
else:

```
godot --path hardware/godot res://settle.tscn -- --scene <path.glb> --free "coil-v-*" --out settled.json
tools/cad-venv/bin/python hardware/scripts/_settled.py settled.json
```

What comes back is an arrangement. The derivation takes it as the target a rule
is seated on, so `placed` still reads a rule off the geometry.

**5 — [the audit in the engine](machine.gd).** The card over the view, the
bodies a failing row names painted, everything else a ghost of its own colour.
`--check <id>` narrows to one row:

```
godot --path hardware/godot -- --scene <path.glb> --card <scorecard.json> --check bodies-clear
```

A row names its bodies in its own prose, so the bodies painted are the scene's
own names that turn up in it.

## What the collision world can hold

Jolt collides convex shapes. A concave body is decomposed and every piece is
that piece's region or larger, so the error runs one way — a body reads as
touching sooner than it does — and it grows with how concave the body is.

Freed in place with nothing pulling on them, against an exact audit that reads
**0 clashes**:

| | bodies moved past the 1 mm floor | worst |
|---|---|---|
| valve coils alone | 0 of 30 | 0.95 mm |
| the whole pack | 121 of 145 | 157.7 mm |

A compact body comes back inside a millimetre. A tube through several bends
comes back a hundred, and that reading is about the decomposition rather than
about the pack. `_clearing.gap` is the exact answer for a pair; this is what to
ask about several bodies at once, which is the question with no exact form.

## The walls

The enclosure's size is three constants, and every hole in it is derived from
where bodies sit — port cutouts, heat-set stations, Wago wells, the funnel
throat. A wall the engine punches is not the wall that goes to the printer. A
wall from the kernel is 4.30 s cold and 0.02 s warm through `_realized`.
