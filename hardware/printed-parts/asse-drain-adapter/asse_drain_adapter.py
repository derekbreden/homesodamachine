"""TPU 85A sleeve: ASSE atmospheric-vent barb to 4 mm OD LLDPE.

Print upright, large socket on the bed. The two sockets have independent
zip-tie lands. The smooth internal reducer rises 60 degrees above the bed
into the tube bore. Tube depth is marked at assembly. Dimensions are an
unprinted fit candidate.
The 6.10 mm socket is based on the specified 1/4-inch hose size, not a
measurement of the barb crests. The reference's 8 mm cylinder is an envelope.
"""
from pathlib import Path
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "reference/multiplex-asse1022"))
from _cadq_export import export_assembly
from _material_base import M_TPU_BLACK, one_body
import multiplex_asse1022 as bfp

BARB_BORE = 6.10
BARB_DEPTH = 12.8
TUBE_BORE = 3.80
TUBE_DEPTH = 14.0
TAPER_ANGLE = 60.0  # Degrees above the print bed.
REDUCER_LENGTH = (BARB_BORE - TUBE_BORE) / 2 * math.tan(math.radians(TAPER_ANGLE))
TUBE_START = BARB_DEPTH + REDUCER_LENGTH
LENGTH = TUBE_START + TUBE_DEPTH
MIN_WALL = 3.45  # Shared relaxed radial minimum at both ties and socket mouths.
GROOVE_DEPTH = .50
BARB_OD = BARB_BORE + 2 * (MIN_WALL + GROOVE_DEPTH)
TUBE_OD = TUBE_BORE + 2 * (MIN_WALL + GROOVE_DEPTH)
OUTER_REDUCER_START = TUBE_START - (BARB_OD - TUBE_OD) / 2 * math.tan(math.radians(TAPER_ANGLE))
ENTRY = .40
ENTRY_HEIGHT = ENTRY * math.tan(math.radians(TAPER_ANGLE))
MOUTH_BEVEL = GROOVE_DEPTH - ENTRY
MOUTH_BEVEL_HEIGHT = 2 * MOUTH_BEVEL  # 63.4 degrees above the bed.
GROOVE_FLAT = 2.80  # Existing 0.1-inch / 2.54 mm-wide four-inch ties.
GROOVE_RAMP = 1.0  # At most .5 mm radial growth / mm build rise.
BARB_TIE_Z = 5.5
TUBE_TIE_Z = LENGTH - 6.0
BODY_CLEARANCE = .50
INSTALLED_REACH = bfp.BODY_UNDERSIDE_Z - BODY_CLEARANCE


def _revolve(profile):
    return (cq.Workplane("XZ").polyline(profile).close()
            .revolve(360, (0, 0), (0, 1)).val())


def build(*, installed=False):
    """Relaxed printable solid, or a conservative expanded occupied envelope.

    The installed view opens sockets to the reference barb envelope and tube
    OD, and increases outside radii by conserving annular section area. This
    is placement geometry, not an elastomer deformation or sealing model.
    """
    barb_d = bfp.VENT_D if installed else BARB_BORE
    tube_d = 4.0 if installed else TUBE_BORE
    barb_od = math.sqrt(BARB_OD**2 + barb_d**2 - BARB_BORE**2)
    tube_od = math.sqrt(TUBE_OD**2 + tube_d**2 - TUBE_BORE**2)
    rb, rt = barb_od / 2, tube_od / 2
    outer = _revolve([
        (0, 0), (rb - MOUTH_BEVEL, 0), (rb, MOUTH_BEVEL_HEIGHT),
        (rb, OUTER_REDUCER_START), (rt, TUBE_START),
        (rt, LENGTH - MOUTH_BEVEL_HEIGHT), (rt - MOUTH_BEVEL, LENGTH), (0, LENGTH),
    ])
    bore = _revolve([
        (0, -.1), (barb_d / 2 + ENTRY, -.1),
        (barb_d / 2 + ENTRY, 0), (barb_d / 2, ENTRY_HEIGHT),
        (barb_d / 2, BARB_DEPTH), (tube_d / 2, TUBE_START),
        (tube_d / 2, LENGTH - ENTRY_HEIGHT),
        (tube_d / 2 + ENTRY, LENGTH),
        (tube_d / 2 + ENTRY, LENGTH + .1), (0, LENGTH + .1),
    ])
    body = outer.cut(bore)
    for centre, radius in ((BARB_TIE_Z, rb), (TUBE_TIE_Z, rt)):
        lo, hi = centre - GROOVE_FLAT / 2, centre + GROOVE_FLAT / 2
        tool = _revolve([
            (radius, lo - GROOVE_RAMP), (radius - GROOVE_DEPTH, lo),
            (radius - GROOVE_DEPTH, hi), (radius, hi + GROOVE_RAMP),
            (radius + 1, hi + GROOVE_RAMP), (radius + 1, lo - GROOVE_RAMP),
        ])
        body = body.cut(tool)
    return body.clean()


def placed(vent_tip):
    """Large mouth up, clear of the body; small mouth points straight down."""
    x, y, z = vent_tip
    return (build(installed=True).rotate((0, 0, 0), (1, 0, 0), 180)
            .translate((x, y, z + INSTALLED_REACH)))


def tube_mouth(vent_tip):
    x, y, z = vent_tip
    return (x, y, z + INSTALLED_REACH - LENGTH)


def main():
    shape = build()
    stl = HERE / "asse-drain-adapter.stl"
    step = HERE / "asse-drain-adapter.step"
    cq.exporters.export(shape, str(stl), tolerance=.025, angularTolerance=.08)
    export_assembly(one_body(shape, "asse-drain-adapter", M_TPU_BLACK), str(step))
    import flute_payload
    flute_payload.cut(step, stl, preserve_print_triangles=True)
    sys.path.insert(0, str(HARDWARE.parent / "tools"))
    from docgen import substitute_md
    substitute_md(HERE / "README.md", variables={
        "BARB_BORE": f"{BARB_BORE:.2f}", "BARB_DEPTH": f"{BARB_DEPTH:g}",
        "TUBE_BORE": f"{TUBE_BORE:.2f}", "TUBE_DEPTH": f"{TUBE_DEPTH:g}",
        "TAPER_ANGLE": f"{TAPER_ANGLE:g}", "LENGTH": f"{LENGTH:.2f}",
        "BARB_OD": f"{BARB_OD:g}", "TUBE_OD": f"{TUBE_OD:g}",
        "MIN_WALL": f"{MIN_WALL:.2f}",
        "VOLUME": f"{shape.Volume()/1000:.3f}",
    })
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh; {shape.Volume()/1000:.3f} cm3")


if __name__ == "__main__":
    main()
