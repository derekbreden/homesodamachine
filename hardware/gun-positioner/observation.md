# Gun-positioner observation

The toolkit in [`tools/gun-positioner-observation/`](../../tools/gun-positioner-observation/README.md)
records what the positioner does. Two cameras' native 3840 × 2160 frames, the
cameras' optical settings, every controller move receipt and the live-weld
probe channels go onto one host monotonic timeline, in append-only session
directories. Offline, it fits the local response of image features to screw
counts, validates the fit on held-out trials, and proposes bounded corrections
that default to no motion. It contains no laser, trigger, wire-feed or rotator
output. Hardware moves only through the controls `Client`, and only when the
caller passes `allow_hardware=True`.

## Boundary with the controls package

The [controls package](control.md) owns the controller: firmware, the USB
`Client` with its heartbeat, sequencing and request bounds
(`firmware/src_gun_positioner/host/positioner.py`), axis order X, Y, Z, U, V, W,
6,400 counts/mm, soft limits and `split_target` (`host/kinematics.py`), and
`fit_jacobian`/`correction` (`host/visual_servo.py`). The observation toolkit
imports those modules from their files and redefines none of them. It owns:

| Part | Module |
|---|---|
| Camera capture, frame receipts, drop evidence | `capture.py`, `helper_stream.py`, `helper/` |
| Optical settings, VISCA, the measurement gate | `optics.py`, `visca.py` |
| Move receipts on the session timeline | `moves.py`, `controls.py`, `timeline.py` |
| Session directories and the record schema | `dataset.py`, `schema.py`, [`observation-schema.json`](../../tools/gun-positioner-observation/observation-schema.json) |
| Feature extraction | `features.py` |
| Offline response fit and held-out validation | `response.py`, `validation.py` |
| No-motion gates, reversal take-up and stall guards around `correction()` | `proposal.py` |
| Dry-learning runs and the simulator | `experiment.py`, `simulation.py` |
| The `learn` workflow, operator templates and the gates before real motion | `learn.py`, `config.py` |
| Contact-probe channels and cold baselines | `liveweld.py` |

`visual_servo.correction()` computes every correction step. `fit_jacobian`
is fitted on the same training trials as a held-out baseline in each
validation report.

## Running it

Use `tools/cad-venv/bin/python` (numpy and Pillow) from the repository root.
Session directories and filled configurations belong outside the repository.

```sh
# 134 tests, about 30 s
tools/cad-venv/bin/python -m unittest discover -s tools/gun-positioner-observation/tests

# Dry learning on the simulator: engage, probe, fit, validate, closed loop
tools/cad-venv/bin/python tools/gun-positioner-observation/observe.py simulate \
  --root /tmp/gpo/sessions --out /tmp/gpo/analysis --closed-loop

# Fit and inspect recorded sessions
tools/cad-venv/bin/python tools/gun-positioner-observation/observe.py fit SESSION_DIR --out ANALYSIS_DIR
tools/cad-venv/bin/python tools/gun-positioner-observation/observe.py check SESSION_DIR
```

## Camera setup from the templates

[`examples/cameras.example.json`](../../tools/gun-positioner-observation/examples/cameras.example.json)
holds camera A and camera B: unique ID and listed name, physical position
label, the measured capture format, the optics source (an optics receipt, or a
VISCA connection with its serial port or IP address) and the clock-check
receipt. [`examples/operator-optics.example.json`](../../tools/gun-positioner-observation/examples/operator-optics.example.json)
is one camera's optics receipt: focus, exposure and tracking state, zoom,
focus, shutter, iris, gain and white balance as displayed or read back, the
lens, and when, by whom and how they were recorded. Every operator entry is
`FILL_ME` or null, including the verified format, which is measured on this Mac
with the camera rather than taken from the manual.

