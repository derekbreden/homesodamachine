# Carbonator Body Squash Dies

3D-printed die set for crushing a round 304 SS tube into the racetrack cross-section carbonator body in a single 12-ton press stroke.

## What this does

A two-piece external die set (upper = ram side, lower = bed side), each with a half-racetrack cavity cut into its parting face. The starting workpiece is a 5.000" OD x 0.065" wall x 6.000" long 304 SS round tube. With the tube laid into the lower cavity and the upper die lowered onto it, a press stroke closes the two halves until their parting planes meet at Z=0; the tube is plastically deformed into the combined racetrack OD cavity (5.600" x 4.000"). No butt welds are needed on the body — the result is a seamless pressure vessel ready for end-cap welding.

## Why tube-squash vs D-halves (alternate path)

The primary fabrication path in this repo is `carbonator-body-press-dies/` — form two flat-sheet D-halves and butt-weld them along both flat edges. The tube-squash path, specified here, is an alternate:

| | D-half press dies | Tube-squash dies (this folder) |
|---|---|---|
| Starting material | Flat 0.048" 304 SS sheet blanks | 5" OD x 0.065" wall x 6" round tube |
| Stock cost | ~$15 for two blanks (SendCutSend) | ~$40 per tube (McMaster, ~$80/ft) |
| Number of welds on body | 2 long butt welds (both flats, 6" each) | 0 |
| Wall thickness | 0.048" (sheet) | 0.065" (smallest std. catalog wall on 5" OD) |
| Hoop-stress safety factor at 70 PSI | 4.9x | 6.6x |
| Internal support during forming | Not needed (male punch is the mandrel) | Required — flats will oil-can without it |
| Press force | 1-3 tons | Somewhat higher but still well within 12 tons |
| Main risk | Weld quality / leaks on butt seams | Wrinkling, uneven squash, flat oil-canning |

Tube-squash wins on leak surface (no longitudinal welds), loses on material cost and forming complexity.

Note: the 0.065" wall is a real design change vs the 0.048"-wall D-half plan. Since 0.065" is the smallest standard catalog wall on 5" OD round tube stock, the body OD grows slightly — OD semicircle R goes from 1.983" to 2.000", overall OD from 5.566" x 3.966" to 5.600" x 4.000". The body ID at the curved end is unchanged at R = 1.935", so **end-cap DXFs from the primary path are reusable without modification**.

## Sourcing the tube

Commercial-grade 304 SS round tube, 5.000" OD x 0.065" wall x 6.000" long (or longer and cut to length). Welded tube is fine — food-grade inside finish is nice but not required; the end-caps and flavor injection happen downstream. Mill finish or 2B outside is fine.

- McMaster-Carr 89955K85 or similar (welded 304, 5" OD, 0.065" wall) — price-check before ordering; tube stock pricing moves.
- Onlinemetals / MetalsDepot have comparable SKUs.

Cut to 6.000" +0.030 / -0 with a cold saw or portaband; deburr ID and OD. The axial length is non-critical — end-caps slip-fit into the ID and are welded at the ID/OD corner, so an extra 0.030" of length just gets trimmed off at final assembly.

## Starting vs final dimensions

| Dimension | Starting tube (round) | Final body (racetrack) |
|-----------|-----------------------|-------------------------|
| Length along tube axis (Y) | 6.000" | 6.000" |
| Bounding box (X x Z) | 5.000" x 5.000" | 5.600" x 4.000" |
| OD semicircle radius | R = 2.500" (full circle) | R = 2.000" at each end |
| OD flat length (X) | n/a | 1.600" top + 1.600" bottom |
| ID semicircle radius | R = 2.435" | R = 1.935" at each end |
| ID flat length (X) | n/a | 1.600" top + 1.600" bottom |
| Wall thickness | 0.065" | 0.065" (minor thinning at flat-to-semi transitions) |

The racetrack OD cross-section (major axis along X, minor along Z):

```
            X (long axis)
  <----------- 5.600" ----------->
    ___________________________
   /                           \   ^
  /                             \  |
 |          top flat             | |
 |      (1.600" across, X)       | |
 |                               | 4.000"  Z (press axis)
 |       bottom flat             | |
  \                             /  |
   \___________________________/   v
```

Two semicircles (R = 2.000") at each end, joined by two straight flats (length 1.600", one at Z = +2.000" and one at Z = -2.000").

## Internal support — design decision

The tube flats (1.600" span x 0.065" wall x 6" long) will oil-can inward during pressing without something inside the tube pushing back. Three strategies:

### 1. Sand-pack (primary — recommended)

Plug one end of the tube (rubber cap, tape, whatever), fill with fine dry silica sand (play sand, #70-100 mesh, dry), tamp/tap to settle, plug the other end. Press. Remove plugs, pour sand out, re-use. Traditional pipefitter technique for bending thin-wall tube without kinks. The sand column is nearly incompressible in bulk — it supports the flats against inward collapse while still allowing the cross-section to deform into the racetrack shape because the sand flows plastically to redistribute.

**Why this is the primary path:** zero printed-part complexity, cheap, infinitely reusable, no mandrel extraction problem.

### 2. Splittable multi-piece mandrel (alternate, not designed here)

A racetrack-shaped mandrel placed inside the tube before pressing. The racetrack mandrel cross-section has a 5.470" x 3.870" bounding box — diagonal 5.473" — which exceeds the round tube ID of 4.870". So the mandrel cannot be inserted axially as one piece; it would have to assemble inside the tube from 3+ axial segments, or split longitudinally and spread. Designable but fussy. Not generated in this directory.

### 3. Two-stage forming with mid-stage mandrel insertion (alternate, not designed here)

Partial-press the round tube to an oval with its long axis >= 5.470" (clearing the racetrack mandrel diagonal), open the press, slide a single-piece racetrack mandrel in from one end, finish-press. Requires a pair of intermediate-stage dies and careful stroke control. Not generated.

If sand-pack produces unacceptable flat bulging in v1, re-evaluate option 3 first (one-piece mandrel is simpler than a segmented one); option 2 is the last resort.

## Die architecture

### Upper die (ram side) — concave upper-half cavity

A solid rectangular block with the upper half of the racetrack OD cavity cut into its lower (parting) face, extruded along the tube axis (Y). The block sits above the parting plane Z=0 and extends upward to Z = +2.500". The cavity removes material from Z=0 down to the flat at Z = +2.000" plus the two upper semicircle halves at (X = +/-0.800, Z=0).

- Cavity cross-section: two quarter-arcs of R = 2.000" centered at (X=+/-0.800, Z=0), connecting the parting-plane points (X=+/-2.800, Z=0) up to the flat-tangent points (X=+/-0.800, Z=+2.000"); a straight flat at Z = +2.000" from X = -0.800 to X = +0.800
- Cavity half-depth: 2.000" (Z=0 to Z=+2.000")
- Wall: 0.500" around the cavity perimeter on all four sides (matches body-press-dies convention)
- Floor above cavity: 0.500" for press-ram contact
- Block height: 2.000" (cavity) + 0.500" (floor) = 2.500"
- Block footprint: (5.600 + 2 * 0.500) x (6.000 + 2 * 0.500) = 6.600" x 7.000"

### Lower die (bed side) — concave lower-half cavity

Mirror image of the upper die. Block sits below Z=0 down to Z = -2.500". Cavity is the lower half of the racetrack OD (quarter-arcs at the ends, flat at Z = -2.000").

Footprint matches the upper — 6.600" x 7.000".

### Closed stack

When the press closes and the two parting faces kiss at Z=0, the combined cavity is the full racetrack OD (5.600" X x 4.000" Z x 6.000" Y), and the overall stack height is 5.000" (2 x 2.500").

### Registration

Two dowel pin holes (0.250" dia, 0.375" deep) per die half, on the long-axis centerline (X = 0), flanking the cavity in Y at +/- 3.250". The holes drill downward from the upper die's parting face and upward from the lower die's parting face so they align when the halves close. Same approach and offsets as the D-half body-press-dies and the dishing dies.

## Material

- PA6-CF, 100% infill
- Printer: Bambu H2C (300 x 320 x 325 mm build volume)
- Estimated mass per half: see the generator's diagnostics block output. Target <= 1500 g per half.

Each block fits inside the H2C's build volume and inside a 12-ton H-frame press's typical throat clearance.

## Forming notes

- **Sequence:** cut tube to length, deburr, plug one end, fill with dry sand, tamp, plug other end. Lube OD. Lay tube into lower die cavity centered on Y. Lower upper die by hand until it contacts the tube. Check visually that it's seated straight, not skewed. Apply press force slowly — 1 ton, pause, inspect; 3 tons, pause; close fully. Hold briefly, release. Remove upper die, unplug tube, pour sand, tap out residue.
- **Force:** D-half forming was estimated at 1-3 tons; squashing a thicker-wall tube with sand-pack inside is somewhat higher (sand load transfer adds resistance), but comfortably within the 12-ton VEVOR press. Go slow regardless and listen for any cracking or popping.
- **Springback:** the minor-axis flats will want to re-bulge outward after the press opens. The script exposes a `SPRINGBACK_COMP` constant (default `0.0`) that shrinks the cavity Z depth by the given fractional amount — so the die over-squashes the tube in Z, and the elastic recovery springs it back to 4.000". The X dimension is governed by the semicircle diameter, which is mechanically pinned by the tube's circumference, so X is left un-compensated. Measure the first squashed body against the end-cap slip-fit (R = 1.930" tube ID target at the curved ends, and 4.000" overall Z). If the minor axis measures oversize (flats bulged back out), bump `SPRINGBACK_COMP` to 0.02-0.04 and reprint. Typical 304 SS springback in this geometry is 2-4%.
- **Lubrication:** dry-film or wax on the tube OD and the cavity surfaces. Lube matters here — the tube has to slide radially inward against the cavity walls as it deforms.
- **Sacrifice the first tube.** At ~$40 per blank, burn the first one for calibration: sand-pack quality, squash sequence, springback value. Measure the result, tune `SPRINGBACK_COMP` if needed, reprint dies, then squash the "real" tube.
- **After pressing:** inspect flats for oil-canning and the semicircles for out-of-round at the ends. If one end is worse than the other (often the plug-fill end — sand didn't pack as tightly there), try tamping harder next time. Deburr cut ends, check that end-caps slip-fit (R = 1.930" against the formed ID curves), then weld end-caps.

## Files to generate

- `generate_step_cadquery.py` — parametric CadQuery script producing STEP files for both die halves
- Run with `tools/cad-venv/bin/python`
- Outputs `body-squash-die-upper.step` and `body-squash-die-lower.step` in this directory
