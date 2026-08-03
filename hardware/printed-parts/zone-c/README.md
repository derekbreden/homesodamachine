# Zone C (front-top)

The front-top zone of the enclosure. Zone C holds the flavor fill interface
and the two peristaltic pumps, stacked in the order they're touched. Zone
framing and the other three zones:
[`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).

## One opening, two layers

One rectangular opening spans the top wall behind the display facet
([`../enclosure/enclosure/`](/hardware/printed-parts/enclosure/enclosure/)
`_hopper_hole`). In it, top to bottom:

- **The funnel.** A wide silicone funnel that drops into the opening as the
  hopper — its flat brim resting on the enclosure top is the only visible
  edge. It lifts out by hand for
  the dishwasher — flavor concentrate is sticky, so the cleanable interface
  has to come all the way out. Weekly-touch item. Detail:
  [`hopper-funnel/`](/hardware/printed-parts/zone-c/hopper-funnel/).
- **The pumps.** Lifting the funnel out exposes the two peristaltic pumps
  beneath it. Rare-touch item — reached only to swap a worn pump.

The frequent-access piece sits over the rare-access piece, so one opening
serves both fill and pump service, and the funnel covers the pumps the rest
of the time.

## The funnel

One shared basin, sized to take a full 440 mL SodaStream concentrate bottle
dumped in one pour. Silicone, removable, dishwasher-safe; cast in the
two-piece printed mold
([`hopper-funnel-mold/`](/hardware/printed-parts/zone-c/hopper-funnel-mold/)).
Its spout feeds the V-B hopper gate on the V-A/V-B tray; the valve
manifold, not the funnel, picks the channel, so one funnel serves both
flavors. Valve states:
[`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md).

## The pumps

Two Kamoer peristaltic pumps (1/4" OD LLDPE through the head), off-the-shelf
assemblies. The pumps pull flavor from the internal hard reservoirs nested in
the cold core (Zone A,
[`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/))
and inject it at the dispense nozzle alongside the carbonated water.
Direction is forward-only; fill, dispense, and clean are selected by the
valve manifold. The silicone pump tubing is the wear item — the reason the
pumps are what you reach when the funnel comes out. The funnel's throat drops
the clear column between the two pumps; the enclosure mount is an open item.

## Lives in other zones

- Flavor reservoirs and level sensing — Zone A, nested in the foam shell ([`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/)).
- Valve manifold — the Zone-B trays on the foam-cap top ([`/hardware/printed-parts/valve-manifold/`](/hardware/printed-parts/valve-manifold/)).
- Dispense spout and config display — front face ([`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md)).
