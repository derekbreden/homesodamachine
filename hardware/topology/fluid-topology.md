# Soda Machine Fluid Topology

## Valves

| Valve | Purpose |
|---|---|
| V-A | Tap water inlet gate |
| V-B | Hopper funnel gate |
| V-C | Shared source → Pump A (channel A select) |
| V-D | Shared source → Pump B (channel B select) |
| V-E | Bag A → Pump A inlet |
| V-F | Pump A outlet → Bag A |
| V-G | Pump A outlet → Nozzle A |
| V-H | Bag B → Pump B inlet |
| V-I | Pump B outlet → Bag B |
| V-J | Pump B outlet → Nozzle B |
| V-K-A | BiB A inlet gate (channel A) |
| V-K-B | BiB B inlet gate (channel B) |

All valves are normally closed solenoid valves. Flow direction is inlet (I) to outlet (O) only.

## Y-Junctions

| Junction | Port 1 | Port 2 | Port 3 |
|---|---|---|---|
| Y-A | V-A-O (tap water) | V-B-O (hopper) | Y-B-1 (to channel split) |
| Y-B | Y-A-3 (from tap/hopper merge) | V-C-I (channel A select) | V-D-I (channel B select) |
| Y-KA | V-C-O (channel A shared source) | V-K-A-O (channel A BiB) | Y-C-1 (to pump A inlet) |
| Y-C | Y-KA-3 (channel A source merge) | V-E-O (bag A to pump return) | P-A-I (pump A inlet) |
| Y-D | P-A-O (pump A outlet) | V-F-I (pump to bag A) | V-G-I (pump to nozzle A) |
| Y-E | V-F-O (pump to bag A return) | Bag A port | V-E-I (bag A to pump) |
| Y-KB | V-D-O (channel B shared source) | V-K-B-O (channel B BiB) | Y-F-1 (to pump B inlet) |
| Y-F | Y-KB-3 (channel B source merge) | V-H-O (bag B to pump return) | P-B-I (pump B inlet) |
| Y-G | P-B-O (pump B outlet) | V-I-I (pump to bag B) | V-J-I (pump to nozzle B) |
| Y-H | V-I-O (pump to bag B return) | Bag B port | V-H-I (bag B to pump) |

## Tube Segments

### Shared

| # | From | To | Notes |
|---|---|---|---|
| 1 | Tap water source | Flow regulator inlet | |
| 2 | Flow regulator outlet | V-A-I | |
| 3 | V-A-O | Y-A-1 | |
| 4 | Hopper funnel bottom | V-B-I | |
| 5 | V-B-O | Y-A-2 | |
| 6 | Y-A-3 | Y-B-1 | |
| 7 | Y-B-2 | V-C-I | |
| 8 | Y-B-3 | V-D-I | |

### Channel A

| # | From | To | Notes |
|---|---|---|---|
| 9 | BiB A connector | V-K-A-I | |
| 10 | V-K-A-O | Y-KA-2 | |
| 11 | V-C-O | Y-KA-1 | |
| 12 | Y-KA-3 | Y-C-1 | |
| 13 | V-E-O | Y-C-2 | |
| 14 | Y-C-3 | P-A-I | |
| 15 | P-A-O | Y-D-1 | |
| 16 | Y-D-2 | V-F-I | |
| 17 | V-F-O | Y-E-1 | |
| 18 | Bag A port | Y-E-2 | |
| 19 | Y-E-3 | V-E-I | |
| 20 | Y-D-3 | V-G-I | |
| 21 | V-G-O | Nozzle A | |

### Channel B

| # | From | To | Notes |
|---|---|---|---|
| 22 | BiB B connector | V-K-B-I | |
| 23 | V-K-B-O | Y-KB-2 | |
| 24 | V-D-O | Y-KB-1 | |
| 25 | Y-KB-3 | Y-F-1 | |
| 26 | V-H-O | Y-F-2 | |
| 27 | Y-F-3 | P-B-I | |
| 28 | P-B-O | Y-G-1 | |
| 29 | Y-G-2 | V-I-I | |
| 30 | V-I-O | Y-H-1 | |
| 31 | Bag B port | Y-H-2 | |
| 32 | Y-H-3 | V-H-I | |
| 33 | Y-G-3 | V-J-I | |
| 34 | V-J-O | Nozzle B | |

---

## Operations — Valve States

Open valves listed; all others closed.

This table is canonical for the integrated flavor manifold. Pumps run forward only. Valve state, not pump reversal, selects whether a pump draws from a bag, hopper, BiB input, or tap-water source and whether the outlet returns to a bag or goes to the nozzle. Stopped peristaltic pumps are not used as shutoff valves; normally closed solenoid valves define the closed state and keep the dispense paths primed.

### Dispense A

- Open: V-E, V-G
- Pump A: ON
- Path: Bag A → V-E → P-A → V-G → Nozzle A

### Dispense B

- Open: V-H, V-J
- Pump B: ON
- Path: Bag B → V-H → P-B → V-J → Nozzle B

### Fill from Hopper → Bag A

- Open: V-B, V-C, V-F
- Pump A: ON
- Path: Hopper → V-B → V-C → P-A → V-F → Bag A

### Fill from Hopper → Bag B

- Open: V-B, V-D, V-I
- Pump B: ON
- Path: Hopper → V-B → V-D → P-B → V-I → Bag B

### Fill from BiB → Bag A

- Open: V-K-A, V-F
- Pump A: ON
- Path: BiB A → V-K-A → P-A → V-F → Bag A

### Fill from BiB → Bag B

- Open: V-K-B, V-I
- Pump B: ON
- Path: BiB B → V-K-B → P-B → V-I → Bag B

### Clean Water Fill → Bag A

- Open: V-A, V-C, V-F
- Pump A: OFF (line pressure through idle pump)
- Path: Tap → V-A → V-C → P-A (idle) → V-F → Bag A

### Clean Water Fill → Bag B

- Open: V-A, V-D, V-I
- Pump B: OFF (line pressure through idle pump)
- Path: Tap → V-A → V-D → P-B (idle) → V-I → Bag B

### Clean Flush A (water out)

- Open: V-E, V-G
- Pump A: ON
- Path: Bag A → V-E → P-A → V-G → Nozzle A
- (Same as Dispense A)

### Clean Flush B (water out)

- Open: V-H, V-J
- Pump B: ON
- Path: Bag B → V-H → P-B → V-J → Nozzle B
- (Same as Dispense B)

### Air Purge In → Bag A

- Open: V-B, V-C, V-F
- Pump A: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-C → P-A → V-F → Bag A
- (Same path as hopper fill)

### Air Purge In → Bag B

- Open: V-B, V-D, V-I
- Pump B: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-D → P-B → V-I → Bag B

### Air Purge Out A

- Open: V-E, V-G
- Pump A: ON
- Path: Bag A → V-E → P-A → V-G → Nozzle A
- (Same as Dispense A)

### Air Purge Out B

- Open: V-H, V-J
- Pump B: ON
- Path: Bag B → V-H → P-B → V-J → Nozzle B
- (Same as Dispense B)
