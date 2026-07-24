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

All valves are normally closed solenoid valves. Flow direction is inlet (I) to outlet (O) only.

> **V-K** — the water-supply fill/shutoff solenoid, an 11th valve of the same Beduan NC type — is **not** part of this manifold. It gates the carbonator supply line as the machine's master inlet, upstream of the ASSE 1022 (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd) and [`assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), driven off the board's spare `J2.OUT3` channel.

## Junctions

Eight 3-port junctions. **Y-A and Y-B are PP2308E Y-dividers** (the source-select tray's trident fittings); the other six — **Y-C, Y-D, Y-E, Y-F, Y-G, Y-H** — are **PP0208E Tees** (in-line run + branch). The `Y-` prefix is a stable identifier, not a claim that the fitting is a Y. Per-tray grouping is in [fluid-topology-trays.mmd](/hardware/topology/fluid-topology-trays.mmd).

| Junction | Port 1 | Port 2 | Port 3 |
|---|---|---|---|
| Y-A | V-A-O (tap water) | V-B-O (hopper) | Y-B-1 (to channel split) |
| Y-B | Y-A-3 (from tap/hopper merge) | V-C-I (channel A select) | V-D-I (channel B select) |
| Y-C | V-C-O (channel A shared source) | V-E-O (bag A to pump return) | P-B-I (pump B inlet) |
| Y-D | P-B-O (pump B outlet) | V-F-I (pump to bag A) | V-G-I (pump to nozzle A) |
| Y-E | V-F-O (pump to bag A return) | Bag A port | V-E-I (bag A to pump) |
| Y-F | V-D-O (channel B shared source) | V-H-O (bag B to pump return) | P-A-I (pump A inlet) |
| Y-G | P-A-O (pump A outlet) | V-I-I (pump to bag B) | V-J-I (pump to nozzle B) |
| Y-H | V-I-O (pump to bag B return) | Bag B port | V-H-I (bag B to pump) |

## Tube Segments

Each segment is one labelled edge in [fluid-topology-manifold.mmd](/hardware/topology/fluid-topology-manifold.mmd). `scorecard.py` reads these tables as `fluid-1` … `fluid-28`, the connection inventory the enclosure must carry, and [`_lines.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_lines.py) authors each one port to port.

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
| 9 | V-C-O | Y-C-1 | |
| 10 | V-E-O | Y-C-2 | |
| 11 | Y-C-3 | P-B-I | |
| 12 | P-B-O | Y-D-1 | |
| 13 | Y-D-2 | V-F-I | |
| 14 | V-F-O | Y-E-1 | |
| 15 | Bag A port | Y-E-2 | |
| 16 | Y-E-3 | V-E-I | |
| 17 | Y-D-3 | V-G-I | |
| 18 | V-G-O | Nozzle A | |

### Channel B

| # | From | To | Notes |
|---|---|---|---|
| 19 | V-D-O | Y-F-1 | |
| 20 | V-H-O | Y-F-2 | |
| 21 | Y-F-3 | P-A-I | |
| 22 | P-A-O | Y-G-1 | |
| 23 | Y-G-2 | V-I-I | |
| 24 | V-I-O | Y-H-1 | |
| 25 | Bag B port | Y-H-2 | |
| 26 | Y-H-3 | V-H-I | |
| 27 | Y-G-3 | V-J-I | |
| 28 | V-J-O | Nozzle B | |

---

## Operations — Valve States

Open valves listed; all others closed.

This table is canonical for the integrated flavor manifold. Pumps run forward only. Valve state selects whether a pump draws from a bag, hopper, or tap-water source and whether the outlet returns to a bag or goes to the nozzle. Normally closed solenoid valves define the closed state and keep the dispense paths primed.

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
