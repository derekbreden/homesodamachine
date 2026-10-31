# Rear-port rebuild

The above-core arrangement rebuilt from the rear ports inward, the hardest part to place first.
Each part goes where it has to be and is measured against what is already placed. Routes and
thin tubes come last; the soda inlet, the water split's stub, the CO2 tube and the short pieces of
3/8 in tube in the pump's joints are the only tubes drawn.

The [study](study.py) writes the scenes the [page spec](page.json) draws, the measurements in
[study.json](study.json), and the figures below. The page is published at
https://claude.ai/artifact/RppC6x7HmYNP8n2d6EyTMN.

## Placed

| Part | Where it stands |
|---|---|
| PISCO RVFUP1/4-1/4-0.3 regulator | Its long-neck inlet passes a hole of its own, d[13.86](PISCO_HOLE_D), at the CO2 station, X[77.5](CO2_X) Z[328](ROW_1). The inlet release face is on the mouth plane, Y[480.8](MOUTH_Y). The shoulder is [0.09](PISCO_ON_LAND) mm off the clamping land's inner face. |
| Scanned threaded ASSE chain | On TAP, through a d[19.31](TAP_HOLE_D) hole on the PP010822E's own axis. A [9.5](STUB) mm stub of 1/4 in tube, cut [42.7](STUB_CUT) mm, runs from the PP061208W's collet into the branch of a JG PP0208E union tee. The tee's run stands square to the stub, east-west. |
| Soda, OVER, flavor A and flavor B bulkheads | Dropped [10.38](GRID_DROP) mm with the grid, to rows Z[328](ROW_1), Z[296](ROW_2) and Z[264](ROW_3) |
| Label tiles | [1.8](TILE_T) mm tiles in [2](CHANNEL_DEPTH) mm channels between side rails. The bottom tiles stand on the channel floor at Z[252](TILE_SEAT_Z). The TAP tile is bored d[19.28](TAP_BORE_D) on the PP010822E's axis. |
| DIGITEN flow meter | Straight into the soda union: its outlet collet face is on the union's inboard collet face, with no tube showing. The larger side is down. |
| Soda inlet | Production's continuous inlet, laid off the meter's inlet: the printed R[14](BEND_R) bend holder, the 1/4 in tube and one [52](FOAM_LEN) mm piece of 1 in foam. The bend starts [4](BEND_OFF_METER) mm off the meter's mouth and turns straight down, [28.6](DROP_LEN) mm to the cold-core cap's face. |
| V-K, its stem elbow and its wall | Production's arrangement, moved [1.4](VK_EAST) mm east, [11.2](VK_AFT) mm aft and [7.0](VK_DOWN) mm down, until the elbow's release face is on the union tee's east collet face. The elbow's socket is [0.2](VK_TILT)° off the tee's run. The wall carries V-K's posts as production's does and reaches the side wall's inner face instead of the cap, with a [1.9](VK_ARM) mm arm. |
| G Ganen carbonator pump | From where production stands it on the cold-core cap, [17.0](PUMP_AFT) mm aft and [24.5](PUMP_WEST) mm west, with a [joint](../../../reference/pump-barb-joint/README.md) on each barb. The suction joint, on V-K's line, bends [13.1](SUCTION_BEND)° down to pass under V-K. |
| neoFit [ACVUS-44](../../../reference/neofit-acvus44-check/README.md) stem check valve | Its stem in the Pisco's outlet, up to the collar on the outlet's release face, with the tip [1.4](CHECK_TIP_SHORT) mm short of the tube stop. The socket faces forward, its mouth at Y[383.6](CHECK_MOUTH_Y). |
| Elbows on V-K's line | A neoFit ATEU44W in the suction joint's 1/4 in collet, its socket facing fore, and production's ATEU44W in V-K's bottom port, turned to face aft |
| CO2 tube | Red 1/4 in LLDPE, [100](CO2_LEN) mm from the check's socket to the cap at X[59.1](CO2_LAND_X) Y[354.7](CO2_LAND_Y), beside V-K, and on straight down past the carbonator's rim. It leaves the socket straight forward, turns down in one bend no tighter than R[25](CO2_BEND), and comes onto the cap in an S no tighter than R[52](CO2_S_R). |

## Back-top

Today's back-top, with:

- its six old bores plugged and the new ones cut;
- both roof pockets filled back to the full [9](ROOF_T) mm roof;
- the [6](LAND_T) mm clamping land carried down to the dropped bottom nuts;
- each column's chip pockets opened into one channel, with side rails and no bottom rail;
- a seat for each of the ASSE chain, the Pisco and the meter;
- no mounting brackets. The fillet where the side wall meets the rear wall stays.

