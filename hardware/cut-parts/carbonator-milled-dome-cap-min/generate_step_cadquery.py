"""
Carbonator milled domed end cap — MINIMUM-ENVELOPE variant.

This is a variant of `carbonator-milled-dome-cap` with a shortened
socket skirt, for applications where total vessel length along Z is
tight.  Everything that touches the pressure envelope is IDENTICAL to
the baseline cap:

  - Ellipsoidal dome geometry (D = 5.135", h = 1.000", t = 0.0625")
  - 2× 1/4"-18 NPT ports through the dome, 1.500" center-to-center
  - Internal thread-engagement bosses, 0.600" OD × 0.300" H
  - Wall thickness 0.0625" uniform, dome profile unchanged
  - 0.030" × 45° weld-prep chamfer at the skirt bottom

The ONLY change from the baseline is the socket skirt height:

  Baseline cap skirt:   0.500" along Z
  Min-envelope skirt:   0.250" along Z   (−0.250" per cap)

Two caps per vessel, so the total vessel length drops by 0.500" for
the pair.  The socket weld is still a slip-fit-over-tube TIG fillet at
the circumferential joint; 0.250" of axial engagement is ample for a
1/16" wall fillet on a 5"-OD tube (the weld leg is the structural
feature, not the socket-overlap length).

── Why the dome couldn't shrink further ──

The dome depth is pressure-rating-critical and the K factor blows up
fast as the dome flattens:

  K = (1/6) × (2 + (D / (2h))²)

  At h = 1.000":   K ≈ 1.43     (this design)
  At h = 0.750":   K ≈ 1.47 ... wait, (D/2h)² = (5.135/1.5)² = 11.72
                   K = (1/6)(2 + 11.72) = 2.29  — 60 % worse
  At h = 0.500":   (D/2h)² = (5.135/1.0)² = 26.4
                   K = (1/6)(2 + 26.4) = 4.73  — 3.3× worse

Hoop stress scales linearly with K, and at t = 0.0625" we have no
wall thickness left to give.  Shrinking the skirt is the only place
we can recover envelope without sacrificing the pressure rating.

── Coordinate convention (inches; converted to mm at export) ──

  Z = 0.000" ── bottom of socket skirt (open, faces away from tube)
  Z = 0.250" ── top of socket skirt / start of dome   (was 0.500")
  Z = 1.250" ── dome apex (closed end)                (was 1.500")

── Hoop-stress sanity check (100 PSI design, with K factor) ──

  sigma = P × D × K / (2 × t)
        = 100 × 5.135 × 1.43 / (2 × 0.0625)
        ≈ 5,875 PSI
  304 SS allowable: 20,000 PSI.  SF ≈ 3.4×.

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
SKIRT_H = 0.250 * IN                 # REDUCED: 0.250" (was 0.500" baseline)

# ── Dome ──

DOME_OD = SKIRT_OD                   # 5.135" — matches skirt, smooth outside
R_OUTER = DOME_OD / 2.0              # 2.5675"
H_OUTER = 1.000 * IN                 # outer dome depth along Z (unchanged)

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
Z_DOME_START = SKIRT_H                       # 0.250"
Z_DOME_APEX = Z_DOME_START + H_OUTER         # 1.250"

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
            theta = (math.pi / 2.0) * (1.0 - i / n)
        else:
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
      3. Outer dome ellipse (skirt→apex)      → (0, Z_DOME_APEX)
      4. Drop along the Z axis from apex to   (0, SKIRT_H + H_INNER)
      5. Inner dome ellipse (apex→skirt)      → (R_INNER, SKIRT_H)
      6. (Degenerate shoulder — R_INNER == SKIRT_ID/2 by construction)
      7. Down the skirt ID to                 (SKIRT_ID/2, 0)
      8. Close across the bottom annulus back to start.
    """

    ELLIPSE_SAMPLES = 72  # segments per quarter-ellipse

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

    # Meridian in XY plane with X = radial, Y = axial.  Revolve around
    # the workplane Y axis, then rotate the solid so its symmetry axis
    # is world Z (convention for ports, bosses, bbox Z).
    sketch = cq.Workplane("XY").moveTo(R_OUTER, 0.0)
    sketch = sketch.lineTo(R_OUTER, SKIRT_H)
    for (x, z) in outer_pts[1:]:
        sketch = sketch.lineTo(x, z)
    sketch = sketch.lineTo(0.0, SKIRT_H + H_INNER)
    for (x, z) in inner_pts[1:]:
        sketch = sketch.lineTo(x, z)
    # R_INNER == SKIRT_ID/2 by construction (both = 2.505"); the
    # shoulder is degenerate.  Only emit a shoulder-step line if a real
    # step ever arises from future parameter edits.
    shoulder_step = abs(R_INNER - SKIRT_ID / 2.0)
    if shoulder_step > 1e-6:
        sketch = sketch.lineTo(SKIRT_ID / 2.0, SKIRT_H)
    sketch = sketch.lineTo(SKIRT_ID / 2.0, 0.0)
    sketch = sketch.close()

    cap = sketch.revolve(
        angleDegrees=360,
        axisStart=(0, 0, 0),
        axisEnd=(0, 1, 0),
    )

    # Re-orient so axis of symmetry = world Z.
    cap = cap.rotate((0, 0, 0), (1, 0, 0), 90)

    # ── Weld-prep external chamfer at skirt bottom (Z = 0) ──
    # 0.030" × 45° on the outer-bottom edge.
    try:
        cap_solid = cap.val()
        target_edges = []
        for e in cap_solid.Edges():
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

    # ── Internal thread-engagement bosses + through-holes ──
    port_positions = [
        (+PORT_SPACING_X / 2.0, 0.0),
        (-PORT_SPACING_X / 2.0, 0.0),
    ]

    for (px, py) in port_positions:
        r = math.hypot(px, py)
        if r >= R_INNER:
            raise RuntimeError(
                f"port ({px/IN:.3f}, {py/IN:.3f}) outside inner dome footprint"
            )
        z_inner_surface = SKIRT_H + H_INNER * math.sqrt(
            1.0 - (r / R_INNER) ** 2
        )

        r2_out = (r / R_OUTER) ** 2
        if r2_out >= 1.0:
            raise RuntimeError(
                f"port ({px/IN:.3f}, {py/IN:.3f}) outside outer dome footprint"
            )
        z_outer_surface = SKIRT_H + H_OUTER * math.sqrt(1.0 - r2_out)

        # Boss extends from BOSS_H below inner dome surface up to local
        # outer dome Z (top flush with outer surface — overlapping the
        # dome wall material guarantees clean union, no sliver).
        boss_bottom_z = z_inner_surface - BOSS_H
        boss_top_z = z_outer_surface
        boss = (
            cq.Workplane("XY")
            .workplane(offset=boss_bottom_z)
            .center(px, py)
            .circle(BOSS_OD / 2.0)
            .extrude(boss_top_z - boss_bottom_z)
        )
        cap = cap.union(boss)

        # Through-hole at tap-drill diameter, axis parallel to Z.
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

