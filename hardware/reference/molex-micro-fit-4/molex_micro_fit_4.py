"""The four-circuit Molex Micro-Fit 3.0 pump connector and its panel interface.

The fixed half is Molex 43020-0400: a black, dual-row plug housing with its own panel-mount
ears.  The removable pump-cartridge half is 43025-0400.  Both take the bought BNTECHGO
22 AWG 4P ribbon through 43031-0001 male and 43030-0001 female crimp terminals.

The connector is drawn from Molex customer drawing SD-43020-006 and product specification
PS-43045.  The printed panel uses the customer drawing's keyed cut-out, but opens it by one
FDM slip.  A shallow recess behind a 3 mm host wall leaves a 2 mm local panel: inside the
specified 1.40--2.54 mm range and with one millimetre of printed backing around it.

Coordinate convention -- the same wall frame as ``riteav_keystone``:
  Y = mating axis. +Y = outward, toward the removable cartridge connector.
  Origin = the panel's outward face at the centre of the drawing's 7.11 mm main opening.
  +Z = the keyed side of the panel cut-out. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/reference/molex-micro-fit-4/molex_micro_fit_4.py
    tools/cad-venv/bin/python hardware/reference/molex-micro-fit-4/molex_micro_fit_4.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly  # noqa: E402
from _materials import M_DONOR_BLACK, one_body  # noqa: E402

STEP = _here.parent / "molex-micro-fit-4-panel.step"

FIXED_HOUSING = "43020-0400"
FREE_HOUSING = "43025-0400"
MALE_TERMINAL = "43031-0001"
FEMALE_TERMINAL = "43030-0001"

# --- Molex SD-43020-006 recommended panel cut-out -------------------------------
# Four-circuit row in the drawing. C is the housing opening; D reaches the two panel ears.
CUT_BODY_W = 7.21
CUT_BODY_H = 7.11
CUT_EAR_W = 10.90
CUT_EAR_H = 4.06
CUT_KEY_W = 1.98
CUT_TOTAL_H = 8.71
CUT_KEY_H = CUT_TOTAL_H - CUT_BODY_H
CUT_CORNER_R_MAX = 0.18

# Printed PET-GF clearance, per side. The drawing already tolerances the punched hole, but a
# printed edge is not a punch: this is the one process allowance added to every cut edge.
CUT_SLIP = 0.15

# The housing is designed for 1.40--2.54 mm sheet. The host rib is 3 mm, so its cavity face is
# locally relieved until this much panel remains.
PANEL_T_MIN = 1.40
PANEL_T_MAX = 2.54
PANEL_T = 2.00
RECESS_W = 16.0
RECESS_H = 14.0

# --- fixed housing envelope ------------------------------------------------------
# The customer drawing gives A = 6.85 mm for four circuits, 6.85 mm across the other face,
# 16.89 mm body depth, and 8.38 mm from the mating end to the panel-mount datum. The ears are
# represented at their full D-width so the assembly model reserves the motion and finger room.
BODY_W = 6.85
BODY_H = 6.85
BODY_D = 16.89
MOUTH_PROUD = 8.38
INBOARD_D = BODY_D - MOUTH_PROUD
EAR_W = CUT_EAR_W - 0.20
EAR_H = CUT_EAR_H - 0.20
EAR_RAMP_D = 5.0
PANEL_STOP_W = 12.0
PANEL_STOP_H = 0.80
PANEL_STOP_D = 0.60

# The four terminal cavities shown on the 3 mm grid. They are only visual relief in the
# reference solid; the purchased housing, rather than this model, controls the contact fit.
CONTACT_PITCH = 3.0
CAVITY = 1.93
CAVITY_D = 5.0


def panel_profile(slip: float = CUT_SLIP):
    """The drawing's keyed cut-out polygon on X/Z, opened by ``slip`` per edge.

    The 7.11 mm body window carries a 1.60 mm central key above it. The two snap ears use the
    wider 10.90 mm band over the lower 4.06 mm. This is the asymmetric orientation Molex calls
    out: the panel features lock on the face opposite the punch side.
    """
    xi = CUT_BODY_W / 2.0 + slip
    xo = CUT_EAR_W / 2.0 + slip
    xk = CUT_KEY_W / 2.0 + slip
    zb = -CUT_BODY_H / 2.0 - slip
    zs = CUT_BODY_H / 2.0 + slip
    # ``zs`` already moved the main opening's top edge up by ``slip``. The key's far edge is
    # the nominal overall top plus that same one edge allowance, not another allowance again.
    zt = CUT_BODY_H / 2.0 + CUT_KEY_H + slip
    ze = zb + CUT_EAR_H + 2.0 * slip
    return [
        (-xi, zb), (-xo, zb), (-xo, ze), (-xi, ze),
        (-xi, zs), (-xk, zs), (-xk, zt), (xk, zt),
        (xk, zs), (xi, zs), (xi, ze), (xo, ze), (xo, zb),
    ]


def panel_cut(host_t: float, panel_t: float = PANEL_T):
    """Return the through cut plus the cavity-side thinning pocket for a ``host_t`` wall.

    Positive extrusion off an XZ workplane runs toward -Y, which is into the panel in this
    module's frame. The returned cutter therefore starts just outside Y=0 and finishes just
    behind the host wall.
    """
    if not (PANEL_T_MIN <= panel_t <= PANEL_T_MAX):
        raise ValueError(f"Micro-Fit panel must be {PANEL_T_MIN:.2f}--{PANEL_T_MAX:.2f} mm")
    if host_t < panel_t:
        raise ValueError("Micro-Fit host wall is thinner than its local panel")
    through = (
        cq.Workplane("XZ")
        .polyline(panel_profile())
        .close()
        .extrude(host_t + 0.04)
        .translate((0.0, 0.02, 0.0))
    )
    if host_t <= panel_t + 1e-9:
        return through.val()
    recess = (
        cq.Workplane("XZ")
        .rect(RECESS_W, RECESS_H)
        .extrude(host_t - panel_t + 0.02)
        .translate((0.0, -panel_t + 0.01, CUT_KEY_H / 2.0))
    )
    return through.union(recess).val()


def panel_footprint() -> tuple:
    """The cavity-face land reserved around the mounted housing, as ``(X, Z)``."""
    return (RECESS_W, RECESS_H)


def panel_cutout() -> tuple:
    """The keyed cut-out's overall printed envelope, as ``(X, Z)``."""
    return (CUT_EAR_W + 2.0 * CUT_SLIP, CUT_TOTAL_H + 2.0 * CUT_SLIP)


