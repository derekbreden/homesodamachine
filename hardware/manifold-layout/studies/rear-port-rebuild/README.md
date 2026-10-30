# Rear-port rebuild

The above-core arrangement rebuilt from the rear ports inward, the hardest part to place first.
Each part goes where it has to be and is measured against what is already placed. Routes and
thin tubes come last; the soda inlet is the one route drawn.

The [study](study.py) writes the scenes the [page spec](page.json) draws, the measurements in
[study.json](study.json), and the figures below. The page is published at
https://claude.ai/artifact/RppC6x7HmYNP8n2d6EyTMN.

## Placed

| Part | Where it stands |
|---|---|
| PISCO RVFUP1/4-1/4-0.3 regulator | Its long-neck inlet passes a hole of its own, d[13.86](PISCO_HOLE_D), at the CO2 station, X[77.5](CO2_X) Z[328](ROW_1). The inlet release face is on the mouth plane, Y[480.8](MOUTH_Y). The shoulder is [0.09](PISCO_ON_LAND) mm off the clamping land's inner face. |
| Scanned threaded ASSE chain | On TAP, through a d[19.31](TAP_HOLE_D) hole on the PP010822E's own axis |
| Soda, OVER, flavor A and flavor B bulkheads | Dropped [10.38](GRID_DROP) mm with the grid, to rows Z[328](ROW_1), Z[296](ROW_2) and Z[264](ROW_3) |
| Label tiles | [1.8](TILE_T) mm tiles in [2](CHANNEL_DEPTH) mm channels between side rails. The bottom tiles stand on the channel floor at Z[252](TILE_SEAT_Z). The TAP tile is bored d[19.28](TAP_BORE_D) on the PP010822E's axis. |
| DIGITEN flow meter | Straight into the soda union: its outlet collet face is on the union's inboard collet face, with no tube showing. The larger side is down. |
| Soda inlet | Production's continuous inlet, laid off the meter's inlet: the printed R[14](BEND_R) bend holder, the 1/4 in tube and one [52](FOAM_LEN) mm piece of 1 in foam. The bend starts [4](BEND_OFF_METER) mm off the meter's mouth and turns straight down, [28.6](DROP_LEN) mm to the cold-core cap. |

## Back-top

Today's back-top, with:

- its six old bores plugged and the new ones cut;
- both roof pockets filled back to the full [9](ROOF_T) mm roof;
- the [6](LAND_T) mm clamping land carried down to the dropped bottom nuts;
- each column's chip pockets opened into one channel, with side rails and no bottom rail;
- no mounting brackets. The fillet where the side wall meets the rear wall stays.

It and the cap's two top layers are cropped to the port corner.

## Where the soda inlet lands

The drop comes down at X[77.5](DROP_X) Y[367.5](DROP_Y). The cap's soda guide, where the line enters
the carbonator, is at X[50.0](SODA_GUIDE_X) Y[342.4](SODA_GUIDE_Y). The drop is [27.5](DROP_EAST) mm east
and [25.1](DROP_AFT) mm aft of it, [37.2](DROP_APART) mm apart. It lands [1.25](DROP_CO2_OFF) mm off the
axis of the cap's CO2 inlet guide.

## Clearances

- The Pisco is [7.2](PISCO_UNDER_CEILING) mm under the ceiling, [7.5](PISCO_TO_SIDE_WALL) mm from the
  side wall and [3.4](PISCO_TO_STOCK) mm from the full-thickness stock east of the port field.
- The ASSE is [1.45](ASSE_UNDER_CEILING) mm under the ceiling.
- The meter is [12.1](METER_UNDER_PISCO) mm under the Pisco and [2.1](METER_TO_SIDE_WALL) mm from the
  side wall.
- The foam is [8.3](FOAM_TO_SIDE_WALL) mm from the side wall and [1.1](FOAM_TO_CAP) mm over the cap.

No two parts overlap, apart from the scanned fittings' own thread mating and the tube's
[15.7](METER_INSERTION) mm insertion into the meter's inlet.

## Rebuild

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/rear-port-rebuild/study.py
python3 tools/viz/build.py hardware/manifold-layout/studies/rear-port-rebuild/page.json --out rear-port-rebuild.html
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/manifold-layout/studies/rear-port-rebuild/study.py`
