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
The upright V-A and V-K take the header at their upper inlet ports and discharge
through their lower outlet ports, with their underside flow arrows downward.

**A stopped pump is not a closed valve.** A parked KPHM600 head slowly leaks under gravity, so every path in this manifold is held by its NC solenoids alone, and each dispense path carries a gate at both ends of its pump. The clean-fill modes actively run the selected pump to move tap water into its reservoir, with inlet pressure limited by the YZMSZ 0.3 MPa regulator on V-A's feed.

The carbonated-water draw uses one continuous tube through the plain core
guide and an accepted R14 bend holder directly into the meter inlet. The guide
adds no fitting, insertion or tube cut. A single 63 mm square-ended foam piece
covers the tube and holder before the meter connects. The meter, external inlet holder and foam, and the concealed outlet join belong
to back-top. Prepare the meter and rear outlet fittings together on the open
subassembly; the continuous inlet crosses the plain guide into the core.

> **V-K** — the water-supply fill/shutoff solenoid, an 11th valve of the same Beduan NC type — is **not** part of this manifold. It mounts on back-top east of the G Ganen pump and gates the carbonator fill on the water-split's branch to that pump's suction, downstream of the ASSE 1022 (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd) and [`assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), driven off the main board's spare `J2.OUT3` channel.

The water discharge and CO2 feed each use one purchased neoFit ACHV44-E
check, oriented by its flow arrow toward the carbonator. The selected reference
and its fit and service limits are in
[the check-valve record](/hardware/reference/neofit-achv44-check/README.md).

## The pack

[4](LIMB_COUNT) limbs connect the [10](LIMB_VALVES) valves, [6](TEE_COUNT) three-port junctions and [2](PUMP_COUNT) pumps. All [6](PURCHASED_TEE_COUNT) junctions are purchased PP0208E tees, [4](PUMP_TEE_COUNT) of them on the pump ports.

**A limb is a lane.** Each pump has an inner and outer valve lane. Channel A stands east of the mirror plane and channel B west. The two source tees meet their neighbouring valves face to face. Behind front-top's collet plate, each pump tee takes a prepared pump's LLDPE tube in its branch, reaches its fore valve on a short upper tube and reaches its rear valve on a lower return from its lower port: a stem elbow in each collet and one straight tube between them.

**The pack occupies two fixed decks.** The topology assigns [8](UPPER_COUNT) logical nodes to the upper deck and [8](LOWER_COUNT) to the lower one. The four lower returns cross between them, each from a pump tee's lower port aft into its rear valve's bottom collet. The relocated V-A and V-B source paths reach the fixed Y-A and Y-B tees through their named native tubes and stem fittings.

Per-limb grouping is in [fluid-topology-limbs.mmd](/hardware/topology/fluid-topology-limbs.mmd); where each body stands and how it is turned is [`manifold-layout/README.md`](/hardware/manifold-layout/README.md).

## Junctions

The six three-port junction identifiers are **Y-A, Y-B, Y-C, Y-D, Y-F and Y-G**, all purchased John Guest PP0208E tees. Y-A and Y-B stand on the inner limbs. Y-C, Y-D, Y-F and Y-G stand on the pump ports, each branch on its pump tube's axis and each run upright. The `Y-` identifiers and numbered hydraulic ports are the topology's names.

**Neither reservoir has a junction.** Each carries **two mouths of its own**, both bores in its own cap — the fill, ending above the liquid, and the draw, whose line goes on down to the floor as the reservoir's dip tube — so each pair's two valves reach one directly and nothing stands between them. Every junction here therefore joins two VALVES, or connects two valves to a pump port.

Y-A and Y-B retain their fixed front-manifold stations. V-A and V-B stand above the core and reach those tees through the routed source connections. Each pump tee's branch stands in a bore through front-top's tee wall, which holds it in X and Z, and its branch collet stands extended in the collet plate's recess.

**Y-A and Y-B are the SELECTS-SOURCE junction.** Each stands on its own inner limb's axis, one valve forward of the select it feeds, so its RUN is the limb — the source valve one side, the select the other. The two branches face each other across the mirror plane and meet on segment 6, which is what puts all four ports on one hydraulic node. Every mode opens exactly one of {V-A, V-B} and exactly one of {V-C, V-D}, so the traffic the pair carries is always one source to one select — straight down a limb, or down half a limb, across the bar and down the other half.

**Y-C, Y-D, Y-F and Y-G are the pump tees.** The prepared pump's LLDPE tube
passes front-top's collet plate into the branch, where the extended collet grips it, and
bottoms at the tee's stop. The upper port reaches its fore
valve on a straight tube with [15.251 mm](UPPER_LINK_EXPOSED) exposed. The lower port
reaches its rear valve on a lower return: a stem elbow in the tee's lower collet, one
straight tube, and a stem elbow in the valve. Factory cuts and assembly
follow [internal plumbing §3](/hardware/assembly/internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps).
Y-C and Y-F take suction; Y-D and Y-G discharge.

Y-A's and Y-B's run ports are numbered from the source end down the limb. The pump tees' port numbers are given below; Y-C-3 and Y-F-3 reach the two suctions, and Y-D-1 and Y-G-1 reach the two discharges.

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
set of two stem `elbows` and a straight tube from a pump tee to its rear valve, a `pump-dock`
connection, or a `drawn` connection made from its ordered native tubes and physical fittings. Reported lengths sum the actual tube centrelines; fitting flow paths add no connecting tube.
Of [26](SEGMENT_COUNT) manifold segments, [3](BUTT_COUNT) carry no exposed tube,
[4](UPPER_LINK_COUNT) short upper tubes have [15.251 mm](UPPER_LINK_EXPOSED) exposed
and [4](LOWER_RETURN_COUNT) lower return tubes are reported as cut stock, both socket
insertions included. Reported LLDPE paths total [3414.5 mm](FLUID_TOTAL). Native routed
paths include their authored socket insertions, with the insertion basis recorded
in the production route data. The short upper links need their actual fitting
insertions when making finished blanks. A butt
joint still needs tube through both fittings despite its zero exposed length. The
factory marks each actual fully seated insertion in the purchased collets before
cutting.
The pump tubes come fitted in the prepared pumps and are not counted here. A bare run of
[`_fluid_topology_sync.py`](/hardware/topology/_fluid_topology_sync.py) prints every
construction, known stock length and exposed path.

Each reservoir also has an independent, bidirectional air path: headspace →
flush TPU grommet → 4 mm OD / 2.5 mm ID tube → equipment-space air
above the foam cap. Its dedicated printed passage keeps insulation off the
tube. These two passive air tubes do not cross-connect the reservoirs or use
any valve. [Reservoir air paths](/hardware/printed-parts/cold-core/reservoir/vent.md).

Four of the liquid conduits in the cold core's top cap are this circuit's: a fill and a draw for each reservoir.

### Shared

| # | From | To | Notes |
|---|---|---|---|
| 1 | water-split to-flavor | flow-regulator inlet | Above-core tee-to-regulator feed (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd)) |
| 2 | flow-regulator outlet | V-A-I | Native tube through the regulator-to-V-A elbow above the core |
| 3 | V-A-O | Y-A-1 | V-A outlet elbow, under-head and forward native tubes, fixed Y-A stem elbow |
| 4 | funnel-drain-union outlet | V-B-I | Gravity drain, aft off the funnel's drain elbow |
| 5 | V-B-O | Y-B-1 | V-B outlet stem and return fittings, native tube to the fixed Y-B stem elbow |
| 6 | Y-A-3 | Y-B-3 | The crossbar — branch to branch, face to face |
| 7 | Y-A-2 | V-C-I | Butted |
| 8 | Y-B-2 | V-D-I | Butted |

### Channel A

| # | From | To | Notes |
|---|---|---|---|
| 9 | V-C-O | Y-C-1 | One straight LLDPE tube between a stem elbow in Y-C's lower port and one in V-C's bottom collet |
| 10 | V-E-O | Y-C-2 | Short upper LLDPE tube from V-E's bottom collet into Y-C's upper port; add actual valve and tee insertion |
| 11 | Y-C-3 | P-A-I | Prepared pump A suction tube in Y-C's branch collet, through the collet plate |
| 12 | P-A-O | Y-D-1 | Prepared pump A discharge tube through the collet plate into Y-D's branch collet |
| 13 | Y-D-2 | V-F-I | Short upper LLDPE tube from Y-D's upper port into V-F's bottom collet; add actual tee and valve insertion |
| 14 | V-F-O | Reservoir A fill bore | East tube of the paired Y205/Y304 lid anchors, then through the plain `reservoir-a-fill` guide to the reservoir's fill bore; one continuous tube |
| 16 | Reservoir A draw | V-E-I | One continuous dip tube from A's floor through the plain `reservoir-a` guide and the west seats of the paired Y304/Y205 lid anchors to V-E |
| 17 | Y-D-3 | V-G-I | One straight LLDPE tube between a stem elbow in Y-D's lower port and one in V-G's bottom collet, leaning inboard |
| 18 | V-G-O | bulkhead-flavor-a tube-in | Aft over the pack and across the machine to the +Y wall of back-top |

### Channel B

| # | From | To | Notes |
|---|---|---|---|
| 19 | V-D-O | Y-F-1 | One straight LLDPE tube between a stem elbow in Y-F's lower port and one in V-D's bottom collet |
| 20 | V-H-O | Y-F-2 | Short upper LLDPE tube from V-H's bottom collet into Y-F's upper port; add actual valve and tee insertion |
| 21 | Y-F-3 | P-B-I | Prepared pump B suction tube in Y-F's branch collet, through the collet plate |
| 22 | P-B-O | Y-G-1 | Prepared pump B discharge tube through the collet plate into Y-G's branch collet |
| 23 | Y-G-3 | V-I-I | Short upper LLDPE tube from Y-G's upper port into V-I's bottom collet; add actual tee and valve insertion |
| 24 | V-I-O | Reservoir B fill bore | Aft and down the `reservoir-b-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 26 | Reservoir B draw | V-H-I | The dip tube up off B's floor and out its `reservoir-b` cap conduit, forward west of the funnel drain's elbow |
| 27 | Y-G-2 | V-J-I | One straight LLDPE tube between a stem elbow in Y-G's lower port and one in V-J's bottom collet, leaning inboard |
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
- Pump A: ON
- Path: Tap → flow regulator → V-A → V-C → P-A → V-F → Reservoir A

### Clean Water Fill → Reservoir B

- Open: V-A, V-D, V-I
- Pump B: ON
- Path: Tap → flow regulator → V-A → V-D → P-B → V-I → Reservoir B

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
- Funnel: dry, open to air; in the clean cycle, whatever it holds
- Path: Air → V-B → V-C → P-A → V-G → flavor tube A
- Reservoir A is not on the path; V-F stays closed and the whole discharge goes to flavor tube A

### Air Purge Through B (source to the gooseneck)

- Open: V-B, V-D, V-J
- Pump B: ON
- Funnel: dry, open to air; in the clean cycle, whatever it holds
- Path: Air → V-B → V-D → P-B → V-J → flavor tube B
- Reservoir B is not on the path; V-I stays closed

The two Through states with the two Purge In states above them air-fill every segment the flavor
manifold carries except the two reservoir draws, whose ports stand under the liquid. The
appliance's bench dry cycle runs the four of them in turn.

The clean cycle ([`machine_policy.h`](/firmware/lib/machine_policy/machine_policy.h)) opens with
the channel's Through state on whatever the funnel holds — air when it is dry, or water poured
in before a flavor change — and then runs its rounds of Clean Water Fill and Clean Flush. Tap
water enters at Y-A, so segments 4 and 5, from the funnel's drain through V-B to Y-B, carry
water only from the funnel.

## Sources
[value](NAME) texts are updated by:
- `/hardware/topology/_fluid_topology_sync.py`
