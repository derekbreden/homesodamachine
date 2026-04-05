---
name: Plumbing connection details and failure modes
description: Physical details of tubing types, connection methods, observed failure modes, water supply, and clean cycle plumbing plan
type: project
---

## Tubing Strategy

1/4" OD hard tubing (PE or PU) with John Guest push-to-connect fittings for ALL internal plumbing. Hard tubing pushes directly into every fitting in the system (Beduan solenoid valves, John Guest bulkheads, dock tube stubs) — zero tools, zero skill.

Silicone tubing used ONLY in four places:
1. Peristaltic pump heads (mechanical requirement)
2. Faucet cosmetic run (1/8" ID black silicone zip-tied to matte black gooseneck, visible to user)
3. Back panel PG7/PG9 cable gland pass-throughs (flexibility for external routing)
4. Short vibration-dampening segments near pump cartridge dock (optional, absorbs pulsation)

Why hard tubing wins over silicone-everywhere:
- Silicone does NOT hold in push-connect fittings (deforms and slips out)
- PE/PU doesn't absorb flavors the way silicone does
- Cut to length, push in — every unit identical, no zip-tie skill variance
- Volume difference vs 1/8" ID silicone is negligible (single-digit mL over full runs)

## Platypus Bag Connection

- Platypus Hydration Drink Tube Kit (B07N1T6LNW) blue tubing has slightly larger ID than black silicone OD
- Black silicone slides *inside* blue tube, creating overlap/sleeve joint of a couple inches
- Zip ties compress the blue tube onto the inner black tube to seal
- Zip tie torque balancing act: too loose → leaking under backpressure; too tight → collapses inner tube
- Transitions to hard tubing via short silicone-to-hard-tube adapter at the bag end

## Available Spare Parts

- Unopened ice maker kit: multiple tees, Ys, single connectors, elbows, manual (on/off) valves, and a large winding of 1/4" OD hard tubing — more than enough for clean cycle plumbing
- All standard 1/4" push-connect, same ecosystem as existing solenoid valves

## Current Flavoring Line Path

```
Platypus bag → blue tube → (zip tie joint) → hard tubing → [dispensing solenoid] → hard tubing → [peristaltic pump (silicone through head)] → hard tubing → faucet → 1/8" black silicone cosmetic run → dispensing point
```

## Observed Failure: Leak Under Pump Backpressure

- One flavor line had insufficiently tightened zip ties at the blue-to-black-silicone joint
- A kink (flat spot) formed in the platypus bag as it emptied
- The peristaltic pump was pumping hard against the remaining small amount of liquid
- The pressure differential was enough to push liquid past the loose zip-tie joint, causing leaking
- Fix: tightened the zip tie a small amount — problem went away immediately

## Water Supply (Clean Cycle)

- Lilium under-sink carbonated water machine has 3 outputs: "tap water", "cold water", "cold carbonated water"
- All outputs are 1/4" push-connect
- Only "cold carbonated water" is currently in use
- "Tap water" output (filtered, room temp ~55-65°F) will be used for clean cycle
  - Room temp preferred over cold (35-40°F): dissolves sugar/flavoring residue faster, doesn't deplete chiller reservoir
- Direct 1/4" push-connect connection — no adapters needed

## Clean Cycle Plumbing Plan (March 2026)

Tee connects between bag and dispensing solenoid, so clean water fills the bag itself. All connections are 1/4" push-connect with hard tubing.

```
Platypus bag → TEE → [dispensing solenoid] → [pump] → dispensing point
                ↑
  water supply → needle valve → [clean solenoid]
```

Needle valve and water supply shared; a second tee splits to both clean solenoids.

### Clean Cycle Sequence

1. **Fill bag**: dispensing solenoid CLOSED, clean solenoid OPEN, pump OFF → water fills the bag
2. **Flush**: dispensing solenoid OPEN, clean solenoid CLOSED, pump ON → pump empties the bag out the dispensing point
3. **Repeat** steps 1-2 until water runs clear
4. User refills bag with new flavoring (manually now, via hopper later)

### Parts Ordered (March 2026)

- YKEBVPW 1/4" needle valve flow control (B0FBFVTNLM) — $7.49
- Beduan 12V 1/4" solenoid valve NC, qty 2 (B07NWCQJK9) — $8.99 each
- Tee fittings and hard tubing: already available from ice maker kit
- Total: ~$25.47

## Documentation

- `docs/plumbing.md` covers tubing strategy, connection methods, current line paths, water supply, solenoid valves, pumps, failure modes, and clean cycle plan
