# Replaying the cup photographs

The restored setup uses a new reference photograph after Derek put the tubing back and changed the electrical connections. The time of the earlier pump fall is unknown. Keep the earlier width series and the intervening observations separate from the restored-head calibration. The transition table preserves the camera readings for `gap-1b`. Its left and right readings disagree sharply. Both calibrations use other trials.

## Restored tubing

The dry front graduations register each color photograph against its own setup. The liquid measurement comes from averaged luminance exposures. The color sample has a separate presentation timestamp. A projection from clear glass to the left quarter-cup scale supplies the approximate left volume when printing obscures that contact. The right contact has a direct scale reading. Both share the uncalibrated kitchen cup and changing brightness in reflected glass.

`reset_check.py` matches local surface profiles against the reset photograph across the left, central and right-hand glass. `outer_check.py` independently locates a falling brightness crossing just outside the operating pixels. This outer strip was held out of the decision to run or correct a pump. The other regional measurements also served as checks during acquisition. Their independently recorded results retain the stretch measured on the qualification shots. Two areas can thus agree on direction while showing different pixel displacements.

Use Python with NumPy, Pillow and SciPy. Run from the dated record directory. The output includes settled trial endpoints, actual signed changes, requested destinations, missed targets, and idle drift.

```sh
python optics/audit_reset.py . --output /tmp/restored-cup-replay
python optics/verify_optics.py . /tmp/cup-registration-replay.json
```

The raw reference is available under `camera`. The endpoint crops and color tiles are in `frames` and `ink`. Inspect an individual endpoint with its own color sample by passing the two source paths to `reset_check.py`. The direction figure pairs actual luminance crops from the same camera window used by the reader. Every panel uses the same display stretch.

## Earlier cup view

`independent.py` fits each side of the surface in separate unprinted patches outside the operating strips. Each flank searches for an edge without reading a motor command or the opposite side. The search suppresses stationary printing and compares local brightness above and below the liquid with the higher-fill reference. A fit through the accepted stations estimates the contact at the fixed sightline. The tables retain both camera rows and positions relative to the cup's dry ink. Each side converts its height using its own printed graduations.

```sh
python optics/reduce.py --frames frames --ink ink --logs logs --log-prefix qualification-a.jsonl --log-prefix width- --log-prefix gap-1.jsonl --output /tmp/earlier-cup-replay
python optics/reduce.py --frames frames --ink ink --logs logs --log-prefix gap-1b.jsonl --output /tmp/cup-transition-replay
```

`pre-reset/optical-summary.json` gives the observed idle limits, disagreement between printed scales, and the difference from the operating reader. The spread among patches tests sensitivity to the sightline. Variation across separately commanded trials includes pump behavior and optical uncertainty. An idle observed at a particular fill gives an empirical local check on drift.
