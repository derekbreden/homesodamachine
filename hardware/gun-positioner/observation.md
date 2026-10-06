# One-camera learning and replay

One FoMaKo K20UH and Raynox DCR-250 view the actual aiming dot, actual wire
endpoint and seam. The camera measures projected image-plane positions.
It does not observe hidden depth or independently establish focus. All
learning is dry; the stand withdraws before welding. The qualified path
then replays continuously from the existing rotator pedal.

Use the [mechanical and electrical checks](commissioning.md) first. The
following commands run from the repository root with `tools/cad-venv/bin/python`.
Files filled with observations/configurations belong outside this public
repository. Examples use `/tmp/pgfun`; use a durable personal folder for
accepted sessions. Replace the camera ID and serial-device examples with
actual enumerated values.

## Camera setup

Keep its base level. Withdraw the macro upright/cassette before every camera
boot: automatic self-test moves the head and zoom. After self-test, set the
head to the recorded 29-degree downward view and reattach the macro carrier.
Use the supplied 12 V adapter and USB3 A-to-B cable through the acquired
Anker 332 USB-C hub. Camera and positioner use its two USB-A data ports;
the unrelated panel camera is disconnected during these measurements.

Set the camera's HDMI video format to 4K and enable USB 4K mode. The camera
manual makes these prerequisites for native USB 3840x2160 output; its LAN/NDI
stream becomes 1080p in that mode. The helper and new observer require native
3840x2160 frames. A scaled 1080p stream does not satisfy this procedure.

With the camera's web/OSD controls, set manual focus, manual exposure,
fixed white balance and auto-tracking off. Record zoom, focus, exposure and
pan/tilt settings in the local configuration. The new observer's booleans are
operator records, not a camera read-back. Any setting or stand movement
requires new scale/noise calibration and affected learning.

Start near the DCR-250's approximately 109 mm working distance. Adjust stand,
head, cassette and optical zoom until the actual wire endpoint, red dot and
seam are simultaneously sharp and visible across the intended small sweep.
Start with about 10 mm field width. Reject clipped dot pixels, reflections
that compete with the dot, and a wire silhouette merged with the seam.
Reduce exposure or improve lighting/angle instead of identifying the wire
nozzle as the endpoint. Check rim occlusion in the received setup.

## Scale, regions and stationary noise

Enumerate the physical camera and copy the template:

```sh
mkdir -p /tmp/pgfun
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/observe.py --list
cp firmware/src_pgfun_positioner/host/optics.example.json /tmp/pgfun/optics-initial.json
```

Fill `dot`, `wire` and `seam` ROIs as `[x,y,width,height]` in native full-frame
pixels. Each should isolate its actual feature. Set wire approach direction
and dark/bright polarity from the real image; configure seam orientation
from its local straight segment. ROIs are arrays, not dictionaries.

Calibrate tangent and normal scales separately in the joint's reference
plane, using a known long dimension measured with the acquired caliper.
A 20 mm baseline reduces the relative effect of its coarse resolution.
Repeat at an independent length/location and record the scale discrepancy.
For a small field, acquire the long baseline at a wider recorded zoom, then
calibrate the final zoom directly with the largest known dimension that fits;
do not assume a zoom-ratio conversion. A temporary coupon with caliper-checked
edges in that plane supplies the reference. Do not use commanded motor
counts as the length reference. Include scale-error contribution over the
observed correction range in the 0.0025 mm measurement uncertainty allowance.

Set `mm_per_pixel` to the two measured values, `manual_focus` and
`manual_exposure` true, `auto_tracking` false, and an initial conservative
`stationary_sigma_px` of 1. Keep `noise_qualified` false. Save a native camera
frame using its camera application or the shared helper's frame-export path,
and retain it with ROI/scale records. Focus and exposure must remain fixed.

Record a 30-second stationary sequence with motors holding the working mass
and cable after warm-up. The observer can collect this initial sequence;
the motor-response learner refuses it until noise is qualified.

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/observe.py \
  --camera-id 'ACTUAL_CAMERA_ID' --config /tmp/pgfun/optics-initial.json \
  --latest /tmp/pgfun/latest.json --log /tmp/pgfun/stationary.jsonl --seconds 30
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/noise.py \
  /tmp/pgfun/stationary.jsonl /tmp/pgfun/optics-initial.json \
  /tmp/pgfun/optics.json --receipt /tmp/pgfun/noise-receipt.json
