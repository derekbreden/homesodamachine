# Optical evidence for the pour trials

The archived camera pixels reproduce each settled reading. Use Python with NumPy, SciPy and Pillow. Commands below run from this directory. Supply the directory that contains the preserved controller journals as `<logs>`.

## Reading the calibrated glass

```sh
python geometry_volume.py /path/to/camera/windows/AFTER --before /path/to/camera/windows/BEFORE
python geometry_volume.py evidence/windows/q1-post --before evidence/windows/q1-pre
python replay.py unpack q1-pre /tmp/cup-replay/q1-pre
python replay.py unpack q1-post /tmp/cup-replay/q1-post
python geometry_volume.py /tmp/cup-replay/q1-post --before /tmp/cup-replay/q1-pre
python geometry_audit.py --logs <logs>
```

`geometry_volume.read(window)` accepts a native window, compact evidence window or lossless reconstructed crop. It returns each contact row, contrast, acceptance flags and nominal mL. An optional parsed map selects another calibration. The default is the exact `geometry-used.json` frozen for the reserved experiments. The near-left and far-right glass measurements use separate detector columns. Both volume axes use the same photographed left-hand graduations. Their disagreement tests the image measurement, and their common cup graduations limit absolute accuracy. Each endpoint must lie between photographed anchors and meet the same contrast gate as acquisition. Raw displacement remains available beyond that interval.

`geometry-results/summary.json` gives the recorded volume interval, local flank sensitivity, rising-direction checks, stopped-cup drift, paired reader disagreements and returns to the original still. `same-pour-method-comparison.csv` compares the printed-face and clear-glass disagreements on the same validation pours. `fresh-scenarios.csv`, `native-scenarios.csv` and `fill-pairs.csv` compare the separate forecast and fill hypotheses. `known-recipe-trials.csv` preserves the frozen recipe and fixed-width forecast side by side on the identical reserved servings. Training indices and timing eligibility are in the summary. `photos/clear-pour-examples.jpg` shows the first complete reserved pour of each head. Its marked mean-luma crops contain the pixels used to read the two contacts.

`geometry_audit.py` re-derives the original width calibration and fresh forecasts from the preserved training endpoints and the ideal pulse widths in `designs/`. The two-step known-recipe check independently recomputes its training mean and checks each validation command's receipt time against its numerical freeze. `dry-mark-drift.csv` records the apparent position of the upper printed stroke on each face over the session. The forecast calibration remains fixed. To redraw the matched-reader comparison with Matplotlib, run `python plot_optical_agreement.py`.

`fill-pairs.csv` records each high–low difference in both native pixels and nominal mL. To separate the numerical contributions, each pair multiplies the difference in row displacements by the average of the two local scale factors, and multiplies the difference in scale factors by the average displacement. Their sum equals the recorded nominal-volume difference. `fill-specific-forecast-trials.csv` preserves the later reserved test of a fill-specific mean against the pooled forecast. `return_edges.py --logs <logs>` reconstructs both the broad scanner's largest gradient and the qualified liquid contact on each returned photograph. `photos/return-edge-selection.jpg` marks both far-side features.

## Replaying a settled cup photograph

```sh
python replay.py read q1-post --detail
python replay.py unpack q1-post /tmp/cup-replay/q1-post
python cup_volume.py /tmp/cup-replay/q1-post
python replay.py verify
python coverage.py --logs <logs> --out /tmp/cup-archive-coverage.json
python score_optics.py --logs <logs>
```

`evidence/layout.json` defines the original upright sensor coordinates and the order of the columns in the lossless PNG tiles. `replay.py unpack` restores the exact source pixels used by the frozen algorithms to their original crop coordinates. Unused regions are black. Each window records its original PNG hashes, frame timestamps, packed hashes and a comparison with the readings on the complete native images. The mean luma uses the listed frames. Each color photograph has its own timestamp, and the capture record gives its offset from the middle luma frame.

`evidence/coverage.json` inventories every preserved label against the archived journals and fingerprints the ordered capture records. The original source check also hashes both native PNGs and both capture timing files per window. Supply `--native /path/to/camera/windows` to `coverage.py` when the native acquisition folder is available.

`cup_volume.py` is the frozen acquisition reader. It locates the near liquid-to-dark-bulk boundary on each face, rejects contact crossings on red ink and registers the result to the photographed graduation centers. Its operational output is the right-hand thirds scale. The left-hand quarters scale uses green-channel profiles and a separate liquid search. `left_ruler.py` also removes the patches overlapping the operating strip from this left search. It receives only the color image and a zero luma array. Its result is the `independent` column in `results/`. The left reading can move visibly between fits where the one-cup stroke and printed text obscure the contact. `photos/stationary-cup.jpg` annotates two parked raw exposures showing this behavior. `photos/originals/` retains the native RGB and luma pair for those and the qualification examples.

