# SMD pads on a plane net are auto-stitched to the plane

A through-hole pin's plated barrel pierces every layer, so on a plane net (GND / 3V3 / 5V /
V12) it commons to the pour at its barrel for free — the board's through-hole connector power scheme. An SMD
pad is copper on one layer. A pad whose net is poured on a *different* layer is not connected
by the pour; it needs a via down to the plane's layer — the SMD analogue of the THT barrel.

## It's automatic (the core patch)

The `@tscircuit/core` patch does this in the copper-pour render: every SMD pad whose net is
poured on another layer gets a **through** stitch via (top↔bottom) carrying that net. Nothing is
declared in the board — `pcba.tsx` has no stitch `<pcbtrace>`s. A pad already on its plane's
layer (e.g. a top pad on the top V12 island) connects directly and gets none. Two details have
to hold together:

- **One pass, all nets, before any pour solves.** Pours render in arbitrary order; if a pad's
  via were created only by its own net's pour, a different-net pour solving first would flood
  over the not-yet-existing via and short to it. So the first pour to render stitches *every*
  poured net's cross-layer pads (idempotent — later pours skip a pad that already has a via), and
  every pour's brep then antipads every foreign via.
- **Through, never blind.** The via spans top↔bottom even when its plane is an inner layer —
  JLCPCB drills through-holes only, not blind vias. The through-via antipad guard (below)
  connects it to its net's plane wherever that sits and clears the rest, so a top 3V3 pad gets a
  top↔bottom via that floods onto the inner1 3V3 plane and is antipadded on 5V and GND.

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

## The router must reserve the stitch spot

The stitch via is created in the copper-pour render, which runs *after* autorouting — so the
autorouter doesn't know the via is coming and will lay a different-net trace across that spot on
the bottom (routable) layer, shorting to the via. So the same `@tscircuit/core` patch, where the
router builds its obstacle list, drops a **stitch-keepout** (the via footprint, on the opposite
outer layer the through via crosses) at every such pad. The router routes other nets around it;
the pour render then drops the real via in the reserved gap. DRC can't catch this short either
(the via lands post-routing, post-DRC), so the keepout is the only thing between a dropped signal
and a GND short.

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