```sh
OBS=tools/gun-positioner-observation; PY=tools/cad-venv/bin/python; SETUP=~/gpo-setup; mkdir -p $SETUP
ls $OBS/helper/build/GPOCapture.app   # shipped ready to use; $OBS/helper/build.sh rebuilds it from source
$PY $OBS/observe.py cameras --save $SETUP/cams-none.json        # both K20UH unplugged
$PY $OBS/observe.py cameras --new-since $SETUP/cams-none.json --save $SETUP/cams-a.json   # camera A plugged in
$PY $OBS/observe.py cameras --new-since $SETUP/cams-a.json      # camera B plugged in
cp $OBS/examples/cameras.example.json $SETUP/cameras.json
cp $OBS/examples/operator-optics.example.json $SETUP/cam_a-optics.json
cp $OBS/examples/operator-optics.example.json $SETUP/cam_b-optics.json
$PY $OBS/observe.py validate-config $SETUP/cameras.json         # after filling both unique_id and name
$PY $OBS/observe.py capture --config $SETUP/cameras.json --root ~/gpo-sessions --label format-check --seconds 10 --every-n 100
$PY $OBS/observe.py format-report "$(ls -d ~/gpo-sessions/*-format-check-* | tail -1)"
$PY $OBS/observe.py optics check $SETUP/cam_a-optics.json --camera-id cam_a
$PY $OBS/observe.py optics check $SETUP/cam_b-optics.json --camera-id cam_b
$PY $OBS/observe.py clock-check --out $SETUP/clock-check.json
$PY $OBS/observe.py validate-config $SETUP/cameras.json --measurement
$PY $OBS/observe.py capture --config $SETUP/cameras.json --root ~/gpo-sessions --label dry-measure --seconds 10 --measure
$PY $OBS/observe.py check "$(ls -d ~/gpo-sessions/*-dry-measure-* | tail -1)"
```

Each `--new-since` run prints the one device that appeared: copy its
`unique_id` and `name` into that camera's entry. Covering camera B's lens during
the format-check capture makes its stored frames dark, a second check of the
assignment. The first capture asks once for camera access for GPOCapture. Copy
each camera's `verified_format` block from the format report, then fill
`position`, the optics source and the receipts. With VISCA, `observe.py optics
inquire --camera-id cam_a --serial PORT --baud N --out $SETUP/cam_a-optics.json
--recorded-by NAME` writes the read-back receipt.

`validate-config` with only the unique IDs filled is enough for that dry
capture, whose frames are never measurements. `--measurement` and
`capture --measure` refuse the configuration, before any session directory is
made, while any `FILL_ME` or required null remains, while the verified format is
incomplete or not 3840 × 2160 with `require_native_4k`, while a receipt is
unfilled, for another camera, older than `receipt_max_age_hours`, or shows
autofocus, automatic exposure or tracking on or unknown, while a VISCA entry is
incomplete, and while the clock check is missing or no longer matches.

The clock check: session records carry `mono_ns` from `time.monotonic_ns()`,
which orders frames, moves and probe samples and never steps, and `wall_ns` from
`time.time_ns()`, which is for people and can step when the clock is set. The
check reads the helper's `CLOCK_UPTIME_RAW` and CoreMedia host-clock values
between two `time.monotonic_ns()` readings and passes when both lie inside that
bracket. Its receipt names this Python's monotonic clock and the helper build's
SHA-256, so rebuilding the helper or changing Python requires a new check.

## Cameras on this Mac

