"""3/8" female-flare swivel × 1/4" push-to-connect adapter — the single fitting
that turns the ASSE 1022's 3/8" male-flare outlet straight onto 1/4" LLDPE, so
the water path leaves the backflow preventer at 1/4" OD and never carries 3/8"
tubing on toward the pump ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2).
It is what lets the ASSE feed the 1/4" split (V-K + V-A) directly; the earlier
design ran an FFL38BARB38 + 3/8" silicone hose to a 3/8" tap tee here.

External envelope only — a chrome-plated brass swivel nut (a wrench hex that
spins on the body and never touches water; flat-faced flare seal, no tape, the
nut draws the ASSE 1022's flare nose against the seat) and a 1/4" PTC collet
body the LLDPE pushes into. The physical part is a flare-to-push-connect adapter,
or equivalently a 3/8" FFL × 1/4" MNPT brass flare adapter carrying a John Guest
1/4" female push-fit — sourcing in [`ledger/bom.md`](/hardware/ledger/bom.md) §3.

Frame: +X = flow axis, the swivel-nut face at X = 0 — it lands flat on the ASSE
1022's outlet face, so the two mate at that plane. The PTC collet mouth is at +X.
Centered on Y and Z. Overall length matches the FFL38BARB38 it replaces, so the
chain's downstream terminal keeps its place.

Run:
    tools/cad-venv/bin/python hardware/reference/flare38-14ptc/flare38_14ptc.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

NUT_ACROSS_CORNERS = 22.0   # 3/4" swivel nut hex, on the ASSE's 3/8" flare thread
NUT_LENGTH = 14.0           # nut body along the flow axis — the flare it draws up
NUT_BORE_D = 15.88          # 3/8" flare thread major Ø — bored, so the ASSE 1022's
                            # flare nose occupies the nut rather than its metal
NECK_D = 13.0               # body between the nut and the collet
NECK_LENGTH = 9.0
COLLET_D = 14.0             # 1/4" PTC collet body OD
COLLET_LENGTH = 13.5        # push-in cartridge + release collar
TUBE_D = 6.35              # the 1/4" OD LLDPE it accepts
LENGTH = NUT_LENGTH + NECK_LENGTH + COLLET_LENGTH


def flare_face():
    """The swivel nut's seating face: (position, outward axis). Lands flat on the
    ASSE 1022's flare outlet, so this face and that one are the same plane."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def tube_port():
    """The 1/4" PTC mouth the LLDPE pushes into: (position, outward axis)."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build():
    """Swivel nut (X = 0, at the flare) → neck → 1/4" PTC collet (+X)."""
    nut = cq.Workplane("YZ").polygon(6, NUT_ACROSS_CORNERS).extrude(NUT_LENGTH).val()
    nut = nut.cut(cq.Solid.makeCylinder(
        NUT_BORE_D / 2.0, NUT_LENGTH, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0)))
    neck = cq.Solid.makeCylinder(
        NECK_D / 2.0, NECK_LENGTH, cq.Vector(NUT_LENGTH, 0, 0), cq.Vector(1, 0, 0))
    collet = cq.Solid.makeCylinder(
        COLLET_D / 2.0, COLLET_LENGTH,
        cq.Vector(NUT_LENGTH + NECK_LENGTH, 0, 0), cq.Vector(1, 0, 0))
    return nut.fuse(neck).fuse(collet)


def main():
    part = build()
    bb = part.BoundingBox()
    print("3/8\" FFL × 1/4\" PTC adapter (ASSE 1022 outlet -> 1/4\" LLDPE)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Nut {NUT_ACROSS_CORNERS} across corners x {NUT_LENGTH:g}; "
          f"collet Ø{COLLET_D} x {COLLET_LENGTH:g}; total {LENGTH:g} mm")
    out = _here.parent / "flare38-14ptc.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
