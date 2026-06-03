# Lite enclosure contents assembly

The Lite Edition contents — everything that goes inside the enclosure — packed
together: the [reservoir-pockets](../printed-parts/reservoir-pockets/) box with
the four [valve-manifold](../../../hardware/printed-parts/valve-manifold/) tray
assemblies — source-select, bag-circuit, bib-gate, nozzle-gate — two bare
[Kamoer KPHM400](../../../hardware/reference/kamoer-kphm400/) pumps, and the
[hopper funnel](../printed-parts/funnel/). A layout model for fit and
tube-routing review, not a printed part. The enclosure shell that wraps these
contents lives in [`../enclosure/`](../enclosure/) and the combined enclosure
+ contents view in [`../enclosure-assembly/`](../enclosure-assembly/).

## Frame

The reservoir's frame carries through: Z+ up, X left/right, Y front/back
(depth), floor on Z=0. The +X doorway faces the enclosure back (bags load from
the rear); the −X wall is the enclosure front and carries both bag-spout exits
low (y = ±36, z ≈ 12).

## Arrangement

Each group takes a different region around the reservoir, so nothing collides:
the trays on the −X wall, source-select on the +Y wall, the pumps out front on
the floor, and the funnel at the front +Y top.

- **bag-circuit → bib-gate → nozzle-gate** stack in Z **largest to smallest**
  against the **−X wall** (the enclosure front, where the bag exits are), at the
  trays' native 63 mm stack pitch (bag z 0–63, bib 63–126, nozzle 126–189).
  The stack is nudged **+Y ≈ 30 mm** so the quick-connect 90° elbows that go on
  the trays' −Y ports stay inside the reservoir's −Y wall (**≈ 24 mm** of elbow
  clearance to that face).
- **source-select** stands vertical against the **+Y wall**: rotated 90° about
  X, then 90° about Y (its 225 mm long axis up Z), then 180° about Z. It is
  butted in −X against the tray stack (x = −79) and **lifted ≈ 24 mm off the
  floor** — the same clearance the stack leaves to the −Y wall — so its bottom
  port has matching elbow room. Sitting at the −X end frees the +X end of the
  +Y wall for connections.
- **two Kamoer KPHM400 pumps** stand vertical, **stacked end to end** in
  **front** of the tray stack (−X of it), native orientation (tube barbs out
  +Y, into open space). They sit on the **−Y half** so the +Y half is free for
  the funnel; the lower pump is **on the floor** (z 0–121), the upper above it
  (z 125–246). They push the **X footprint** out (to −222) rather than Y.
- **funnel** (the hopper) rides on the **front (−X)**, its front edge **flush
  with the pumps' front** (so it reads as a front element, center x ≈ −157),
  filling the **+Y half** of the front top clear of the −Y pumps. Its **130 mm**
  square inlet sits flush with the lid (z = 289), tapering down to a spout at
  z = 199; the spout reaches back to V-B. Fits inside the pumps' X envelope.

Inter-tray links are tubing (the topology
[Tube Segments](../../../hardware/topology/fluid-topology.md) tables). The
reservoir's rod-end bosses (y = ±81, high Z) share a bounding-box column with
source-select but are well clear in Z — the generator confirms with a real
solid-intersection test, not bounding boxes.

Overall envelope **299 × 219 × 289 mm** (X × Y × Z), no solid collisions. The
pumps out front set the −X extent (−222); Y stays at 219 (no −Y push).

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/enclosure-contents-assembly/enclosure_contents_assembly.py`
→ `enclosure-contents-assembly.step` (46 solids; translucent reservoir, the
four trays each a distinct color, two slate-gray pumps, and the translucent
funnel). Placement constants — `GAP`, `Y_SHIFT`, `PUMP_GAP`, plus the per-part
rotations and anchors — are at the top of `enclosure_contents_assembly.py` and
in `build()`.