`ffmpeg -f avfoundation` selects a camera only by list index or by name. Two
K20UH cameras share a name, and indices move when another camera appears, so
neither identifies a camera. AVFoundation's unique ID does: for a UVC camera it
combines the USB location with the vendor and product IDs, and it stays fixed
while the camera stays in its port (`system_profiler SPCameraDataType` shows the
bench's 16MP UVC camera as `0x13000032e41298`). The Swift helper
`helper/GPOCapture` opens a camera with `AVCaptureDevice(uniqueID:)`.

The helper asks for samples in the device's native format. AVFoundation lists
the bench's 16MP Motion-JPEG camera only in decoded formats (`420v`, `yuvs`), so
a K20UH's 4K Motion-JPEG stream is expected to arrive as pixels decoded by
macOS rather than as JPEG bytes. The helper writes the luma plane (`gray8`),
or luma with interleaved chroma (`nv12`, for the red aiming dot), and writes
compressed samples byte for byte when a device offers them. A 3840 × 2160
luma frame is 8.3 MB as PGM and an NV12 frame 12.4 MB, so by default only
frames inside measurement windows are stored; PNG storage is lossless and
smaller.

The FoMaKo manual (section 1.3) gives 3840 × 2160 at 30 fps over USB only as
MJPG or H.264, only in USB 4K mode and only while HDMI output is 4K; YUY2/NV12
stop at 1080p and NDI at 1080p30. Each frame's delivered size is checked, and a
frame that is not 3840 × 2160 is excluded from measurement.

macOS grants camera access to an app bundle. `HelperSource` launches
`GPOCapture.app` through LaunchServices (`open -n -W -g -o FIFO`) so the bundle
holds its own permission, as `tools/panelcam-shot` does; an `exec` launch works
from a terminal application that already has camera access. Both launch paths
carry the helper's stream into Python on this Mac.

Each frame record carries the helper's sample sequence number, the sample's
presentation time on the host clock, the helper's callback time
(`CLOCK_UPTIME_RAW`), and Python's `time.monotonic_ns()` and wall time at
receipt. On this Mac `time.monotonic_ns()` is `mach_absolute_time()`;
`observe.py clock-check` confirms that the helper's clocks read inside a
Python bracket. Presentation time is the frame's arrival in the capture
pipeline, not its exposure time. Drops are recorded as `frame_gap` records with
their evidence: AVFoundation drop notices, presentation-time gaps (with the
number of notices that explain them), helper sequence gaps and host-queue
overflow.

## Optical settings and the measurement gate

A frame is a measurement only when every camera's optics are known to be fixed:
manual focus, manual exposure and auto-tracking off. Otherwise a measurement
window is refused (`measurement_refused`), or opened with its frames recorded as
non-measurement and the reasons logged (`--on-unknown log`). Optics are recorded
at session start, at the start of every window and, where they can be read
back, at its end. A change in zoom, focus, pan, tilt, exposure or video system
between the two readings invalidates the window; frame gaps and the two
cameras' frame-pairing skew are recorded with it.

`visca.py` encodes and decodes the messages tabulated in the
[FoMaKo manual](https://www.fomako.net/uploads/20250529/ce40713967c8ae0e137cabdd8a72ff1d.pdf),
section 5, byte for byte: ACK, Completion and error replies with `y = x + 8`;
zoom, focus, exposure and white-balance commands; inquiries for power, zoom,
focus mode and position, exposure mode, shutter, iris, gain limit, brightness,
white balance, pan/tilt position, video system and version. The serial
transport uses the manual's 8 data bits, no parity, 1 stop bit at 2400, 4800,
9600, 38400 or 115200 baud. The manual names network ports 1259 ("IP Visca")
and 52381 ("Sony Visca") without stating TCP or UDP or any header; the TCP and
UDP transports send bare VISCA messages to a chosen port, and no 52381 header is
encoded. The manual prints the Tracking OFF/ON packets only for address 1 and
has no tracking inquiry, so tracking reads `off_commanded` only after this
session's Tracking OFF returned its Completion. Every exchange records its
send, ACK and Completion times.

`optics lock --apply` sends Tracking OFF, manual focus, manual exposure and any
direct zoom, focus, shutter, iris, gain-limit, brightness and white-balance
values, then reads them back. It sends no pan/tilt or power command; the
[camera-stage startup](../printed-parts/fixtures/gun-positioner-observation/README.md)
governs powering the camera. A camera whose optics source is a receipt is
gated on that receipt, aged from its `recorded_at`; its optics records are
marked `operator_entered_not_read_back`, and values outside the documented
vocabularies are rejected.

## Data format

```text
<root>/<UTC start>-<label>-<4 hex>/
  manifest.json        written once: schema gpobs/1, host, clock implementation, configuration
  events.jsonl         every record, appended and flushed
  frames/<camera>/<seq>.pgm|png|jpg
  helper-<camera>.log  the capture helper's diagnostics
  controller-client.jsonl   the controls Client's own log, when it runs
  closing.json         written once at close
```

Nothing is rewritten or deleted; failed, faulted and unresponsive trials keep
their outcome in `trial_end`. Every record carries `kind`, `rec`, `mono_ns` and
`wall_ns`. [`schema.py`](../../tools/gun-positioner-observation/gpobs/schema.py)
defines the kinds — camera, optics, frame, frame_gap, measurement windows,
move_command/ack/complete, clock_exchange, trial_start/end, observation,
proposal, probe_sample, table_encoder, cool_reference, notes — and
`observation-schema.json` is its JSON Schema. `observe.py check` verifies
record numbering, schema conformance, per-camera sequence and receipt order,
stored frame files, unterminated trials and moves without completion.

A move receipt maps one `Client.move()` call:

| Field | Source |
|---|---|
| `move_command.issued_mono_ns` | host stamp before the call |
| `move_ack.ack_mono_ns`, `controller_time_us`, `vm_epoch` | the Client log's receipt of the `ack` whose `op` is `MOVE6` and whose sequence is the move's; an ack with that sequence for another op, such as a late `PING` ack, is never used |
| `move_complete.complete_mono_ns` | host receipt of the first reply after that ack, from the same boot, whose `completed_seq` is the move's sequence |
| `controller_time_us` | the device's `completed_us` |
| `completion_mapped_mono_ns` and uncertainty | `completed_us` on the host clock, through a map fitted to the session's `clock_exchange` brackets |
| `reported_counts` | the returned status `count` (issued pulse history) |
| `controller` | every other status field: state, fault, health, `profile`, `current_scales`, `configured_vsense`, `vsense`, `microsteps`, `max_rate`, `vm_epoch`, `timer_ticks` |
| `driver_state` | `drivers()` rows read after the move, with `cs_actual`, `configured_cs`, `configured_vsense`, `sample_valid`, `microsteps`, `vsense`, `sample_us` |

Move durations come from the controller's reported `max_rate` (1,000 counts/s
when unreported) and its acceleration limit; a requested duration shorter than
those allow is refused. Relative moves larger than 640 counts are split with
the controls `split_target`. A rejected move changes nothing. A fault, stop or
timeout makes the moved axes' take-up state unknown, and a change in
`vm_epoch` between receipts — a motor-supply cycle — makes every axis's state
unknown and flags frames captured in that interval. A move the `Client`
completed whose log lacks its MOVE6 command, ack or completion reply is recorded
as `unverified` with the reason: it carries no ack or completion times, the
moved axes' take-up state becomes unknown, and a gated session halts.

## Dry-session learning

`observe.py learn` runs a dry session from the operator's files.
[`examples/features.example.json`](../../tools/gun-positioner-observation/examples/features.example.json)
defines, per camera, the region and detector thresholds of the dot, the wire
tip and the seam; [`examples/target.example.json`](../../tools/gun-positioner-observation/examples/target.example.json)
defines the desired relationships (a feature value, a difference of two, or a
point's signed distance from a seam line), their tolerances in pixels (or in
millimetres with a named calibration) and the axes a correction may move. A seam line is
reported as (x − cx)·cos θ + (y − cy)·sin θ = ρ about its region's centre
(cx, cy), where an angle error barely moves ρ. Every entry is `FILL_ME` until
the operator fills it, and `learn` refuses the files until they validate. Each region must hold its feature over the whole jog
excursion; an observation missing a feature makes its steps unusable.
`record`, `jog` and `execute` default to the simulator, which keeps its state
in `ROOT/simulated-world.json` and places each feature in its region.

```sh
OBS=tools/gun-positioner-observation; PY=tools/cad-venv/bin/python; SETUP=~/gpo-setup; RUN=~/gpo-sessions; SIM=~/gpo-sim
cp $OBS/examples/features.example.json $SETUP/features.json
cp $OBS/examples/target.example.json $SETUP/target.json
$PY $OBS/observe.py export-frame "$(ls -d $RUN/*-format-check-* | tail -1)" --camera cam_a --out $SETUP/cam_a.png
$PY $OBS/observe.py export-frame "$(ls -d $RUN/*-format-check-* | tail -1)" --camera cam_b --out $SETUP/cam_b.png
$PY $OBS/observe.py learn check --features $SETUP/features.json --target $SETUP/target.json --cameras $SETUP/cameras.json
$PY $OBS/observe.py learn plan --out $SETUP/jog-plan.json --axes X
# rehearsal on the simulator
$PY $OBS/observe.py learn jog --plan $SETUP/jog-plan.json --features $SETUP/features.json --root $SIM
$PY $OBS/observe.py learn fit "$(ls -d $SIM/*-jog-* | tail -1)" --features $SETUP/features.json --out $SIM/analysis
$PY $OBS/observe.py learn validate "$(ls -d $SIM/*-jog-* | tail -1)" --model $SIM/analysis/model.json --split $SIM/analysis/split.json --out $SIM/analysis
# 1. feature recording, real cameras, no motion
$PY $OBS/observe.py learn record --backend cameras --cameras $SETUP/cameras.json --features $SETUP/features.json --target $SETUP/target.json --root $RUN
# 2. jog trials on the controller (operator arms at the prompt)
$PY $OBS/observe.py learn jog --backend controller --port /dev/cu.usbmodemPICO --cameras $SETUP/cameras.json --features $SETUP/features.json --plan $SETUP/jog-plan.json --root $RUN --i-understand-this-moves-hardware
# 3. local response fit and held-out validation
$PY $OBS/observe.py learn fit "$(ls -d $RUN/*-jog-* | tail -1)" --features $SETUP/features.json --out $RUN/analysis
$PY $OBS/observe.py learn validate "$(ls -d $RUN/*-jog-* | tail -1)" --model $RUN/analysis/model.json --split $RUN/analysis/split.json --out $RUN/analysis
# 4. review proposal from the latest recorded observation (never executed)
$PY $OBS/observe.py learn record --backend cameras --cameras $SETUP/cameras.json --features $SETUP/features.json --target $SETUP/target.json --root $RUN
$PY $OBS/observe.py learn propose --model $RUN/analysis/model.json --validation $RUN/analysis/validation.json --features $SETUP/features.json --target $SETUP/target.json --session "$(ls -d $RUN/*-record-* | tail -1)" --out $RUN/proposal.json
# 5. corrections on the controller, each move confirmed by the operator
$PY $OBS/observe.py learn execute --backend controller --port /dev/cu.usbmodemPICO --cameras $SETUP/cameras.json --features $SETUP/features.json --target $SETUP/target.json --model $RUN/analysis/model.json --validation $RUN/analysis/validation.json --root $RUN --i-understand-this-moves-hardware
```

| Step | Writes | Result |
|---|---|---|
| `learn check` | nothing | exit 0, or 1 with every problem listed per file |
| `learn plan` | `jog-plan.json`: axes, sizes, repeats, trials per size, per-move bound, engagement counts | exit 2 if a size or the bound exceeds 640 counts |
| `learn record` | a `record` session: frames, optics, observations; `feature-summary.json` with each value's valid fraction, spread and confidence, and each target quantity's value, noise and error | exit 0 when every feature was found in every observation |
| `learn jog` | a `jog` session: engagement and probe trials (+s ×r, hold, −s ×2r, hold, +s ×r: both directions, two reversals, net zero), every move receipt, observations after settling, trial outcomes; with the controller, `controller-client.jsonl` | exit 0; 2 refused before connecting; 3 the operator ended before motion; 4 halted by a gate or a move that did not finish (the session is kept) |
| `learn fit` | `model.json`; `split.json` naming the training and held-out trials | exit 2 with the reason when too few steps are usable |
| `learn validate` | `validation.json`; `validation-report.txt`, first line `VALIDATION: PASS` or `VALIDATION: FAIL`, then each feature's held-out RMS, skill and verdict, each axis-direction's verdict and the reasons | exit 0 PASS, 1 FAIL |
| `learn propose` | `proposal.json`: `review_only`, the bounded counts or zero with reasons, each quantity's observed and desired value, and each axis's sensitivity in pixels per count | never executed |
| `learn execute` | an `execute` session: engagement of the target axes, then proposals, confirmed moves and observations | exit 0 when within tolerance; 1 at the precision floor, declined or faulted; 2 refused; 3 ended before motion |

The jog plan grows each axis's step only after the previous size moved the
features by at least eight noise units on two steps. `fit` counts a step only
once its axis's take-up state is known, after a one-direction run of at least
`--max-deadband` counts (default 400); keep twice the plan's `engage_counts` at
or above it. `propose` evaluates the latest observation as of its capture and
never moves anything; `execute` recomputes each move from a fresh observation,
because a reviewed proposal is stale once the controller is armed. It first
engages each target axis (a run of 1.5 estimated dead-bands plus 16 counts
each way, ending near the start) because a new session does not know the
take-up state. Choose target axes with the largest sensitivities in
`proposal.json`; a target more than four trust regions away is refused, so
bring the gun near with the controls console's coarse moves first.

Real motion (`--backend controller`) is refused, before anything connects to
the controller, without the `--i-understand-this-moves-hardware` flag, a port,
a camera configuration that passes `validate-config --measurement` with a
passing clock check, and features, plan or target files that validate; and
`execute` also needs a validation report that passed. After connecting, the
tool sends nothing until the operator types, at its prompt, the controls
console's own `clear`, `reference central` (after physically establishing the
central datum) and `arm`, then `go`. `go` is accepted only when the controller
reports `drivers_ok`, microsteps verified as 16 on every axis, referenced,
armed, no fault, and the current scales, configured and decoded VSENSE and rate
that the controls host's `PROFILES` and `VSENSE_PROFILES` give for its profile.
Every move is then checked against the controller's latest
status, the plan's or `--max-step` bound (never above 640 counts) and the soft
limits from its reported counts; the first refusal, or a move that does not
finish, halts the session. `execute` shows each move and sends it only after
the operator types `y`. Leaving the session sends `STOP`, as the controls
console does, which invalidates the reference.