```

The noise check requires 300 valid physical frames, at least 15 seconds,
98% valid coverage, sigma <=0.0025 mm, p95 <=0.005 mm and maximum <=0.010 mm.
It derives an empirical pixel-jitter floor. The live observer also propagates
feature and seam-angle uncertainty; stationary jitter alone cannot certify
absolute endpoint accuracy or scale bias. Improve optics/support if the
result fails, without lowering the requirement or inventing a noise value.

Restart the observer with `/tmp/pgfun/optics.json`, the same camera ID,
latest path and a new log, with `--seconds 3600`. Keep that process running
in a separate terminal for all dry learning. Frames older than 200 ms,
sequence gaps, clipped dots and invalid features cannot control motion.

## Loaded responses, including reversals

Align and remove both parking pins before **each** motion session. The
`--reference-central` option records that physical action; it does not perform
it. Use the same pin bias, tube setup, temperature and cable route.

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/servo.py learn \
  --port /dev/cu.YOUR_POSITIONER --latest /tmp/pgfun/latest.json \
  --output /tmp/pgfun/train.json --reference-central
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/servo.py fit \
  /tmp/pgfun/train.json /tmp/pgfun/model-candidate.json
```

Repeat `learn` into `/tmp/pgfun/response-holdout.json` after a fresh physical
datum, then qualify:

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/servo.py qualify \
  /tmp/pgfun/model-candidate.json /tmp/pgfun/response-holdout.json \
  /tmp/pgfun/model.json
```

The learner probes 2/4/8/16/32/64-count levels with two independent vectors
in each of four direction branches. Each probe returns from the opposite
approach before observation. It fits a loaded 4x2 response and per-axis
reversal deadband of 0..32 counts. Deadband at the search boundary calls for
larger bounded probe levels or mechanical correction; it is not established
as <=32 simply because the search stops there. The holdout requires five
independent responses per branch and the stated error limits. Inspect all
fitted deadbands and useful movement before accepting the model.

At a focused, physically correct working pose, copy a fresh valid
`latest.json` to `/tmp/pgfun/target.json`. Check its dot/wire positions and
retain a frame showing both at the intended joint. The target must have the
same optical-configuration digest as the response model. Do not use a
synthetic coordinate or the commanded count-zero as the target.

## Learn periodic correction

Index the tube/nest physically, choose one rotator direction and a speed of
5..15 mm/s, and release the pedal for at least 12 seconds before each run.
The example uses **8 mm/s, clockwise, index label `tube-zero`**. This gives
about 48.6 seconds per revolution. Keep camera observation running.

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/trajectory.py capture \
  --port /dev/cu.YOUR_POSITIONER --reference-central \
  --latest /tmp/pgfun/latest.json --output /tmp/pgfun/baseline.json \
  --log /tmp/pgfun/baseline-control.jsonl --seconds 110 \
  --speed 8 --direction cw --index tube-zero
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/trajectory.py fit \
  /tmp/pgfun/baseline.json /tmp/pgfun/model.json /tmp/pgfun/target.json \
  /tmp/pgfun/path-candidate.json
```

Hold the existing pedal when the capture reports ready. The positioner
waits 20 ms debounce plus 200 ms to match the rotator's cold-start settling.
Capture at least two full revolutions and 512 observations, with three
independent observations in every one of 64 phase bins. Host/device clock
uncertainty must be <=5 ms. A three-harmonic fit learns repeatable runout;
nonrepeatable residual beyond 0.005 mm rejects the setup.

The inverse includes the measured reversal branches and lost-motion
allowance. That compensation is a candidate until measured during replay.
It is not a claim that an advertised backlash value was removed exactly.
All 256 path knots and their interpolated cubic envelope must satisfy travel,
rate and acceleration limits. Required correction outside 0.250 mm local
neighbourhood or outside the two-axis span calls for improved static alignment.

## Independent dry validation and welding

Capture the candidate twice using the preceding capture command with
`--profile /tmp/pgfun/path-candidate.json`, separate output/control-log
filenames, and a fresh physical index/datum before each. Keep identical
speed, direction, index label and optical settings. Then:

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/trajectory.py qualify \
  /tmp/pgfun/path-candidate.json /tmp/pgfun/dry-a.json /tmp/pgfun/dry-b.json \
  --output /tmp/pgfun/path.json
```

Both independent replays must keep dot and actual wire errors at maximum
0.010 mm and p95 0.005 mm. If a repeatable residual remains, fit a revised
candidate using a captured replay and the same qualified model/target, then
collect two new holdouts of that exact candidate. Training and validation
samples may not overlap. Repositioning or changed optics require a new model.

After an accepted dry result, stop observation and withdraw the entire camera
stand. Match the accepted tube index, datum, cable route, speed and direction.
Use the factory gun trigger with the working weld recipe while replaying:

```sh
tools/cad-venv/bin/python firmware/src_pgfun_positioner/host/trajectory.py replay \
  --port /dev/cu.YOUR_POSITIONER --reference-central \
  --profile /tmp/pgfun/path.json --seconds 60 --log /tmp/pgfun/weld-control.jsonl
```

Release the pedal to stop the lap and factory trigger to stop emission.
Replay has no camera input and no rotator angle encoder; its qualification is
specific to the independent dry repeatability of that setup. It is a
continuous motor path, not a sequence of stop-and-settle camera corrections.
Automatic emission control depends on the separate X1 interface work.
