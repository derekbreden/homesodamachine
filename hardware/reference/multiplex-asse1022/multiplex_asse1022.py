"""Scan-derived exterior of the received Multiplex 19-0897 ASSE 1022.

The coated MINI 2 capture establishes the wrench sections, turned shoulders,
port envelopes and radial vent. Threads use smooth crest envelopes; the
visible mouths have shallow display closures. Hidden checks, seals and vent
mechanism are not modeled. See README.md and scan-evidence.json.

Frame: +X = inlet to outlet, inlet rim at X=0; the vent points down, with its
tip at Z=0. The coaxial port center is (Y=0, Z=BODY_CENTER_Z). Dimensions are mm.
"""

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly
from _materials import M_BRASS, one_body

TOTAL_LENGTH = 65.05
INLET_LENGTH = 12.70       # Observed tip to collar shoulder, not sealing engagement.
FLARE_LENGTH = 15.85       # Observed shoulder to flare nose.
BARREL_LENGTH = TOTAL_LENGTH - INLET_LENGTH - FLARE_LENGTH
BODY_CENTER_Z = 27.45
HEX_ACROSS_FLATS = 28.65
CAP_ACROSS_FLATS = 28.73
HEX_ACROSS_CORNERS = 33.10  # Maximum occupied corner diameter, including the outlet cap.
BODY_UNDERSIDE_Z = BODY_CENTER_Z - HEX_ACROSS_FLATS / 2.0
VENT_X = 24.65
VENT_Y = .07
VENT_D = 7.70              # Maximum exposed stem-root envelope; not a sealing-fit bore.
VENT_DROP = BODY_UNDERSIDE_Z
VENT_INTO_BODY = .40
INLET_THREAD_D = 17.70     # Coated crest envelope at the root.
FLARE_THREAD_D = 15.80

# (X, radius), measured from the inlet rim. Rounds use short conical sections.
INLET_PROFILE = ((0., 6.60), (.4, 7.25), (1.0, 7.85), (1.6, 8.40),
                 (11.7, 8.75), (INLET_LENGTH, INLET_THREAD_D / 2))
COLLAR_PROFILE = ((12.70, 11.65), (13.0, 12.20), (13.4, 12.60),
                  (14.0, 12.90), (17.4, 12.90), (17.65, 13.0), (17.80, 13.45))
BODY_PROFILE = ((17.75, 12.95), (17.80, 14.70), (18.0, 15.80),
                (18.3, 16.17), (30.8, 16.17), (31.15, 16.10),
                (31.45, 15.60), (31.65, 14.50), (31.90, 14.20),
                (36.10, 14.22))
CAP_PROFILE = ((36.10, 14.22), (36.40, 14.40), (36.80, 15.00),
               (37.30, 15.90), (37.70, 16.55), (47.65, 16.55),
               (48.0, 16.30), (48.4, 15.70), (48.9, 14.90), (49.20, 14.30))
FLARE_PROFILE = ((49.20, 8.65), (49.5, 8.15), (49.9, FLARE_THREAD_D / 2),
                 (58.5, FLARE_THREAD_D / 2), (59.1, 7.40), (59.7, 6.90),
                 (62.40, 6.90), (TOTAL_LENGTH, 4.25))
# (Z, radius), tip first. The stem's measured smooth band fits Ø6.93 mm.
VENT_PROFILE = ((0., 2.85), (.25, 3.20), (.6, 3.40), (1.3, 3.50),
                (2.4, 3.50), (3.1, 3.42), (4.2, 3.55), (5.4, 3.40),
                (6.5, 3.45), (7.5, 3.60), (8.4, 3.75), (8.95, VENT_D / 2))


def inlet():
    """The 3/8-inch NPT male inlet rim: (position, outward axis)."""
    return (0.0, 0.0, BODY_CENTER_Z), (-1.0, 0.0, 0.0)