## Response model and held-out validation

A step is the change between two settled observations of one trial, with the
moves executed between them:

```text
Δy = J⁺·m⁺ + J⁻·m⁻ + d·Δt
```

`m` is each axis's output motion after reversal take-up (an axis absorbs up to
its dead-band `b` after a reversal), split into positive and negative parts so
each axis has its own response in each direction; `d` is feature drift. The
take-up state runs through the session's whole ordered move history, and steps
taken while it is unknown are excluded. J⁺, J⁻ and d are fitted by iteratively
reweighted least squares with Huber weights; steps beyond six robust standard
deviations are reported as outliers. Each axis's dead-band is chosen by a profile
search of the same loss, with a profile interval. Responses are per count;
`jacobian_mm()` gives them per mm of screw extension. Features stay in pixels
until an independent calibration supplies physical scale.

Validation holds out whole trials, stratified by probed axis, and never splits
a trial. The report gives each feature's held-out RMS, bias and skill against a
zero-change prediction, each axis-direction's held-out coverage and skill, every
held-out residual, and the `fit_jacobian` baseline. Held-out outliers are
judged by the fit's own rule; more than 10 % of them fails validation. Only
axis-directions the report validates are used for corrections.

## Corrections

`propose()` feeds `visual_servo.correction()` a weighted, column-scaled
Jacobian with damping rows appended, which makes its normal equations the damped
least-squares system, and chooses the damping so the step lies in the trust
region. One unit is one per-axis maximum step; the default maximum is 64 counts,
the commissioning document's initial 0.01 mm trust region. It proposes zero
motion, with reasons, when there is no validated model; the controller status
shows drivers not OK, unverified (null) microsteps, a fault or no reference; a
feature is missing, low-confidence or too uncertain; the observation is stale
or began before the last completion plus settling; no validated axis can
observe the error; the target lies beyond four trust radii; the rounded step is
zero or exceeds a bound or soft limit; the predicted change is below noise; or
an axis to be moved has an unknown take-up state. It never moves anything.

