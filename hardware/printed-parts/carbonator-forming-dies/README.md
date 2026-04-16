# Carbonator Tube Forming Dies

3D-printed die set for pressing 5" round 304 SS tube into a stadium/racetrack cross-section using a hydraulic press.

## What this does

A two-piece die (female cavity on bottom, male plug on top) that deforms a round tube into a racetrack shape in a single press stroke. The tube's circumference is preserved — no material is stretched or compressed, only redistributed.

## Source geometry

All dimensions are defined in:
`hardware/cut-parts/carbonator-endcaps-racetrack/generate_dxf.py`

The die cavity profile is exported as:
`hardware/cut-parts/carbonator-endcaps-racetrack/die-profile-racetrack.dxf`

## Target racetrack (tube OD after forming)

| Dimension | Value |
|-----------|-------|
| Semicircle radius | 2.000" |
| Flat side length | 1.600" |
| Overall width (major axis) | 5.600" |
| Overall height (minor axis) | 4.000" |
| Circumference | 15.766" |
| Original round circumference | 15.708" (5.000" OD circle) |

## Tube stock

| Property | Value |
|----------|-------|
| Material | 304 SS, welded |
| OD | 5.000" |
| Wall | 0.065" |
| Length | 6.000" |
| D/t ratio | ~77 |

## Press: VEVOR 12-ton H-frame hydraulic shop press

| Spec | Value |
|------|-------|
| Capacity | 12 ton / 26,000 lbs |
| Stroke | 4.9" (125 mm) |
| Adjustable height range | 1.6–27.8" (40–705 mm) |
| Overall frame dimensions | 22 × 20.1 × 52.5" |
| Relief valve | Auto at 12T |

Ram diameter is ~1.75" (45mm, standard 12-ton bottle jack). Clear opening between uprights is ~16–18" (22" overall minus ~2–3" channel steel uprights each side). Neither constrains the die design — the die set is ~8" wide and the male die top face is vastly larger than the ram.

## Springback compensation

304 SS at R/t = 30 will spring back after the press releases. The die must over-form to compensate.

**Starting estimates (expect 2–3 iterations to dial in):**

| Dimension | Target (final part) | Die cavity (compensated) |
|-----------|-------------------|------------------------|
| Minor axis (height) | 4.000" | 3.85–3.90" |
| Major axis (width) | 5.600" | 5.65–5.70" |
| Semicircle end radius | 2.000" | 1.85–1.90" |

Rationale:
- 304 SS yield ~30–35 ksi (annealed), E = 28 Msi
- Springback ratio (σ_y/E) is ~0.0012, roughly 1.5–2× mild steel
- At R/t = 30, expect 5–8% radial springback on the minor axis
- The minor axis recovers ~0.05–0.08" after release
- These are starting-point numbers — form a test piece, measure, adjust, reprint

## Weld seam orientation

The tube's longitudinal weld seam must be placed at 3 o'clock or 9 o'clock (on a flat side), NOT at the semicircular ends where bending strain is highest. Mark the die with an orientation indicator.

## Die design requirements

### Material
- PA6-CF (carbon fiber nylon), 100% infill
- Printer: Bambu H2C, build volume 325 × 320 × 320 mm (single nozzle)
- Estimated die set cost: ~$130–180 in filament

### Architecture: two-piece closed cavity
- **Female die (bottom):** Sits on the press platen. Racetrack-shaped cavity facing up. The round tube sits in this cavity and the sides constrain the tube as it deforms, preventing wrinkling on the flat sections.
- **Male die (top):** Racetrack-shaped plug that descends into the female cavity, pushing the tube down and inward. The ram pushes on the flat top of the male die.
- At bottom dead center, the male and female dies fully enclose the tube — every surface of the final racetrack shape is in contact with a die surface.

### Critical features
- **Full enclosure:** Both halves must fully constrain the tube at BDC. If the flat sections are unsupported, the 0.065" wall will buckle/wrinkle inward (D/t = 77, wrinkling is a real risk).
- **Registration:** Dowel pins, interlocking shoulders, or guide features to keep male/female halves aligned under load.
- **Tube length support:** Dies must be at least 6.25" long (tube is 6.0") to support the full length and prevent end flare.
- **Entry chamfers:** The female cavity should have entry chamfers/radii to guide the round tube into the cavity as it begins to deform.
- **Weld seam relief:** Optional shallow groove (~0.030" deep × 0.125" wide) along the flat section at 3 or 9 o'clock to clear the internal weld bead if present.
- **Ram interface:** The male die top face must be flat and large enough to distribute the ram force without point-loading the PA6-CF.

### Stroke and force
- The minor axis reduces from 5.000" to ~3.85–3.90" (compensated). That's ~1.1" of travel.
- Press stroke is 4.9" — plenty of clearance.
- Estimated forming force: 2–6 tons. The 12-ton press has comfortable margin.
- Go slow — 0.5–1 inch/second. Fast forming increases wrinkling risk.

### Forming notes
- Lubricate the tube OD and die cavity surfaces (wax or dry-film lube)
- PA6-CF dies may last 10–50 parts before noticeable wear. Fine for prototyping and low-volume production.
- Measure springback immediately after forming and again after 24 hours (304 SS exhibits small time-dependent recovery)
- The press platen height is adjustable — set it so the die stack sits at a comfortable working height with full stroke available

## Files to generate
- `generate_step_cadquery.py` — parametric CadQuery script producing STEP files for both die halves
- Run with `tools/cad-venv/bin/python`
