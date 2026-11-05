"""Measure opposing planar gaps on the four finished enclosure quadrants.

Run after materializing the enclosure. The enclosure recipe places the required gaps; the
kernel program `enclosure-mating` (tools/hsm/enclosure-shell/src/bin/enclosure-mating.rs)
measures every reading on the quadrants' fine models, the `.step.npz` written beside each STEP.
It reads positive-area opposed faces, including exact contact that a whole-solid
volume-intersection check misses. Every measured printed mating face requires its applicable
fit and supported-face allowances, including clamping faces, seating shoulders, closure ends and
rail ends. Y-normal head-on closure faces use static clearance; tangential sliding faces use
running clearance. Faces printed against the actual build plate retain the base allowance
without the supported-overhang addition. Curved contacts, insertion sweeps and physical support
finish are separate checks.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "hardware/printed-parts/enclosure/enclosure"
sys.path[:0] = [str(DIRECTORY), str(ROOT / "hardware/scripts")]
import enclosure as e
import _box_spec
import _rust_part

NAMES = ("front-bottom", "back-bottom", "front-top", "back-top")
PRINT_UP = {"front-bottom": 1, "back-bottom": 1, "front-top": 1, "back-top": -1}


def required_gaps(box):
    """Each gap the recipe sets at an intersection: a point on the first piece's face, the way
    across to the second piece's face, and the gap between them."""
    gaps = []
    def gap_at(feature, first, second, point, normal, gap):
        gaps.append({"feature": feature, "parts": [first, second], "point": list(point),
                     "normal": list(normal), "gap": gap})
    bed, roof, _crown = e._handhold_levels(box.inner)
    for xi, sx in ((box.inner[0], 1.), (box.inner[1], -1.)):
        side = "west" if sx > 0 else "east"
        _flank, cap = e._band_x(xi - sx*e.wall, sx)
        gap = e.fits.running + e.fits.supported_surface
        # The middle of the full fore rib beside the open head access. The opening has no
        # opposing face, and the front inner wall ends at its separate backing joint before
        # the aft rib's full width.
        fore_rib_y = box.y_joint + (e.lip_len - e.y_stack_cbore_dia)/4.0
        gap_at(f"{side} handhold inner wall/knuckle fore rib", "front-bottom", "back-bottom",
               (cap - sx*e.handhold_wall/2, fore_rib_y, roof - gap), (0., 0., 1.), gap)
        # The floor and both inner walls close on one pair of plumb faces, the front's square
        # end one running fit before the back's.
        gap_at(f"{side} inner wall and floor square end", "front-bottom", "back-bottom",
               (cap - sx*e.handhold_wall/2, e._handhold_backing_end(box.y_joint, "front"),
                (bed + roof)/2), (0., 1., 0.), e.fits.running)
        _hk, _xf, arm, back = e._rail_x(xi, sx, "front")
        gap_at(f"{side} rail entrance/tee wall", "front-bottom", "front-top",
               ((arm + back)/2, box.pack.collet_plate["wall_aft_y"] + e.slide_slip,
                box.splits[0] + 1.), (0., -1., 0.), e.slide_slip)
    for x, y, _z in box.pack.vent_chase:
        gap_at("vent chase seam", "back-bottom", "back-top",
               (x - e.vent_rib_wall/2, y, box.splits[1] + e.z_rise), (0., 0., 1.), e.slide_slip)
    for col, zj in zip(("front", "back"), box.splits):
        for xi, sx, y0, y1, _lane in e._z_rail_runs(
                box.inner, box.y_joint, col, box.pack.collet_plate, box.pack.vent_chase):
            sy = 1. if y1 > y0 else -1.
            x_hook, x_foot, _arm, _back = e._rail_x(xi, sx, col)
            side = "west" if sx > 0 else "east"
            gap_at(f"{col} {side} rail end", f"{col}-top", f"{col}-bottom",
                   ((x_hook + x_foot)/2, y1 - sy*e.rail_stop_len, zj + e.hook_foot/2),
                   (0., sy, 0.), e.slide_slip)
    return gaps


def survey(directory=DIRECTORY):
    box, _ = _box_spec.read(e.Box, e.Bound, (e.Pack, e.PortField, e.Nameplate))
    numbers = {
        "pieces": [{"name": name,
                    "model": str((directory / f"enclosure-{name}.step.npz").relative_to(ROOT)),
                    "print_up": PRINT_UP[name]} for name in NAMES],
        "fits": {"slip": e.fits.slip, "running": e.fits.running,
                 "supported_surface": e.fits.supported_surface},
        "probes": required_gaps(box),
    }
    return _rust_part.check("enclosure-shell", "enclosure-mating", numbers)


if __name__ == "__main__":
    report = survey()
    target = DIRECTORY.parent / "mating-clearance-check.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    failed = len(report["failures"])
    readings = f"{report['checked_patches']} mating patches and {len(report['required_gaps'])} required gaps"
    print(f"✓ {readings} keep their fits." if not failed
          else f"✗ {failed} of {readings} miss their fits; see {target.relative_to(ROOT)}.")
    raise SystemExit(0 if report["status"] == "pass" else 1)
