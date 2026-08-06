# Soda Machine Fluid Topology

## Valves

| Valve | Purpose |
|---|---|
| V-A | Tap water inlet gate |
| V-B | Hopper funnel gate |
| V-C | Shared source → Pump B (channel A select) |
| V-D | Shared source → Pump A (channel B select) |
| V-E | Bag A → Pump B inlet |
| V-F | Pump B outlet → Bag A |
| V-G | Pump B outlet → Nozzle A |
| V-H | Bag B → Pump A inlet |
| V-I | Pump A outlet → Bag B |
| V-J | Pump A outlet → Nozzle B |

All valves are normally closed solenoid valves. Flow direction is inlet (I) to outlet (O) only.

> **V-K** — the water-supply fill/shutoff solenoid, an 11th valve of the same Beduan NC type — is **not** part of this manifold. It gates the carbonator fill line on the water-split's run to the SeaFlo suction, downstream of the ASSE 1022 (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd) and [`assembly/internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), driven off the board's spare `J2.OUT3` channel.

## Junctions

Seven 3-port junctions — **Y-A, Y-B, Y-C, Y-D, Y-E, Y-F, Y-G** — and every one of them is a **PP0208E Tee** (in-line run + branch). The `Y-` prefix is a stable identifier, not a claim that the fitting is a Y.

Reservoir B has no junction: it carries **two mouths of its own** — the draw on the bulkhead at the bottom of its wet V, the fill on a bore in its own cap — so its pair's two valves each reach one directly and nothing stands between them. Reservoir A still meets its pair at Y-E.

Which of the two a junction wants follows from the placed geometry more than from the circuit: a **divider** joins two ports side by side — its outlets are parallel, which is the shape two valves standing beside each other present — and a **Tee** joins two ports one corridor serves, the run taking those and the branch turning to the third. What decides it is the pair's own sitting AND the room the fitting has: a trident is 38.5 mm from stem tip to outlet face and needs that much clear ahead of the pair it joins, where a Tee standing across a band needs only its own 13.7 mm diameter. Nothing in this machine has that much clear, so nothing in it is a trident.

No junction is carried by a tray: a tray seats valves only, so each fitting hangs on the two collets it joins. [7](TRAY_COUNT) trays carry the [11](TRAY_VALVE_COUNT) valves and all of them are placed — [4](TWO_VALVE_COUNT) of the [two-valve](/hardware/printed-parts/valve-manifold/two-valve-tray/README.md) plate and [3](ONE_VALVE_COUNT) of the [single-valve](/hardware/printed-parts/valve-manifold/single-valve-tray/README.md) one, because a plate takes a second seat only where a PAIR meets at one junction and three valves in this machine stand alone. A tray carries no valve above another — nothing holds a valve down, so every tray in the machine lies plate-up, and where a plate has two seats they stand side by side — so **a junction reaching between trays can only ever be a Tee**, and that is six of the eight. The other two join one tray's own pair, and there the room decides: **Y-E** has a 16.9 mm strip between the pump row and the head column, and stands a Tee ACROSS it.

