# Plumbing

## Tubing Strategy

1/4" OD hard tubing (PE or PU, food-grade) with John Guest push-to-connect fittings is the primary tubing for all internal plumbing. The entire fluid system already uses 1/4" push-connect fittings (Beduan solenoid valves, John Guest bulkheads, dock tube stubs), so hard tubing pushes directly into every fitting — zero tools, zero skill.

Silicone tubing is used only in four specific places:

1. **Peristaltic pump heads** — mechanical requirement. Peristaltic pumps need flexible tubing to compress against the rollers.
2. **Faucet cosmetic run** — 1/8" ID black silicone zip-tied to the matte black gooseneck faucet. This is the only user-visible tubing; the black silicone blends with the faucet finish.
3. **Back panel PG7/PG9 cable gland pass-throughs** — flexibility needed for external routing through the gland seals.
4. **Short vibration-dampening segments near the pump cartridge dock** (optional) — absorbs peristaltic pump pulsation to prevent transmitted vibration.

### Why Hard Tubing

- **Push-connect compatibility**: hard tubing seats properly in push-connect fittings. The rigid tube holds against the collet grip and the O-ring seals against the smooth, firm outer surface.
- **Silicone does NOT hold in push-connect fittings**: the silicone deforms under the collet grip and slips out. The old approach required stretching silicone over a hard tube stub inserted into the QC fitting, secured with zip ties — every connection was two connections (one push-fit, one stretch + zip tie). Hard tubing eliminates all of that.
- **Flavor absorption**: PE/PU doesn't absorb flavors the way silicone does. Important for a flavor injection system where users change flavors.
- **Manufacturability**: cut to length, push in. Every unit identical. No zip-tie skill variance.
- **Volume**: the ID difference between 1/8" silicone and ~0.170" hard tubing is negligible (single-digit mL over full line runs).

## Push-Connect Fittings

Push-connect (quick-connect) fittings are used on solenoid valves, tee splitters, elbows, manual valves, and bulkheads. They accept 1/4" OD tubing — push the tube in, the collet grabs it.

Hard tubing works. Silicone does not. Never push silicone directly into a push-connect fitting.

## Platypus Bag Connection

The Platypus Hydration Drink Tube Kit (B07N1T6LNW) comes with blue tubing that has a slightly larger ID than the black silicone's OD. The black silicone slides *inside* the blue tube, creating an overlap/sleeve joint of a couple inches. Zip ties compress the blue tube onto the inner black tube to hold and seal.

Zip tie torque on this joint is a balancing act:

- **Too loose** — leaking under backpressure (see failure mode below).
- **Too tight** — collapses the inner black silicone tube, restricting or blocking flow. Possible but hasn't been an ongoing issue.

The Platypus bag connection transitions to hard tubing via a short silicone-to-hard-tube adapter segment at the bag end of the line.

## Current Flavoring Line Path

Each of the two flavor lines follows this path:

```
Platypus bag
  → blue tube (from Platypus drink tube kit)
    → zip tie joint (blue over black silicone adapter)
      → 1/4" OD hard tubing (push-connect into dispensing solenoid)
        → [dispensing solenoid valve, Beduan 12V NC, 1/4" push-connect]
          → 1/4" OD hard tubing
            → [peristaltic pump, Kamoer 400ml/min 12V] (silicone segment through pump head)
              → 1/4" OD hard tubing → faucet gooseneck
                → 1/8" ID black silicone (cosmetic run, zip-tied to faucet)
                  → dispensing point
```

The two flavor lines are independent and identical in layout. An air switch toggles which flavor is active.

## Water Supply

The Lilium under-sink carbonated water machine has three 1/4" push-connect outputs:

- **"Cold carbonated water"** — currently in use for the soda dispensing system.
- **"Tap water"** — filtered, room temperature (~55-65°F). Available for clean cycle.
- **"Cold water"** — filtered, chilled (35-40°F). Available but not preferred for cleaning.

All three outputs receive the same filtered water input (Waterdrop 15UC-UF inline filter). The carbonated output adds CO2 via TAPRITE dual-gauge regulator.

