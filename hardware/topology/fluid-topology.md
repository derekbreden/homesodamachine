# Soda Machine Fluid Topology

## Valves

| Valve | Purpose |
|---|---|
| V-A | Tap water inlet gate |
| V-B | Funnel gate |
| V-C | Shared source → Pump A (channel A select) |
| V-D | Shared source → Pump B (channel B select) |
| V-E | Reservoir A → Pump A inlet |
| V-F | Pump A outlet → Reservoir A |
| V-G | Pump A outlet → flavor tube A |
| V-H | Reservoir B → Pump B inlet |
| V-I | Pump B outlet → Reservoir B |
| V-J | Pump B outlet → flavor tube B |

All valves are normally closed solenoid valves. Flow direction is inlet (I) to outlet (O) only.

**A stopped pump is not a closed valve.** A parked KPHM600 head passes flow both ways — gravity drains a standing line down through one — so every path in this manifold is held by its NC solenoids alone, and each dispense path carries a gate at both ends of its pump. It is also what carries the clean-fill modes below, where tap pressure crosses an idle pump to reach a reservoir.

> **V-K** — the water-supply fill/shutoff solenoid, an 11th valve of the same Beduan NC type — is **not** part of this manifold. It stands on the cold core's crown east of the SeaFlo and gates the carbonator fill on the water-split's branch to that pump's suction, downstream of the ASSE 1022 (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd) and [`assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), driven off the main board's spare `J2.OUT3` channel.

## The pack

[4](LIMB_COUNT) limbs carry the [10](LIMB_VALVES) valves and the [6](TEE_COUNT) junction tees, over [2](PUMP_COUNT) pumps.

**A limb is a lane.** Every valve is straight through and every junction's run takes two valve ports, so a limb is one line of valves and tees butted collet to collet, front to back, on one column of X. A tee dropped on a pump barb by its BRANCH puts its RUN across the head's face, so each pump hands out two of these lanes, 57 mm apart — an inner limb and an outer one, both on its own side of the mirror plane. Channel A stands east of that plane in the machine and channel B west.

**The pack is folded in two** about the hinge the four barb tees' front collets stand on. [8](UPPER_COUNT) bodies ride up onto the second deck and [8](LOWER_COUNT) stay on the first, and the four connections crossing the hinge each become a 180° hairpin. The fold turns every mouth that leaves the pack to face the back of the machine.

Per-limb grouping is in [fluid-topology-limbs.mmd](/hardware/topology/fluid-topology-limbs.mmd); where each body stands and how it is turned is [`manifold-layout/README.md`](/hardware/manifold-layout/README.md).

## Junctions

Six 3-port junctions — **Y-A, Y-B, Y-C, Y-D, Y-F, Y-G** — and every one of them is a **PP0208E Tee** (in-line run + branch). The `Y-` prefix is a stable identifier, not a claim that the fitting is a Y.

**Neither reservoir has a junction.** Each carries **two mouths of its own** — the draw on the bulkhead at the bottom of its wet V, the fill on a bore in its own cap — so each pair's two valves reach one directly and nothing stands between them. Every junction here therefore joins two VALVES, or a valve and a pump barb.

No junction is carried by anything: none of them seats on a body, so each hangs on the collets it joins.

**Y-A and Y-B are the SELECTS-SOURCE junction.** Each stands on its own inner limb's axis, one valve forward of the select it feeds, so its RUN is the limb — the source valve one side, the select the other. The two branches face each other across the mirror plane and meet on segment 6, which is what puts all four ports on one hydraulic node. Every mode opens exactly one of {V-A, V-B} and exactly one of {V-C, V-D}, so the traffic the pair carries is always one source to one select — straight down a limb, or down half a limb, across the bar and down the other half.

**Y-C, Y-D, Y-F and Y-G are the PUMP-BARB junctions.** Each takes its barb by its BRANCH across the collet plate's berth — a short tube over the barb, through the steel, into the collet, the joint that releases when the pump cartridge is pulled — so its RUN lies across the pump head's face and IS the outboard half of a limb, with a valve on each end. Y-C and Y-F take suction, Y-D and Y-G discharge.

