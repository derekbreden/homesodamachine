# Pump Cartridge Buckle & Docking Interface

## Context

The pump case houses a single peristaltic pump. The user replaces two of these cartridges when pumps wear out. Each cartridge has a flat +Z face that slots into a dock on the device.

The dock is roughly the inverse of the pump case shape, reaching up around 1/4 to 1/3 of the way around to hug the cartridge and guide it toward alignment.

## The +Z face interface

Four parallel protrusions on the flat +Z face, all inserted in one motion:

- **Two 1/4" hard RO tubes** — liquid in/out. Sealed by custom TPU printed sleeve-o-ring-things in the dock.
- **Two metal rods** — 12V and GND. Banana clip style contacts in the dock — smooth insertion, solid grip, no snap or lock of their own.

The symmetry of "two tubes go in, two rods go in" is intentional. The user doesn't need to think about which is which. Push it in, buckle it down, done.

### Power contacts

Just two conductors needed (12V + GND, single motor per cartridge, H-bridge on the device side). Banana-style spring contacts chosen because:

- No snap or latch — the buckle provides all retention
- Smooth insertion with solid grip
- Standard, cheap, available everywhere
- Self-centering in their sockets
- Low voltage, low current (~500mA), well within ratings

Brass or nickel-plated brass rod press-fit into the printed case, protruding the same distance as the tubes. Polarity protection via asymmetric placement (the tube positions and cartridge shape already make it non-reversible).

### Liquid near electrical — not a concern

The pump-cartridge interface and wet-control hardware live on the 12V DC bus: solenoid valves with liquid flowing through them, the diaphragm pump pushing water, and the peristaltic pump cartridge all share the same appliance enclosure. The harvested ice-maker compressor is a separate switched 120 VAC load. Two low-voltage cartridge contacts next to two sealed tubes is not the risk to worry about.

## The buckle

The buckle is the only thing that feels "locked." Everything else (tubes, power contacts) just slides in.

The buckle must:
- Press the cartridge down firmly to seal the tubes into the TPU sleeves
- Feel secure and intentional
- Be tool-free
- Be obvious to the user how it works

### Candidate approaches

**Flaps on the dock side:** Fold out of the way to insert/remove the cartridge, fold back down on top after insertion. The flaps carry the buckle latch pieces.

**Arms on the cartridge side:** Hinged arms that lie flat against the cartridge during insertion. Once seated, the user flips them outward and they hook under a lip on the dock. The lever action multiplies closing force — like a ski boot buckle. To remove: flip arms flat, pull straight out.

The arms-on-cartridge approach has an advantage: when the cartridge is out of the dock, it's obvious how it works. The user can see the arms, see where they hook. No hidden mechanism inside the dock to figure out. The mechanical advantage of the lever puts the force exactly where it's needed — pressing the tubes into their seals.

### Open questions

- Exact placement of power rods relative to tubes on the +Z face
- How far the dock reaches around the cartridge (1/4? 1/3?)
- Whether the lever arms are printed as part of the cartridge or separate pieces
- Spring force vs lever geometry for the right "locked down" feel
- How to make the buckle obvious to a first-time user without instructions
