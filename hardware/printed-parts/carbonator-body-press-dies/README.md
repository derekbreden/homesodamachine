# Carbonator Body Press Dies

3D-printed die set for press-forming flat 0.048" 304 SS blanks into D-shaped halves of the racetrack-cross-section carbonator tube body.

## What this does

A two-piece die (concave female on bottom, convex male on top) wrap-bends a flat sheet blank around a D-shaped punch into a matching D-shaped cavity. The resulting D-half is half of the full racetrack tube cross-section, split along the racetrack's minor (short) axis. Two D-halves butt-weld together along both flat edges to close the full racetrack. This approach avoids rolling a closed loop on the slip roll, which would jam in the rollers.

## Source geometry

Body sheet blanks are defined in:
`hardware/cut-parts/carbonator-body-sheet/generate_dxf.py`

Blanks are laser-cut by SendCutSend at 7.754" x 6.000" x 0.048" 304 SS annealed.

## D-half geometry

The D-half cross-section (viewed along the tube axis) is a flat-bottomed U rotated 180 degrees: two vertical tangent walls flanking a half-circle at the bottom.

Inside surface (what the male punch shapes):
  Semicircle radius: 1.935" (= tube ID at the curved end, matches end-cap slip-fit at R=1.930")
  Tangent-wall length: 0.800" per side (two per D-half)
  Tube axis length: 6.000"

Outside surface (what the female cavity shapes):
  Semicircle radius: 1.935 + 0.048 = 1.983" (tube OD at the curved end)
  Tangent walls at X = +/-1.983"

Developed flat blank length (straight-bend neutral-axis at mid-thickness):
  L = 0.800 + pi * (1.935 + 0.048/2) + 0.800
    = 0.800 + 6.154 + 0.800
    = 7.754"

## Blank and final dimensions

| Dimension | Blank (pre-forming) | Final D-half (after pressing) |
|-----------|---------------------|------------------------------|
| Length along tube axis (Y) | 6.000" | 6.000" |
| Width (developed / wrapped) | 7.754" | 7.754" wrapped around D |
| Inside semicircle radius | flat | 1.935" |
| Tangent-wall height | flat | 0.800" per side |
| Thickness | 0.048" | 0.048" (minor thinning at apex) |

The butt-weld seam sits at the top of each D-half's tangent walls. When two D-halves are welded together, the result is the full racetrack tube: two semicircles of R = 1.935" (ID) connected by two flat walls each 1.600" tall (0.800" + 0.800").

## Die architecture

### Female die (bottom) — concave cavity

A solid rectangular block with a D-shaped cavity on the top face, extruded along the tube axis (Y). The blank lies flat on the top face (the "die land") before pressing. The cavity's inside surface matches the sheet's outside surface (all radii = 1.983", walls at X = +/-1.983").

- Cavity cross-section: two vertical walls at X = +/-1.983" from Z = 0 down to Z = -0.800, then a semicircle of R = 1.983" from (+1.983, -0.800) through apex (0, -2.783) to (-1.983, -0.800)
- Cavity depth: 2.783" (total Z travel from die land to apex)
- Wall: 0.500" around the cavity perimeter on all four sides (heavier than the dishing die because the cavity is much deeper and forming forces are higher)
- Floor under cavity: 0.500"
- Block height: 2.783" (cavity) + 0.500" (floor) = 3.283"
- Block footprint: (2 * 1.983 + 2 * 0.500) x (6.000 + 2 * 0.500) = 4.966" x 7.000"

### Male die (top) — convex punch

A rectangular flange/backing block with a D-shaped punch protruding from its bottom face, extruded along the tube axis (Y). The punch matches the blank's inside surface (all radii = 1.935", walls at X = +/-1.935"), so the radial gap between punch and cavity equals 0.048" = sheet thickness at every point on the D.

- Punch cross-section: two vertical walls at X = +/-1.935" from Z = 0 down to Z = -0.800, then a semicircle of R = 1.935" from (+1.935, -0.800) through apex (0, -2.735) to (-1.935, -0.800)
- Punch descent below flange: 2.735"
- Flange (blank holder): the flat surround rests on the female die's top surface during forming; it pins the blank edges so they cannot wrinkle or lift as the punch descends
- Backing plate above flange: 0.500" for press-ram contact
- Block height: 2.735" (punch) + 0.500" (backing) = 3.235"
- Block footprint: matches the female — 4.966" x 7.000"

### Registration

Two dowel pin holes (0.250" dia, 0.375" deep) per die half, on the tube-axis centerline (X = 0), flanking the cavity in Y at +/-3.250". The holes drill downward from the female's die-land face and upward from the male's flange face so they align when the halves are brought together. Same approach as the dishing dies.

## Material

- PA6-CF, 100% infill
- Printer: Bambu H2C
- Estimated mass: ~1180 g (female), ~1450 g (male), from the generator's diagnostics block. Both under the 1500 g per-half target.

Each block fits well inside the H2C's 300 x 320 x 325 mm build volume and well inside a 12-ton H-frame press's typical throat clearance.

## Forming notes

- Estimated forming force: 1–3 tons peak for this wrap-bend (0.048" 304 SS annealed, 2 x 6" bend length, R/t ~= 40). The 12-ton VEVOR press is comfortably oversized. Go slow regardless and listen for cracking at the tangent-to-semicircle transitions on the first press.
- Springback: 304 SS at R/t ~= 40 typically springs back 3–8% on tight wraps; on this low R/t the semicircle portion will hold tight but the tangent walls may open slightly. The first die revision uses zero springback compensation. Measure the first formed D-half against the end-cap slip fit (R = 1.930" tube ID target) and, if the walls splay open, introduce a `SPRINGBACK_COMP` parameter in the script for v2 that pre-rotates the tangent walls slightly inward.
- Lubrication: dry-film or wax on both surfaces of the blank. Lubricant matters more here than on the dishing die because the sheet has to slide significantly along the punch as it wraps.
- The blank holder (male flange on female die land) is critical. Without the flange pinning the edges, the 0.800" tangent sections will lift and the part will form as a pure half-pipe with no flats — useless for butt-welding.
- Quantity: two D-halves per vessel. Order qty 2 of this die set if you want to form both halves in parallel, or cycle one die set twice.
- After pressing: deburr the butt edges, fixture the two D-halves together, TIG butt-weld both flat seams end-to-end along the 6.000" tube axis length. That closes the racetrack tube, ready for end-cap weld bungs.

## Files to generate

- `generate_step_cadquery.py` — parametric CadQuery script producing STEP files for both die halves
- Run with `tools/cad-venv/bin/python`
- Outputs `body-press-die-female.step` and `body-press-die-male.step` in this directory
