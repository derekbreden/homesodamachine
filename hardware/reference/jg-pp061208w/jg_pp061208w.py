"""John Guest PP061208W reducer stem, 3/8" OD stem × 1/4" OD push-to-connect,
white polypropylene with a food-grade EPDM O-ring — the second half of the
tap-point branch adapter ([`ledger/bom.md`](/hardware/ledger/bom.md) §3). The
bare 3/8" stem plugs into the PP451223W's collet; the 1/4" collet carries the
branch on as 1/4" OD LLDPE to the flow regulator.

External envelope plus the wetted bore — a plain molded barrel, no wrench flats:
the stem, the shoulder ring the stem butts against, the barrel swelling out to
the mouth collar, and the collet standing proud of it in three steps. Inside,
one bore step: the 1/4" tube bore back to the tube stop, then the smaller
through bore running the length of the stem. That step is the reduction.

The stem is a tube surrogate — the mating fitting's collet teeth bite it and its
O-ring seals on it, so it is held to the tube tolerance and does not bottom out:
its shoulder lands on the mating collet mouth with the tip still short of the
mating tube stop. It stays free to rotate in that socket.

Frame: +X = flow axis, the 3/8" stem tip at X = 0 facing −X, so the stem enters a
socket lying at negative X and the part occupies positive X. Centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp061208w/jg_pp061208w.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

STEM_D = 9.53               # 3/8" OD, JG tube tolerance +0.001/-0.004" (JG tech spec)
STEM_LENGTH = 18.29         # JG 3/8" cavity F1 = 0.720", the length swallowed by the mating collet
STEM_TIP_CHAMFER = 0.6      # lead-in that starts the stem past the mating collet teeth

SHOULDER_D = 10.35          # the ring that lands on the mating collet mouth — wider than its bore
SHOULDER_CONE_LENGTH = 1.3
SHOULDER_LENGTH = 3.0
BARREL_D = 15.6             # the waist behind the mouth collar
BODY_CONE_LENGTH = 7.2      # shoulder ring out to the barrel
BODY_D = 17.3               # mouth collar, the widest part, carrying the NSF-51 marking
BARREL_CONE_LENGTH = 4.2    # barrel out to the mouth collar
MOUTH_COLLAR_LENGTH = 5.0

COLLET_NECK_D = 11.4        # collet barrel where it leaves the body face
COLLET_NECK_LENGTH = 1.7
COLLET_RIM_D = 12.4         # the release collar you push square to let the tube go
COLLET_RIM_LENGTH = 0.7
COLLET_TIP_D = 11.0         # the nose the rim chamfers back down to
COLLET_TIP_LENGTH = 1.0
COLLET_PROUD = COLLET_NECK_LENGTH + COLLET_RIM_LENGTH + COLLET_TIP_LENGTH

TUBE_BORE_D = 6.48          # JG 1/4" cavity ØC = 0.255", the bore the tube runs in
THROUGH_BORE_D = 5.84       # JG 1/4" cavity ØG = 0.230", the bore past the tube stop
TUBE_STOP_DEPTH = 14.10     # JG 1/4" cavity F1 = 0.555", body face to tube stop
TUBE_D = 6.35               # the 1/4" OD LLDPE the collet accepts

stem_to_shoulder_x = STEM_LENGTH + SHOULDER_CONE_LENGTH
shoulder_to_cone_x = stem_to_shoulder_x + SHOULDER_LENGTH
cone_to_barrel_x = shoulder_to_cone_x + BODY_CONE_LENGTH
barrel_to_collar_x = cone_to_barrel_x + BARREL_CONE_LENGTH
body_face_x = barrel_to_collar_x + MOUTH_COLLAR_LENGTH
LENGTH = body_face_x + COLLET_PROUD

tube_stop_x = body_face_x - TUBE_STOP_DEPTH

# How far the 1/4" tube travels past the collet mouth before it bottoms out.
TUBE_INSERTION_DEPTH = COLLET_PROUD + TUBE_STOP_DEPTH


def stem_tip():
    """The free tip of the 3/8" stem: (position, outward axis) — it enters the
    mating 3/8" collet from here, STEM_LENGTH deep, until the shoulder lands."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def tube_port():
    """The collet mouth the 1/4" OD tube pushes into: (position, outward axis) —
    it travels TUBE_INSERTION_DEPTH in to reach the tube stop."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build_stem():
    """The 3/8" stem along +X from the chamfered tip at X = 0."""
    lead = cq.Solid.makeCone(
        STEM_D / 2.0 - STEM_TIP_CHAMFER, STEM_D / 2.0, STEM_TIP_CHAMFER,
        cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))
    shank = cq.Solid.makeCylinder(
        STEM_D / 2.0, STEM_LENGTH - STEM_TIP_CHAMFER,
        cq.Vector(STEM_TIP_CHAMFER, 0, 0), cq.Vector(1, 0, 0))
    return lead.fuse(shank)


