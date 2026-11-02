"""Scan-derived exterior of the received Multiplex 19-0897 ASSE 1022.

The coated MINI 2 capture establishes the wrench sections, turned shoulders,
port envelopes and radial vent. Threads use smooth crest envelopes; the
visible mouths have shallow display closures. Hidden checks, seals and vent
mechanism are not modeled. See README.md and scan-evidence.json.

Frame: +X = inlet to outlet, inlet rim at X=0; the vent points down, with its
tip at Z=0. The coaxial port center is (Y=0, Z=BODY_CENTER_Z). Dimensions are mm.


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'multiplex-asse1022.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'multiplex-asse1022.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'multiplex-asse1022.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

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
    import cadquery as cq
    outline = [(profile[0][0], 0), *profile, (profile[-1][0], 0)]
    return (cq.Workplane('XY').polyline(outline).close()
            .revolve(360, (0, 0), (1, 0)).val())


def _wrench(profile, across_flats, clock):
    import cadquery as cq
    vertices = [(across_flats / math.sqrt(3) * math.cos(math.radians(i * 60 + clock)),
                 across_flats / math.sqrt(3) * math.sin(math.radians(i * 60 + clock)))
                for i in range(6)]
    prism = (cq.Workplane('YZ', origin=(profile[0][0], 0, 0))
             .polyline(vertices).close().extrude(profile[-1][0] - profile[0][0]).val())
    return _turned(profile).intersect(prism)


def build():
    """Fitted turned and wrench surfaces, with the vent base and visible mouths."""
    import cadquery as cq
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
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    main()


def __getattr__(name):
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'M_BRASS', 'one_body'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
