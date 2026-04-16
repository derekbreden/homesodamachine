# Carbonator End Cap Dishing Dies

3D-printed die set for press-doming flat 0.060" 304 SS racetrack blanks into shallow domed end caps for the carbonator vessel.

## What this does

A two-piece die (concave female on bottom, convex male on top) that presses a flat racetrack blank into a shallow spherical dome. The dome converts the stress mode from plate bending to membrane, allowing 0.060" sheet to do the work of 0.250" flat plate.

## Source geometry

End cap blanks are defined in:
`hardware/cut-parts/carbonator-endcaps-racetrack/generate_dxf.py`

## Dome geometry

The dome is a spherical cap — a single sphere radius intersected with the racetrack footprint. The sphere radius is set so the dome apex reaches 0.250" below the rim at the major axis extremes (the longest unsupported span, which drives the UG-32 calculation).

Sphere radius from the major axis half-span:
  a = 5.460 / 2 = 2.730" (final cap major half-span)
  h = 0.250" (dome height at major axis extremes)
  R = (a² + h²) / (2h) = (7.4529 + 0.0625) / 0.500 = 15.03"

Dome heights at key points:
  Major axis extremes (±2.730" from center): 0.250"
  Minor axis extremes (±1.930" from center): 0.125"
  Center of cap: 0.250" (apex)

The dome is subtle — 0.250" over a 5.5" span is barely visible. But it's enough to switch the structural mode from bending to membrane.

## Blank and final dimensions

| Dimension | Blank (pre-forming) | Final (after doming) |
|-----------|-------------------|-------------------|
| Semicircle radius | 1.946" | 1.930" |
| Flat length | 1.600" | 1.600" |
| Overall | 5.492" × 3.892" | 5.460" × 3.860" |
| Thickness | 0.060" | 0.060" (minor thinning at apex) |

The blank overhangs the die rim by 0.016" per side on the semicircle ends. This excess material draws inward during doming, so the finished rim matches the slip-fit dimensions.

## Die architecture

### Female die (bottom) — concave cavity

A block with a racetrack-shaped rim on the top face. Below the rim, a concave spherical dome cavity. The blank sits on the rim, overhanging slightly. The dome surface is a sphere of radius R = 15.03" intersected with the racetrack footprint.

- Rim outline: final cap dimensions (R=1.930", flat=1.600")
- Cavity depth at center (apex): 0.250"
- Flat bottom face sits on the press platen
- Wall: 0.375" around the rim (less load than tube forming dies — the forming force for 0.060" sheet is very low)
- Floor under cavity: 0.250"
- Block height: 0.250" (cavity) + 0.250" (floor) = 0.500"
- Block footprint: (5.460 + 2×0.375) × (3.860 + 2×0.375) = 6.210" × 4.610"

### Male die (top) — convex punch

A block with a convex dome protruding from the bottom face. The dome matches the female cavity but with radius reduced by the sheet thickness (R_male = 15.03 - 0.060 = 14.97") so the gap between punch and cavity equals 0.060" at all points.

- Dome protrusion: 0.250" below the flat surround
- The flat surround acts as a blank holder — it presses the blank rim against the female die rim to control material flow during doming
- Flat top face for the press ram
- Same footprint as female die
- Block height: 0.250" (dome) + 0.375" (backing plate) = 0.625"

### Registration

Two dowel pin holes (0.250" dia, 0.375" deep) on the parting faces, flanking the racetrack in the Y direction. Same approach as the tube forming dies.

## Material

- PA6-CF, 100% infill
- Printer: Bambu H2C
- Estimated mass: 150–250g per half (much smaller than tube forming dies)

## Forming notes

- The forming force for dishing 0.060" 304 SS to 0.250" dome is very low — well under 1 ton. The 12-ton press is vastly oversized for this operation. Go slow regardless.
- The blank holder (male die flat surround pressing on female rim) is important — without it, the blank can wrinkle at the edges as material draws inward. The surround should contact the blank before the dome apex does.
- Lubricate the blank (both sides) with dry-film or wax.
- The weld bung holes are pre-cut in the blank. They will distort slightly during doming — stretching larger and slightly elliptical. This is acceptable: the bung body (0.700") drops through a hole that started at 0.710" and got bigger.
- The male die dome does NOT need clearance holes for the bung hole positions — the dome is so shallow (0.250") that the punch surface is essentially flat near the bolt circle. The pre-cut holes in the blank simply deform over the smooth punch surface.

## Files to generate

- `generate_step_cadquery.py` — parametric CadQuery script producing STEP files for both die halves
- Run with `tools/cad-venv/bin/python`