def build_body():
    """Shoulder ring → barrel → mouth collar, a plain molded barrel swelling
    from the stem to the body face in two cones."""
    shoulder_cone = cq.Solid.makeCone(
        STEM_D / 2.0, SHOULDER_D / 2.0, SHOULDER_CONE_LENGTH,
        cq.Vector(STEM_LENGTH, 0, 0), cq.Vector(1, 0, 0))
    shoulder = cq.Solid.makeCylinder(
        SHOULDER_D / 2.0, SHOULDER_LENGTH,
        cq.Vector(stem_to_shoulder_x, 0, 0), cq.Vector(1, 0, 0))
    body_cone = cq.Solid.makeCone(
        SHOULDER_D / 2.0, BARREL_D / 2.0, BODY_CONE_LENGTH,
        cq.Vector(shoulder_to_cone_x, 0, 0), cq.Vector(1, 0, 0))
    barrel_cone = cq.Solid.makeCone(
        BARREL_D / 2.0, BODY_D / 2.0, BARREL_CONE_LENGTH,
        cq.Vector(cone_to_barrel_x, 0, 0), cq.Vector(1, 0, 0))
    collar = cq.Solid.makeCylinder(
        BODY_D / 2.0, MOUTH_COLLAR_LENGTH,
        cq.Vector(barrel_to_collar_x, 0, 0), cq.Vector(1, 0, 0))
    return shoulder_cone.fuse(shoulder).fuse(body_cone).fuse(barrel_cone).fuse(collar)


def build_collet():
    """The stepped collet standing proud of the body face: barrel, release
    collar, then the nose chamfered back in toward the tube."""
    neck = cq.Solid.makeCylinder(
        COLLET_NECK_D / 2.0, COLLET_NECK_LENGTH,
        cq.Vector(body_face_x, 0, 0), cq.Vector(1, 0, 0))
    rim_x = body_face_x + COLLET_NECK_LENGTH
    rim = cq.Solid.makeCylinder(
        COLLET_RIM_D / 2.0, COLLET_RIM_LENGTH,
        cq.Vector(rim_x, 0, 0), cq.Vector(1, 0, 0))
    tip = cq.Solid.makeCone(
        COLLET_RIM_D / 2.0, COLLET_TIP_D / 2.0, COLLET_TIP_LENGTH,
        cq.Vector(rim_x + COLLET_RIM_LENGTH, 0, 0), cq.Vector(1, 0, 0))
    return neck.fuse(rim).fuse(tip)


def build_bore_cut():
    """The wetted path, stem tip to collet mouth: the through bore up the stem,
    then the 1/4" tube bore out to the collet. The step where the through bore
    opens out to the tube bore is the tube stop."""
    through = cq.Solid.makeCylinder(
        THROUGH_BORE_D / 2.0, tube_stop_x,
        cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))
    tube = cq.Solid.makeCylinder(
        TUBE_BORE_D / 2.0, LENGTH - tube_stop_x,
        cq.Vector(tube_stop_x, 0, 0), cq.Vector(1, 0, 0))
    return through.fuse(tube)


def build():
    return build_stem().fuse(build_body()).fuse(build_collet()).cut(build_bore_cut())


def main():
    part = build()
    bb = part.BoundingBox()
    print("John Guest PP061208W 3/8\" OD stem × 1/4\" PTC reducer stem")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Stem Ø{STEM_D} × {STEM_LENGTH:g}; shoulder Ø{SHOULDER_D}; "
          f"collar Ø{BODY_D}; collet proud {COLLET_PROUD:g}; total {LENGTH:g} mm")
    print(f"  Stem swallowed {STEM_LENGTH:g} mm by the mating 3/8\" collet; "
          f"1/4\" tube insertion depth {TUBE_INSERTION_DEPTH:.2f} mm "
          f"(tube stop at X = {tube_stop_x:.2f})")
    print(f"  Bore steps Ø{TUBE_BORE_D} (1/4\" end) → Ø{THROUGH_BORE_D} (stem)")
    for name, (pos, axis) in (("stem_tip", stem_tip()), ("tube_port", tube_port())):
        print(f"  {name}: at ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) "
              f"facing ({axis[0]:g}, {axis[1]:g}, {axis[2]:g})")
    print(f"  Solid valid: {part.isValid()}")
    out = _here.parent / "jg-pp061208w.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
