"""John Guest PP0208E — the 1/4" push-to-connect union tee in black polypropylene.

Three identical ports on one body: a straight RUN of two in line, and a BRANCH off the middle of
it at a right angle. Every port takes 1/4" OD LLDPE by push, and nothing on the fitting threads,
clamps or takes a tool. It is the tee in the install kit, the split on the ASSE 1022's outlet
(`../water-split/`), and six of the manifold's eight junctions.

The figures are John Guest's own, off the Polypropylene Equal Tee data sheet Pp4608_01/23, 1/4"
row — the row `PP0208W` (white), `PP0208W-B` (white, blue collet) and `PP0208E` (black) share.
`*B`, `*C` and `*G` are dimensioned there WITH THE COLLETS IN THE RELEASE POSITION, pressed home
against the collar, which is the state the solid here is cut in; at rest each collet stands
1.65 mm further out, calipered on the fitting in hand at `../tee-connector/README.md`.

The arm's own steps — the barrel between the hub and the collar, and the collet's outside — are
not on the data sheet. They are the tree's one drawing of a John Guest 1/4" push-fit port, shared
with the Quick Start's plumbing scenes (`../../quickstart/plumbing/`), so a collet the customer
pushes a tube into is the same collet wherever this repository draws one.

Coordinate frame
----------------
- The RUN on Z, its two collet faces at ±`REACH`. The BRANCH on +Y, its face at the same
  `REACH`. All three ports are coaxial with the body centre, which is the origin.
- The same frame `../tee-connector/` states, so a turn written for one tee turns the other.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp0208e-tee/jg_pp0208e_tee.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly, import_step
from _materials import M_JG_BLACK_PP, one_body

STEP = _here.parent / "jg-pp0208e-tee.step"

# --- the data sheet, Pp4608_01/23, 1/4" row ---------------------------------

TUBE_OD = 6.35            # A — the tube the three ports accept, +0.03 / −0.10
RUN_SPAN = 39.0           # B — collet face to collet face along the run
REACH = 19.5              # C — body centre to any one of the three collet faces
INSERTION = 15.7          # D — collet face to the internal tube stop
COLLAR_D = 16.3           # E — the collar on each arm, and the fitting's widest section
BORE_D = 4.3              # F — the through bore
BRANCH_ENVELOPE = 27.7    # G — branch collet face to the far side of the run body

# --- the arm's profile, shared with `../../quickstart/plumbing/` -------------
# Outward from the hub each arm carries the same three sections: a barrel the neighbouring arm's
# root crosses, then the collar standing full `COLLAR_D`, then the release collet standing proud
# of the collar's face so a thumb reaches it around the tube.
ARM_D = 10.6
COLLAR_NEAR = 8.2         # where the barrel ends and the collar begins
COLLAR_FAR = 16.3         # where the collar ends and the collet stands out of it
COLLET_D = 9.7
COLLET_BORE = 6.70        # the tube passes it with 0.35 of slip
COLLET_PROUD = REACH - COLLAR_FAR

MEASURE_TOL = 0.06        # what the data sheet's millimetre column is rounded to

# The three arms, each as `(outward axis, the port's own name)`. The run's two are the tee's
# straight-through path and the branch is what turns off it; which leg of a junction lands on
# which is the topology's business (`../../topology/fluid-topology.md`).
ARMS = (((0.0, 0.0, 1.0), "+z"), ((0.0, 0.0, -1.0), "-z"), ((0.0, 1.0, 0.0), "branch"))


def run(sign: float) -> tuple:
    """One of the run's two collinear ports, `sign` picking the +Z or −Z end:
    `(position, outward axis)`. The station is the COLLET'S own outer face — the plane a tube
    crosses to enter, and runs `INSERTION` beyond."""
    s = 1.0 if sign > 0 else -1.0
    return ((0.0, 0.0, s * REACH), (0.0, 0.0, s))


def branch() -> tuple:
    """The third port, perpendicular to the run, out +Y."""
    return ((0.0, REACH, 0.0), (0.0, 1.0, 0.0))


def stations() -> dict:
    """All three ports, under the ends they stand on."""
    return {"+z": run(+1.0), "-z": run(-1.0), "branch": branch()}


def envelope() -> tuple:
    """`(across the run, along the run, off the branch)` — the box the fitting takes, and what
    crowds a neighbour. The branch reads to the far side of the run body, not to its own centre,
    because that is the side a wall stands on."""
    return (COLLAR_D, RUN_SPAN, BRANCH_ENVELOPE)


def _cyl(d: float, axis, near: float, far: float) -> cq.Solid:
    """A cylinder of `d` on `axis`, between two stations measured from the body centre."""
    direction = cq.Vector(*axis)
    return cq.Solid.makeCylinder(
        d / 2.0, far - near, direction.multiply(near), direction)


def _arm(axis) -> cq.Solid:
    """One arm's material: the barrel, the collar, and the collet standing proud of it, bored
    `COLLET_BORE` so the collet reads as the ring a thumb presses."""
    collet = (_cyl(COLLET_D, axis, COLLAR_FAR, REACH)
              .cut(_cyl(COLLET_BORE, axis, COLLAR_FAR - 0.2, REACH + 0.2)))
    return (_cyl(ARM_D, axis, 0.0, COLLAR_NEAR)
            .fuse(_cyl(COLLAR_D, axis, COLLAR_NEAR, COLLAR_FAR))
            .fuse(collet))


def build_jg_pp0208e_tee() -> cq.Workplane:
    """The tee as a single solid: a hub the three arms leave, each bored the tube's socket, and
    the through passage between them at the bore of the tube itself."""
    solid = cq.Solid.makeSphere(ARM_D / 2.0, cq.Vector(0, 0, 0), angleDegrees1=-90)
    sockets = None
    for axis, _name in ARMS:
        solid = solid.fuse(_arm(axis))
        socket = _cyl(TUBE_OD, axis, REACH - INSERTION, REACH + 0.2)
        sockets = socket if sockets is None else sockets.fuse(socket)
    bores = _cyl(BORE_D, (0.0, 0.0, 1.0), -REACH - 0.2, REACH + 0.2).fuse(
        _cyl(BORE_D, (0.0, 1.0, 0.0), 0.0, REACH + 0.2))
    return cq.Workplane(obj=solid.cut(sockets).cut(bores).clean())


def stations_hold():
    """Hold the data sheet's figures to `jg-pp0208e-tee.step`.

    The three collet faces are extents of the solid's own box, and so is the collar that carries
    `COLLAR_D`. `BRANCH_ENVELOPE` is the one figure that is neither: it spans the branch face to
    the far side of the run body, which is the box's whole Y."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (
            ("+z collet face", REACH, bb.zmax),
            ("−z collet face", -REACH, bb.zmin),
            ("branch collet face", REACH, bb.ymax),
            ("run span", RUN_SPAN, bb.zlen),
            ("collar across the run", COLLAR_D, bb.xlen),
            ("branch envelope", BRANCH_ENVELOPE, bb.ylen)):
        if abs(claimed - actual) > MEASURE_TOL:
            raise ValueError(
                f"jg-pp0208e-tee {what} is {claimed:g} on the data sheet and {STEP.name} carries "
                f"{actual:.4f} — a line laid to this figure is laid to a fitting that is not "
                f"there.")


def main():
    part = build_jg_pp0208e_tee()
    bb = part.val().BoundingBox()
    print("John Guest PP0208E — 1/4\" push-to-connect union tee, black polypropylene")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Run {RUN_SPAN:g} face to face, {REACH:g} to each of the three faces; "
          f"collar Ø{COLLAR_D:g}, bore Ø{BORE_D:g}")
    print(f"  {INSERTION:g} mm of Ø{TUBE_OD:g} tube in each port")
    for name, (pos, axis) in stations().items():
        print(f"  {name:>6}: ({pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f})  out {axis}")
    print(f"  Solid valid: {part.val().isValid()}")
    export_assembly(one_body(part, "jg-pp0208e-tee", M_JG_BLACK_PP), str(STEP))
    print(f"-> {STEP.name}")
    stations_hold()


if __name__ == "__main__":
    main()
