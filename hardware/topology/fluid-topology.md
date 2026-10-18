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

[4](LIMB_COUNT) limbs carry the [10](LIMB_VALVES) valves and the [6](TEE_COUNT) junction tees, over [2](PUMP_COUNT) pumps.

**A limb is a lane.** Every valve is straight through and every junction's run takes two valve ports, so a limb is one line of valves and tees, front to back, on one column of X. The inner junctions meet their fixed neighbours face to face. The four pump-side tees stand in fixed wall saddles. Stationary S links connect their run ports to the fore valves, and permanent TPU receivers connect their branches to the prepared pump stems. Each pump-side tee puts its RUN across the head's face, so each pump hands out two lanes, 57 mm apart — an inner limb and an outer one, both on its own side of the mirror plane. Channel A stands east of that plane in the machine and channel B west.

**The pack occupies two fixed decks.** [8](UPPER_COUNT) bodies stand on the folded deck and [8](LOWER_COUNT) on the other. Four stationary 180° hairpins connect the rows to the pump-side tees. The arrangement turns every mouth that leaves the pack toward the back of the machine.

Per-limb grouping is in [fluid-topology-limbs.mmd](/hardware/topology/fluid-topology-limbs.mmd); where each body stands and how it is turned is [`manifold-layout/README.md`](/hardware/manifold-layout/README.md).

## Junctions

Six 3-port junctions — **Y-A, Y-B, Y-C, Y-D, Y-F, Y-G** — and every one of them is a **PP0208E Tee** (in-line run + branch). The `Y-` prefix is a stable identifier, not a claim that the fitting is a Y.

**Neither reservoir has a junction.** Each carries **two mouths of its own** — the draw on the bulkhead at the bottom of its wet V, the fill on a bore in its own cap — so each pair's two valves reach one directly and nothing stands between them. Every junction here therefore joins two VALVES, or connects the valves to a pump through its permanent receiver.

Y-A and Y-B inherit location from their fixed face-to-face valve joints. Y-C, Y-D, Y-F and Y-G are tied into fixed bulkhead saddles; their collets and rear tubing remain stationary during a pump change.

**Y-A and Y-B are the SELECTS-SOURCE junction.** Each stands on its own inner limb's axis, one valve forward of the select it feeds, so its RUN is the limb — the source valve one side, the select the other. The two branches face each other across the mirror plane and meet on segment 6, which is what puts all four ports on one hydraulic node. Every mode opens exactly one of {V-A, V-B} and exactly one of {V-C, V-D}, so the traffic the pair carries is always one source to one select — straight down a limb, or down half a limb, across the bar and down the other half.

**Y-C, Y-D, Y-F and Y-G are the pump-side junctions.** Each BRANCH takes a
permanent straight [18.175 mm](FIXED_TAIL_CUT) LLDPE tail from a wall-supported TPU
receiver. The customer's prepared machined flanged stem enters the receiver's
front land and separates there when the cartridge is withdrawn. The tee and its
commercial collet stay fixed. One run port carries a stationary hairpin to the aft
valve row; the other reaches its fore valve through a fixed R14 S link with
[15.2531 mm](BOWED_EXPOSED) of exposed developed path. That figure excludes insertion
inside either fitting. Y-C and Y-F take suction, Y-D and Y-G discharge.

Y-A's and Y-B's run ports are numbered from the source end down the limb. On a pump-side tee the branch takes the number nearest its pump connection — Y-C-3 and Y-F-3 at the two suctions, Y-D-1 and Y-G-1 at the two discharges.

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
connection inventory. A segment is a face-to-face `butt`, a known `straight`, a fixed
`bowed` S link, a `fold` hairpin, a `turn` out of a deck plane, or a swept `drawn` run.
Of [26](SEGMENT_COUNT) manifold segments, [3](BUTT_COUNT) carry no exposed tube and
[4](BOWED_COUNT) use [15.2531 mm](BOWED_EXPOSED) exposed S links across
[15.253 mm](BOWED_GAP) mouth-to-mouth chords. Make each S-link blank from its exposed
path plus the actual insertion into both fittings; the valve-side insertion is a
factory measurement. Reported tube lengths total [2601.5 mm](FLUID_TOTAL), including
the four complete permanent receiver-to-tee tails and excluding the four S links.
Other mouth-to-mouth path lengths need their actual fitting insertions when making
the finished blanks; a butt joint needs tube through both fittings despite its
zero exposed length.
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
| 9 | V-C-O | Y-C-1 | Stationary 180° hairpin on the A1 limb's column |
| 10 | V-E-O | Y-C-2 | Fixed R14 S link: exposed developed path plus actual insertion into the valve and fixed tee |
| 11 | Y-C-3 | P-A-I | Fixed tee tail → permanent TPU receiver → prepared pump A suction stem; the stem/receiver slip joint separates for service |
| 12 | P-A-O | Y-D-1 | Prepared pump A discharge stem → permanent TPU receiver → fixed tee tail; the stem/receiver slip joint separates for service |
| 13 | Y-D-2 | V-F-I | Fixed R14 S link: exposed developed path plus actual insertion into the fixed tee and valve |
| 14 | V-F-O | Reservoir A fill bore | Aft and down the `reservoir-a-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 16 | Reservoir A draw | V-E-I | Up the `reservoir-a` cap conduit, off the bulkhead at the bottom of the wet V |
| 17 | Y-D-3 | V-G-I | Stationary 180° hairpin on the A2 limb's column |
| 18 | V-G-O | bulkhead-flavor-a tube-in | Aft over the pack and across the machine to the +Y wall of back-top |

### Channel B

| # | From | To | Notes |
|---|---|---|---|
| 19 | V-D-O | Y-F-1 | Stationary 180° hairpin on the B1 limb's column |
| 20 | V-H-O | Y-F-2 | Fixed R14 S link: exposed developed path plus actual insertion into the valve and fixed tee |
| 21 | Y-F-3 | P-B-I | Fixed tee tail → permanent TPU receiver → prepared pump B suction stem; the stem/receiver slip joint separates for service |
| 22 | P-B-O | Y-G-1 | Prepared pump B discharge stem → permanent TPU receiver → fixed tee tail; the stem/receiver slip joint separates for service |
| 23 | Y-G-3 | V-I-I | Fixed R14 S link: exposed developed path plus actual insertion into the fixed tee and valve |
| 24 | V-I-O | Reservoir B fill bore | Aft and down the `reservoir-b-fill` cap conduit, onto the bore in the reservoir's own cap, above the liquid |
| 26 | Reservoir B draw | V-H-I | Up the `reservoir-b` cap conduit, off the bulkhead at the bottom of the wet V |
| 27 | Y-G-2 | V-J-I | Stationary 180° hairpin on the B2 limb's column |
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
