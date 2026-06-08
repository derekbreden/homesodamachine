# Funnel (hopper)

The hopper you pour batch liquid into. It drains through its spout to **V-B**
on the [source-select tray](../../../../hardware/printed-parts/valve-manifold/source-select-tray/)
— fluid topology [segment 4](../../../../hardware/topology/fluid-topology.md),
"Hopper funnel bottom → V-B-I". A **pour-through guide**, not a batch reservoir:
what you pour gets pumped straight on to a bag.

## Shape

A **130 mm square inlet** tapering over 78 mm — a square-to-round loft — to a
**round spout**: 12 mm long, 10 mm OD, **6.5 mm bore** to match the 1/4 in tube
line used elsewhere (the reservoir's port holes). Walls are **2 mm**, open
through both ends. **90 mm** tall overall.

Local frame: centered on Z (x = y = 0), spout outlet on Z = 0, inlet opening up
at Z = 90. In the [enclosure assembly](../../enclosure-assembly/) it rides on
the **front (−X)**, its front edge flush with the pumps' front,
filling the +Y half of the front top (inlet flush with the lid); the spout
reaches back to V-B.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/printed-parts/funnel/funnel.py`
→ `funnel.step`. Dimensions are the constants at the top of `funnel.py`
(`inlet_side`, `wall`, `taper_height`, `spout_od/id`, `spout_length`).
