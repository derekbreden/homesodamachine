# borrowed-04-axis-map: where a pivot can physically be

Origin: swarm. Maturity: developed (an analysis, not an arrangement). Scene: `scenes/borrowed-04-axis-map/index.html`. Numbers: `calc/free_directions.py`.

## Picture it

A flat map of every direction you could point an axis from the laser dot, coloured teal where something fits on it and dark red where it runs into the tube wall, the endcap or the bench. Slide a shaft thickness and the teal shrinks to a small patch up and inward from the corner. Switch to a ring bearing around the axis instead of a shaft and almost the whole map turns teal. The reference gun's three rotation axes and its beam line sit on the map as coloured circles.

## The proposal

Not an arrangement: a check every donor pivot should pass before it is drawn. Photo pano heads, geared heads, gimbals, goniometer cradles, moving-head yokes and telescope forks all rotate about a point in free air. The dot is at a corner of metal. For each axis direction the page asks three questions: does a shaft (thickness ρ, widening from a needle at the dot by a taper) fit on one side; does one fit through the dot on both sides (a yoke or fork); does a ring bearing (bore radius R, housing half-thickness w, at distance d along the axis) fit without touching metal.

## What carries loads, establishes position, is free or driven

Nothing: it decides where a bearing may stand. The solids are the tube wall (r 61.85 to 63.5 mm, z 0 to 152.4), the endcap (r to 61.72, z 139.7 to 146.05) and the bench plane; the rotator base and towers are not included.

## Software: command, observe, manual

Nothing to command or observe. Manual: choosing where the pivots go.

## What was tried to break it

1. **Is the map what a designer needs?** Conflict: a shaft only has to clear metal away from the dot in this model; a real cantilever axis also needs a bearing housing and the gun to clear. Change: the ring test checks only the ring's circle, and the page says the gun that must pass through it is not tested. Uncertain: the gun's real shape (scan).
2. **Rays that start in the wall.** Conflict found while writing it: an outward ray from the dot passes through the 1.65 mm wall before it reaches free air, so a shaft that starts beyond the wall is not connected to the dot. Change: the shaft test starts at the dot with a taper (radius min(ρ, k t)); the crease line, the level inward axis and straight up are blocked for any thickness.
3. **Ring test on an axis in the plate plane.** A ring 80 mm out along the hole axis, radius 60, is free (the ring is outside the wall); the same ring on the inward side is blocked (its circle crosses the plate and wall). The verdict table reports which side works.

Numbers (calc/free_directions.py, shaft from t0 = 12 mm, length 150 mm, geometry [repo] dimensions; the scene uses a taper from the dot, so its verdicts for the vertical axis are stricter):

| shaft radius | fraction of directions free, one side | free on both sides |
|---|---|---|
| 0 | 100 % | 100 % |
| 2 mm | 64 % | 38 % |
| 5 mm | 38 % | 12 % |
| 10 mm | 1.6 % | 0 % |
| 20 mm | 0 % | 0 % |

With ρ = 5 mm and t0 = 12 mm the vertical axis fits one-sided, the level inward and tangent axes never do (they lie on the endcap face and the wall face).

## Branches and combinations

- Feeds borrowed-01-ring-pivots (the case for rings) and borrowed-02-gimbal-on-gantry (the case for giving up the dot as a pivot).
- Transferable: the free-direction map for any other pivot or camera-mount question at the joint.

## Unresolved problems and questions that need Derek

- Whether the printed shell can be thin enough near the nozzle for a cantilever to be more than a needle (measurement of the nozzle region from the scan).
- No questions for Derek's observation beyond the scan.

## Assumptions

- Tube and endcap dimensions [repo] via the kit; nose taper, shaft radius, bearing length, ring size and distance: illustrative sliders; dial values start at the reference scene's opening pose (illustrative); clearances are analytic distances to solids of revolution; no fasteners, printed wall or tolerances.

## Sourcing pointers

None needed.

## Scene

`borrowed-04-axis-map`