Y-A's and Y-B's run ports are numbered from the source end down the limb. On a barb tee the branch takes the number nearest the barb it drops onto — Y-C-3 and Y-F-3 at the two suctions, Y-D-1 and Y-G-1 at the two discharges.

| Junction | Port 1 | Port 2 | Port 3 |
|---|---|---|---|
| Y-A | V-A-O (tap water) | V-C-I (channel A select) | Y-B-3 (crossbar to Y-B) |
| Y-B | V-B-O (funnel) | V-D-I (channel B select) | Y-A-3 (crossbar to Y-A) |
| Y-C | V-C-O (channel A shared source) | V-E-O (reservoir A to pump return) | P-A-I (pump A inlet) |
| Y-D | P-A-O (pump A outlet) | V-F-I (pump to reservoir A) | V-G-I (pump to flavor tube A) |
| Y-F | V-D-O (channel B shared source) | V-H-O (reservoir B to pump return) | P-B-I (pump B inlet) |
| Y-G | P-B-O (pump B outlet) | V-J-I (pump to flavor tube B) | V-I-I (pump to reservoir B) |

## Tube Segments

Each segment is one labelled edge in [fluid-topology-manifold.mmd](/hardware/topology/fluid-topology-manifold.mmd). [`_scorecard.py`](/hardware/manifold-layout/_scorecard.py) reads these tables as the flavor connection inventory the enclosure assembly owes, and each one is made one of four ways: butted collet to collet, folded into a hairpin across the hinge, turned out of a deck plane, or drawn as a swept run by [`_lines.py`](/hardware/manifold-layout/_lines.py). An edge that carries no tube says so on its label; the rest the chart names by segment id alone. How every one of them is made, what it measures and how many corners it turns is what a bare run of [`_fluid_topology_sync.py`](/hardware/topology/_fluid_topology_sync.py) prints — no length is drawn on a chart, so none of them can go stale where nothing reads it.

Four of the seven conduits in the cold core's top cap are this circuit's: a fill and a draw for each reservoir.

### Shared

| # | From | To | Notes |
|---|---|---|---|
| 1 | water-split to-flavor | flow-regulator inlet | Off the ASSE 1022's split, west lane (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd)) |
| 2 | flow-regulator outlet | V-A-I | Across the machine and up onto the folded deck |
| 3 | V-A-O | Y-A-1 | Quarter turn out of the deck plane, then the step aft over the core's crown |
| 4 | Funnel bottom | V-B-I | Gravity drain |
| 5 | V-B-O | Y-B-1 | The mirror of segment 3 |
| 6 | Y-A-3 | Y-B-3 | The crossbar — branch to branch, face to face |
| 7 | Y-A-2 | V-C-I | Butted |
| 8 | Y-B-2 | V-D-I | Butted |

### Channel A

| # | From | To | Notes |
|---|---|---|---|
| 9 | V-C-O | Y-C-1 | Across the hinge — one 180° hairpin on the A1 limb's column |
| 10 | V-E-O | Y-C-2 | Butted |
| 11 | Y-C-3 | P-A-I | The barb tube: over the suction barb, through the collet plate, into the tee's branch — the cartridge's release joint |
| 12 | P-A-O | Y-D-1 | The barb tube: over the discharge barb, through the collet plate, into the tee's branch |
| 13 | Y-D-2 | V-F-I | Butted |
| 14 | V-F-O | Reservoir A fill bore | Aft and down the `reservoir-a-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 16 | Reservoir A draw | V-E-I | Up the `reservoir-a` cap conduit, off the bulkhead at the bottom of the wet V |
| 17 | Y-D-3 | V-G-I | Across the hinge — one 180° hairpin on the A2 limb's column |
| 18 | V-G-O | bulkhead-flavor-a tube-in | Aft over the pack and across the machine to the +Y wall of back-top |

### Channel B

| # | From | To | Notes |
|---|---|---|---|
| 19 | V-D-O | Y-F-1 | Across the hinge — one 180° hairpin on the B1 limb's column |
| 20 | V-H-O | Y-F-2 | Butted |
| 21 | Y-F-3 | P-B-I | The barb tube: over the suction barb, through the collet plate, into the tee's branch — the cartridge's release joint |
| 22 | P-B-O | Y-G-1 | The barb tube: over the discharge barb, through the collet plate, into the tee's branch |
| 23 | Y-G-3 | V-I-I | Butted |
| 24 | V-I-O | Reservoir B fill bore | Aft and down the `reservoir-b-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 26 | Reservoir B draw | V-H-I | Up the `reservoir-b` cap conduit, off the bulkhead at the bottom of the wet V |
| 27 | Y-G-2 | V-J-I | Across the hinge — one 180° hairpin on the B2 limb's column |
| 28 | V-J-O | bulkhead-flavor-b tube-in | Aft to the +Y wall of back-top |

