# Lite device assembly

The whole Lite Edition as one package: the
[reservoir-pockets](../printed-parts/reservoir-pockets/) box with the four
[valve-manifold](../../../hardware/printed-parts/valve-manifold/) tray
assemblies — source-select, bag-circuit, bib-gate, nozzle-gate — mounted on two
of its faces. A layout model for fit and tube-routing review, not a printed
part.

## Frame

The reservoir's frame carries through: Z+ up, X left/right, Y front/back
(depth), floor on Z=0. The +X doorway faces the enclosure back (bags load from
the rear); the −X wall is the enclosure front and carries both bag-spout exits
low (y = ±36, z ≈ 12).

## Arrangement

Two adjacent reservoir faces carry the manifold, so the groups never share a
face and nothing collides.

- **source-select** stands vertical against the **+Y wall**: rotated 90° about
  X then 90° about Y so its 225 mm long axis runs up Z, centered on X, on the
  floor. A tall panel on the back-depth wall.
- **bag-circuit → bib-gate → nozzle-gate** stack in Z **largest to smallest**
  against the **−X wall** (the enclosure front, where the bag exits are), at the
  trays' native 63 mm stack pitch (bag z 0–63, bib 63–126, nozzle 126–189).
  The stack is nudged **+Y ≈ 30 mm** so the quick-connect 90° elbows that go on
  the trays' −Y ports stay inside the reservoir's −Y wall (≈ 24 mm of elbow
  clearance to that face).

Inter-tray links are tubing (the topology
[Tube Segments](../../../hardware/topology/fluid-topology.md) tables). The
reservoir's rod-end bosses (y = ±81, high Z) share a bounding-box column with
source-select but are well clear in Z — the generator confirms with a real
solid-intersection test, not bounding boxes.

Overall envelope **229 × 219 × 289 mm** (X × Y × Z), no solid collisions.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/device-assembly/device_assembly.py`
→ `device-assembly.step` (27 solids; one translucent reservoir plus the four
trays, each a distinct color). Placement constants — `GAP`, `Y_SHIFT`, the
per-tray rotations and anchors — are at the top of `device_assembly.py` and in
`build()`.