## Solenoid Valves

Beduan 12V 1/4" Inlet Water Solenoid Valve (B07NWCQJK9), normally closed. $8.99 each.

- Working pressure: 0.02-0.8 MPa (~3-116 PSI)
- 1/4" push-connect fittings (blue collets)
- 12V DC, 4.8W
- Currently 2 installed (one per flavor line, prevent backflow)
- 2 more planned for clean cycle

## Peristaltic Pumps

Kamoer peristaltic pumps (B09MS6C91D), 400ml/min at 12V. $32.55 each.

- Duty-cycle driven by flow meter readings (burst mode, not continuous)
- Burst duration: 50-300ms realistic range
- A stopped pump is not a shutoff valve. Solenoid valves prevent gravity backflow, keep the dispense points primed, and define the active fluid path.
- In the integrated manifold design, the pumps run forward only; source/destination selection is handled by valves. See `hardware/topology/fluid-topology.md`.
- Silicone tubing through the pump head transitions to hard tubing on both the inlet and outlet sides

## Observed Failure: Leak Under Pump Backpressure

One flavor line had insufficiently tightened zip ties at the blue-to-black-silicone joint. A kink (flat spot) formed in the platypus bag as it emptied. The peristaltic pump was pulling hard against the remaining small amount of liquid. The pressure differential was enough to push liquid past the loose zip-tie joint, causing leaking at the bag end of the line.

Fix: tightened the zip tie a small amount. Problem went away immediately.

**Takeaway**: all joints in the line must be snug enough to withstand the pump's suction pressure, especially when bags are near-empty and more prone to kinking.

## Clean Cycle Plumbing (Prototype / Legacy Plan)

This section describes the small retrofit clean-cycle path for the Lilium-based prototype. The integrated appliance uses the fuller valve manifold in `hardware/topology/fluid-topology.md`, which is the canonical forward-looking topology.

Two new solenoid valves (one per flavor line) and a needle valve for flow restriction. Tee fittings and hard tubing sourced from an existing ice maker kit. All connections are 1/4" push-connect with hard tubing.

### Layout

The tee connects between the bag and the dispensing solenoid, so clean water can fill the bag itself (not just the line downstream of the solenoid).

```
Platypus bag → TEE → [dispensing solenoid] → [pump] → dispensing point
                ↑
  water supply → needle valve → [clean solenoid]
```

Each flavor line gets its own clean solenoid and tee. The needle valve and water supply are shared — a second tee splits the water line to both clean solenoids.

### Why a Needle Valve Instead of a Pressure Regulator

Household water pressure is 40-80 PSI. The flavoring lines operate at well under 10 PSI. A pressure regulator in the 1/4" RO ecosystem is designed to protect RO membranes — they reduce to ~60 PSI, not the 5-10 PSI we need, and aren't reliable at the extreme low end of their range.

A needle valve restricts *flow* by physically narrowing the passage with a screw. Turn it down and only a trickle gets through, regardless of input pressure. The pressure issue solves itself because so little water can pass at once. Simpler, cheaper, and more reliable at low flow rates.

### Clean Cycle Sequence

1. **Fill bag with water**: Dispensing solenoid CLOSED, clean solenoid OPEN, pump OFF. Water flows through the needle valve, through the tee, into the bag. The bag fills with clean water, dissolving residual flavoring.
2. **Flush**: Dispensing solenoid OPEN, clean solenoid CLOSED, pump ON. Pump pulls the water (plus dissolved flavoring residue) from the bag, through the dispensing point and out.
3. **Repeat** steps 1-2 as many times as needed until water runs clear.
4. User refills bag with new flavoring (manually now, via hopper system later).

Room-temperature tap water is preferred over chilled — dissolves sugar/flavoring residue faster and doesn't deplete the chiller reservoir.

### Parts

- YKEBVPW 1/4" needle valve flow control (B0FBFVTNLM) — $7.49
- Beduan 12V 1/4" solenoid valve NC x2 (B07NWCQJK9) — $8.99 each
- Tee fittings and hard tubing: from ice maker kit (already on hand)