def outlet():
    """The 3/8-inch SAE 45-degree male flare nose: (position, outward axis)."""
    return (TOTAL_LENGTH, 0.0, BODY_CENTER_Z), (1.0, 0.0, 0.0)


def vent():
    """The atmospheric-vent barb tip: (position, outward axis). The vent stub
    slips on here, and the drip leaves its far end."""
    return (VENT_X, VENT_Y, 0.0), (0.0, 0.0, -1.0)


def _turned(profile):
    outline = [(profile[0][0], 0), *profile, (profile[-1][0], 0)]
    return (cq.Workplane('XY').polyline(outline).close()
            .revolve(360, (0, 0), (1, 0)).val())


def _wrench(profile, across_flats, clock):
    vertices = [(across_flats / math.sqrt(3) * math.cos(math.radians(i * 60 + clock)),
                 across_flats / math.sqrt(3) * math.sin(math.radians(i * 60 + clock)))
                for i in range(6)]
    prism = (cq.Workplane('YZ', origin=(profile[0][0], 0, 0))
             .polyline(vertices).close().extrude(profile[-1][0] - profile[0][0]).val())
    return _turned(profile).intersect(prism)


def build():
    """Fitted turned and wrench surfaces, with the vent base and visible mouths."""
    body = _turned(INLET_PROFILE).fuse(_turned(COLLAR_PROFILE))
    body = body.fuse(_wrench(BODY_PROFILE, HEX_ACROSS_FLATS, .3))
    body = body.fuse(_wrench(CAP_PROFILE, CAP_ACROSS_FLATS, .9))
    body = body.fuse(_turned(FLARE_PROFILE))
    # Only entry surfaces are represented. Blind floors are unobserved display closures.
    inlet_mouth = _turned(((-.1, 5.60), (.4, 5.45), (6.0, 5.45)))
    outlet_mouth = _turned(((TOTAL_LENGTH - 8., 3.60), (TOTAL_LENGTH + .1, 3.60)))
    body = body.cut(inlet_mouth).cut(outlet_mouth).translate((0, 0, BODY_CENTER_Z))

    stem = _turned(VENT_PROFILE).rotate((0, 0, 0), (0, 1, 0), -90)
    base = (cq.Workplane('XY', origin=(0, 0, 8.95)).polygon(6, 11.2 / math.cos(math.pi / 6))
            .workplane(offset=BODY_UNDERSIDE_Z + VENT_INTO_BODY - 8.95)
            .polygon(6, 10.9 / math.cos(math.pi / 6)).loft().val()
            .rotate((0, 0, 0), (0, 0, 1), -21))
    blank = cq.Solid.makeCylinder(6.25, 5., cq.Vector(0, 0, 8.8))
    base = base.intersect(blank)
    vent_mouth = cq.Solid.makeCylinder(2.0, 3.6, cq.Vector(0, 0, -.1))
    vent_shape = stem.fuse(base).cut(vent_mouth).translate((VENT_X, VENT_Y, 0))
    return body.fuse(vent_shape).clean()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', type=Path, help='Also export the fitted exterior as STL at this path.')
    args = parser.parse_args()
    part = build()
    bb = part.BoundingBox()
    print("Multiplex 19-0897 ASSE 1022 backflow preventer")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Wrench flats: body {HEX_ACROSS_FLATS:g}, cap {CAP_ACROSS_FLATS:g} mm")
    print(f"  Vent at ({VENT_X:g}, {VENT_Y:g}, 0); axis height {BODY_CENTER_Z:g} mm")
    out = _here.parent / "multiplex-asse1022.step"
    export_assembly(one_body(part, "multiplex-asse1022", M_BRASS), str(out))
    if args.stl:
        cq.exporters.export(part, str(args.stl), tolerance=.025, angularTolerance=.08)
        print(f'-> {args.stl}')
    print(f"-> {out}")


if __name__ == "__main__":
    main()
