# trials-23-frame-clock: time is a calibration too

Scene: `scenes/trials-23-frame-clock/index.html` (developed; a lens with a small simulation). Origin: new, from the framing, in the new direction "calibrating the observation itself". Combines `trials-03-dot-touch-probe` (the knee), `trials-18-steerable-mule` (a pointer to step and sweep), `trials-04-seam-map-replay` (angle keyed), `trials-19-fixed-point-cal` (a hand and joint readings). Calc: `calc/frame_clock.py`. Sourcing: `sourcing/trials.md`, wave 3 (cameras with a trigger input).

## Picture it

Four curves cross a shared 50 per cent line at four different places: the plate-side fraction of the dot swept up and down the seam at a slow speed and a fast one. The true seam is the middle of the up and down knees at either speed, the gap between the knees grows linearly with speed, and the slope of that line is how late the camera's picture is. Beside them a bar chart says which time errors matter: a sweep, a hand, and not much else.

## The proposal

Every comparison the trial loop makes has a clock on each side: the frame (exposure, readout, USB, a host timestamp), the rotator's angle (a step count over serial at 115200 baud, `firmware/src_weld_rotator/README.md`), the positioner's command (then its motion). A time error shows only when **something moves between the two clocks**. At rest there is nothing to mismatch. So the calibration is mostly a matter of knowing which comparisons move.

- **A sweep** that carries the dot across the seam at v mm/s reads the knee late by v times the chain's latency, in the direction of travel (and lash does the same). With a frame stamped 125 ms late and a sweep at 1 mm/s that is 0.125 mm, plus half the lash.
- **A hand** that moves the arm (`trials-19`, `borrowed-03`) makes the joint readings and the frame describe different poses: 20 mm/s times 0.1 s is 2 mm, against a fit floor of 0.03 to 0.3 mm.
- **A closed loop** loses phase margin; the loops of `trials-20` and `borrowed-05` are slow enough (tenths of a hertz) that this is a tuning matter.
- **A smooth seam map** does not care: it is learned and replayed at the same lag, and a change of bead speed from 8 to 12 mm/s with 0.15 s of latency moves a first harmonic at the rig's limit (0.125 mm) by 1 micrometre, a rough seating (0.6 mm) by 6, and a small third harmonic by 1.5 (`calc/frame_clock.py`, section 4).

What the loop does about it:

