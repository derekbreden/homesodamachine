# Second grip insert — H2C

One grip-cover insert for the pair of production enclosure grips. The mesh matches
the insert in the [accepted v4 grip trial](../physical-acceptance.json).

H2C reports task **1300913879** complete at 20/20 layers with no print error or
HMS alert. [completion.json](completion.json) records that reading and the user's
clear-bed confirmation for the next print. Print quality and the second insert's
physical fit are not recorded here. [launch.json](launch.json) retains the launch
receipt and startup observations.

The H2C native slice uses the accepted trial's PET-CF profile for black PET-GF,
the left 0.4 mm nozzle, and the left external spool. The first layer is 0.20 mm,
the body layers are 0.24 mm, and the top curve uses 0.08 mm layers. Both end wings
print on the first layer. There are no support paths or brim.

Requested Z trim is **+0.18 mm**. The textured-plate compensation produces
`G29.1 Z0.16` in the emitted start G-code. The estimated print time is 11 minutes
47 seconds, across 20 layers.

[preflight.json](preflight.json) records the source and slice hashes, accepted
layer comparison, wing bead overlap, and Z commands. [preview.png](preview.png)
shows the single centered part. [prestart-status.json](prestart-status.json)
records H2C's completed front-bottom job and Mark2's running back-bottom job.
[launch.json](launch.json) records the new H2C job and printer confirmation.

The native archive is submitted through Bambu Connect with Timelapse On, Bed
Leveling On, Flow Dynamic Calibration Auto, and Nozzle Offset Calibration Auto.

To prepare another reviewed slice:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/enclosure/grip-cover/h2c-second-insert/prepare.py --revision 3
```

[prepare.py](prepare.py) checks the accepted source hash, preserves its print
settings and layer schedule, applies H2C's Z trim, slices with Bambu Studio's
native slicer, and writes the verification record. Each revision uses a separate
directory under `.cache/prints/`.