It is cropped to the port corner.

## Seats and snap caps

Back-top is inverted on the bench for assembly. The ASSE chain, the Pisco and the meter each drop into
a seat [16](SLIDE) mm ahead of their stations and slide aft into place. The PP010822E's and the Pisco's
noses go through the rear wall, and the meter goes onto the soda union's stub. Each seat is one block
on back-top with its part's upper side cut into it in plain steps, swept forward by the slide. The
ASSE's steps are also swept [1.5](SNAP_THREAD) mm either way, how far a taped joint may leave the body
from its station. Along the slide every part stays [0.16](SLIDE_GAP) mm or more off its seat.

A snap cap then holds each part's other side. It is one half pipe under the part. Its two
[3](SNAP_WING) mm side walls rise past the part's axis as the springs, each hooking
[0.6](SNAP_REACH) mm over a ledge in a pocket in the seat's flank. The pocket's ends are the cap's
end shoulders. The other walls are [3](SNAP_WALL) mm.

| Cap | Goes on | Holds |
|---|---|---|
| ASSE | From below | The outlet bonnet round, the main wrench's lower faces and the inlet thread. Its aft end bears on the GAGIRA's fore face, and a notch in its west wall passes the vent. |
| Pisco | From below | The outlet fitting. Its lip stands in front of the step down to the outlet's neck. |
| Meter | From the west | The housing's west end and rim, in a block whose top and bottom walls run east past the housing. The bottom wall stops short of the lead's slot. |

Each cap stands [0.15](CAP_GAP) mm or more off what it holds, and [0.11](WAY_ON_GAP) mm or more on its way on.

## Straight down past the cap

The drop comes down at X[77.5](DROP_X) Y[367.5](DROP_Y). Carried on straight down past the cap's face,
its tube clears reservoir A by [10.5](DROP_TO_RESERVOIR) mm, the evaporator coil by [15.9](DROP_TO_COIL) mm
and the carbonator by [22.3](DROP_TO_CARBONATOR) mm. Of the cold core, only the carbonator, its coil and
the two reservoirs are drawn.

## The stub

The stub is the shortest, in 0.5 mm steps, that stands V-K, its elbow and its wall
[1](VK_CLEAR) mm off the soda inlet. At [9.5](STUB) mm, V-K's back is [1.0](VK_TO_SODA) mm in front of
the foam on the drop.

## The pump and its joints

From where production stands it on the cap, the pump moves aft until its butt, its rearmost point,
meets the rear wall's inner face at Y[462.3](REAR_IN): [17.0](PUMP_AFT) mm. It then moves west, in half
millimetres, until it stands [1](PUMP_CLEAR) mm off every bulkhead and nut: [24.5](PUMP_WEST) mm. The
nearest is the flavor B bulkhead, [1.2](PUMP_TO_FLAVOR_B) mm off.

Each barb carries a [joint](../../../reference/pump-barb-joint/README.md): a piece of 3/8 in clear tube,
[23.4](SUCTION_TUBE) mm on the suction barb and [23.1](DISCHARGE_TUBE) mm on the discharge barb, a
PP061208W with its stem trimmed to [10](STEM_TRIM) mm, and two YDS clamps with their housings up and
their keys aft.

The suction joint is on V-K's line, and a neoFit ATEU44W stands in its collet. The elbow's stem is
cut to the collet's [17.5](ELBOW_STEM) mm depth, its shoulder is on the collet's mouth, and its socket
faces fore toward V-K's bottom port. Straight, the elbow runs into the underside of V-K's coil, so
the joint bends down until the reducer, its clamp and the elbow pass under it:
[13.1](SUCTION_BEND)°, the least bend in tenths of a degree at which none of them overlaps V-K. There
the elbow's hub meets the coil's bottom edge at its terminal end, [0.00](UNDER_VK) mm off, and stands
[0.3](ELBOW_TO_SPADE) mm from the nearer of V-K's spades, which are drawn bare.

The barb and its clamp stay as they are. The reducer and its clamp turn about the lowest point of
the barb's tip, where the stem's tip bears on it. The tube runs straight on each and creases on the
plane halfway between them.

The joints' 1/4 in collet mouths stand at X[56.0](SUCTION_MOUTH_X) Z[272.4](SUCTION_MOUTH_Z) on the
suction side and X[-86.5](DISCHARGE_MOUTH_X) Z[280.5](DISCHARGE_MOUTH_Z) on the discharge side, both at
Y[346.8](JOINT_Y).