`CorrectionController` evaluates each executed move by fitting the observed
change as per-axis fractions of the predicted change:

- A change the move does not explain (a misdetection or disturbance) is
  observed again before anything moves. Two agreeing observations after a move
  that disagree with the one before it mark that earlier observation as bad.
- A reversal is taken up on that axis alone: one step of the estimated dead-band
  less a margin, then steps of twice the detectable motion, each evaluated, until
  motion is observed. The dead-band is never added to a correction. Reversals
  too small to matter are held; one smaller than a take-up step is never taken,
  because the completing step overshoots by about that much.
- Counts commanded without observed motion accumulate; beyond twice the
  dead-band plus a step the axis is reported unresponsive, and repeated
  detectable moves without motion stop the loop.
- An error that stops improving stops the loop at the precision floor.

On the simulator these guards bring every tested target within 0.6 px, stop a
jammed axis once its unverified counts pass the limit, and stop a jammed
reversal inside its take-up limit.

## Live-weld development channels

The current process concept compares radial and axial contact followers with a
cold baseline at the same table angle, with a cool reference. `liveweld.py`
records `probe_sample` (radial, axial), `table_encoder` (counts of
`counts_per_rev` from a dedicated encoder or a fiducial read from camera
frames; never USB arrival time, since the rotator supplies no phase stream) and
`cool_reference` records. A `ColdBaseline` is a robust Fourier series in table
angle fitted on dry laps, laser off, with complete angular coverage, and is
validated on held-out laps. Live readings are compared at their interpolated
table angle, and the cool reference's change is subtracted.

