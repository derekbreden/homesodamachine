"""
Pressure-swirl hollow-cone atomizer — two-piece 316L SS CNC assembly for
the soda flavor injector carbonator vessel.

Designed for one-off Xometry CNC production in 316L SS.  Internal
geometry is sized to match the BETE CW25-H operating point (80° hollow
cone, ~1.14 mm orifice, ~0.94 L/min at 40 psi ΔP) so that the spray
characteristics are predictable from published data rather than
requiring empirical tuning from scratch.

── Parts ──

BODY (atomizer-nozzle-body.step):
  - 1/2" hex outside (12.7 mm across flats), ~16 mm long hex collar
  - 1/8"-27 NPT male outlet, 10 mm thread length
  - 1/4"-28 UNF tap-drill bore at inlet (user laps or taps, or uses a
    push-in fitting at the 1/4"-28 nominal ID)
  - Internal bore stepdown:
        Ø6.40 inlet bore → Ø5.00 puck seat → Ø4.00 swirl chamber →
        90° convergent cone → Ø1.10 × 0.70 orifice
  - NPT threads are NOT modeled as helical geometry — the unthreaded
    Ø10.29 outlet shank is the call-out.  Xometry/shop taps the
    1/8"-27 NPT.  Same convention for the 1/4"-28 UNF inlet.

PUCK (atomizer-nozzle-puck.step):
  - Ø5.00 h7 × 2.50 mm swirl distributor, press fit into body seat
  - Ø4.00 central bore (air-core extension of the swirl chamber, not a
    water path)
  - 4× axial feed holes Ø0.50 through the puck (water path from inlet
    pressure side to the tangential slots)
  - 4× tangential slots on the DOWNSTREAM (front) face, each 0.50 mm
    wide × 0.40 mm deep.  Each slot runs along a line tangent to the
    Ø4.00 central bore at 90° spacing.  When the puck front face seats
    against the body shoulder, the slots become closed-top channels
    that direct water tangentially into the swirl chamber.

── Operating point ──

  - Inlet pressure:   ~100 psi (Seaflo 100-psi diaphragm pump)
  - Backpressure:     ~60–70 psi (CO₂ vessel headspace)
  - ΔP across nozzle: 30–40 psi
  - Flow rate:        ~0.20 GPM (0.76 L/min)
  - Spray:            hollow cone, nominally 80° included
  - Droplet size:     ~100–150 µm mass median (from Lefebvre SMD
                      correlation at K≈0.36, ΔP=40 psi, cold water)

── Sources for internal geometry ──

  - BETE CW metric catalog (BETE_CW_hollowcone-metric.pdf) — CW25-H
    at 80°, 1/8" NPT: 1.14 mm orifice, K·ΔP^0.47 flow constant lands
    on 0.94 L/min at 40 psi ΔP.  This is our operating-point anchor.
  - Lefebvre & McDonell, *Atomization and Sprays*, 2nd ed., Ch. 6 —
    design equations for simplex pressure-swirl atomizers: L/d ratios,
    K = A_p / (D_s·d_o) factor, cone angle vs. K curve.
  - Rizk & Lefebvre 1985, "Internal Flow Characteristics of Simplex
    Swirl Atomizers," AIAA J. Propulsion 1(3):193–199 — K definition
    and Cd/α vs K.
  - Rusak et al. 2020, PMC 7345477 — optimized simplex geometry at
    similar small-orifice scale: Ds=4.0, slot 0.5×0.4, 4 slots,
    90° cone, Ls/Ds=0.5.  Our slot geometry is copied from this paper.
  - Chaudhari, Kulshreshtha, Channiwala 2013, IJAET 5(2):76–84 —
    full worked simplex example at d₀=0.8 mm, Ds=3.53 mm, 4 ports.

── Assembly notes (for Xometry order) ──

  - Both parts to be machined in 316L SS (food-contact application,
    CO₂-saturated water, long-term pitting resistance vs 304/303).
  - Body and puck are two separate line items on the Xometry quote.
  - Press-fit assembly: body Ø5.00 H7 bore × puck Ø5.00 h7 OD.  Target
    0.005–0.010 mm diametral interference.  Press manually with a
    vise and a soft-jaw arbor; no thermal assembly required.
  - After press fit, the puck cannot be removed non-destructively —
    this is intentional.  Verify slot alignment is acceptable (any
    rotational orientation is equivalent for axisymmetric spray).
  - Orifice is the critical feature.  Xometry call-out:
        "Ø1.10 ± 0.025, drilled + reamed, sharp-edged inlet,
         no deburr on outlet face, concentric to cone ±0.02 TIR."
  - Slot depth 0.40 ± 0.05 and width 0.50 ± 0.05 are the second
    tolerance priority.  Mill with Ø0.40 end mill or equivalent.
  - Swirl chamber Ø4.00 H7 × 3.00 mm — concentricity to orifice
    ±0.05 TIR.
  - Convergent cone:  90° ± 2° included.  A 90° spot drill or helical
    mill cycle gives this directly.

Run with:  tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import math
import cadquery as cq


# ══════════════════════════════════════════════════════════
# UNITS
# ══════════════════════════════════════════════════════════

IN = 25.4  # mm per inch


# ══════════════════════════════════════════════════════════
# ATOMIZER INTERNAL GEOMETRY
#   (sized to BETE CW25-H operating point; see docstring)
# ══════════════════════════════════════════════════════════

ORIFICE_D = 1.10                 # mm, exit orifice diameter
ORIFICE_L = 0.70                 # mm, orifice cylindrical land length
                                 #   (L/D = 0.64, within Lefebvre 0.5–1.0)

SWIRL_D   = 4.00                 # mm, swirl chamber diameter
                                 #   (D_s/d_o = 3.6, within Rizk 3–5)
SWIRL_L   = 3.00                 # mm, swirl chamber length in BODY
                                 #   (L_s/D_s = 0.75)

CONE_INCL_DEG = 90.0             # convergent cone included angle
CONE_L = (SWIRL_D - ORIFICE_D) / (2.0 * math.tan(math.radians(CONE_INCL_DEG / 2.0)))
#   For 90° included, tan(45°) = 1 → CONE_L = (4.0 − 1.1)/2 = 1.45 mm

PUCK_OD = 6.00                   # mm, press-fit OD.  Chosen larger than
                                 #   Ø5 reference so the annular ring on
                                 #   the puck front face (between Ø4.00
                                 #   bore and OD) is wide enough to fit
                                 #   a Ø0.50 drilled feed hole with safe
                                 #   (≥0.25 mm) material margins on both
                                 #   radial sides.  Increases the body
                                 #   puck seat bore from Ø5 to Ø6; the
                                 #   hex envelope still leaves ≥3.3 mm
                                 #   of wall at the flats.
PUCK_L  = 2.50                   # mm, puck axial length
PUCK_ID = 4.00                   # mm, puck central bore
                                 #   = air-core extension of swirl chamber
                                 #   (NOT a water path)

SLOT_N = 4                       # count of tangential inlet slots
SLOT_W = 0.50                    # mm, slot width (perpendicular to tangent)
SLOT_D = 0.40                    # mm, slot depth (axial, into front face)
SLOT_TANGENT_R = SWIRL_D / 2.0   # mm, perpendicular distance from axis to slot
                                 #   = swirl chamber radius → slot is tangent
                                 #   to Ø4.00 bore (90° off-radial, max swirl)

FEED_HOLE_D = 0.50               # mm, axial water feed hole through puck
                                 #   (Ø equal to slot width for clean union)

BACK_CHAMFER = 0.30              # mm × 45° chamfer on puck back central bore


# ══════════════════════════════════════════════════════════
# BODY OUTER ENVELOPE
# ══════════════════════════════════════════════════════════

HEX_AF = 0.500 * IN              # 12.7 mm across flats (1/2" wrench)
HEX_AC = HEX_AF * 2.0 / math.sqrt(3.0)
#   across-corners = AF / cos(30°); used directly in .polygon(6, AC)

# Inlet end: 1/4"-28 UNF female (user taps after CNC).  We cut the
# tap-drill diameter, not the thread form.
INLET_BORE_D = 6.40              # mm, 1/4"-28 UNF tap drill (7/32" → 5.56 mm
                                 #   minor, plus CNC tolerance; we're generous
                                 #   at 6.40 to accept a push-in fitting too)
INLET_BORE_L = 8.00              # mm, inlet bore depth

# Outlet end: 1/8"-27 NPT male (user taps/tails after CNC).  We model
# the unthreaded shank at nominal pipe OD.
NPT_NOMINAL_OD = 0.405 * IN      # 10.287 mm, 1/8" NPT pipe OD
NPT_L = 10.00                    # mm, NPT thread length

OVERCUT = 0.05                   # mm, boolean cut overshoot for clean breakout


# ══════════════════════════════════════════════════════════
# BODY Z-AXIS LAYOUT
#   Z = 0 at INLET face (top);  +Z → OUTLET face (bottom).
# ══════════════════════════════════════════════════════════

Z_INLET_FACE    = 0.0
Z_PUCK_SEAT_TOP = Z_INLET_FACE    + INLET_BORE_L      # 8.00
Z_SWIRL_TOP     = Z_PUCK_SEAT_TOP + PUCK_L            # 10.50
Z_CONE_TOP      = Z_SWIRL_TOP     + SWIRL_L           # 13.50
Z_ORIFICE_TOP   = Z_CONE_TOP      + CONE_L            # 14.95
Z_OUTLET_FACE   = Z_ORIFICE_TOP   + ORIFICE_L         # 15.65

BODY_TOTAL_L = Z_OUTLET_FACE
HEX_L = BODY_TOTAL_L - NPT_L                           # 5.65 mm hex collar
Z_NPT_TOP = HEX_L                                      # NPT shank Z range


# ══════════════════════════════════════════════════════════
# BODY
# ══════════════════════════════════════════════════════════

def build_body():
    """CNC body:  hex collar + NPT male shank, with internal swirl stack."""

    # ── Outer envelope ──
    # Hex collar from Z = 0 down to Z = HEX_L
    hex_collar = (
        cq.Workplane("XY")
        .polygon(6, HEX_AC)
        .extrude(HEX_L)
    )

    # NPT shank from Z = HEX_L down to Z = BODY_TOTAL_L
    npt_shank = (
        cq.Workplane("XY")
        .workplane(offset=HEX_L)
        .circle(NPT_NOMINAL_OD / 2.0)
        .extrude(NPT_L)
    )

    body = hex_collar.union(npt_shank)

    # ── Internal bore stack (subtractive) ──

    # 1. Inlet threaded bore (Ø6.40 × 8.0 mm, will be tapped 1/4"-28 UNF)
    inlet_bore = (
        cq.Workplane("XY")
        .circle(INLET_BORE_D / 2.0)
        .extrude(INLET_BORE_L)
    )
    body = body.cut(inlet_bore)

    # 2. Puck seat (Ø5.00 H7 × 2.50 mm)
    puck_seat = (
        cq.Workplane("XY")
        .workplane(offset=Z_PUCK_SEAT_TOP)
        .circle(PUCK_OD / 2.0)
        .extrude(PUCK_L)
    )
    body = body.cut(puck_seat)

    # 3. Swirl chamber (Ø4.00 H7 × 3.00 mm)
    swirl_chamber = (
        cq.Workplane("XY")
        .workplane(offset=Z_SWIRL_TOP)
        .circle(SWIRL_D / 2.0)
        .extrude(SWIRL_L)
    )
    body = body.cut(swirl_chamber)

    # 4. Convergent cone (Ø4.00 → Ø1.10 over CONE_L, 90° included)
    cone = (
        cq.Workplane("XY")
        .workplane(offset=Z_CONE_TOP).circle(SWIRL_D / 2.0)
        .workplane(offset=CONE_L).circle(ORIFICE_D / 2.0)
        .loft(ruled=True)
    )
    body = body.cut(cone)

    # 5. Orifice (Ø1.10 × 0.70 mm cylindrical land; overcut to break out)
    orifice = (
        cq.Workplane("XY")
        .workplane(offset=Z_ORIFICE_TOP)
        .circle(ORIFICE_D / 2.0)
        .extrude(ORIFICE_L + OVERCUT)
    )
    body = body.cut(orifice)

    return body


# ══════════════════════════════════════════════════════════
# PUCK (swirl distributor)
#
#   Geometry detail for the tangential slot + feed hole system:
#
#   For each slot i (i = 0..SLOT_N-1):
#     θ_i  = 2π·i/SLOT_N                            (angular index)
#     T_i  = inner tangent point on Ø4.00 bore
#          = (SLOT_TANGENT_R·cos θ_i,
#             SLOT_TANGENT_R·sin θ_i)
#     ê_i  = unit tangent vector at T_i
#          = (−sin θ_i, cos θ_i)
#
#   The slot is a rectangle in the XY plane, centered along the line
#   from T_i outward along ê_i, with length L_slot and width SLOT_W.
#
#   L_slot = √((PUCK_OD/2)² − SLOT_TANGENT_R²)
#          = √(2.5² − 2.0²) = 1.50 mm
#
#   i.e., the slot runs from the Ø4.0 tangent point all the way to the
#   tangent point on the Ø5.0 puck OD.  It is cut into the front face
#   to depth SLOT_D; the slot is "closed" on the +Z side by the body
#   shoulder when the puck is pressed home.
#
#   A Ø0.50 axial feed hole is drilled through the puck at distance
#   FEED_T along ê_i from T_i.  FEED_T is chosen so the feed hole is
#   well inside the puck material on both sides (radial margin checks
#   in the code below).
# ══════════════════════════════════════════════════════════

FEED_T = 1.50                    # mm along ê_i from T_i.  Places feed hole
                                 # at radial 2.5 mm (midline of the ring),
                                 # giving 0.25 mm material margins on both
                                 # radial sides of a Ø0.50 feed hole.
                                 # Verified at runtime.


def build_puck():
    """CNC swirl distributor — 4 tangential slots + 4 axial feed holes."""

    # ── Blank ──
    puck = (
        cq.Workplane("XY")
        .circle(PUCK_OD / 2.0)
        .extrude(PUCK_L)
    )

    # ── Central bore Ø4.00 through ──
    puck = puck.faces(">Z").workplane().hole(PUCK_ID)

    # ── Back-face chamfer on central bore (0.30 × 45°) ──
    # Cut a conical frustum at the back face:  Ø(PUCK_ID + 2·BACK_CHAMFER)
    # at Z = 0, tapering to Ø PUCK_ID at Z = BACK_CHAMFER.
    back_chamfer_cutter = (
        cq.Workplane("XY")
        .circle((PUCK_ID + 2.0 * BACK_CHAMFER) / 2.0)
        .workplane(offset=BACK_CHAMFER)
        .circle(PUCK_ID / 2.0)
        .loft(ruled=True)
    )
    puck = puck.cut(back_chamfer_cutter)

    # ── Slot and feed-hole geometry ──
    slot_len = math.sqrt((PUCK_OD / 2.0) ** 2 - SLOT_TANGENT_R ** 2)
    # = 1.50 mm for our numbers

    # Radial margin check for feed hole
    feed_hole_r = math.sqrt(SLOT_TANGENT_R ** 2 + FEED_T ** 2)
    margin_outer = (PUCK_OD / 2.0) - (feed_hole_r + FEED_HOLE_D / 2.0)
    margin_inner = (feed_hole_r - FEED_HOLE_D / 2.0) - (PUCK_ID / 2.0)
    if margin_outer < 0.10 or margin_inner < 0.10:
        raise RuntimeError(
            f"Feed hole radial margin too thin: outer={margin_outer:.3f} mm, "
            f"inner={margin_inner:.3f} mm (need ≥ 0.10 mm). "
            f"Adjust FEED_T."
        )

    for i in range(SLOT_N):
        theta = 2.0 * math.pi * i / SLOT_N

        # Inner tangent point T_i on Ø4.00 bore (world XY)
        ix = SLOT_TANGENT_R * math.cos(theta)
        iy = SLOT_TANGENT_R * math.sin(theta)

        # Unit tangent ê_i (outward along slot)
        tx = -math.sin(theta)
        ty = math.cos(theta)

        # Unit normal (perpendicular to tangent in XY plane, for slot width)
        nx = -ty
        ny = tx

        # ── Tangential slot (rectangle cut into front face) ──
        # Slot extends from slightly inside Ø4.00 (overshoot for clean
        # breakout into swirl chamber) to the tangent point on Ø5.00 OD.
        start_x = ix - tx * OVERCUT
        start_y = iy - ty * OVERCUT
        end_x = ix + tx * slot_len
        end_y = iy + ty * slot_len

        hw = SLOT_W / 2.0
        corners = [
            (start_x + nx * hw, start_y + ny * hw),
            (end_x + nx * hw, end_y + ny * hw),
            (end_x - nx * hw, end_y - ny * hw),
            (start_x - nx * hw, start_y - ny * hw),
        ]
        slot_cutter = (
            cq.Workplane("XY")
            .workplane(offset=PUCK_L - SLOT_D)
            .polyline(corners)
            .close()
            .extrude(SLOT_D + OVERCUT)
        )
        puck = puck.cut(slot_cutter)

        # ── Axial feed hole Ø0.50, full depth through puck ──
        feed_x = ix + tx * FEED_T
        feed_y = iy + ty * FEED_T
        feed_cutter = (
            cq.Workplane("XY")
            .workplane(offset=-OVERCUT)
            .moveTo(feed_x, feed_y)
            .circle(FEED_HOLE_D / 2.0)
            .extrude(PUCK_L + 2.0 * OVERCUT)
        )
        puck = puck.cut(feed_cutter)

    return puck


# ══════════════════════════════════════════════════════════
# BUILD + DIAGNOSTICS + EXPORT
# ══════════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

body = build_body()
puck = build_puck()

bb_body = body.val().BoundingBox()
bb_puck = puck.val().BoundingBox()

vol_body_mm3 = body.val().Volume()
vol_puck_mm3 = puck.val().Volume()
mass_body_g = (vol_body_mm3 / 1000.0) * 7.98   # 316L SS density ≈ 7.98 g/cm³
mass_puck_g = (vol_puck_mm3 / 1000.0) * 7.98

print()
print("Pressure-swirl hollow-cone atomizer — 316L SS 2-piece assembly")
print()
print("BODY:")
print(f"  Bounding box: {bb_body.xmax-bb_body.xmin:.2f} × "
      f"{bb_body.ymax-bb_body.ymin:.2f} × "
      f"{bb_body.zmax-bb_body.zmin:.2f} mm")
print(f"  Volume:       {vol_body_mm3/1000.0:.3f} cm³")
print(f"  Mass (316L):  {mass_body_g:.2f} g")
print()
print("PUCK:")
print(f"  Bounding box: {bb_puck.xmax-bb_puck.xmin:.2f} × "
      f"{bb_puck.ymax-bb_puck.ymin:.2f} × "
      f"{bb_puck.zmax-bb_puck.zmin:.2f} mm")
print(f"  Volume:       {vol_puck_mm3/1000.0:.3f} cm³")
print(f"  Mass (316L):  {mass_puck_g:.2f} g")
print()
print("Critical dimensions:")
print(f"  Orifice:           Ø{ORIFICE_D:.2f} × {ORIFICE_L:.2f} mm "
      f"(L/D = {ORIFICE_L/ORIFICE_D:.2f})")
print(f"  Swirl chamber:     Ø{SWIRL_D:.2f} × {SWIRL_L:.2f} mm in body "
      f"(L/D = {SWIRL_L/SWIRL_D:.2f})")
print(f"  Convergent cone:   {CONE_INCL_DEG:.0f}° included × "
      f"{CONE_L:.2f} mm axial")
print(f"  Puck:              Ø{PUCK_OD:.2f} × {PUCK_L:.2f} mm, "
      f"Ø{PUCK_ID:.2f} central bore")
print(f"  Tangential slots:  {SLOT_N} × ({SLOT_W:.2f} × {SLOT_D:.2f}) mm, "
      f"tangent to Ø{SWIRL_D:.2f}")
slot_len = math.sqrt((PUCK_OD / 2.0) ** 2 - SLOT_TANGENT_R ** 2)
print(f"  Slot length:       {slot_len:.2f} mm "
      f"(Ø{SWIRL_D:.1f} tangent → Ø{PUCK_OD:.1f} tangent)")
print(f"  Feed holes:        {SLOT_N} × Ø{FEED_HOLE_D:.2f} through, "
      f"at r={math.sqrt(SLOT_TANGENT_R**2 + FEED_T**2):.2f} mm")
print(f"  Body hex:          {HEX_AF:.2f} mm AF (1/2\" wrench)")
print(f"  Body total L:      {BODY_TOTAL_L:.2f} mm "
      f"({HEX_L:.2f} hex + {NPT_L:.2f} NPT)")
print()
print("Total slot flow area:    "
      f"{SLOT_N * SLOT_W * SLOT_D:.3f} mm²")
print("Orifice area:            "
      f"{math.pi * (ORIFICE_D / 2.0) ** 2:.3f} mm²")
print(f"K = Ap/(Ds·do):          "
      f"{(SLOT_N * SLOT_W * SLOT_D)/(SWIRL_D * ORIFICE_D):.3f}  "
      f"(Rizk/Lefebvre; ~0.3 gives ~80° cone)")
print()

body_path = out_dir / "atomizer-nozzle-body.step"
puck_path = out_dir / "atomizer-nozzle-puck.step"

cq.exporters.export(body, str(body_path))
cq.exporters.export(puck, str(puck_path))

print(f"Exported:  {body_path.name}")
print(f"Exported:  {puck_path.name}")
