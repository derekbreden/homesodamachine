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
  +Z = the keyed/latching side. The enclosure turns this side down into the empty pump bay.
  X completes the right-handed frame.

Geometry is in the frozen STEPs and display payloads beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "molex-micro-fit-4-panel.step"
PAYLOAD_PATH = _here.parent / "molex-micro-fit-4-panel.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

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

# --- removable housing and service motion ---------------------------------------
# SD-43025 gives the four-circuit body as 6.85 mm wide, 8.28 mm high and 14.00 mm
# long. Its complete latching envelope is 10.81 mm high and the latch works over an
# 11.0 mm length. The same drawing gives 24.77 mm for the complete mated pair.
FREE_BODY_W = 6.85
FREE_BODY_H = 8.28
FREE_BODY_D = 14.00
FREE_LATCH_H = 10.81 - FREE_BODY_H
FREE_LATCH_D = 11.00
MATED_PAIR_D = 24.77

# The fixed housing runs from -INBOARD_D to +MOUTH_PROUD. The mated-pair dimension
# starts at that same fixed wire face, so these two planes place the removable body's
# wire and mating faces in this module's frame. The overlap is the axial nesting that
# has to be withdrawn before the two housings are clear. One further millimetre gives
# the service path actual air instead of declaring tangent faces disconnected.
FREE_WIRE_Y = -INBOARD_D + MATED_PAIR_D
FREE_MATE_Y = FREE_WIRE_Y - FREE_BODY_D
MATED_OVERLAP = BODY_D + FREE_BODY_D - MATED_PAIR_D
SERVICE_AIR = 1.00
SERVICE_PULL = MATED_OVERLAP + SERVICE_AIR


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


def panel_footprint() -> tuple:
    """The cavity-face land reserved around the mounted housing, as ``(X, Z)``."""
    return (RECESS_W, RECESS_H)


def panel_cutout() -> tuple:
    """The keyed cut-out's overall printed envelope, as ``(X, Z)``."""
    return (CUT_EAR_W + 2.0 * CUT_SLIP, CUT_TOTAL_H + 2.0 * CUT_SLIP)


def main():
    print("molex-micro-fit-4-panel")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
