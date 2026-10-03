# Magnetic float

The current float is one **36 × 28 mm ASA Aero body** with a **K&J RC62 ring
magnet centered 14 mm above its bottom**. A pause allows insertion before the
pocket closes. Three articles serve the carbonator and the two flavor reservoirs.

[Float CAD, calculations and print evidence](all-aero/README.md) ·
[Rod positions and reed calibration](all-aero/installation.md) ·
[Assembly](/3d?file=printed-parts/cold-core/magnetic-float/all-aero/assembly.step) ·
[Section](/3d?file=printed-parts/cold-core/magnetic-float/all-aero/section.step)

Each 3.175 mm guide rod stands **20 mm from the inside wall**. The 4.8 mm
float bore provides running clearance; the body has 2 mm nominal wall clearance.
The carbonator register and reservoir rod bosses derive from the same
[`_float_interface.py`](../_float_interface.py) dimensions.

## Reed reach

The printed ASA Aero float's reported usable distance is **20 mm from the
nearest float edge to the reed center**. Response at 21–24 mm is intermittent;
25 mm consistently does not work. The initial design maximum is **18 mm**,
including upright retreat through the guide bore. Current maximum distances are
**5.714 mm in the carbonator** and **11.063 mm in either reservoir**. The
20 mm guide-axis-to-inside-wall drilling datum is a separate dimension.
The [physical record](all-aero/physical-observations.json) preserves the report
and its scope; installed liquid switching heights still require
[calibration](all-aero/installation.md#reed-calibration).

### Bare RC62 reference

Measured on the bench with one bare RC62 and one Littelfuse MDSR-7-10-15 reed,
the reed standing parallel to the magnet's axis. Each distance runs from the
reed to the magnet's nearest outer edge. The signal stayed stable while the
magnet was turned about 45° off that orientation in any direction.

| Reed to magnet edge | Height of magnet travel with a stable signal |
| --- | --- |
| 30 mm | about 30 mm, ±15 mm about the reed's center |
| 40 mm | about 25 mm, ±12.5 mm |
| 50 mm | the limit of stable detection |

These magnet-edge measurements use a different datum from the float-edge test.
They do not establish the printed float's waterline or directional closure and
release through an installed vessel wall.

## Physical record

[Physical observations](all-aero/physical-observations.json) bind the successful
paused insertion and initial covering layers to the accepted v1 print. Finished
buoyancy, pressure endurance and compatibility with the actual flavoring have
no acceptance record. ASA Aero is the selected trial material throughout the float.

[Material research](asa-aero-research.md) ·
[Pressure-process research](pressure-printing-research.md) ·
[Separate PETG-shell bench reference](petg-bench-reference.md)
