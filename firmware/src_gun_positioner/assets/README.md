# Prepared Pico upload assets

Two RP2040 Pico images are compiled and bound to the source and mechanical
geometry in [build-manifest.json](build-manifest.json). Both use 16 external
microsteps, fixed SpreadCycle and R110 module sense resistors.

| Image | Fixed RMS current estimate | Peak count rate | Intended commissioning stage |
|---|---:|---:|---|
| [gun-positioner-bench.uf2](gun-positioner-bench.uf2) | 0.337 A | 2,000/s | Isolated secured motor tests, belts disconnected |
| [gun-positioner-loaded-development.uf2](gun-positioner-loaded-development.uf2) | Z 1.271 A; pitch 0.459 A; other axes 0.337 A | 1,000/s | Loaded dry development after passive retention, overload and wiring acceptance |

Unplug 24 V and engage mechanical supports before BOOTSEL upload. Copy only
the explicitly selected image to RPI-RP2. After power and console connection,
verify the named `profile`, `current_scales` = [10,10,10,10,10,10] or
[10,10,22,10,14,10], `configured_vsense` = [1,1,1,1,1,1] or [1,1,0,1,1,1],
matching decoded `vsense`, `max_rate` = 2,000 or 1,000, six decoded `microsteps` = 16
and `counts_per_mm` = 6,400 after `clear`. Null VSENSE/microsteps mean unverified.
Neither image is a qualified
loaded-motion, camera-accuracy or laser-control release. No board was flashed
or positioner actuated during asset preparation.

Run `python3 firmware/src_gun_positioner/verify_assets.py` before sharing or
uploading. Source/geometry changes require rebuilding and updating this manifest.
See the [commissioning procedure](../../../hardware/gun-positioner/commissioning.md).
