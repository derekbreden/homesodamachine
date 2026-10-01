"""Measure opposing planar gaps on the four finished enclosure STEP solids.

Run after materializing the enclosure. This reads positive-area opposed faces,
including exact contact that a whole-solid volume-intersection check misses.
Only the stated clamp faces, seating shoulders and rail stops permit zero gap.
Curved contacts, insertion sweeps and physical support finish are separate checks.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "hardware/printed-parts/enclosure/enclosure"
sys.path.insert(0, str(DIRECTORY))
import enclosure as e
import _box_spec

NAMES = ("front-bottom", "back-bottom", "front-top", "back-top")
PRINT_UP = {"front-bottom": 1, "back-bottom": 1, "front-top": 1, "back-top": -1}
TOL = 1e-5


def datum(parts, normal, center, box):
    """The locating faces explicitly allowed to touch, never all zero-gap faces."""
    x, y, z = center
    if parts in (("front-bottom", "back-bottom"), ("front-top", "back-top")):
        if abs(normal[1]) > .999 and abs(y - box.y_joint) < TOL:
            return "Y seam closure end face"
        if abs(normal[0]) > .999:
            for xi, sx in ((box.inner[0], 1.), (box.inner[1], -1.)):
                _seat, tip, _heat, _cap = e._boss_x(xi - sx * e.wall, sx)
                if abs(x - tip) < TOL:
                    return "M3 screw-clamped socket/plug face"
    for col, zj in zip(("front", "back"), box.splits):
        if set(parts) != {f"{col}-bottom", f"{col}-top"}:
            continue
        if abs(normal[2]) > .999 and abs(z - zj) < TOL:
            return "Z seam seating shoulder"
        if abs(normal[1]) > .999:
            for _xi, _sx, y0, y1, _lane in e._z_rail_runs(
                    box.inner, box.y_joint, col, box.pack.collet_plate, box.pack.vent_chase):
                sy = 1. if y1 > y0 else -1.
                if abs(y - (y1 - sy * e.rail_stop_len)) < TOL:
                    return "Closed-end rail stop"
    return None


def survey(directory=DIRECTORY):
    box, _ = _box_spec.read(e.Box, e.Bound, (e.Pack, e.PortField, e.Nameplate))
    groups, sources, solids = {}, {}, {}
    for name in NAMES:
        path = directory / f"enclosure-{name}.step"
        sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        solid = cq.importers.importStep(str(path)).val()
        solids[name] = solid
        groups[name] = {}
        for index, face in enumerate(solid.Faces()):
            if face.geomType() != "PLANE":
                continue
            normal = np.array(face.normalAt().toTuple())
            key = tuple(np.round(normal, 5))
            b = face.BoundingBox()
            row = (index, face, normal, np.array(face.Center().toTuple()),
                   np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax]))
            groups[name].setdefault(key, []).append(row)
    readings = []
    for first, second in combinations(NAMES, 2):
        for key, faces in groups[first].items():
            others = groups[second].get(tuple(-np.array(key)), [])
            if not others:
                continue
            centers = np.array([r[3] for r in others])
            lows, highs = (np.array([r[i] for r in others]) for i in (4, 5))
            for ia, fa, normal, ca, low, high in faces:
                gaps = (centers - ca) @ normal
                overlap = (np.minimum(high, highs - gaps[:, None] * normal)
                           - np.maximum(low, lows - gaps[:, None] * normal))
                selected = (gaps >= -TOL) & (gaps <= .751) & (overlap >= -TOL).all(axis=1)
                for j in np.flatnonzero(selected):
                    ib, fb, nb, _cb, _lb, _hb = others[j]
                    projected = fa.intersect(fb.translate(tuple(-gaps[j] * normal)))
                    if projected.Area() < .05:
                        continue
                    center = projected.Center().toTuple()
                    locating = datum((first, second), normal, center, box)
                    # Bed-contact and intentional bearing planes are handled above.
                    # Other horizontal print-down mating faces need rough-face room.
                    rough = (int(normal[2] * PRINT_UP[first] < -.99)
                             + int(nb[2] * PRINT_UP[second] < -.99))
                    target = 0. if locating else e.fits.running + rough * e.fits.supported_surface
                    gap = float(max(0., gaps[j]))
                    b = projected.BoundingBox()
                    readings.append({
                        "parts": [first, second], "face_indices": [ia, ib],
                        "gap_mm": gap, "minimum_mm": target,
                        "pass": bool(gap + TOL >= target),
                        "classification": locating or "Assembly sliding clearance",
                        "rough_faces_counted": 0 if locating else rough,
                        "area_mm2": projected.Area(), "center_mm": center,
                        "normal_from_first": normal.tolist(),
                        "bounds_mm": [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax],
                    })
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in sources.items())
    probes = []
    def measure(label, first, second, point, normal, gap):
        other = tuple(a + gap*b for a,b in zip(point, normal))
        errors = []
        for name, xyz, direction in ((first, point, normal),
                                      (second, other, tuple(-v for v in normal))):
            vertex = cq.Vertex.makeVertex(*xyz)
            faces = [f for f in solids[name].Faces() if f.geomType() == "PLANE"
                     and np.dot(f.normalAt().toTuple(), direction) > .999]
            errors.append(min(f.distance(vertex) for f in faces))
        middle = tuple(a + gap*b/2 for a,b in zip(point, normal))
        air = not any(solids[n].isInside(cq.Vector(*middle), TOL) for n in (first, second))
        probes.append({"feature": label, "parts": [first, second],
                       "face_points_mm": [point, other], "gap_mm": gap,
                       "maximum_surface_error_mm": max(errors), "gap_contains_air": air,
                       "pass": max(errors) < TOL and air})
    _bed, roof, _crown = e._handhold_levels(box.inner)
    for xi, sx in ((box.inner[0], 1.), (box.inner[1], -1.)):
        side = "west" if sx > 0 else "east"
        _seat, _tip, _heat, cap = e._boss_x(xi - sx*e.wall, sx)
        measure(f"{side} handhold roof/tab", "front-bottom", "back-bottom",
                (cap - sx*e.handhold_wall/2, box.y_joint+e.lip_len-1.5, roof),
                (0.,0.,-1.), e.fits.running+e.fits.supported_surface)
        measure(f"{side} scarf/backing wall", "front-bottom", "back-bottom",
                (cap+sx*e.fits.running, e._handhold_backing_end(box.y_joint,"back")+.5, -.5),
                (-sx,0.,0.), e.fits.running)
        _hk, _xf, arm, back = e._rail_x(xi, sx, "front")
        measure(f"{side} rail entrance/tee wall", "front-bottom", "front-top",
                ((arm+back)/2, box.pack.collet_plate["wall_aft_y"]+e.slide_slip, box.splits[0]+1.),
                (0.,-1.,0.), e.slide_slip)
    for x,y,_z in box.pack.vent_chase:
        measure("vent chase seam", "back-bottom", "back-top",
                (x-e.vent_rib_wall/2, y, box.splits[1]+e.z_rise), (0.,0.,1.), e.slide_slip)
    failures = [r for r in readings if not r["pass"]] + [r for r in probes if not r["pass"]]
    return {"status": "fail" if failures else "pass", "source_sha256": sources,
            "scope": "Opposed parallel planar patches above 0.05 mm2, gaps up to 0.751 mm, on four finished quadrant STEP solids. Excludes curved/nonparallel contacts, insertion sweeps, accessories and physical support quality.",
            "checked_patches": len(readings), "failures": failures,
            "required_gaps": probes, "patches": readings}


if __name__ == "__main__":
    report = survey()
    target = DIRECTORY.parent / "mating-clearance-check.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "checked_patches", "failures")}, indent=2))
    raise SystemExit(0 if report["status"] == "pass" else 1)
