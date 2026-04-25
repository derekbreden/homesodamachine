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

── Wall-thickness variants ──

This script exports THREE wall-thickness variants of the same 5" OD,
6" length tube.  The catalog floor for 5" OD 304 tube at general US
distributors is 0.065", but mill-run custom pulls and some manufacturing
platforms (Xometry, SendCutSend, Protolabs, Fictiv) may access thinner
stock.  Upload all three to each platform and let them tell you what
they can actually source.

The 0.049" variant matches the SendCutSend sheet stock the original
D-half plan uses, so end-cap geometry stays bit-identical if this wall
is available.  The 0.035" variant is aggressive — a 20 ga wall — and
may not be rollable at this OD without buckling; included for completeness.

Hoop stress at 70 PSI scales with 1/wall:

  0.035":  sigma = 70 * 5.07 / (2*0.035) = 5,070 PSI   (3.9× SF)
  0.049":  sigma = 70 * 5.10 / (2*0.049) = 3,640 PSI   (5.5× SF)
  0.065":  sigma = 70 * 5.13 / (2*0.065) = 2,761 PSI   (7.2× SF)

All three clear the 20,000 PSI allowable by ample margin.

Units: inches throughout, converted to mm for CadQuery at export.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Tube stock dimensions ──

OD = 5.000 * IN              # outer diameter
LENGTH = 6.000 * IN          # one vessel worth

# Wall thicknesses to export (inches).  Ordered thinnest → thickest.
#   0.035" — aggressive, 20 ga equivalent; mill-custom
#   0.049" — matches SCS sheet stock; end-cap DXFs reuse unchanged
#   0.065" — catalog floor at general US distributors
WALLS_IN = [0.035, 0.049, 0.065]


def make_tube(wall_in: float) -> cq.Workplane:
    """Build a hollow round tube at the given wall thickness (inches)."""
    wall = wall_in * IN
    id_ = OD - 2 * wall
    return (
        cq.Workplane("XY")
        .circle(OD / 2)
        .circle(id_ / 2)
        .extrude(LENGTH)
    )


# ═══════════════════════════════════════════════════════
# BUILD + DIAGNOSTICS + EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

for wall_in in WALLS_IN:
    tube = make_tube(wall_in)

    bb = tube.val().BoundingBox()
    dx = bb.xmax - bb.xmin
    dy = bb.ymax - bb.ymin
    dz = bb.zmax - bb.zmin

    vol_cm3 = tube.val().Volume() / 1000.0
    mass_g = vol_cm3 * 7.93   # 304 SS density

    id_in = (OD - 2 * wall_in * IN) / IN

    print(f"\nTube (5\" OD × {wall_in:.3f}\" wall × {LENGTH/IN:.3f}\" long):")
    print(f"  Bounding box: {dx:.1f} × {dy:.1f} × {dz:.1f} mm"
          f"  ({dx/IN:.3f} × {dy/IN:.3f} × {dz/IN:.3f} in)")
    print(f"  Volume:       {vol_cm3:.1f} cm³")
    print(f"  Mass (304 SS, 7.93 g/cm³): {mass_g:.0f} g  ({mass_g/453.6:.2f} lb)")
    print(f"  OD: {OD/IN:.3f}\"   ID: {id_in:.3f}\"   Wall: {wall_in:.3f}\"")

    wall_tag = f"{wall_in:.3f}".replace(".", "p")   # e.g., "0p065"
    length_tag = f"{LENGTH/IN:.0f}in"
    fname = f"carbonator-body-tube-5od-{wall_tag}wall-{length_tag}.step"
    path = out_dir / fname
    cq.exporters.export(tube, str(path))
    print(f"  Exported: {path}")
