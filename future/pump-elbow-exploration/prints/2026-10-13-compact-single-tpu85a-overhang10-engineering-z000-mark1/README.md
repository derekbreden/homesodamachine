# Single TPU 85A elbow — overhang speed 10 mm/s

**Prepared offline; not submitted.** Native estimate: **68 minutes / 4.30 g**.

The user reports [filament drying underway](filament-drying.json) and plans
the next attempt on 2026-10-14. The screenshot displays a 75°C / 18-hour
drying run, at 74°C with 17:48 remaining. Drying completion is unreported.

One compact elbow, Mark1 right fixed 0.6 mm nozzle, TPU 85A, glued Engineering
Plate and zero user Z trim. The native mesh and pose match the
[rough 225°C article with accepted manual fit](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json).
This candidate uses that article's recipe: 225°C nozzle, 35°C bed,
0.20 mm first / 0.12 mm normal layers, 0.62 mm line widths, six requested walls,
100% infill, inner/outer wall order, full part and auxiliary cooling,
5 mm brim and no supports. Cuff dimensions and insertion depths are retained.

The [native readback](native-readback.json) identifies exactly two process
changes plus the recipe label: `overhang_2_4_speed` from 50 to 10 mm/s and
`overhang_3_4_speed` from 30 to 10 mm/s. The ordinary outer-wall setting
remains 10 mm/s. The filament override remains off; its separate table is
inactive. The mild-overhang zero entry retains the ordinary role speed;
the remaining overhang entries are already 10 mm/s.

The [actual lip review](curl-toolpath-review.json) records **10 mm/s throughout
layers 17–33** on the complete closed exterior perimeter, including feed-only
commands. A separate modal-feed scan finds **10 mm/s on all 13,728 outer-wall
extrusions across normal layers 2–184**. This establishes the intended emitted
speed; the earlier outer-wall-setting-10 archive emits 14.37 mm/s at layer 21
and 16.40 mm/s at layer 27 on the actual lip.

Bambu Studio's overhang interpolation can replace the ordinary outer-wall
speed with a higher table value. The exact installed release's
[interpolation](https://github.com/bambulab/BambuStudio/blob/926a7192574bcb9b3a732e1ec59a46d79cb45466/src/libslic3r/GCode.cpp#L6677-L6708)
and [replacement](https://github.com/bambulab/BambuStudio/blob/926a7192574bcb9b3a732e1ec59a46d79cb45466/src/libslic3r/GCode.cpp#L7221-L7231)
explain the mismatch. This candidate directly tests a slower lip against the
identified 225°C fit baseline. It supplies no physical surface or fit result.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-overhang10-engineering-right06-z000-mark1.3mf)
- [Native sliced archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1/2026-10-13-compact-single-elbow-tpu85a-overhang10-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)
- [Manual toolpath review](../../review_curl_toolpath.py)

The preparation script only slices the saved geometry offline. It does not
connect to or submit a job to a printer.