Which two of a Tee's three ports take the **run** follows from the geometry the same way the divider/Tee choice does. A Tee's run is a **lane** — one straight length of tube passing through the fitting — and its branch is the leg that leaves that lane. So the run takes the two ports the same corridor serves and the branch takes the one that departs it, and the port numbering below is a naming rather than a claim about which is which: the table says where each port goes, and [`_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py)'s `_tee_local` is where a name meets a run end or a branch.

**Y-A and Y-B are the SELECTS-SOURCE junction**, and the lane each takes is a **column**. The source pair stands in the selects pair's own two seats one stack pitch up, so the four ports between them lie in two vertical columns — V-A over V-C, V-B over V-D — and each column is one Tee's run: the tap-water source falls straight through Y-A to channel A's select (segments 3 and 7), the hopper source through Y-B to channel B's (5 and 8). The two branches face each other across the seat pitch and meet on segment 6, which is what puts all four ports on one hydraulic node. Every mode opens exactly one of {V-A, V-B} and exactly one of {V-C, V-D}, so the traffic the pair carries is always one source to one select — straight down a column, or down half a column, across the bar and down the other half.
Channel A's and channel B's four are the PUMP-ROW junctions.

Channel A's stand in the **pump lane**, the strip west of the head column and aft of channel A's pump, each on the column of the barb its run butts. Their runs lie along that lane and their branches stand **up** out of it, which is the axis both third legs leave on: Y-C's branch takes the fall from the selects pair a stack pitch above (segment 9), and Y-D's is the storey-and-a-half climb to the nozzle gate in the loft (segment 17). Nothing else on the row changes level — the pump's two barbs stand on the bag-A pair's own port plane, so the whole row is flat and only the branches climb.

Channel B's do **not** share one lane, and pump A is why: it stands in the front column beside channel A's, so both of its junctions are up in the loft and the two legs between them and the barbs cross a storey and a half. **Y-G** stands in the lane east of V-K's plate — the corridor segment 27 already runs down — with its RUN along that lane and one valve on each end: the bag's fill gate forward (segment 23), the nozzle gate aft (segment 27). Its branch takes the climb up out of the front column (segment 22), and both run legs lie on the aft stand's own port plane, so only the branch changes level. **Y-F** stands in the loft's own pump lane, the strip between the trays and the water deck, with its run along the lane — the shared source's climb in from the front column (segment 19), the pump's suction out the other end (segment 21) — and its branch reaching sideways at the bag-B draw (segment 20). It is the only branch in the manifold that is horizontal, and the only row whose RUN legs change level.

**Y-E** is the one junction left that joins a tray's own pair, and it stands ACROSS the strip rather than ahead of it: what is ahead of the bag-A pair is a strip a fitting's diameter deep, so it stands across it with its collets in one vertical plane — the RUN along the strip carrying reservoir A's line in from the tray-east lane (segment 15) and the bag draw out the other end (segment 16), the BRANCH facing down on V-F's own column at the fill (segment 14). A down-facing collet is entered by a rising leg, so it stands over the pair's port plane and both valve legs climb into it. Per-tray grouping is in [fluid-topology-trays.mmd](/hardware/topology/fluid-topology-trays.mmd).

Y-E's three ports are numbered from the end the **bag** rides — Y-E-2 the east end of its run, with a valve on each of the other two — where Y-A's and Y-B's are numbered from the source end down their columns. Y-G's run is numbered from its AFT end — Y-G-2 at the nozzle gate, Y-G-3 forward at the bag's fill valve — each of the two the nearer to the collet it reaches. Reservoir A is reached by one line on the cold core's front face carrying both its fill and its draw; reservoir B is reached by two, each on its own conduit through the top cap.

| Junction | Port 1 | Port 2 | Port 3 |
|---|---|---|---|
| Y-A | V-A-O (tap water) | V-C-I (channel A select) | Y-B-3 (crossbar to Y-B) |
| Y-B | V-B-O (hopper) | V-D-I (channel B select) | Y-A-3 (crossbar to Y-A) |
| Y-C | V-C-O (channel A shared source) | V-E-O (bag A to pump return) | P-B-I (pump B inlet) |
| Y-D | P-B-O (pump B outlet) | V-F-I (pump to bag A) | V-G-I (pump to nozzle A) |
| Y-E | V-F-O (pump to bag A return) | Bag A port | V-E-I (bag A to pump) |
| Y-F | V-D-O (channel B shared source) | V-H-O (bag B to pump return) | P-A-I (pump A inlet) |
| Y-G | P-A-O (pump A outlet) | V-J-I (pump to nozzle B) | V-I-I (pump to bag B) |

## Tube Segments

Each segment is one labelled edge in [fluid-topology-manifold.mmd](/hardware/topology/fluid-topology-manifold.mmd). `scorecard.py` reads these tables as `fluid-1` … `fluid-28`, the connection inventory the enclosure must carry, and [`_lines.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_lines.py) authors each one port to port.

