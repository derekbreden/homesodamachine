"""brewhardware FFL38BARB38 swivel flare adapter, 3/8" female flare × 3/8" OD
hose barb — the single piece that turns the ASSE 1022's male flare outlet into a
barb for the JoyTube silicone hose running to the SeaFlo pump suction
([`ledger/bom.md`](/hardware/ledger/bom.md) §3).

External envelope only — a chrome-plated brass swivel nut (a wrench hex, which
spins on the barb stem and never touches water) and a 304 SS barb stem with its
ridges as stacked cones. The flare seal is flat-faced, so no tape: the nut pulls
the ASSE 1022's flare nose against the adapter's seat.

Frame: +X = flow axis, the swivel-nut face at X = 0 — it lands flat on the ASSE
1022's outlet face, so the two mate at that plane. Centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/ffl38barb38/ffl38barb38.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

NUT_ACROSS_CORNERS = 22.0   # 3/4" swivel nut hex (19.05 across flats)
NUT_LENGTH = 14.0           # nut body along the flow axis — the flare it draws up
NUT_BORE_D = 15.88          # 3/8" flare thread major Ø — bored through, so the ASSE
                            # 1022's flare nose occupies the nut rather than its metal
STEM_D = 11.0               # barb stem shoulder Ø, between nut and ridges
STEM_LENGTH = 6.0
BARB_D = 9.53               # 3/8" hose barb ridge Ø
BARB_ROOT_D = 7.9           # between ridges
BARB_RIDGES = 3
RIDGE_PITCH = 5.5
HOSE_ID = 9.53              # the 3/8" ID silicone hose it takes
LENGTH = NUT_LENGTH + STEM_LENGTH + BARB_RIDGES * RIDGE_PITCH


def flare_face():
    """The swivel nut's seating face: (position, outward axis). It lands flat on
    the ASSE 1022's flare outlet, so this face and that one are the same plane."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def barb_tip():
    """The barb tip the silicone hose slips over: (position, outward axis)."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build():
    """Swivel nut (X = 0, at the flare) → stem → barb ridges (+X). Each ridge is a
    cone rising from the root Ø to the ridge Ø, the shape the hose ratchets over."""
    nut = cq.Workplane("YZ").polygon(6, NUT_ACROSS_CORNERS).extrude(NUT_LENGTH).val()
    nut = nut.cut(cq.Solid.makeCylinder(
        NUT_BORE_D / 2.0, NUT_LENGTH, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0)))
    stem = cq.Solid.makeCylinder(
        STEM_D / 2.0, STEM_LENGTH, cq.Vector(NUT_LENGTH, 0, 0), cq.Vector(1, 0, 0))
    part = nut.fuse(stem)
    x = NUT_LENGTH + STEM_LENGTH
    for _ in range(BARB_RIDGES):
        part = part.fuse(cq.Solid.makeCone(
            BARB_ROOT_D / 2.0, BARB_D / 2.0, RIDGE_PITCH,
            cq.Vector(x, 0, 0), cq.Vector(1, 0, 0)))
        x += RIDGE_PITCH
    return part


def main():
    part = build()
    bb = part.BoundingBox()
    print("brewhardware FFL38BARB38 3/8\" FFL × 3/8\" hose-barb adapter")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Nut {NUT_ACROSS_CORNERS} across corners × {NUT_LENGTH:g}; "
          f"{BARB_RIDGES} ridges Ø{BARB_D} at {RIDGE_PITCH:g} pitch; total {LENGTH:g} mm")
    out = _here.parent / "ffl38barb38.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