---

## Operations — Valve States

Open valves listed; all others closed.

This table is canonical for the integrated flavor manifold. Pumps run forward only. Valve state selects whether a pump draws from a reservoir, the funnel, or tap water and whether the outlet returns to a reservoir or goes to the gooseneck. Normally closed solenoid valves define the closed state and keep the dispense paths primed.

### Dispense A

- Open: V-E, V-G
- Pump A: ON
- Path: Reservoir A → V-E → P-A → V-G → flavor tube A

### Dispense B

- Open: V-H, V-J
- Pump B: ON
- Path: Reservoir B → V-H → P-B → V-J → flavor tube B

### Fill from the funnel → Reservoir A

- Open: V-B, V-C, V-F
- Pump A: ON
- Path: Funnel → V-B → V-C → P-A → V-F → Reservoir A

### Fill from the funnel → Reservoir B

- Open: V-B, V-D, V-I
- Pump B: ON
- Path: Funnel → V-B → V-D → P-B → V-I → Reservoir B

### Clean Water Fill → Reservoir A

- Open: V-A, V-C, V-F
- Pump A: OFF (line pressure through idle pump)
- Path: Tap → V-A → V-C → P-A (idle) → V-F → Reservoir A

### Clean Water Fill → Reservoir B

- Open: V-A, V-D, V-I
- Pump B: OFF (line pressure through idle pump)
- Path: Tap → V-A → V-D → P-B (idle) → V-I → Reservoir B

### Clean Flush A (water out)

- Open: V-E, V-G
- Pump A: ON
- Path: Reservoir A → V-E → P-A → V-G → flavor tube A
- (Same as Dispense A)

### Clean Flush B (water out)

- Open: V-H, V-J
- Pump B: ON
- Path: Reservoir B → V-H → P-B → V-J → flavor tube B
- (Same as Dispense B)

### Air Purge In → Reservoir A

- Open: V-B, V-C, V-F
- Pump A: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-C → P-A → V-F → Reservoir A
- (Same path as the funnel fill)

### Air Purge In → Reservoir B

- Open: V-B, V-D, V-I
- Pump B: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-D → P-B → V-I → Reservoir B

### Air Purge Out A

- Open: V-E, V-G
- Pump A: ON
- Path: Reservoir A → V-E → P-A → V-G → flavor tube A
- (Same as Dispense A)

### Air Purge Out B

- Open: V-H, V-J
- Pump B: ON
- Path: Reservoir B → V-H → P-B → V-J → flavor tube B
- (Same as Dispense B)

### Air Purge Through A (source to the gooseneck)

- Open: V-B, V-C, V-G
- Pump A: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-C → P-A → V-G → flavor tube A
- Reservoir A is not on the path; V-F stays closed and the whole discharge goes to flavor tube A

### Air Purge Through B (source to the gooseneck)

- Open: V-B, V-D, V-J
- Pump B: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-D → P-B → V-J → flavor tube B
- Reservoir B is not on the path; V-I stays closed

The two Through states with the two Purge In states above them air-fill every segment the flavor
manifold carries except the two reservoir draws, whose ports stand under the liquid.
[`/hardware/service/pump-replacement.md`](/hardware/service/pump-replacement.md) runs the four of
them as the dry cycle before a quadrant lift.

## Sources
[value](NAME) texts are updated by:
- `/hardware/topology/_fluid_topology_sync.py`
