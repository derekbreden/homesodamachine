# Camera timing for the metered pours

The camera remained open across the appliance trials. Each upright frame has a native presentation timestamp on the same host clock as the meter transmissions and appliance acknowledgements. The original, fixed and restored settings are in `reference/`. The reference photograph identifies the liquid and the marks on the measuring cup. All optical movements in the timing results are native pixels.

## Replay

Run from this directory with Python, NumPy and Pillow. Matplotlib produces the optional chart.

```sh
python3 replay/verify_camera_archive.py .
python3 replay/read_pour_timings.py upper-rim.csv.gz appliance-timeline.json --out original.json
python3 replay/read_pour_timings.py upper-rim.csv.gz appliance-timeline.json --inner-contact direct-inner-contact.csv.gz --out direct.json
python3 replay/score_optics.py original.json frozen-optics.json --out scored-original.json
python3 replay/score_optics.py direct.json frozen-direct-contact.json --out scored-direct.json
python3 replay/replay_native.py gate-profiles/*.npz --rim-reference reference/rim-reference.npz --contact-reference reference/upper-contact-reference.npz --trace upper-rim.csv.gz --direct direct-inner-contact.csv.gz --out replay-check.json
python3 replay/read_hold.py holds/*.npz --out hold-readings.json
python3 replay/hold_variation.py holds/*.npz --out within-hold-repeatability.json
python3 replay/front_holds.py score front-holds/*.npz --out front-hold-readings.json
python3 replay/inspect_hold_feature.py inspect low-hold-features.npz --out low-hold-features.json
python3 replay/return_contacts.py reference/station-idle-average.png reference/home-final-settled-full.png --out returned-contact-shifts.json
python3 replay/dry_waves.py dry-waves/*.npz --out dry-motion.json
python3 replay/score_fill_timing.py direct.json --out fill-timing.json
python3 replay/front_wall.py score appliance-timeline.json front-wall --out front-wall-timing.json
python3 replay/score_front_wall.py front-wall-timing.json front-wall-plan.json --out front-wall-agreement.json
python3 replay/sampling_coverage.py frames.csv.gz appliance-timeline.json --out cadence-check.json
python3 replay/plot_pour_phases.py upper-rim.csv.gz direct-inner-contact.csv.gz appliance-timeline.json release-reopen.png
```

The native recordings contain complete consecutive-frame samples of the two upper-rim strips around every direct positioning gate and metered pour. Each strip retains its native row pitch and constituent column averages. The storage codec represents the differences between consecutive integer frames. `replay/native_profiles.py` reconstructs the exact recorded integers. Each group also carries the starting tracker state, host times, meter transitions, reported burst count and presentation timestamps. The cadence report lists longer gaps between delivered camera frames and counts native observations in the measurement windows.

The original tracking method matches the local appearance of the surface on each strip. An inner-strip reflection crossed this template in training. The separate direct-contact reader locates the clear-to-dark upper boundary across its native columns. The original predictions, the training diagnostic and the separately frozen direct-contact predictions are retained. The independent outer strip is common to both readouts.

The early comparison uses median surface positions before the interrupted schedule resumes bursting. The release and closure comparisons use separate median windows. The ring-down fit describes oscillation of the visible surface after the simulated last motor-off time. The appliance reports its opening and closure acknowledgements and total burst count. The timeline identifies the intermediate switching times calculated from its policy.

The stationary files preserve native liquid strips throughout the hold and dry printed rows at a lower cadence. The long pre-pump record includes the brief loss of contrast visible in the inner strip. Each example contains a lossless native luma crop and tiles of the dry and submerged ink from a separately timestamped RGB sample. Its index identifies the exact average-frame and color times.

The dry-wave samples come from front printed strokes during the photographed continuous, interrupted, full and partial programs. Their fitted oscillation uses the same absolute camera times as the liquid fit. The fill comparison normalizes each trial's displacement at final meter release by its own settled displacement, then pairs high and low starting fills within each head and block.

The front-wall recordings preserve selected pixels from the timestamped preview at the two graduated-volume sightlines. Each receipt carries the two native endpoint coordinates when the geometry reader ran during the experiment. A separately replayable image measurement follows the front contact from that starting photograph and compares its settled displacement to the final photograph. The low-hold feature crops show a stationary case where the absolute x990 reader selects a different reflection. The front preview uses wider pixel and time spacing than the upper native strips.
