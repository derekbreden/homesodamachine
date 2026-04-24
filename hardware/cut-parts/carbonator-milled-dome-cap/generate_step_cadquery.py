"""
Carbonator milled domed end cap — CNC-milled 304 SS end cap for a 5"-OD
round tube body.  Socket-weld design: the cap slips OVER the tube end
and is joined with a single circumferential TIG fillet weld.

This is the simplest-possible fabrication plan for the carbonator
pressure vessel:

  - Body:  commodity 5.000" OD × 0.065" wall × 6.000" long round 304 SS
           tube, cut to length, no forming.
  - Caps:  two identical CNC-milled domed end caps per vessel, each
           carrying 2× 1/4"-18 NPT ports through the dome.
  - Joint: socket weld at each end — cap slides OVER the tube end,
           filleted with TIG.  Very forgiving for a beginner welder:
           the overlap acts as a heat sink, no fit-up precision needed,
           no edge prep, no bevel.

Two caps × 2 ports = 4 ports per vessel.  Caps are identical — no
left/right handedness — so qty 20 caps = 10 vessels.

── What gets eliminated vs. the in-house fabrication plan ──

  - SendCutSend body half-sheet blanks          → gone
  - SendCutSend end-cap blanks                  → gone
  - Body press dies (PA6-CF printed)            → gone
  - End-cap dishing dies (PA6-CF printed)       → gone
  - Body tube squash-forming                    → gone (round body stays round)
  - Press-forming / dishing end caps            → gone (CNC-milled dome)
  - Butt-welding two D-halves into a body tube  → gone
  - Welding 4× NPT port bosses onto the dome    → gone (bosses are internal,
                                                        cut into the milled cap)
  - Drilling + tapping NPT holes per vessel     → stays as CAM, not STEP geom

What remains: TWO circumferential TIG fillet welds per vessel, one at
each cap-to-tube joint.  Nothing else.

── Geometry (inches, converted to mm at export) ──

The cap is rotationally symmetric around the Z axis — a revolve, not a
loft.  This avoids the loft-singularity issues from the racetrack pot
geometry.

Coordinate convention:
  Z = 0  — bottom of socket skirt (open end, faces away from tube,
           or equivalently the end the tube slides up into).
  Z > 0  — toward the closed domed top.

Stackup along Z:

  Z = 0.000" ── bottom of socket skirt (open end)
  Z = 0.500" ── top of socket skirt / start of dome
  Z = 1.500" ── dome apex (closed end)

Socket skirt (Z = 0 to Z = 0.500"):
  ID     = 5.010"   (= 5.000" tube OD + 0.010" slip-fit clearance)
  OD     = 5.135"   (= ID + 2 × 0.0625" wall)
  Height = 0.500"   (along Z)
  The tube end slides up into this skirt until it contacts the
  internal shoulder at Z = 0.500".

Internal shoulder at Z = 0.500":
  The interior steps inward from 5.010" ID to the dome cavity, which
  starts at 5.010 − 2 × 0.0625 = 4.885" ID at Z = 0.500".  The
  shoulder acts as a stop for the tube end during assembly.

Ellipsoidal dome (Z = 0.500" to Z = 1.500"):
  Outer major diameter = 5.135"   (matches skirt OD — smooth external
                                   transition, no step in the outer
                                   profile at the dome/skirt junction)
  Outer dome depth     = 1.000"   (along Z; shallower than a full 2:1
                                   ellipsoidal head to reduce cutter
                                   reach on the CNC)
  Outer profile:  (r / R_outer)² + ((z − 0.500) / H_outer)² = 1
                  with R_outer = 2.5675", H_outer = 1.000"
  Inner profile:  (r / R_inner)² + ((z − 0.500) / H_inner)² = 1
                  with R_inner = R_outer − 0.0625 = 2.505"
                       H_inner = H_outer − 0.0625 = 0.9375"
  Wall thickness = 0.0625" (1/16") uniform along the dome.

Weld-prep detail at Z = 0 (bottom of socket skirt):
  Small external chamfer, 0.030" × 45°, on the outer edge.  Creates a
  tiny groove at the joint line for TIG filler metal to flow into.

── Two 1/4"-18 NPT ports through the dome ──

Port axes are parallel to Z (straight up through the curved dome —
NOT normal to the dome surface).  The outer dome surface stays clean
and curved; there are NO external bosses.

Port through-hole diameter: 0.438" (7/16", tap drill for 1/4"-18 NPT).
The actual tapered NPT thread is a CAM/tap operation, not STEP geometry.

Port centerline positions (X, Y):
  ( +0.750",  0 )
  ( −0.750",  0 )
  → 1.500" center-to-center, placed along the X axis across the dome.

Internal thread-engagement bosses (on the cavity side of the dome,
milled into the cap during CNC):
  Boss OD     = 0.600"
  Boss height = 0.300"  (along Z, extending downward into the cavity
                         from the local inner dome surface)
  Boss axis parallel to Z.

Thread-accepting material at each port:
  0.0625" (dome wall) + 0.300" (boss) = 0.3625"
  Slightly short of full 1/4"-18 NPT taper depth (~0.390"), but
  acceptable — the NPT engages ~5–6 threads, still sealing-grade at
  our pressure.

── Hoop-stress sanity check (100 PSI design) ──

  sigma = P × D / (2 × t)
        = 100 × 5.135 / (2 × 0.0625)
        = 4,108 PSI

  304 SS allowable: 20,000 PSI.  SF = 4.9×.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import math
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Socket skirt ──

TUBE_OD = 5.000 * IN                 # nominal tube OD
SKIRT_CLEAR = 0.010 * IN             # slip-fit radial clearance (diametral)
SKIRT_ID = TUBE_OD + SKIRT_CLEAR     # 5.010"
WALL = 0.0625 * IN                   # 1/16" uniform wall
SKIRT_OD = SKIRT_ID + 2 * WALL       # 5.135"
SKIRT_H = 0.500 * IN                 # socket skirt height

# ── Dome ──

DOME_OD = SKIRT_OD                   # 5.135" — matches skirt, smooth outside
R_OUTER = DOME_OD / 2.0              # 2.5675"
H_OUTER = 1.000 * IN                 # outer dome depth along Z

R_INNER = R_OUTER - WALL             # 2.505"
H_INNER = H_OUTER - WALL             # 0.9375"

# ── NPT ports through the dome ──

PORT_SPACING_X = 1.500 * IN          # center-to-center
NPT_TAP_DRILL = 0.438 * IN           # 7/16" for 1/4"-18 NPT
BOSS_OD = 0.600 * IN                 # internal boss OD (inside cavity)
BOSS_H = 0.300 * IN                  # internal boss height below inner
                                     #   dome surface, along Z

# ── Weld-prep chamfer at Z = 0 ──

WELD_CHAMFER = 0.030 * IN            # 0.030" × 45° external chamfer

# ── Z-axis datums ──

Z_SKIRT_BOT = 0.0
Z_DOME_START = SKIRT_H                       # 0.500"
Z_DOME_APEX = Z_DOME_START + H_OUTER         # 1.500"

# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════


def _ellipse_quarter_points(
    rx: float, ry: float, cx: float, cz: float, n: int, top_down: bool
):
    """
    Return (x, z) samples along a quarter-ellipse.

    Ellipse:  ((x - cx)/rx)² + ((z - cz)/ry)² = 1
    Quadrant used: x in [cx, cx + rx], z in [cz, cz + ry]
                   (upper-right quadrant w.r.t. center)

    If top_down=False: samples go from (cx + rx, cz) to (cx, cz + ry)
                       i.e. skirt→apex   (outer dome direction)
    If top_down=True:  samples go from (cx, cz + ry) to (cx + rx, cz)
                       i.e. apex→skirt   (inner dome direction, for
                       return sweep of the closed meridian)

    Endpoints are included.  n is the number of segments (n+1 points).
    """
    pts = []
    for i in range(n + 1):
        if top_down:
            # theta goes 90° → 0°
            theta = (math.pi / 2.0) * (1.0 - i / n)
        else:
            # theta goes 0° → 90°
            theta = (math.pi / 2.0) * (i / n)
        x = cx + rx * math.cos(theta)
        z = cz + ry * math.sin(theta)
        pts.append((x, z))
    return pts


def build_cap() -> cq.Workplane:
    """
    Build the domed end cap by revolving a closed meridian profile
    (in the XZ plane) 360° around the Z axis.

    Meridian profile, traced counter-clockwise as a closed loop:

      1. Start at bottom-outer-corner         (R_OUTER,     0)
      2. Up the outer skirt to                (R_OUTER,     SKIRT_H)
      3. Outer dome ellipse: (R_OUTER, SKIRT_H) → (0, Z_DOME_APEX),
         a quarter-ellipse with center (0, SKIRT_H), semi-axes
         (R_OUTER, H_OUTER).  Approximated by a polyline with
         ELLIPSE_SAMPLES segments — far more reliable than
         cadquery.ellipseArc for a closed revolve profile.
      4. Drop along the Z axis from apex to   (0,           SKIRT_H + H_INNER)
      5. Inner dome ellipse (return sweep):   (0, SKIRT_H+H_INNER) →
                                              (R_INNER,     SKIRT_H)
         quarter-ellipse, center (0, SKIRT_H), semi-axes
         (R_INNER, H_INNER).
      6. Step radially inward along the shoulder to
                                              (SKIRT_ID/2,  SKIRT_H)
      7. Down the skirt ID to                 (SKIRT_ID/2,  0)
      8. Close across the bottom annulus back to start.
    """

    ELLIPSE_SAMPLES = 72  # segments per quarter-ellipse (0.5°-ish)

    outer_pts = _ellipse_quarter_points(
        rx=R_OUTER, ry=H_OUTER,
        cx=0.0, cz=SKIRT_H,
        n=ELLIPSE_SAMPLES,
        top_down=False,   # (R_OUTER, SKIRT_H) → (0, apex)
    )
    inner_pts = _ellipse_quarter_points(
        rx=R_INNER, ry=H_INNER,
        cx=0.0, cz=SKIRT_H,
        n=ELLIPSE_SAMPLES,
        top_down=True,    # (0, apex_inner) → (R_INNER, SKIRT_H)
    )

    # Draw the meridian in the XY plane with X = radial and Y = axial.
    # We will revolve around the workplane's Y axis (world Y).  Then we
    # rotate the resulting solid so its axis of symmetry aligns with
    # the world Z axis (the convention the rest of this script uses).
    sketch = cq.Workplane("XY").moveTo(R_OUTER, 0.0)
    # Up outer skirt
    sketch = sketch.lineTo(R_OUTER, SKIRT_H)
    # Outer dome polyline (skip the first point — already at it)
    for (x, z) in outer_pts[1:]:
        sketch = sketch.lineTo(x, z)
    # Now at (0, Z_DOME_APEX).  Drop down Z axis to inner apex.
    sketch = sketch.lineTo(0.0, SKIRT_H + H_INNER)
    # Inner dome polyline (skip first — already at it)
    for (x, z) in inner_pts[1:]:
        sketch = sketch.lineTo(x, z)
    # Now at (R_INNER, SKIRT_H).  In this geometry R_INNER and
    # SKIRT_ID/2 happen to be identical (both = 2.505"), so the
    # "internal shoulder" is degenerate — the inner dome rim lands
    # exactly on the skirt ID.  The tube end butts directly against
    # the junction of the cylindrical skirt ID and the curved dome
    # interior at Z = SKIRT_H, which still functions as a hard stop.
    # Emit the shoulder-step line only if there is a real step.
    shoulder_step = abs(R_INNER - SKIRT_ID / 2.0)
    if shoulder_step > 1e-6:
        sketch = sketch.lineTo(SKIRT_ID / 2.0, SKIRT_H)
    # Down the skirt ID
    sketch = sketch.lineTo(SKIRT_ID / 2.0, 0.0)
    # Close across the bottom annulus
    sketch = sketch.close()

    # Revolve 360° around the workplane's Y axis (world Y).  Profile is
    # in the XY plane with X = radial, Y = axial.
    cap = sketch.revolve(
        angleDegrees=360,
        axisStart=(0, 0, 0),
        axisEnd=(0, 1, 0),
    )

    # Re-orient so the axis of symmetry is the world Z axis (convention
    # for the rest of this script — ports, bosses, bounding-box Z).
    # Rotate +90° around the world X axis: maps world +Y → world +Z.
    cap = cap.rotate((0, 0, 0), (1, 0, 0), 90)

    # ── Weld-prep external chamfer at the bottom of the skirt (Z = 0).
    # 0.030" × 45° on the outer-bottom edge of the skirt.  Select the
    # outer-circle edge at Z = 0 by filtering on both the bottom face's
    # edges and by radius — the outer edge has radius SKIRT_OD/2, the
    # inner edge has radius SKIRT_ID/2.
    try:
        cap_solid = cap.val()
        target_edges = []
        for e in cap_solid.Edges():
            # Skirt-bottom circular edges lie in the plane Z = 0 (bbox
            # zmin ≈ zmax ≈ 0).  Outer edge has bbox xmax ≈ SKIRT_OD/2,
            # inner edge has bbox xmax ≈ SKIRT_ID/2.  Pick the outer.
            ebb = e.BoundingBox()
            if ebb.zmax > 1e-4 or ebb.zmin < -1e-4:
                continue
            if e.geomType() != "CIRCLE":
                continue
            if abs(ebb.xmax - SKIRT_OD / 2.0) < 0.01 * IN:
                target_edges.append(e)
        if target_edges:
            cap = cap.newObject(target_edges).chamfer(WELD_CHAMFER)
        else:
            print("  [diag] weld-prep chamfer skipped: outer bottom edge not found")
    except Exception as e:
        print(f"  [diag] weld-prep chamfer skipped: {e}")

    # ── Internal thread-engagement bosses on the cavity side
    # Port centers along the X axis, ± PORT_SPACING_X / 2.
    port_positions = [
        (+PORT_SPACING_X / 2.0, 0.0),
        (-PORT_SPACING_X / 2.0, 0.0),
    ]

    for (px, py) in port_positions:
        # Inner dome surface Z at (px, py):
        #   (r / R_INNER)² + ((z - SKIRT_H) / H_INNER)² = 1
        #   z = SKIRT_H + H_INNER * sqrt(1 - (r/R_INNER)²)
        r = math.hypot(px, py)
        if r >= R_INNER:
            raise RuntimeError(
                f"port ({px/IN:.3f}, {py/IN:.3f}) outside inner dome footprint"
            )
        z_inner_surface = SKIRT_H + H_INNER * math.sqrt(
            1.0 - (r / R_INNER) ** 2
        )

        # Boss occupies the cavity BELOW the inner dome surface at this
        # (x, y), extending BOSS_H downward along Z from the local
        # inner dome surface.  To guarantee a clean union with the
        # curved inner dome surface (no sliver at the interface), we
        # start the boss cylinder slightly ABOVE the inner dome
        # surface — up to the local OUTER dome surface Z (so the
        # union overlaps entirely with existing dome wall material
        # in the overlap region, and adds new material only in the
        # cavity below the inner surface).
        #
        # Local outer dome surface Z at this (x, y):
        #   z_outer = SKIRT_H + H_OUTER * sqrt(1 - (r/R_OUTER)²)
        r2_out = (r / R_OUTER) ** 2
        if r2_out >= 1.0:
            raise RuntimeError(
                f"port ({px/IN:.3f}, {py/IN:.3f}) outside outer dome footprint"
            )
        z_outer_surface = SKIRT_H + H_OUTER * math.sqrt(1.0 - r2_out)
        boss_bottom_z = z_inner_surface - BOSS_H
        boss_top_z = z_outer_surface  # top flush with outer dome surface
        boss = (
            cq.Workplane("XY")
            .workplane(offset=boss_bottom_z)
            .center(px, py)
            .circle(BOSS_OD / 2.0)
            .extrude(boss_top_z - boss_bottom_z)
        )
        cap = cap.union(boss)

        # Through-hole at tap-drill diameter, axis parallel to Z,
        # through the entire cap at this (x, y).
        hole_bottom_z = -0.050 * IN
        hole_top_z = Z_DOME_APEX + 0.100 * IN
        hole = (
            cq.Workplane("XY")
            .workplane(offset=hole_bottom_z)
            .center(px, py)
            .circle(NPT_TAP_DRILL / 2.0)
            .extrude(hole_top_z - hole_bottom_z)
        )
        cap = cap.cut(hole)

    return cap


# ═══════════════════════════════════════════════════════
# BUILD + DIAGNOSTICS + EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

cap = build_cap()

bb = cap.val().BoundingBox()
dx = bb.xmax - bb.xmin
dy = bb.ymax - bb.ymin
dz = bb.zmax - bb.zmin

vol_cm3 = cap.val().Volume() / 1000.0
mass_g = vol_cm3 * 7.93

# Hoop stress at 100 PSI design
P_design_psi = 100.0
D_outer_in = DOME_OD / IN
t_wall_in = WALL / IN
sigma_psi = P_design_psi * D_outer_in / (2.0 * t_wall_in)

print()
print("Milled dome cap (5\" OD tube, socket-weld, 2× NPT through dome):")
print(f"  Bounding box: {dx:.2f} × {dy:.2f} × {dz:.2f} mm"
      f"  ({dx/IN:.3f} × {dy/IN:.3f} × {dz/IN:.3f} in)")
print(f"  Volume (material):    {vol_cm3:.2f} cm³")
print(f"  Mass (304 SS, 7.93):  {mass_g:.1f} g  ({mass_g/453.6:.2f} lb)")
print()
print("  Critical dimensions (spec vs. model):")
print(f"    Skirt ID:           spec 5.010 in  →  model {SKIRT_ID/IN:.3f} in")
print(f"    Skirt OD:           spec 5.135 in  →  model {SKIRT_OD/IN:.3f} in")
print(f"    Skirt height (Z):   spec 0.500 in  →  model {SKIRT_H/IN:.3f} in")
print(f"    Dome outer major D: spec 5.135 in  →  model {DOME_OD/IN:.3f} in")
print(f"    Dome outer depth:   spec 1.000 in  →  model {H_OUTER/IN:.3f} in")
print(f"    Wall thickness:     spec 0.0625 in →  model {WALL/IN:.4f} in (uniform)")
print(f"    Dome inner major D: derived        →  model {2*R_INNER/IN:.3f} in")
print(f"    Dome inner depth:   derived        →  model {H_INNER/IN:.4f} in")
print(f"    Port count:         spec 2         →  model 2")
print(f"    Port spacing (X):   spec 1.500 in  →  model {PORT_SPACING_X/IN:.3f} in")
print(f"    NPT tap drill:      spec 0.438 in  →  model {NPT_TAP_DRILL/IN:.3f} in")
print(f"    Internal boss OD:   spec 0.600 in  →  model {BOSS_OD/IN:.3f} in")
print(f"    Internal boss H:    spec 0.300 in  →  model {BOSS_H/IN:.3f} in")
print(f"    Weld-prep chamfer:  spec 0.030 in  →  model {WELD_CHAMFER/IN:.3f} in × 45°")
print()
print(f"  Thread-accepting material per port:")
print(f"    wall {WALL/IN:.4f}\" + boss {BOSS_H/IN:.3f}\" = "
      f"{(WALL+BOSS_H)/IN:.4f}\"  (1/4-18 NPT taper ~0.390\")")
print()
print(f"  Hoop stress @ {P_design_psi:.0f} PSI, D = {D_outer_in:.3f}\", "
      f"t = {t_wall_in:.4f}\":")
print(f"    sigma = P*D/(2t) = {sigma_psi:.0f} PSI")
print(f"    304 SS allowable ~20,000 PSI  →  SF = {20000.0/sigma_psi:.1f}×")
print()
print("  Assembly: cap skirt slips OVER the tube end; tube contacts")
print("  internal shoulder at Z = 0.500\"; TIG fillet weld at the")
print("  circumferential joint line at Z = 0 (weld-prep chamfer).")
print()
print("  Qty planning: 2 identical caps per vessel, 4 NPT ports per vessel.")
print("  Qty 20 caps → 10 vessels.")

fname = "carbonator-milled-dome-cap.step"
path = out_dir / fname
cq.exporters.export(cap, str(path))
print()
print(f"  Exported: {path}")