1. **Sweep both ways at two speeds.** knee(d, v) = seam + d (v tau + L/2): the mean of the two directions is the seam at any speed; the half difference is a line in v with slope tau (the latency) and intercept L/2 (half the lash). Four knees give all three, with one degree of freedom spare for a check. At 0.25 and 1.0 mm/s, knee noise 0.02 mm and 15 ms of timestamp jitter, four sweeps give the seam to 11 micrometres, the latency to 31 milliseconds and the lash to 41 micrometres; five pairs per speed give 5 micrometres, 14 ms and 19 micrometres. It is the unidirectional approach of `trials-02` and the labels of `trials-18` again: both lash and latency flip sign with the direction of travel, so the same pair cancels both.
2. **Step at a random phase.** Command a step of the pointer (or the positioner), record the first frame that shows it. With the step at a random phase against the frame clock the delay averages the latency plus half a frame, so latency = mean delay minus T/2 with a standard deviation T over root 12 N: 1 ms after 100 steps at 30 frames per second, 0.3 ms at 100 fps (Monte Carlo agrees). A minute of work, and the number to re-measure hourly.
3. **Compare at rest.** Gate a joint reading on the dot's own image speed (under 0.3 mm/s for twice the latency): the mismatch falls from 2 mm to 30 micrometres at 0.1 s.
4. **Remove the latency by construction.** Let the axis (or the rotator's ESP32 from its step counter) trigger the exposure, so each frame is taken at a known step and there is no timestamp to find; needs a camera with a trigger input (listed in `sourcing/trials.md` where seen). Or put a **Gray-coded counter in a wide camera's view** (eight LEDs and a shift register driven by the step counter): a frame that catches the bar mid-change reads at most one count wrong, where a binary counter going from 127 to 128 can read anything from 0 to 255. It fits a 130 mm view and not a 25 mm close-up.

## What carries the loads, what establishes position, what stays free

Not the subject. Any positioner that steps a fraction of a millimetre, or the steerable pointer of `trials-18` (no mass, so the fastest sweeps), does the sweeps; the rotator turns the tube. Position is established by the seam itself: the mean of the two directions.

## What software could command, observe, and what stays manual

- **Command:** sweeps up and down at two speeds; a step at a random phase; the exposure trigger from the axis (proposed).
- **Observe:** the knee of every sweep in command units; the delay from a commanded step to the first frame that shows it; frame count against trigger count (drops, duplicates); the dot's image speed (the stillness gate); the frame difference (zero means a repeated frame).
- **Manual:** choosing a camera with a trigger input or device timestamps; wiring the axis pulse; mounting a slate in a wide camera's view.

## What was tried to break it

1. **Which errors are worth chasing** (defaults: 25 ms command to motion, 100 ms exposure to stamp, 20 ms jitter; all illustrative). One fast sweep read alone is 0.175 mm late; a hand at 20 mm/s is 2.5 mm out; the four-sweep seam is good to 12 micrometres; the map replayed at another speed is 5 micrometres out; a tack's place along the seam is 0.16 mm out (8 mm/s times the angle-stamp jitter, along the seam where it does not move the radial map). *Assumption behind a casual "sync the clocks":* every time error matters equally. *Change:* it matters in proportion to the speed of what moves between the two clocks. *Left standing:* the real chain has never been measured.
2. **Lash and latency look alike at one speed.** A pair at one speed cannot tell them apart; two speeds can. *Assumption:* the achieved position lags the command by half the lash in the direction of travel and nothing else. *Left standing:* a real servo's or stage's lag is speed dependent (stiction, acceleration): a third speed is the check.
3. **Two clocks drift apart.** An ESP32 crystal is good to tens of parts per million against the host's: 50 ppm is 0.18 s an hour. *Change:* stamp both on arrival at the host, or trigger, or run the step test hourly. *Left standing:* which stamps the rotator firmware can attach.
4. **A stalled camera repeats a frame** and the loop sees a perfectly steady dot. Sensor read noise makes real frames differ, so an identical frame is a duplicate (frame difference exactly zero). *Left standing:* a driver that re-delivers a buffer with new noise from a denoiser.
5. **A red dot in a compressed colour stream** is smeared by chroma subsampling; measure on a monochrome or raw stream, with a 650 nm bandpass filter (`sourcing/trials.md`). *Left standing:* an unchecked claim about the listed cameras' formats.
6. **A slate does not fit a close-up.** The 25 mm frame of the corner has room for the dot and the wall. *Change:* trigger the exposure instead, or use a wide camera for the slate. *Left standing:* a light pipe from an LED to the edge of a close-up frame is untried.
7. **Rolling shutter is not the problem it looks.** A 16 ms readout skews a tube edge 0.13 mm along the seam at 8 mm/s (0.008 mm per mm across, so 1 micrometre) and a dot swept at 0.5 mm/s by 8 micrometres across the frame.

## Branches and combinations

- Uses `trials-03` (the knee), `trials-18` (the pointer and its labels), `trials-04` (angle keyed maps), `trials-19` (the hand's joint readings), `trials-02` (the one-sided approach). Feeds `trials-24` (the clock node) and `trials-17` (latency and jitter as recorded factors).
- Transferable: sweep both ways at two speeds; step at a random phase; compare at rest; a Gray-coded counter in the frame.

## Unresolved problems and questions that need Derek

- Q: with a phone in slow motion (240 fps) film the rotator's display and the camera's own preview at once, or the laser box's lamps and a screen: how far behind is the preview? (a rough latency in one take)
- Q: does the camera you would use have a trigger input? The listed Arducam UVC camera does not say.
- The rotator ESP32's status rate and any buffering (the firmware README gives the command set, not the timing).

## Assumptions

All latencies, jitters, lash, speeds and noise **[illustrative]**; bead speed 8 mm/s at r = 61.85 mm **[repo]**; the estimator is weighted least squares for seam, tau and L/2, its scatter the analytic covariance; the step-test scatter T over root 12 N **[derived]**. The 0.05 mm marker in the bar chart is not a requirement.

## Sourcing pointers

`sourcing/trials.md`, wave 3 (Prime listings, page not opened): a UVC global-shutter OV9281 module whose title claims an external trigger and strobe ($35.99, 48 ratings, next-day) and an IMX296 Raspberry Pi global-shutter module with an external trigger ($43, 20 ratings); a light-red (635 nm) machine-vision bandpass filter ($121, 13 ratings, thin), noting that the many "650nm" listings are IR-cut filters, not bandpass; a 74HC595 shift register and an 8-LED bar module for a slate ($8 to $10, commodity). Trigger timing against the exposure is unchecked for all of them.

## Scene

`trials-23-frame-clock`. Controls: the camera chain (branch), command-to-motion, exposure-to-stamp and jitter (scene edits), fast sweep speed (actuator), pairs per speed and the stillness gate (state), a run button (state), the axis's lash, one knee's noise and the hand's speed (scene edits), the counter value (view).