### Shared

| # | From | To | Notes |
|---|---|---|---|
| 1 | Tap water source | Flow regulator inlet | Fed from the water-split's AFT run — 1/4" PTC off the ASSE 1022's split (see [`fluid-topology-carbonator.mmd`](/hardware/topology/fluid-topology-carbonator.mmd)) |
| 2 | Flow regulator outlet | V-A-I | |
| 3 | V-A-O | Y-A-1 | Down the west column, through Y-A's run |
| 4 | Hopper funnel bottom | V-B-I | |
| 5 | V-B-O | Y-B-1 | Down the east column, through Y-B's run |
| 6 | Y-A-3 | Y-B-3 | The crossbar — branch to branch, one straight length |
| 7 | Y-A-2 | V-C-I | |
| 8 | Y-B-2 | V-D-I | |

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
| 23 | Y-G-3 | V-I-I | |
| 24 | V-I-O | Bag B FILL port | Down the cap conduit onto the bore in the reservoir's own cap, above the liquid |
| 26 | Bag B DRAW port | V-H-I | Out of the `reservoir-b` conduit at the head of the +Y band, off the bulkhead at the bottom of the wet V |
| 27 | Y-G-2 | V-J-I | |
| 28 | V-J-O | Nozzle B | |

---

## Operations — Valve States

Open valves listed; all others closed.

This table is canonical for the integrated flavor manifold. Pumps run forward only. **P-B is channel A's pump and P-A is channel B's** — the pairing the junction and segment tables above carry, and the one both editions' packs are built to. Valve state selects whether a pump draws from a bag, hopper, or tap-water source and whether the outlet returns to a bag or goes to the nozzle. Normally closed solenoid valves define the closed state and keep the dispense paths primed.

### Dispense A

- Open: V-E, V-G
- Pump B: ON
- Path: Bag A → V-E → P-B → V-G → Nozzle A

### Dispense B

- Open: V-H, V-J
- Pump A: ON
- Path: Bag B → V-H → P-A → V-J → Nozzle B

### Fill from Hopper → Bag A

- Open: V-B, V-C, V-F
- Pump B: ON
- Path: Hopper → V-B → V-C → P-B → V-F → Bag A

### Fill from Hopper → Bag B

- Open: V-B, V-D, V-I
- Pump A: ON
- Path: Hopper → V-B → V-D → P-A → V-I → Bag B

### Clean Water Fill → Bag A

- Open: V-A, V-C, V-F
- Pump B: OFF (line pressure through idle pump)
- Path: Tap → V-A → V-C → P-B (idle) → V-F → Bag A

### Clean Water Fill → Bag B

- Open: V-A, V-D, V-I
- Pump A: OFF (line pressure through idle pump)
- Path: Tap → V-A → V-D → P-A (idle) → V-I → Bag B

### Clean Flush A (water out)

- Open: V-E, V-G
- Pump B: ON
- Path: Bag A → V-E → P-B → V-G → Nozzle A
- (Same as Dispense A)

### Clean Flush B (water out)

- Open: V-H, V-J
- Pump A: ON
- Path: Bag B → V-H → P-A → V-J → Nozzle B
- (Same as Dispense B)

### Air Purge In → Bag A

- Open: V-B, V-C, V-F
- Pump B: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-C → P-B → V-F → Bag A
- (Same path as hopper fill)

### Air Purge In → Bag B

- Open: V-B, V-D, V-I
- Pump A: ON
- Funnel: dry, open to air
- Path: Air → V-B → V-D → P-A → V-I → Bag B

### Air Purge Out A

- Open: V-E, V-G
- Pump B: ON
- Path: Bag A → V-E → P-B → V-G → Nozzle A
- (Same as Dispense A)

### Air Purge Out B

- Open: V-H, V-J
- Pump A: ON
- Path: Bag B → V-H → P-A → V-J → Nozzle B
- (Same as Dispense B)

## Sources
[value](NAME) texts are updated by:
- `/hardware/topology/_fluid_topology_sync.py`