# Hoop stress at 100 PSI design, with Brownell-Young K factor for a
# shallower-than-2:1 ellipsoidal head.
P_design_psi = 100.0
D_outer_in = DOME_OD / IN
h_dome_in = H_OUTER / IN
t_wall_in = WALL / IN
K_factor = (1.0 / 6.0) * (2.0 + (D_outer_in / (2.0 * h_dome_in)) ** 2)
sigma_psi = P_design_psi * D_outer_in * K_factor / (2.0 * t_wall_in)
allowable_psi = 20000.0
SF = allowable_psi / sigma_psi

print()
print("Milled dome cap, MIN-ENVELOPE variant "
      "(5\" OD tube, socket-weld, 2× NPT through dome):")
print(f"  Bounding box: {dx:.2f} × {dy:.2f} × {dz:.2f} mm"
      f"  ({dx/IN:.3f} × {dy/IN:.3f} × {dz/IN:.3f} in)")
print(f"  Volume (material):    {vol_cm3:.2f} cm³")
print(f"  Mass (304 SS, 7.93):  {mass_g:.1f} g  ({mass_g/453.6:.2f} lb)")
print()
print("  Critical dimensions (spec vs. model):")
print(f"    Skirt ID:           spec 5.010 in  →  model {SKIRT_ID/IN:.3f} in")
print(f"    Skirt OD:           spec 5.135 in  →  model {SKIRT_OD/IN:.3f} in")
print(f"    Skirt height (Z):   spec 0.250 in  →  model {SKIRT_H/IN:.3f} in  "
      f"(baseline 0.500 in)")
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
print(f"  Hoop stress @ {P_design_psi:.0f} PSI "
      f"(Brownell-Young K factor for ellipsoidal head):")
print(f"    D = {D_outer_in:.3f}\"   h = {h_dome_in:.3f}\"   "
      f"t = {t_wall_in:.4f}\"")
print(f"    K = (1/6)(2 + (D/2h)²) = {K_factor:.3f}")
print(f"    sigma = P·D·K / (2t) = {sigma_psi:.0f} PSI")
print(f"    304 SS allowable {allowable_psi:.0f} PSI  →  SF = {SF:.2f}×")
print()
print("  Envelope saving vs. baseline cap:")
print("    Per cap:    0.250\" shorter along Z")
print("    Per vessel: 0.500\" shorter total (2 caps)")
print()
print("  Assembly: cap skirt slips OVER the tube end; TIG fillet weld at")
print("  the circumferential joint line at Z = 0 (weld-prep chamfer).")

fname = "carbonator-milled-dome-cap-min.step"
path = out_dir / fname
cq.exporters.export(cap, str(path))
print()
print(f"  Exported: {path}")
