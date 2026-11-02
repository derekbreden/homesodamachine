"""Standalone drilling jaws for the candidate water-inlet jet cap stock.

The base lies on the drill table, Z=0. A rod stands on its 8 mm floor. Two
horizontal C-clamps close the loose jaw against the fixed jaw; two more hold
the base flanges to the owned wood backer and drill table. The grooves are
vertical and open at the top. There is no printed drill bushing.

The nominal stock diameter comes from the candidate jet dimensions. Physical
stock fit, printed grip, clamp clearance and spindle alignment are untested.
This bench fixture is not part of the machine assembly or its BOM.

Run with tools/cad-venv/bin/python. No argument exports both print parts;
`selftest` checks geometry without writing files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path



_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "cold-core-layout", _repo / "tools"):
    sys.path.insert(0, str(_path))

from _water_inlet_jet import JET_CAP_D, JET_PASSAGE_D  # noqa: E402
from docgen import substitute_md  # noqa: E402


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


def _native():
    if "cq" in globals():
        return
    import cadquery as cq
    from _cadq_export import export_assembly, note_write
    from _material_base import M_PETGF_BLACK, one_body
    globals().update(cq=cq, export_assembly=export_assembly, note_write=note_write,
                     M_PETGF_BLACK=M_PETGF_BLACK, one_body=one_body)


def __getattr__(name):
    if name not in {"cq", "export_assembly", "note_write", "M_PETGF_BLACK", "one_body"}:
        raise AttributeError(name)
    _native()
    return globals()[name]


ROD_D = JET_CAP_D
GROOVE_RADIAL_SLIP = 0.15
GROOVE_R = ROD_D / 2.0 + GROOVE_RADIAL_SLIP
OPEN_JAW_GAP = 1.0
BASE_X = 120.0
BASE_Y = 90.0
BASE_T = 8.0
JAW_X = 64.0
JAW_DEPTH = 25.0
GRIP_Z = 30.0
HANDLING_BLANK_L = 50.0
MIN_HANDLING_BLANK_L = 40.0
JAW_CLAMP_X = 20.0
BASE_CLAMP_X = 46.0
MESH_TOLERANCE = 0.02
MESH_ANGLE = 0.15


def _box(x0, x1, y0, y1, z0, z1):
    _native()
    return cq.Workplane(obj=cq.Solid.makeBox(
        x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0)
    ))


def _groove():
    _native()
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        GROOVE_R, GRIP_Z + 2.0,
        cq.Vector(0, 0, BASE_T - 1.0), cq.Vector(0, 0, 1)
    ))


def build_fixed():
    floor = _box(-BASE_X / 2, BASE_X / 2, -BASE_Y / 2, BASE_Y / 2, 0, BASE_T)
    jaw = _box(-JAW_X / 2, JAW_X / 2,
               OPEN_JAW_GAP / 2, OPEN_JAW_GAP / 2 + JAW_DEPTH,
               BASE_T, BASE_T + GRIP_Z).cut(_groove())
    return floor.union(jaw)


def build_loose_in_use():
    return _box(-JAW_X / 2, JAW_X / 2,
                -OPEN_JAW_GAP / 2 - JAW_DEPTH, -OPEN_JAW_GAP / 2,
                BASE_T, BASE_T + GRIP_Z).cut(_groove())


def build_loose_print():
    return build_loose_in_use().translate((0, 0, -BASE_T))


def _volume(shape):
    return sum(s.Volume() for s in shape.solids().vals())


def _single_valid(name, shape):
    solids = shape.solids().vals()
    if len(solids) != 1 or not solids[0].isValid() or solids[0].Volume() <= 0:
        raise ValueError(f"{name}: expected one valid, positive-volume solid")
    return solids[0]


def selftest():
    _native()
    fixed = build_fixed()
    loose = build_loose_in_use()
    _single_valid("fixed jaw and base", fixed)
    _single_valid("loose jaw", loose)

    # These are analytic fit checks, not a claim about printed tolerances or friction.
    # Translating the loose jaw by 2R-D brings its groove and the fixed groove into
    # opposed tangent contact with this diameter, leaving a positive split gap.
    fit_readings = []
    for diameter in (ROD_D - 0.1, ROD_D, ROD_D + 0.1):
        closure = 2 * GROOVE_R - diameter
        residual_gap = OPEN_JAW_GAP - closure
        if closure <= 0 or residual_gap <= 0:
            raise ValueError("candidate stock range exhausts jaw travel")
        fit_readings.append({"rod_d_mm": diameter, "closure_mm": closure,
                             "remaining_split_mm": residual_gap})

    # The drilling path ends in the stock, well above the plastic. It never guides
    # off a printed hole. Chuck and real clamp envelopes remain a physical setup check.
    drill_path = cq.Workplane(obj=cq.Solid.makeCylinder(
        JET_PASSAGE_D / 2, 15.0,
        cq.Vector(0, GROOVE_RADIAL_SLIP, BASE_T + MIN_HANDLING_BLANK_L - 4.0),
        cq.Vector(0, 0, 1)
    ))
    if _volume(fixed.intersect(drill_path)) + _volume(loose.intersect(drill_path)) > 1e-6:
        raise ValueError("drilling path reaches a printed jaw")

    for name, part, dims in (
        ("fixed", fixed, (BASE_X, BASE_Y, BASE_T + GRIP_Z)),
        ("loose", build_loose_print(), (JAW_X, JAW_DEPTH, GRIP_Z)),
    ):
        bb = part.val().BoundingBox()
        if any(abs(a - b) > 1e-6 for a, b in zip((bb.xlen, bb.ylen, bb.zlen), dims)):
            raise ValueError(f"{name}: unexpected print envelope")

    print(json.dumps({"status": "CAD checks passed; physical grip and setup untested",
                      "fit": fit_readings}, indent=2))
    return fixed, build_loose_print()


def _export_print(name, part, output=None):
    _native()
    stem = f"water-inlet-jet-fixture-{name}"
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    stl = out / f"{stem}.stl"
    step = out / f"{stem}.step"
    # A sibling slicer mesh keeps this isolated shop fixture out of viewer payloads.
    cq.exporters.export(part, str(stl), tolerance=MESH_TOLERANCE, angularTolerance=MESH_ANGLE)
    note_write(stl)
    export_assembly(one_body(part, stem, M_PETGF_BLACK), str(step))
    print(f"-> {step.name}, {stl.name}: {_volume(part) / 1000:.2f} cm³")


def _native_main(output=None):
    fixed, loose = selftest()
    _export_print("fixed", fixed, output)
    _export_print("loose", loose, output)
    _document()



def numbers():
    """Existing drill jaws in their separate upright print frames."""
    import _rust_part
    _rust_part.start()
    from _material_base import M_PETGF_BLACK
    from _materials import linear
    return {"base": [BASE_X, BASE_Y, BASE_T],
            "jaw": [JAW_X, JAW_DEPTH, GRIP_Z],
            "gap": OPEN_JAW_GAP, "groove_radius": GROOVE_R,
            "stock_diameter": ROD_D, "radial_slip": GROOVE_RADIAL_SLIP,
            "minimum_blank": MIN_HANDLING_BLANK_L, "drill_diameter": JET_PASSAGE_D,
            "color": list(linear(M_PETGF_BLACK))}


def _document():
    substitute_md(_here.parent / "README.md", variables={
        "JET_FIXTURE_BASE": f"{BASE_X:g} × {BASE_Y:g} × {BASE_T:g} mm",
        "JET_FIXTURE_GRIP": f"{GRIP_Z:g} mm",
        "JET_FIXTURE_GROOVE": f"{2 * GROOVE_R:g} mm",
        "JET_FIXTURE_GAP": f"{OPEN_JAW_GAP:g} mm",
        "JET_FIXTURE_BLANK": f"{HANDLING_BLANK_L:g} mm",
        "JET_FIXTURE_MIN_BLANK": f"{MIN_HANDLING_BLANK_L:g} mm",
        "JET_FIXTURE_JAW_CLAMP_X": f"±{JAW_CLAMP_X:g} mm",
        "JET_FIXTURE_BASE_CLAMP_X": f"±{BASE_CLAMP_X:g} mm",
    })



def main(output=None, native=False):
    if native:
        return _native_main(output)
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut("tooling", "water-inlet-jet-fixture", numbers(), out)
    _document()
    print(f"-> water inlet jet fixture: {len(result['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=["selftest"])
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    if options.command == "selftest":
        selftest()
    else:
        main(options.output, options.native)
