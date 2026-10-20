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

**A stopped pump is not a closed valve.** A parked KPHM600 head passes flow both ways — gravity drains a standing line down through one — so every path in this manifold is held by its NC solenoids alone, and each dispense path carries a gate at both ends of its pump. It is also what carries the clean-fill modes below, where tap water, throttled by the flow regulator (the needle valve on V-A's feed), crosses an idle pump to reach a reservoir.

> **V-K** — the water-supply fill/shutoff solenoid, an 11th valve of the same Beduan NC type — is **not** part of this manifold. It stands on the cold core's crown east of the G Ganen pump and gates the carbonator fill on the water-split's branch to that pump's suction, downstream of the ASSE 1022 (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd) and [`assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), driven off the main board's spare `J2.OUT3` channel.

## The pack

[4](LIMB_COUNT) limbs connect the [10](LIMB_VALVES) valves, [6](TEE_COUNT) three-port junctions and [2](PUMP_COUNT) pumps. The junctions comprise [2](PURCHASED_TEE_COUNT) purchased tees and [4](TPU_JUNCTION_COUNT) permanent printed TPU junctions.

**A limb is a lane.** Each pump has an inner and outer valve lane. Channel A stands east of the mirror plane and channel B west. The two source tees meet their neighbouring valves face to face. At the pump wall, each permanent TPU junction receives a prepared pump's LLDPE stub, connects upward to its fore valve through a straight LLDPE link and sends its lower arm aft at 45°. A fixed printed return connects that arm to the aft valve through two straight links.

**The pack occupies two fixed decks.** The topology assigns [8](UPPER_COUNT) logical nodes to the upper deck and [8](LOWER_COUNT) to the lower one. Four compound TPU returns contain the lower changes of direction. Their straight LLDPE links do not make those bends. The source pair's formed R14 paths on segments 3 and 5 have their separate retained scope.

Per-limb grouping is in [fluid-topology-limbs.mmd](/hardware/topology/fluid-topology-limbs.mmd); where each body stands and how it is turned is [`manifold-layout/README.md`](/hardware/manifold-layout/README.md).

## Junctions

The six three-port junction identifiers are **Y-A, Y-B, Y-C, Y-D, Y-F and Y-G**. Y-A and Y-B are purchased PP0208E tees. Y-C, Y-D, Y-F and Y-G are permanent printed TPU junctions with an orthogonal pump inlet/upper outlet and a lower arm angled 45° aft. The `Y-` identifiers and numbered hydraulic ports remain the topology's names.

**Neither reservoir has a junction.** Each carries **two mouths of its own**, both bores in its own cap — the fill, ending above the liquid, and the draw, whose line goes on down to the floor as the reservoir's dip tube — so each pair's two valves reach one directly and nothing stands between them. Every junction here therefore joins two VALVES, or connects the valves to a pump through its permanent receiver.

Y-A and Y-B inherit location from their fixed face-to-face valve joints. The closed PET-GF wall locates Y-C, Y-D, Y-F and Y-G in X/Z; a flat interior keeper captures each junction in Y. Their returns and the return block they snap into remain stationary during a pump change.

**Y-A and Y-B are the SELECTS-SOURCE junction.** Each stands on its own inner limb's axis, one valve forward of the select it feeds, so its RUN is the limb — the source valve one side, the select the other. The two branches face each other across the mirror plane and meet on segment 6, which is what puts all four ports on one hydraulic node. Every mode opens exactly one of {V-A, V-B} and exactly one of {V-C, V-D}, so the traffic the pair carries is always one source to one select — straight down a limb, or down half a limb, across the bar and down the other half.

**Y-C, Y-D, Y-F and Y-G are the pump-side junctions.** The prepared pump's
LLDPE stub enters the TPU funnel and its 6 mm front sealing land. That slip
joint separates when the pump cartridge is withdrawn. The upper port has a
straight [14.501 mm](UPPER_LINK_EXPOSED) exposed link to its fore valve. The lower
port has a straight link to a fixed TPU return and a second straight link from
the return to its aft valve. The fixed socket stops of the junction and the return,
seated in the return block, capture the first link; the purchased valve's collet anchors
the second. Factory cuts and assembly
follow the [dock procedure](/hardware/printed-parts/enclosure/pump-dock/README.md).
Y-C and Y-F take suction; Y-D and Y-G discharge.

Y-A's and Y-B's run ports are numbered from the source end down the limb. The pump-side junction port numbers are given below; Y-C-3 and Y-F-3 reach the two suctions, and Y-D-1 and Y-G-1 reach the two discharges.

| Junction | Port 1 | Port 2 | Port 3 |
|---|---|---|---|
| Y-A | V-A-O (tap water) | V-C-I (channel A select) | Y-B-3 (crossbar to Y-B) |
| Y-B | V-B-O (funnel) | V-D-I (channel B select) | Y-A-3 (crossbar to Y-A) |
| Y-C | V-C-O (channel A shared source) | V-E-O (reservoir A to pump return) | P-A-I (pump A inlet) |
| Y-D | P-A-O (pump A outlet) | V-F-I (pump to reservoir A) | V-G-I (pump to flavor tube A) |
| Y-F | V-D-O (channel B shared source) | V-H-O (reservoir B to pump return) | P-B-I (pump B inlet) |
| Y-G | P-B-O (pump B outlet) | V-J-I (pump to flavor tube B) | V-I-I (pump to reservoir B) |

## Tube Segments

Each segment is one labelled edge in [fluid-topology-manifold.mmd](/hardware/topology/fluid-topology-manifold.mmd).
[`_scorecard.py`](/hardware/manifold-layout/_scorecard.py) reads these tables as the flavor
connection inventory. A segment is a face-to-face `butt`, a known `straight`, a
`elbow-and-tube` with an upright valve elbow, short valve link and bent run, a `pump-dock` connection, a `turn` out of
a deck plane, or a swept `drawn` run.
Of [26](SEGMENT_COUNT) manifold segments, [3](BUTT_COUNT) carry no exposed tube and
[4](UPPER_LINK_COUNT) straight upper links have [14.501 mm](UPPER_LINK_EXPOSED)
exposed spans. The four printed lower returns use [8](LOWER_LINK_COUNT) straight
links. Reported LLDPE paths total [2966.0 mm](FLUID_TOTAL); exposed lengths need
their actual fitting insertions when making finished blanks. A butt joint still
needs tube through both fittings despite its zero exposed length. The factory
sets captive link lengths from the mounted stop spans and fully seats valve-side
links in the actual purchased collets.
Machined pump stems and the continuous TPU fluid passages are separate components,
not tube-stock cuts. A bare run of
[`_fluid_topology_sync.py`](/hardware/topology/_fluid_topology_sync.py) prints every
construction, known stock length and exposed path.

Four of the seven conduits in the cold core's top cap are this circuit's: a fill and a draw for each reservoir.

### Shared

| # | From | To | Notes |
|---|---|---|---|
| 1 | water-split to-flavor | flow-regulator inlet | Off the ASSE 1022's split, west lane (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd)) |
| 2 | flow-regulator outlet | V-A-I | Across the machine and up onto the folded deck |
| 3 | V-A-O | Y-A-1 | Quarter turn out of the deck plane, then the step aft over the core's crown |
| 4 | funnel-drain-union outlet | V-B-I | Gravity drain, aft off the funnel's drain elbow |
| 5 | V-B-O | Y-B-1 | The mirror of segment 3 |
| 6 | Y-A-3 | Y-B-3 | The crossbar — branch to branch, face to face |
| 7 | Y-A-2 | V-C-I | Butted |
| 8 | Y-B-2 | V-D-I | Butted |

### Channel A

| # | From | To | Notes |
|---|---|---|---|
| 9 | V-C-O | Y-C-1 | Two straight LLDPE links and a fixed compound TPU return |
| 10 | V-E-O | Y-C-2 | Straight upper LLDPE link; add actual valve and TPU socket insertion |
| 11 | Y-C-3 | P-A-I | Permanent TPU junction → prepared pump A suction stem; this slip joint separates for service |
| 12 | P-A-O | Y-D-1 | Prepared pump A discharge stem → permanent TPU junction; this slip joint separates for service |
| 13 | Y-D-2 | V-F-I | Straight upper LLDPE link; add actual TPU socket and valve insertion |
| 14 | V-F-O | Reservoir A fill bore | Aft and down the `reservoir-a-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 16 | Reservoir A draw | V-E-I | The dip tube up off A's floor and out its `reservoir-a` cap conduit, forward across the deck between V-A and V-K |
| 17 | Y-D-3 | V-G-I | Fixed compound TPU return and two straight LLDPE links |
| 18 | V-G-O | bulkhead-flavor-a tube-in | Aft over the pack and across the machine to the +Y wall of back-top |

### Channel B

| # | From | To | Notes |
|---|---|---|---|
| 19 | V-D-O | Y-F-1 | Two straight LLDPE links and a fixed compound TPU return |
| 20 | V-H-O | Y-F-2 | Straight upper LLDPE link; add actual valve and TPU socket insertion |
| 21 | Y-F-3 | P-B-I | Permanent TPU junction → prepared pump B suction stem; this slip joint separates for service |
| 22 | P-B-O | Y-G-1 | Prepared pump B discharge stem → permanent TPU junction; this slip joint separates for service |
| 23 | Y-G-3 | V-I-I | Straight upper LLDPE link; add actual TPU socket and valve insertion |
| 24 | V-I-O | Reservoir B fill bore | Aft and down the `reservoir-b-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 26 | Reservoir B draw | V-H-I | The dip tube up off B's floor and out its `reservoir-b` cap conduit, forward west of the funnel drain's elbow |
| 27 | Y-G-2 | V-J-I | Fixed compound TPU return and two straight LLDPE links |
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
- Pump A: OFF (throttled tap water through the idle pump)
- Path: Tap → flow regulator → V-A → V-C → P-A (idle) → V-F → Reservoir A

### Clean Water Fill → Reservoir B

- Open: V-A, V-D, V-I
- Pump B: OFF (throttled tap water through the idle pump)
- Path: Tap → flow regulator → V-A → V-D → P-B (idle) → V-I → Reservoir B

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
them as the dry cycle before a pump replacement.

## Sources
[value](NAME) texts are updated by:
- `/hardware/topology/_fluid_topology_sync.py`
