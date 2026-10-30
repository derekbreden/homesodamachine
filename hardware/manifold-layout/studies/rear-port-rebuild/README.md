# Rear-port rebuild

The above-core arrangement rebuilt from the rear ports inward, the hardest part to place first.
Each part goes where it has to be and is measured against what is already placed. Routes and
thin tubes come last; the soda inlet and the water split's stub are the only tubes drawn.

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
| G Ganen carbonator pump | Where production stands it on the cold-core cap, without its elbows |
| neoFit [ACVUS-44](../../../reference/neofit-acvus44-check/README.md) stem check valve | Its stem in the Pisco's outlet, up to the collar on the outlet's release face, with the tip [1.4](CHECK_TIP_SHORT) mm short of the tube stop. The socket faces forward, its mouth at Y[383.6](CHECK_MOUTH_Y). |

## Back-top

Today's back-top, with:

- its six old bores plugged and the new ones cut;
- both roof pockets filled back to the full [9](ROOF_T) mm roof;
- the [6](LAND_T) mm clamping land carried down to the dropped bottom nuts;
- each column's chip pockets opened into one channel, with side rails and no bottom rail;
- no mounting brackets. The fillet where the side wall meets the rear wall stays.

It is cropped to the port corner.

## Straight down past the cap

The drop comes down at X[77.5](DROP_X) Y[367.5](DROP_Y). Carried on straight down past the cap's face,
its tube clears reservoir A by [10.5](DROP_TO_RESERVOIR) mm, the evaporator coil by [15.9](DROP_TO_COIL) mm
and the carbonator by [22.3](DROP_TO_CARBONATOR) mm. The cold core is not drawn.

## The stub

The stub is the shortest, in 0.5 mm steps, that stands V-K, its elbow and its wall
[1](VK_CLEAR) mm off the soda inlet. At [9.5](STUB) mm, V-K's back is [1.0](VK_TO_SODA) mm in front of
the foam on the drop.

## Clearances

- The Pisco is [7.2](PISCO_UNDER_CEILING) mm under the ceiling, [7.5](PISCO_TO_SIDE_WALL) mm from the
  side wall and [3.3](PISCO_TO_STOCK) mm from the full-thickness stock east of the port field.
- The ASSE is [1.45](ASSE_UNDER_CEILING) mm under the ceiling.
- The meter is [12.1](METER_UNDER_PISCO) mm under the Pisco and [2.1](METER_TO_SIDE_WALL) mm from the
  side wall.
- The foam is [8.3](FOAM_TO_SIDE_WALL) mm from the side wall.
- V-K is [4.0](VK_TO_SIDE_WALL) mm from the side wall.
- The pump is [4.6](PUMP_TO_OVER) mm from the OVER bulkhead, [7.4](PUMP_TO_ASSE) mm from the ASSE chain,
  [8.6](PUMP_TO_FOAM) mm from the foam and [9.2](PUMP_TO_TEE) mm from the union tee.
- The check valve is [10.1](CHECK_UNDER_CEILING) mm under the ceiling and [12.4](CHECK_TO_FOAM) mm over the
  foam.

No two parts overlap, apart from:

- the scanned fittings' own thread mating;
- the tube's [15.7](METER_INSERTION) mm insertion into the meter's inlet;
- the stem elbow in V-K, as production stands them: its tip [5.2](STEM_PAST_PORT) mm past the bottom of
  V-K's modelled port, and its hub [0.21](HUB_INTO_VK) mm into the top of the port's boss;
- the elbow's release face, [0.02](FOLD_INTO_TEE) mm into the union tee's collet on one side, from the
  [0.2](VK_TILT)° between them.

## Rebuild

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/rear-port-rebuild/study.py
python3 tools/viz/build.py hardware/manifold-layout/studies/rear-port-rebuild/page.json --out rear-port-rebuild.html
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/manifold-layout/studies/rear-port-rebuild/study.py`