## V-K's line

Production's elbow stands in V-K's bottom port, moved with V-K and turned [90](OUTLET_TURN)° about the
port's axis so its socket faces aft, toward the elbow in the suction joint's collet. The suction
joint's elbow has its socket mouth at X[62.1](LINE_FORE_X) Y[325.8](LINE_FORE_Y) Z[271.0](LINE_FORE_Z), facing fore.
V-K's has its socket mouth at X[77.8](LINE_AFT_X) Y[328.6](LINE_AFT_Y) Z[255.8](LINE_AFT_Z), facing aft.

## The CO2 line

The bend off the check's socket is the shortest of those that leave it straight forward, turn down
no tighter than R[25](CO2_BEND) onto a straight drop, and stand [3](CO2_GAP) mm off every part but the
pump and its joints. The nearest part is V-K, [3.0](CO2_TO_VK) mm off.

Under the cap the tube runs straight down beside the carbonator, [5.8](CO2_PUSH) mm out from under the
bend's foot, straight away from the carbonator's axis: there it just touches the carbonator's rim. The
straight runs [64](CO2_STRAIGHT) mm, from the coil's top at Z[189.6](CO2_LOW_Z) up to the floor, the
cap's face at Z[253.4](CAP_FACE). The tube is drawn down to the coil's top.

From the floor, the gentlest S that stands [3](CO2_GAP) mm off every part but the pump and its joints
rises [36](CO2_DROP) mm onto the bend's foot. It bends no tighter than R[52](CO2_S_R).

## Clearances

- The Pisco is [7.2](PISCO_UNDER_CEILING) mm under the ceiling, [7.5](PISCO_TO_SIDE_WALL) mm from the
  side wall and [3.3](PISCO_TO_STOCK) mm from the full-thickness stock east of the port field.
- The ASSE is [1.45](ASSE_UNDER_CEILING) mm under the ceiling.
- The meter is [12.1](METER_UNDER_PISCO) mm under the Pisco and [2.1](METER_TO_SIDE_WALL) mm from the
  side wall.
- The foam is [8.3](FOAM_TO_SIDE_WALL) mm from the side wall.
- V-K is [4.0](VK_TO_SIDE_WALL) mm from the side wall.
- The pump is [1.2](PUMP_TO_FLAVOR_B) mm from the flavor B bulkhead and [3.5](PUMP_TO_FLAVOR_B_NUT) mm from
  its nut, and its butt is on the rear wall.
- The check valve is [10.1](CHECK_UNDER_CEILING) mm under the ceiling and [12.4](CHECK_TO_FOAM) mm over the
  foam.
- The CO2 tube is [3.0](CO2_TO_VK) mm from V-K. Under the cap it is [0.0](CO2_TO_RIM) mm from the
  carbonator and [18.7](CO2_TO_RESERVOIR) mm from reservoir A.
- The meter's seat is [1.5](METER_SEAT_TO_FOAM) mm from the foam and [1.5](METER_SEAT_TO_UNION) mm from the
  soda union.

No two parts overlap, apart from:

- the scanned fittings' own thread mating;
- the tube's [15.7](METER_INSERTION) mm insertion into the meter's inlet;
- the stem elbow in V-K's top port, as production stands them: its tip [5.3](STEM_PAST_PORT) mm past the
  bottom of V-K's modelled port, and its hub [0.21](HUB_INTO_VK) mm into the top of the port's boss;
- the elbow in V-K's bottom port, as production stands it: its tip [5.3](OUTLET_STEM_PAST_PORT) mm past
  the top of the modelled port, and its hub [0.21](OUTLET_HUB_INTO_VK) mm into the bottom of the port's
  boss;
- the same elbow's underside, [5.5](OUTLET_INTO_CAP) mm below the cold-core cap's face;
- the elbow's release face, [0.02](FOLD_INTO_TEE) mm into the union tee's collet on one side, from the
  [0.2](VK_TILT)° between them;
- the suction joint's reducer, its end [5.6](CO2_INTO_REDUCER) mm east into the CO2 tube's S, and the
  elbow in its collet, [2.1](CO2_INTO_ELBOW) mm aft into the S.

## Rebuild

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/rear-port-rebuild/study.py
python3 tools/viz/build.py hardware/manifold-layout/studies/rear-port-rebuild/page.json --out rear-port-rebuild.html
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/manifold-layout/studies/rear-port-rebuild/study.py`