`results/trials.csv` preserves the indices, heads, positive dose on each reader, forecasts and rejections. `results/stationary-pairs.csv` measures between directly consecutive photographs with no logged motion command between them. `results/scenarios.csv` uses the preregistered tolerances and counts each scheduled index at most once. Endpoint disagreement and stationary repeatability describe different error sources. Both scales share a camera, liquid and consumer measuring cup.

## Calibrating the clear glass using photographed crossings

```sh
python fit_geometry.py --journal <logs>/graduations.jsonl
python mark_crossings.py evidence/graduations/<label> --brief
python provisional_grid.py --out /tmp/cup-provisional-early.json
python fit_geometry_v2.py --journal <logs>/graduations.jsonl --from-pixels
python fit_geometry_v3.py --journal <logs>/graduations.jsonl --from-pixels
python verify_graduations.py --map geometry-map-v3.json --observations graduation-observations-v3.json
python select_map.py . /tmp/cup-forecast-map.json --permit-fallback
cmp geometry-used.json /tmp/cup-forecast-map.json
cmp provisional-geometry-map.json /tmp/cup-provisional-early.json
python figures.py --map geometry-used.json
python clear_photos.py --logs <logs>
```

`mark_crossings.py` locates the rounded end of each front graduation in the red pigment. It measures the neighboring foreground liquid on clear columns and compares it to the locally extended centerline of that stroke. Positive signed distance means that the contact appears below the graduation. The operating and opposite glass lanes are separately measured on native luma. The narrow search around the expected near-wall band distinguishes the liquid contact from the brighter back reflection. All recorded strip positions, contrasts, signed distances and flags are in `graduation-observations.json`.

`fit_geometry.py` interpolates the separately observed clear row at a sign change between photographs on the same leg. Each bracketing frame must resolve a sign larger than its local allowance. The three quarter-scale crossings from lowering are the only inputs to the piecewise-linear volume map. Raising supplies the check on each anchor. The separately printed one-cup cap on the opposite face measures parallax. The clear-glass lanes observe different pixels, and both inherit the same nominal left-cap calibration. The output gives source pairs, their raw row brackets, local sensitivities and the middle anchor’s error when only the outer graduations set the line. Ordinary dose conversion is restricted to the interval actually photographed. At an outer anchor, the direction test may evaluate the signed displacement on the neighboring segment for a held-out crossing just outside that interval.

`geometry-map.json` contains the qualifying lowering crossings from the original detector. `geometry-results/` retains each raw row and its nominal volume, the fresh-program forecast comparison and the stopped-cup comparisons. An extreme hold outside the printed calibration interval retains its native displacement. Each stopped comparison gives both endpoint drift and the largest span across its intermediate observations.

The original wide search (`mark_crossings.py`) can mistake a stationary wall feature for x990 as the level falls. `mark_crossings_v2.py` is a separately frozen revision. It compares unprinted neighboring lanes to the original wide pick, then measures the corrected row on the original x990 pixels. Its right-side measurement and graduation criteria follow the initial method. `geometry-map-v2.json` retains every reacquisition with the original and independent continuity rows. The original result is in `geometry-map.json`. The compact tiles include all neighboring luma columns. The original training samples preceded the revision, and its physical qualification used only the initial lowering photographs.

The unrestricted correction also attached to stationary upper printing during the first high excursion. `mark_crossings_v3.py` uses the original contact above the predeclared lower-range transition and the neighboring-lane correction in the lower range. The executable was saved after the first few exposures at the high end of the first lowering return and before its near-crossing exposures. The inputs and exact source timestamp are recorded in `method.json`. `geometry-map-v3.json` identifies the separate later rising segments reserved for its independent test and the accepted lowering images for its map. The first rising sweeps remain diagnostic. Accepted lowering data stops when the final missing graduation acquires its first sign-changing pair. `crossing-brackets-v3.csv` also retains observable signed intervals that missed an optical acceptance criterion. `rejected-crossing-captures.json` keeps photographs rejected by acquisition before an accepted step and records their exclusion from the fits.

The repeated lowering pass at the upper mark left the foreground tangent unresolved. `photos/upper-measurement-limits.jpg` shows the stationary feature that attracted the unrestricted correction and the uneven contacts beside the cap during lowering. For the forecast map, `geometry-used.json`, the lower and middle points come from all qualifying lowering pairs. The upper point comes from the first qualifying exploratory rising pair. The reserved upper observation measures repeatability from that direction. A cross-direction result at the upper anchor remains unresolved. `photos/forecast-graduations.jpg` identifies the direction and shows a raw pair around each selected printed cap. `provisional-geometry-map.json` is the earlier diagnostic snapshot before the later lowering pass supplied a second qualifying middle crossing.