The development steps are: fit and hold out cold baselines over repeated dry
laps; confirm the cool reference stays flat on cold laps; record the channels
during welds fired by the operator outside this toolkit; and compare. Optical
observation during emission, and the protection and filtering it needs, are not
provided here and are not a purchase requirement of this toolkit.

## Development sequence

1. Set up the cameras from the templates (above): unique IDs, measured
   format, optics receipts, clock check, a dry measurement capture.
2. Fill the features and target files, rehearse the `learn` sequence on the
   simulator, record features with the cameras, then run jog trials on the
   controller ([commissioning](commissioning.md) §6), one axis at a time at
   first. Fit, validate on held-out trials, review a proposal, and run
   confirmed corrections from the 64-count trust region.
3. With the tube turning on the existing rotator, record a table fiducial or
   encoder on the same timeline, register the seam, and hold out whole laps.
4. Develop live observation and process corrections only after their own
   optical, containment and welder gates.

## Verified and unverified

The 134 tests run without hardware. They check VISCA bytes and decoding against
the manual's tables; drop evidence, receipt order, size checks and every gate
outcome of measurement windows; append-only storage and integrity checks;
frame/move labelling, supply cycles and controller-clock mapping; the
extractors on rendered images; recovery of J⁺ and J⁻ to within 1 % and of every
dead-band to within 3 counts from a simulated mechanism with backlash,
direction-dependent gains, coupling, drift, noise and outliers; held-out
validation, and its failure for a different mechanism; trust-region bounds and every no-motion
reason; closed-loop convergence, outlier handling and jammed-axis stops; the
cold baseline and cool-reference correction; the firmware constants read from
`motion_policy.h` and `geometry_generated.h`; both profiles' rates, current
scales and VSENSE against the controls export, `driver_profile.h` and the build
manifest, with the nominal currents the header and manifest state; the profile check against
`Client.check_profile`; the `Client.move()` argument bounds; the receipt mapping
against a fake `Client` with the real method signatures, including a late `PING`
ack carrying the move's sequence and the `unverified` refusal; the refusal of both shipped templates and of
each kind of gap in a filled configuration; and the `observe.py` commands
`simulate`, `fit`, `propose`, `check`, `cameras --new-since`, `optics check`,
`validate-config`, `clock-check`, `format-report`, `schema` and `capture`, the
last through the whole template sequence driven by the helper's synthetic
stream; the `learn` sequence on the simulator, from plan to execute, including
a validation that fails for a different mechanism; and every refusal before
real motion, then the complete controller path — operator arming, gated jogs,
fit, validation and confirmed corrections — against the fake `Client` driving a
simulated mechanism rendered into synthetic frames. On this Mac the helper builds,
enumerates cameras with unique IDs, agrees with `time.monotonic_ns()`, and
streams through both launch paths in its synthetic mode.

Not verified: any K20UH camera (its formats under AVFoundation, 4K delivery
rate, decode path and drop behaviour), VISCA over any transport and its timing,
the controls `Client` against a controller, the extractors on real images of
316L, the dot and wire, physical image scale, the table angle and probe
hardware, and anything during emission.