def build_fixed():
    """Conservative solid for the fixed 43020-0400 housing and its two panel ears."""
    # Start at the outboard mating end. Extruding on XZ toward -Y leaves the wire side inboard.
    body = (
        cq.Workplane("XZ")
        .rect(BODY_W, BODY_H)
        .extrude(BODY_D)
        .translate((0.0, MOUTH_PROUD, 0.0))
    )

    # The integral ears grow from the side faces and ramp to the customer-drawing D envelope.
    # Their trailing faces stand just behind the 2 mm panel, so they are the purchased snap and
    # no printed PET-GF feature is asked to flex.
    # The drawing's wide D-band is the lower 4.06 mm of the cut-out, not a band centred on the
    # housing. Put the ears in that band so their deflection sweep passes through the opening
    # and closes behind the panel without entering its upper shoulders.
    z0 = -CUT_BODY_H / 2.0 + 0.10
    for sx in (-1.0, 1.0):
        x_body = sx * BODY_W / 2.0
        x_tip = sx * EAR_W / 2.0
        ear = (
            cq.Workplane("XY")
            .polyline([
                (x_body, 0.4),
                (x_tip, -PANEL_T - 0.2),
                (x_body, -PANEL_T - EAR_RAMP_D),
            ])
            .close()
            .extrude(EAR_H)
            .translate((0.0, 0.0, z0))
        )
        body = body.union(ear)

    # The rigid lower shoulder bears on the punch-side face while the two flexible ears close
    # on the opposite face. Its inboard face is exactly Y=0, so the assembly records contact
    # with the wall without drawing either nylon or PET-GF through the other.
    stop_z0 = -CUT_BODY_H / 2.0 - PANEL_STOP_H + 0.25
    stop = cq.Solid.makeBox(
        PANEL_STOP_W, PANEL_STOP_D, PANEL_STOP_H,
        cq.Vector(-PANEL_STOP_W / 2.0, 0.0, stop_z0),
    )
    body = body.union(stop)

    # Four visible terminal mouths, two rows by two columns. Their shape identifies the part in
    # assembly renders without pretending to reproduce the terminal-locking detail.
    for x in (-CONTACT_PITCH / 2.0, CONTACT_PITCH / 2.0):
        for z in (-CONTACT_PITCH / 2.0, CONTACT_PITCH / 2.0):
            cavity = (
                cq.Workplane("XZ")
                .rect(CAVITY, CAVITY)
                .extrude(CAVITY_D)
                .translate((x, MOUTH_PROUD + 0.01, z))
            )
            body = body.cut(cavity)
    return body.val()


def selftest() -> int:
    ok = True
    if not (PANEL_T_MIN <= PANEL_T <= PANEL_T_MAX):
        print("FAIL: the local panel is outside Molex's thickness range")
        ok = False
    if not (CUT_EAR_W > CUT_BODY_W > BODY_W and CUT_TOTAL_H > CUT_BODY_H):
        print("FAIL: the keyed cut-out does not clear the four-circuit body")
        ok = False
    if min((RECESS_W - CUT_EAR_W) / 2.0, (RECESS_H - CUT_TOTAL_H) / 2.0) < 2.0:
        print("FAIL: the panel recess leaves less than 2 mm of printed land")
        ok = False
    cut = panel_cut(3.0)
    fixed = build_fixed()
    if not cut.isValid() or len(cut.Solids()) != 1:
        print("FAIL: the panel cutter is not one valid solid")
        ok = False
    if not fixed.isValid() or len(fixed.Solids()) != 1:
        print("FAIL: the fixed housing is not one valid solid")
        ok = False
    profile = panel_profile()
    cut_w = max(p[0] for p in profile) - min(p[0] for p in profile)
    cut_h = max(p[1] for p in profile) - min(p[1] for p in profile)
    expected_cut_w, expected_cut_h = panel_cutout()
    if abs(cut_w - expected_cut_w) > 0.02 or abs(cut_h - expected_cut_h) > 0.02:
        print(f"FAIL: panel cut-out is {cut_w:.3f} × {cut_h:.3f} mm, not "
              f"{expected_cut_w:.3f} × {expected_cut_h:.3f} mm")
        ok = False
    bb = fixed.BoundingBox()
    if abs(bb.ymin + INBOARD_D) > 0.02 or abs(bb.ymax - MOUTH_PROUD) > 0.02:
        print(f"FAIL: housing depth is {bb.ymin:.3f}..{bb.ymax:.3f}, not "
              f"{-INBOARD_D:.3f}..{MOUTH_PROUD:.3f}")
        ok = False
    print("PASS: molex-micro-fit-4 housing and panel agree" if ok else "FAIL")
    return 0 if ok else 1


def main():
    export_assembly(one_body(build_fixed(), "molex-micro-fit-4-panel", M_DONOR_BLACK), STEP)
    print(f"-> {STEP}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
