"""NeoFit 1/4-inch stem elbow: supplier dimensions and estimated molded form.

Canonical frame: orthogonal axes intersect at (0, 0, 0); the female socket
opens +Y and the male stem points -X. Geometry is for layout, not manufacture.
The ATEU44 supplier row controls the main dimensions; model-dimensions.json
separates listed dimensions, derived datums and estimated mating insertion.
"""
from pathlib import Path
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from _cadq_export import export_assembly

TUBE_OD = STEM_OD = 6.35
COLLAR_OD = 0.610 * 25.4
STEM_LENGTH = 0.827 * 25.4
OVERALL_STEM_AXIS = 1.370 * 25.4
OVERALL_SOCKET_AXIS = 0.988 * 25.4
SOCKET_INSERTION = 0.665 * 25.4
STEM_TIP_REACH = OVERALL_STEM_AXIS - COLLAR_OD / 2
HUB_BACK_REACH = STEM_TIP_REACH - STEM_LENGTH
# Equal hub back-reach on the two axes is a molded-form estimate. It gives
# 19.05 mm from crossing to female mouth while retaining both listed envelopes.
SOCKET_MOUTH_REACH = OVERALL_SOCKET_AXIS - HUB_BACK_REACH
FLOW_BORE = 4.3


def socket():
    """Female resting release face and its outward axis, millimetres."""
    return (0.0, SOCKET_MOUTH_REACH, 0.0), (0.0, 1.0, 0.0)


def stem_tip():
    """Male tip and its direction of insertion into the receiving fitting."""
    return (-STEM_TIP_REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def stem_shoulder():
    return (-HUB_BACK_REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def seated_host_mouth(insertion=12.7):
    """Host release-face datum with the male tip inserted by `insertion`.

    The default is an estimate for an unmeasured 1/4-inch valve/check socket.
    Supply the host's actual depth when it is known: 16.891 for this NeoFit
    row's female socket, or the separate measured JG tee depth as applicable.
    The stem shoulder remains outside the host by STEM_LENGTH - insertion.
    """
    if not 0 < insertion <= STEM_LENGTH:
        raise ValueError("Insertion must fit within the male stem")
    return (insertion - STEM_TIP_REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def _turned_y(profile):
    # Build about +Z, then turn onto +Y. Profile entries are (station, radius).
    pts = [(0, profile[0][0]), *((r, t) for t, r in profile),
           (0, profile[-1][0])]
    return (cq.Workplane("XZ").polyline(pts).close()
            .revolve(360, (0, 0), (0, 1))
            .rotate((0, 0, 0), (1, 0, 0), -90))


def build():
    """Named body/stem and release collet, with illustrative open passages."""
    hub = (cq.Workplane("XY")
           .box(2 * HUB_BACK_REACH, 2 * HUB_BACK_REACH, 11.5)
           .edges("|Z").fillet(2.2))
    fixed = _turned_y([
        (0.0, 5.75), (4.4, 5.75), (5.3, 6.25),
        (7.0, 6.25), (7.7, 7.15), (8.0, COLLAR_OD / 2),
        (14.5, COLLAR_OD / 2), (14.8, 7.15),
        (17.25, 7.15), (17.7, 6.55),
    ])
    stem = cq.Solid.makeCylinder(
        STEM_OD / 2, STEM_LENGTH + 0.05,
        cq.Vector(-STEM_TIP_REACH, 0, 0), cq.Vector(1, 0, 0))
    body = hub.union(fixed).union(stem)
    stem_bore = cq.Solid.makeCylinder(
        FLOW_BORE / 2, STEM_TIP_REACH + 0.1,
        cq.Vector(-STEM_TIP_REACH - 0.05, 0, 0), cq.Vector(1, 0, 0))
    y_passage = cq.Solid.makeCylinder(
        FLOW_BORE / 2, SOCKET_MOUTH_REACH + .1,
        cq.Vector(0, -.05, 0), cq.Vector(0, 1, 0))
    socket_clearance = cq.Solid.makeCylinder(
        TUBE_OD / 2, SOCKET_INSERTION + 0.1,
        cq.Vector(0, SOCKET_MOUTH_REACH - SOCKET_INSERTION, 0),
        cq.Vector(0, 1, 0))
    body = body.cut(stem_bore).cut(y_passage).cut(socket_clearance)
    collet = _turned_y([
        (17.75, 5.65), (18.6, 5.65), (SOCKET_MOUTH_REACH, 5.5)])
    collet = collet.cut(socket_clearance)
    return [("body_and_stem", body), ("release_collet", collet)]


def export():
    pieces = build()
    assembly = cq.Assembly(name="neofit_stem_elbow_estimated")
    verts, faces, offset = [], [], 0
    checks = []
    for name, piece in pieces:
        solid = piece.val()
        if not solid.isValid():
            raise ValueError(f"Invalid reference solid: {name}")
        checks.append({"name": name, "valid": True,
                       "solids": len(solid.Solids()), "volume_mm3": solid.Volume()})
        assembly.add(piece, name=name, color=cq.Color(
            .90, .91, .88) if name == "body_and_stem" else cq.Color(.76, .79, .77))
        vv, ff = solid.tessellate(.04, .12)
        v = np.asarray([p.toTuple() for p in vv], dtype=np.float32)
        f = np.asarray(ff, dtype=np.int32)
        np.savez_compressed(HERE / f"{name}.npz", v=v, f=f)
        verts.append(v); faces.append(f + offset); offset += len(v)
    export_assembly(assembly, str(HERE / "neofit-stem-elbow.step"))
    v, f = np.vstack(verts), np.vstack(faces)
    np.savez_compressed(HERE / "neofit-stem-elbow.npz", v=v, f=f)
    bounds = [v.min(0).tolist(), v.max(0).tolist()]
    checks = {"pieces": checks, "bounds_mm": bounds,
              "vertices": len(v), "triangles": len(f),
              "socket": socket(), "stem_tip": stem_tip(),
              "stem_shoulder": stem_shoulder(),
              "estimated_unknown_host_mouth": seated_host_mouth()}
    (HERE / "model-check.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    export()
