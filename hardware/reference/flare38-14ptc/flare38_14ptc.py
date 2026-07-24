"""The ASSE 1022's outlet adapter — 3/8" female-flare swivel onto 1/4"
push-to-connect, so the water path leaves the backflow preventer at 1/4" OD and
carries no 3/8" tubing on toward the pump
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2). It is what
lets the ASSE feed the 1/4" split (V-K + V-A) directly.

Two John Guest fittings made up as one stack — no single-piece 3/8"-flare ×
1/4"-push adapter exists in a potable grade, in any material or brand
([`ledger/bom.md`](/hardware/ledger/bom.md) §3):

  * **PI4512F6S** — 3/8" FFL swivel × 3/8" PTC, gray acetal, lead-free. Its
    chrome swivel nut draws the ASSE 1022's flare nose against the seat (flat-
    faced flare seal, no PTFE tape); its 3/8" collet faces downstream.
  * **PP061208W** — 3/8" stem × 1/4" PTC reducer, pushed into that collet. The
    stem is the whole 3/8" run: it starts and ends inside the fitting, and the
    LLDPE leaves at 1/4".

External envelope only — the swivel nut is a wrench hex that spins on the body
and never touches water, and both collets are plain cylinders at the cartridge
OD.

Frame: +X = flow axis, the swivel-nut face at X = 0 — it lands flat on the ASSE
1022's outlet face, so the two mate at that plane. The 1/4" PTC collet mouth is
at +X. Centered on Y and Z.

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

# --- PI4512F6S, 3/8" FFL swivel x 3/8" PTC -------------------------------
NUT_ACROSS_CORNERS = 22.0   # 3/4" swivel nut hex, on the ASSE's 3/8" flare thread
NUT_LENGTH = 14.0           # nut body along the flow axis — the flare it draws up
NUT_BORE_D = 15.88          # 3/8" flare thread major Ø — bored, so the ASSE 1022's
                            # flare nose occupies the nut rather than its metal
NECK_D, NECK_LENGTH = 14.0, 8.0          # body between the nut and the 3/8" collet
COLLET38_D, COLLET38_LENGTH = 17.5, 15.5  # 3/8" PTC cartridge + release collar

# --- PP061208W, 3/8" stem x 1/4" PTC reducer -----------------------------
# The stem itself is buried in the collet above; what stands proud is its collar
# and the 1/4" collet body.
COLLAR_LENGTH = 2.0
COLLET14_D, COLLET14_LENGTH = 14.0, 13.5  # 1/4" PTC cartridge + release collar

TUBE_D = 6.35              # the 1/4" OD LLDPE it accepts
LENGTH = (NUT_LENGTH + NECK_LENGTH + COLLET38_LENGTH
          + COLLAR_LENGTH + COLLET14_LENGTH)


def flare_face():
    """The swivel nut's seating face: (position, outward axis). Lands flat on the
    ASSE 1022's flare outlet, so this face and that one are the same plane."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def tube_port():
    """The 1/4" PTC mouth the LLDPE pushes into: (position, outward axis)."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build():
    """Swivel nut (X = 0, at the flare) → neck → 3/8" collet → the reducer's
    collar → 1/4" PTC collet (+X)."""
    nut = cq.Workplane("YZ").polygon(6, NUT_ACROSS_CORNERS).extrude(NUT_LENGTH).val()
    nut = nut.cut(cq.Solid.makeCylinder(
        NUT_BORE_D / 2.0, NUT_LENGTH, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0)))
    part, x = nut, NUT_LENGTH
    for dia, length in ((NECK_D, NECK_LENGTH),
                        (COLLET38_D, COLLET38_LENGTH),
                        (COLLET38_D, COLLAR_LENGTH),
                        (COLLET14_D, COLLET14_LENGTH)):
        part = part.fuse(cq.Solid.makeCylinder(
            dia / 2.0, length, cq.Vector(x, 0, 0), cq.Vector(1, 0, 0)))
        x += length
    return part


def main():
    part = build()
    bb = part.BoundingBox()
    print("ASSE 1022 outlet adapter — 3/8\" FFL x 1/4\" PTC (PI4512F6S + PP061208W)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Nut {NUT_ACROSS_CORNERS} across corners x {NUT_LENGTH:g}; "
          f"3/8\" collet Ø{COLLET38_D} x {COLLET38_LENGTH:g}; "
          f"1/4\" collet Ø{COLLET14_D} x {COLLET14_LENGTH:g}; total {LENGTH:g} mm")
    out = _here.parent / "flare38-14ptc.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
