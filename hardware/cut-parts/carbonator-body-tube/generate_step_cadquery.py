"""
Carbonator body tube stock — STEP file for quoting and tube-squash forming.

This is an ALTERNATE body-material path to the SendCutSend flat-sheet
half-blanks. Instead of cutting two flat blanks and press-forming each
into a D-half, we source a round 304 SS tube and squash it into the
racetrack cross-section in a single press stroke (with sand-pack or
internal mandrel to prevent flat oil-canning).

See `printed-parts/carbonator-body-squash-dies/` for the forming dies.
See `future.md` body paragraph for the high-level plan.

── Why generate a STEP for tube stock ──

Tube is a commodity — dimensionally defined by OD, wall, length — and
does not need a STEP for the supplier.  But we produce one anyway for:

  1. Upload to instant-quote services (Xometry, Protolabs, etc.) that
     require geometry files.  The site can extract OD/wall/length from
     the STEP automatically.
  2. Downstream CAD imports: the squash-die STEP files, the assembled
     carbonator, any FEA model — all can pull this geometry by reference.
  3. A single source-of-truth for tube dimensions used across the repo.

── Dimension chain ──

The body OD is set by the tube stock.  End-cap geometry keys off the
body ID, which is set by wall thickness:

  Tube OD:          5.000"   (nominal — catalog size)
  Wall thickness:   0.065"   (nominal — smallest stock wall on 5" OD
                              from most US suppliers; reconfirm via
                              supplier quote before ordering)
  Tube ID:          5.000 - 2(0.065) = 4.870"

  Body ID semi-R:   1.935"   (unchanged — set by end-cap slip-fit)
  Body ID flat:     1.600"   (unchanged)
  Body OD semi-R:   1.935 + 0.065 = 2.000"
  Body OD flat:     1.600"   (approx — actual value depends on how
                              tube circumference distributes across
                              the flats vs semicircles during squash)
  Overall OD:       5.600" × 4.000"

Length per vessel:  6.000"

── Stock order planning ──

A single vessel needs 6.000" of tube.  This script exports at
LENGTH = 6.000" — one vessel — for per-part supplier quoting.
Change LENGTH and rerun if you want a multi-vessel stock piece
(12" = 2 vessels, 24" = 4, etc.).

── Material ──

304 stainless steel, welded-and-drawn or seamless.  Commercial grade
acceptable; sanitary-polished (Tri-Clover) not required (significantly
more expensive and the interior surface is covered by carbonated water
anyway).

Hoop stress at 70 PSI:  sigma = P * OD / (2 * t) = 70 * 5.6 / 0.130
                              = 3,015 PSI  (6.6× safety factor vs
                                            20,000 PSI allowable)

Units: inches throughout, converted to mm for CadQuery at export.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Tube stock dimensions ──

OD = 5.000 * IN              # outer diameter
WALL = 0.065 * IN            # wall thickness (smallest std on 5" OD)
LENGTH = 6.000 * IN          # one vessel worth

ID = OD - 2 * WALL           # derived inner diameter

# ═══════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════

tube = (
    cq.Workplane("XY")
    .circle(OD / 2)
    .circle(ID / 2)
    .extrude(LENGTH)
)


# ═══════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════

bb = tube.val().BoundingBox()
dx = bb.xmax - bb.xmin
dy = bb.ymax - bb.ymin
dz = bb.zmax - bb.zmin

vol_mm3 = tube.val().Volume()
vol_cm3 = vol_mm3 / 1000.0
# 304 SS density: 7.93 g/cm³
mass_g = vol_cm3 * 7.93

print(f"Tube stock (5\" OD × {WALL/IN:.3f}\" wall × {LENGTH/IN:.3f}\" long):")
print(f"  Bounding box: {dx:.1f} × {dy:.1f} × {dz:.1f} mm")
print(f"               ({dx/IN:.3f} × {dy/IN:.3f} × {dz/IN:.3f} in)")
print(f"  Volume:       {vol_cm3:.1f} cm³")
print(f"  Mass (304 SS, 7.93 g/cm³): {mass_g:.0f} g  ({mass_g/453.6:.2f} lb)")
print(f"  OD: {OD/IN:.3f}\"   ID: {ID/IN:.3f}\"   Wall: {WALL/IN:.3f}\"")

# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

# Filename encodes key dimensions so suppliers can parse at a glance
wall_tag = f"{WALL/IN:.3f}".replace(".", "p")  # e.g., "0p065"
length_tag = f"{LENGTH/IN:.0f}in"               # e.g., "12in"
fname = f"carbonator-body-tube-5od-{wall_tag}wall-{length_tag}.step"

path = out_dir / fname
cq.exporters.export(tube, str(path))
print(f"\nExported: {path}")
