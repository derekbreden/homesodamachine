"""Test receiver and test cradle for the funnel's elbow cradle snap.

The receiver is the production funnel frame cut down to the block round its plug socket: the
3 mm web with the drain hole and both wing slots, and the socket's walls to 12 mm above the
frame's underside. The cradle is the production elbow cradle. Both print as the production parts
do, on the face that stands lowest in the machine.
"""

import json
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_funnel = _here.parents[1]
_hw = next(p for p in _here.parents if p.name == "hardware")
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
for _p in (_funnel, _hw / "scripts", _tools):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import elbow_cradle as EC                                      # noqa: E402
import funnel as FUN                                           # noqa: E402
import funnel_frame as FF                                      # noqa: E402
from OCP.BRepExtrema import BRepExtrema_DistShapeShape         # noqa: E402

RECEIVER_H = 12.0      # receiver block height above the frame's underside
RECEIVER_RIM = 6.0     # stock beyond the socket's widest X
RECEIVER_HALF_Y = 27.0  # inside the frame's flat-underside run, Y155..Y210 about the hole


def _gap(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


def build():
    """`(receiver, cradle, elbow)` in the hole's local frame: origin on the hole's axis in the
    frame's underside, +Z up."""
    floor, _plug, _rail = FF.datums()
    hole = cq.Vector(FUN.neck_dx, FF.center_y + FUN.neck_dy, floor)
    half_x = FF.socket_width / 2 + RECEIVER_RIM
    keep = cq.Solid.makeBox(2 * half_x, 2 * RECEIVER_HALF_Y, RECEIVER_H,
                            cq.Vector(hole.x - half_x, hole.y - RECEIVER_HALF_Y, floor))
    receiver = FF.build().intersect(keep).translate(-hole).clean()
    assert receiver.isValid() and len(receiver.Solids()) == 1
    elbow = cq.Compound.makeCompound(list(EC.elbow_parts().values()))
    return receiver, EC.build(), elbow


def check(receiver, cradle, elbow):
    s = EC.stations()
    hang = cradle.translate(cq.Vector(0, 0, -EC.CATCH_GAP))
    return {
        "cradle_overlap_home_mm3": cradle.intersect(receiver).Volume(),
        "cradle_gap_home_mm": _gap(cradle, receiver),
        "cradle_overlap_hanging_mm3": hang.intersect(receiver).Volume(),
        "cradle_gap_hanging_mm": _gap(hang, receiver),
        "elbow_overlap_mm3": elbow.intersect(receiver).Volume() + elbow.intersect(cradle).Volume(),
        "elbow_nose_gap_mm": _gap(elbow, receiver),
        "elbow_seat_gap_mm": round(_gap(elbow, cradle), 3),
        "hook_deflection_to_pass_mm": s["bend"]["hook_deflection"],
        "wing_free_length_mm": s["bend"]["free_length"],
        "nominal_root_strain": s["bend"]["root_strain"],
        "lane_mm": s["lane"],
        "hook_overlap_mm": EC.OVERLAP,
        "hook_catch_gap_mm": EC.CATCH_GAP,
        "hole_diameter_mm": EC.HOLE_D,
        "receiver_volume_mm3": receiver.Volume(),
        "cradle_volume_mm3": cradle.Volume(),
        "scope": "Nominal CAD clearances and a tip-loaded cantilever estimate of the wing's "
                 "bend; insertion force, strain tolerance and retention are for the print.",
    }


def main():
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, one_body
    receiver, cradle, elbow = build()
    facts = check(receiver, cradle, elbow)
    out = _here.parent
    z0 = EC.block()[3]
    for name, shape in (("test-receiver", receiver),
                        ("test-cradle", cradle.translate(cq.Vector(0, 0, -z0)))):
        export_assembly(one_body(cq.Workplane(obj=shape), name, M_PETGF_BLACK),
                        str(out / f"{name}.step"))
        cq.exporters.export(shape, str(out / f"{name}.stl"), tolerance=0.05,
                            angularTolerance=0.15)
        print(f"-> {name}.step, {name}.stl; {shape.Volume():.1f} mm3")
    (out / "geometry-check.json").write_text(json.dumps(
        {k: (round(v, 4) if isinstance(v, float) else v) for k, v in facts.items()}, indent=1)
        + "\n")
    print("-> geometry-check.json")
    from docgen import substitute_md
    st = EC.stations()
    substitute_md(out / "README.md", variables={
        "TRIAL_WEB": f"{EC.WEB:g} mm",
        "TRIAL_HOLE": f"{EC.HOLE_D:g} mm",
        "TRIAL_RECEIVER_H": f"{RECEIVER_H:g} mm",
        "TRIAL_RECEIVER": f"{FF.socket_width + 2 * RECEIVER_RIM:g} × {2 * RECEIVER_HALF_Y:g} × "
                          f"{RECEIVER_H:g} mm",
        "TRIAL_HOOK_BED": f"{st['face'] - st['z0']:.1f} mm",
        "TRIAL_PINCH": f"{st['bend']['hook_deflection']:.1f} mm",
        "TRIAL_CATCH": f"{EC.CATCH_GAP:g} mm",
        "TRIAL_NOSE": f"{facts['elbow_seat_gap_mm'] + EC.CATCH_GAP:g} mm",
    })
    print("-> README.md")


if __name__ == "__main__":
    main()
