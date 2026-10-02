# Elbow cradle snap trial

A test receiver and a test cradle for the funnel's drain-elbow cradle. The trial decides
whether the production snap goes together and holds as drawn: full-length wings standing on
the cradle's body, flat hooks reaching outward over the frame's [3 mm](TRIAL_WEB) bottom web, and straight
slots with square edges. The production frame and cradle use the same geometry, so a pass
carries straight to the machine and a failure names the dimension to change before the frame
is printed.

## Parts

- `test-receiver.stl`: the production funnel frame cut down to the block round its plug
  socket: the web with the [11.25 mm](TRIAL_HOLE) drain hole and both wing slots, and the socket's walls
  to [12 mm](TRIAL_RECEIVER_H) above the frame's underside. [48.6 × 54 × 12 mm](TRIAL_RECEIVER).
- `test-cradle.stl`: the production [elbow cradle](../elbow_cradle.py), on its bottom.

[`cradle_trial.py`](cradle_trial.py) cuts both from the production generators and writes
[`geometry-check.json`](geometry-check.json): nominal clearances and the wing-bend estimate.

```sh
tools/cad-venv/bin/python hardware/printed-parts/zone-c/funnel/cradle-trial/cradle_trial.py
```

## Print

Both print in black PET-GF with the enclosure's settings: a 0.20 mm first layer and 0.24 mm
layers above it. The receiver prints on its flat underside, as the frame does, and needs no
support. The cradle prints on its bottom with the pocket opening upward. The two hooks' flat
undersides are retention bearings [33.6 mm](TRIAL_HOOK_BED) above the bed and take accessible supports from the
bed under them. Nothing else on the cradle needs support.

The H2C print and its native slice are recorded in [`h2c-print/`](h2c-print/README.md).

## Procedure

Use the scanned [PP0308E elbow](/hardware/reference/jg-pp0308e-elbow/README.md).

1. Drop the elbow into the cradle, vertical leg up and horizontal leg along the trough. It
   should fall in under its own weight and sit without rocking.
2. Hold the receiver with its socket facing up. From below, guide the elbow's collet into the
   drain hole and each wing into its slot.
3. Pinch both wings inward, about [2.4 mm](TRIAL_PINCH) at the hooks, and push the cradle up until the hooks
   pass the slots' outer edges. Release the wings; the hooks spring out over the web.
4. Let go of the cradle. It drops [0.4 mm](TRIAL_CATCH) and hangs from its hooks.
5. To remove it, press both hooks inward from inside the socket and draw the cradle down.
6. Repeat steps 2 to 5 five times.

## Acceptance

- The cradle goes home by hand with the wings pinched in, and comes back out the same way.
- No wing cracks, whitens at its root, or stays bent after release.
- Hanging from its hooks, the cradle holds the elbow's nose against, or within
  [0.4 mm](TRIAL_NOSE) of, the receiver's underside, with the collet standing up the hole.
- Pulled down by hand, the cradle stays on its hooks.

Record the result in `physical-acceptance.json` beside this file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/zone-c/funnel/cradle-trial/cradle_trial.py`
