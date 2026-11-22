# Cup camera evidence

The USB camera stayed open while the bench controller issued its commands. Each recording uses the presentation timestamp of the image. The companion command logs use the same host monotonic clock. A positive row change moves downward in the upright image. The camera records surface position and the motion of visible objects. Volume estimates in the companion logs come from the printed cup marks.

The early gate files retain the controller channel as it was commanded. The operator reported that a pump fell and that the hoses and electrical connections were changed. The dry-field record locates changes in the image. The electrical identification belongs to the isolated trials after that intervention.

## Replay

Run the following commands from this directory with Python and NumPy. The ink check also uses Pillow. The optional chart generator uses Matplotlib. Each command writes its results to the directory or file named on its command line.

```sh
python3 camera-controls/read_stationary.py camera-controls/stationary-profiles.npz camera-controls/stationary-profile-index.json
python3 camera-controls/autofocus/read_final_focus.py camera-controls/autofocus --out focus-replay.json
python3 gate-motion/read_band_response.py gate-motion/profiles/*.npz --out gate-replay
python3 gate-motion/pulse_phase.py gate-motion/profiles/gap-*.npz --out pulse-replay
python3 off-holds/read_hold.py off-holds/profiles/*.npz --out hold-replay.json
python3 off-holds/read_hold_ink.py off-holds/cup-ink-index.json --out ink-replay.json
python3 hardware-reconfiguration/read_transition.py hardware-reconfiguration/transition-samples.npz
python3 hardware-reconfiguration/read_qualifications.py hardware-reconfiguration/qualifications/*.npz
python3 rewired-motion/read_rewired.py rewired-motion/profiles/*.npz --out rewired-replay
python3 rewired-motion/rewired-phase.py rewired-motion/profiles/pulse-*-sequence.npz --out pulse-boundaries.csv
python3 rewired-motion/rewired_waves.py rewired-motion/profiles/pulse-*-sequence.npz --out pulse-ringdown.csv
```

The stationary records hold native optical profiles from the white-balance intervention and a subsequent untouched interval. Color samples retain the lit cup patch that supplies the accompanying RGB readings.

The autofocus check followed the last pump command. Native dry ink and upper-rim photographs accompany the fixed, autofocus, and fixed-return register readbacks. The upper-rim replay reports a normalized residual and the spread of its individual matches. Large residuals or a wide spread reduce confidence in the displacement. The closure record compares the original control registers with the hardware readback after the camera process stopped.

The gate records retain contiguous native rows at adjoining column bands, one sample per camera frame, and each transmitted command and acknowledgement. The forward track starts from the pre-command rim. The backward track starts from the late rim and helps identify internal reflections and rebound. The unscored recordings contain acknowledged motor motion whose terminal observation was absent from the original controller log.

The hold records retain short windows of the native liquid and dry printed rows throughout unpowered intervals. The independent ink check uses lossless red-ink tiles from a color sample near each end of a hold. The color samples carry their own timestamps. The dry-row displacement in the hold replay uses the closer of the two dry graduations when the liquid lies below both. The ink replay fits several front markings and projects their movement to the liquid row.

The reconfiguration records retain sampled dry-field profiles, the native frame clock across the intervention, and separate tube and liquid observations during the new direction checks. The native horizontal silhouettes distinguish which visible tubes moved. The upper rim supplies the independent direction reading.

The rewired motion records use the clear upper rim at a native-rate inner station and a lower-rate outer station. They retain losslessly packed image samples, a photographed reference, frame timestamps, and motor timings. For the earliest direction checks the outer-station stills are in the qualification records. The outer-station time series begins before the destination trials. Times after a subsequent command belong to its own file.

The pulse-boundary replay samples the visible rim against each recorded start and completion acknowledgement. The ring-down replay fits surface oscillation after the final acknowledgement. The last return recording extends through the undisturbed hold and ends before autofocus was enabled.

The camera cadence and every unusually long interframe interval are listed in `cadence.json`. The SHA-256 manifest identifies the evidence and replay source.
