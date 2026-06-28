# SMD pads on a plane net are auto-stitched to the plane

A through-hole pin's plated barrel pierces every layer, so on a plane net (GND / 3V3 / 5V /
V12) it commons to the pour at its barrel for free — the carrier's whole power scheme. An SMD
pad is copper on one layer. A pad whose net is poured on a *different* layer is not connected
by the pour; it needs a via down to the plane's layer — the SMD analogue of the THT barrel.

## It's automatic (the core patch)

The `@tscircuit/core` patch does this in the copper-pour render: for each pour, every same-net
SMD pad sitting on another layer gets a stitch via (pad layer → pour layer) before the pour is
solved, so the pour floods onto it. Nothing is declared in the board — `pcba.tsx` carries no
stitch `<pcbtrace>`s. A pad already on its plane's layer (e.g. a top pad on the top V12 island)
connects directly and gets none.

## A stitch via must carry the net

A *bare* via — one with no net — does **not** connect. The copper-pour solver only floods onto
copper whose connectivity key matches the pour's; a netless via is foreign copper, so it gets a
**clearance ring** and the pad stays floating. A bare via-in-pad looks like a stitch in the
layout but is an open circuit.

So the patch nets the via the way the autorouter does: it inserts a `pcb_trace` on the pad's
existing pad→net `source_trace` and points the via's `pcb_trace_id` at it. Connectivity then
runs pad → source_trace → net → via, the via lands in the pour's net, and the solver floods
onto it (no ring). The stitch is also inserted *before* the pour's connectivity key is computed
— the generated `connectivity_net` ids aren't stable across rebuilds, so a via added afterward
keys to a different id and rings.

## Through-vias must be antipadded on the inner planes

A stitch via — like every through-via on the board, including the autorouter's signal vias —
drills through all four layers, so each inner plane it does *not* belong to must clear it with
an antipad, or the plane shorts to the via's net. tscircuit emits a via's `layers` as just its
endpoints (`["top","bottom"]`), and the copper-pour solver only antipads a via on a layer that
is in `via.layers` — so inner-plane pours flood straight over every through-via with no
clearance (GND stitch vias short to 3V3 and 5V; routed signal vias short to whatever plane they
cross). The `@tscircuit/copper-pour-solver` patch fixes this by treating any top-and-bottom via
as present on all layers — the same guard the patch already applies to plated through-holes — so
each inner plane antipads the via (or connects to it, if the via is on that plane's net).

## DRC will not catch a broken stitch

tscircuit's DRC is pour-blind — no check references `pcb_copper_pour` — and its connectivity
check exempts any trace that terminates on a net (`checkSourceTracesHavePcbTraces` skips a
`source_trace` whose `connected_source_net_ids` is non-empty). So a floating SMD plane pad — no
via, or a netless via the pour rings — passes DRC with 0 errors, and so does a through-via that
shorts an inner plane. Don't trust DRC here. Verify the pour geometry by hand: for each pour's
`brep_shape`, point-in-polygon the via center against `outer_ring` minus `inner_rings` (a
ring's *centroid* won't sit at the via when its antipad merges with a connected trace's
clearance — test coverage, not centroids). Each via must be **in copper** on its own net's pour
(connected) and **in a clearance void** on every foreign pour it crosses (antipadded, no short),
with the connectivity map putting the via on the expected net.

## Fabrication

The stitch is via-in-pad — the one geometry an automatic pass can place on any pad without a
clearance search. Order the PCBA with **epoxy-filled + capped vias** (JLCPCB POFV) so reflow
solder doesn't wick down the barrel and starve the joint.
