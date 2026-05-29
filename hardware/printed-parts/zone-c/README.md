# Zone C (front-top)

The front-top zone of the enclosure, reached by opening the kitchen cabinet door and lifting the appliance's top door. Zone C holds the flavor fill interface and the peristaltic pump cartridge, stacked under that one door and exposed in the order they're touched. Zone framing and the other three zones: [`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).

## One door, two layers

A single top-face door — the hopper door, centered across the width and anchored to the front (geometry in [`/hardware/printed-parts/enclosure/drawings/line-art/_appliance_model.py`](/hardware/printed-parts/enclosure/drawings/line-art/_appliance_model.py)). Under it, top to bottom:

- **The funnel.** A silicone funnel that seats in the door opening as the hopper. It lifts out by hand for the dishwasher — flavor concentrate is sticky, so the cleanable interface has to come all the way out. Weekly-touch item.
- **The pump cartridge.** Lifting the funnel out exposes the replaceable pump cartridge beneath it. Rare-touch item — reached only to swap a worn pump.

The frequent-access piece sits over the rare-access piece, so one opening serves both fill and pump service, and the funnel covers the pumps the rest of the time.

## The funnel

One shared funnel, sized to take a pour from a SodaStream concentrate bottle without splash. Silicone, removable, dishwasher-safe. Its outlet feeds the pump inlet; a source-selection solenoid routes the pour to the correct internal flavor reservoir, so one funnel serves both flavors — the valve manifold, not the funnel, picks the channel. Valve states: [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md).

The rear bag-in-box adapter ([`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md)) is the alternative fill path for customers running commercial syrup; it feeds the same reservoirs through the pump and bypasses the funnel.

## The pump cartridge

Two Kamoer peristaltic pumps (1/4" OD LLDPE through the head) in a cartridge that swaps without tools — John Guest quick-connects and a palm-squeeze release plate. The pumps pull flavor from the internal hard reservoirs nested in the cold core (Zone A, [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/)) and inject it at the dispense nozzle alongside the carbonated water. Direction is forward-only; fill, dispense, and clean are selected by the valve manifold. The silicone pump tubing is the wear item — the reason the cartridge is what you reach when the funnel comes out.

Cartridge geometry: [`/hardware/printed-parts/flavor/pump-case/`](/hardware/printed-parts/flavor/pump-case/). Tube: [`/hardware/printed-parts/flavor/peristaltic-tube/`](/hardware/printed-parts/flavor/peristaltic-tube/).

## Lives in other zones

- Flavor reservoirs and level sensing — Zone A, nested in the foam shell ([`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/)).
- Valve manifold — internal, placement flexible.
- Dispense spout and rotary display — front face ([`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md)).
