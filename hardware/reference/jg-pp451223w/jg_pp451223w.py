"""John Guest PP451223W female adapter, 3/8" NPTF F × 3/8" OD push-to-connect,
white polypropylene with a food-grade EPDM O-ring — the tap-point branch adapter
([`ledger/bom.md`](/hardware/ledger/bom.md) §3). The NPTF socket threads onto the
MTB-0606WP barb tee's 3/8" MNPT branch; the collet takes the PP061208W reducer
stem, which carries the branch on as 1/4" OD LLDPE.

External envelope plus the wetted bore — a wrench hex, a waist, the collet
barrel, and the collet standing proud of it in three steps; inside, the NPTF
socket as a real 1:16 taper at pitch diameter (no helix), then the through bore,
then the tube bore out to the collet mouth. The step between those two bores is
the tube stop the pushed-in stem bottoms on.

Frame: +X = flow axis, the NPTF mouth at X = 0 facing −X, so a male thread enters
from −X and the part occupies positive X. Centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp451223w/jg_pp451223w.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

HEX_ACROSS_CORNERS = 25.67  # 7/8" hex (22.23 across flats), the size a 3/8" body takes
HEX_LENGTH = 12.0           # wrench flats, at the threaded end and the widest part
WAIST_D = 17.0              # the neck between hex and collet barrel
WAIST_LENGTH = 6.0
BODY_D = 19.7               # collet barrel — JG allows 20.07 (0.790") minimum port spacing at 3/8"
BODY_LENGTH = 14.0

COLLET_NECK_D = 13.6        # collet barrel where it leaves the body face
COLLET_NECK_LENGTH = 2.0
COLLET_RIM_D = 14.8         # the release collar you push square to let the tube go
COLLET_RIM_LENGTH = 0.8
COLLET_TIP_D = 13.2         # the nose the rim chamfers back down to
COLLET_TIP_LENGTH = 1.2
COLLET_PROUD = COLLET_NECK_LENGTH + COLLET_RIM_LENGTH + COLLET_TIP_LENGTH

THREAD_PITCH_D = 15.93      # 3/8-18 NPTF pitch Ø at the mouth (E1 = 0.62701", ASME B1.20.1)
THREAD_TAPER = 1.0 / 16.0   # NPTF taper, on diameter, per unit of depth
SOCKET_DEPTH = 11.5         # molded socket, deeper than the thread a male actually makes up
THREAD_ENGAGEMENT = 9.53    # 3/8 NPT total makeup, hand + wrench (3/8" — ASME B1.20.1 / Machinery's Handbook)

TUBE_BORE_D = 9.65          # JG 3/8" cavity ØC = 0.380", the bore the tube runs in
THROUGH_BORE_D = 8.89       # JG 3/8" cavity ØG = 0.350", the bore past the tube stop
TUBE_STOP_DEPTH = 18.29     # JG 3/8" cavity F1 = 0.720", body face to tube stop
TUBE_D = 9.53               # the 3/8" OD stem the collet accepts

hex_to_waist_x = HEX_LENGTH
waist_to_body_x = hex_to_waist_x + WAIST_LENGTH
body_face_x = waist_to_body_x + BODY_LENGTH
LENGTH = body_face_x + COLLET_PROUD

tube_stop_x = body_face_x - TUBE_STOP_DEPTH
socket_bottom_pitch_d = THREAD_PITCH_D - SOCKET_DEPTH * THREAD_TAPER

# How far the stem travels past the collet mouth before it bottoms out — the
# number that fixes where a mating stem's shoulder lands.
TUBE_INSERTION_DEPTH = COLLET_PROUD + TUBE_STOP_DEPTH


def thread_port():
    """The 3/8" NPTF female mouth: (position, outward axis) — a male thread
    enters here and makes up THREAD_ENGAGEMENT deep."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def tube_port():
    """The collet mouth the 3/8" OD tube or stem pushes into: (position, outward
    axis) — it travels TUBE_INSERTION_DEPTH in to reach the tube stop."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build_body():
    """Hex (X = 0, at the thread) → waist → collet barrel, along +X."""
    hex_sec = cq.Workplane("YZ").polygon(6, HEX_ACROSS_CORNERS).extrude(HEX_LENGTH).val()
    waist = cq.Solid.makeCylinder(
        WAIST_D / 2.0, WAIST_LENGTH,
        cq.Vector(hex_to_waist_x, 0, 0), cq.Vector(1, 0, 0))
    barrel = cq.Solid.makeCylinder(
        BODY_D / 2.0, BODY_LENGTH,
        cq.Vector(waist_to_body_x, 0, 0), cq.Vector(1, 0, 0))
    return hex_sec.fuse(waist).fuse(barrel)


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
    """The wetted path, mouth to collet: the NPTF socket as a 1:16 taper at
    pitch diameter, the through bore, then the tube bore. The step where the
    through bore opens out to the tube bore is the tube stop."""
    socket = cq.Solid.makeCone(
        THREAD_PITCH_D / 2.0, socket_bottom_pitch_d / 2.0, SOCKET_DEPTH,
        cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))
    through = cq.Solid.makeCylinder(
        THROUGH_BORE_D / 2.0, tube_stop_x - SOCKET_DEPTH,
        cq.Vector(SOCKET_DEPTH, 0, 0), cq.Vector(1, 0, 0))
    tube = cq.Solid.makeCylinder(
        TUBE_BORE_D / 2.0, LENGTH - tube_stop_x,
        cq.Vector(tube_stop_x, 0, 0), cq.Vector(1, 0, 0))
    return socket.fuse(through).fuse(tube)


def build():
    return build_body().fuse(build_collet()).cut(build_bore_cut())


def main():
    part = build()
    bb = part.BoundingBox()
    print("John Guest PP451223W 3/8\" NPTF F × 3/8\" PTC female adapter")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex {HEX_ACROSS_CORNERS} across corners × {HEX_LENGTH:g}; "
          f"barrel Ø{BODY_D} × {BODY_LENGTH:g}; collet proud {COLLET_PROUD:g}; "
          f"total {LENGTH:g} mm")
    print(f"  Thread engagement {THREAD_ENGAGEMENT:g} mm; "
          f"tube insertion depth {TUBE_INSERTION_DEPTH:.2f} mm "
          f"(tube stop at X = {tube_stop_x:.2f})")
    for name, (pos, axis) in (("thread_port", thread_port()), ("tube_port", tube_port())):
        print(f"  {name}: at ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) "
              f"facing ({axis[0]:g}, {axis[1]:g}, {axis[2]:g})")
    print(f"  Solid valid: {part.isValid()}")
    out = _here.parent / "jg-pp451223w.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
