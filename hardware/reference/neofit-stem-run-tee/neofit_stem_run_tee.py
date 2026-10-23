"""neoFit ATRU444-E run-stem tee, catalogue datums with photo-derived contours.

Frame (mm): junction at origin; stem points -X; socket run +X; branch -Y.
The stem is shown in full. Host-specific insertion places its tip inside the
receiving socket; stem length does not imply shoulder-to-collet contact.

Run through tmp/takeover/cadq; this creates STEP and a lightweight NPZ.
"""
from pathlib import Path
import json
import math
import re

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
INCH = 25.4
TUBE_OD = STEM_OD = 0.25 * INCH
COLLAR_D = 0.610 * INCH
STEM_LENGTH = 0.827 * INCH                 # A, shoulder to tip
STEM_REACH = 1.063 * INCH                  # L1, junction to tip
OVERALL_RUN = 1.890 * INCH                 # L2, tip to opposite socket
RUN_SOCKET_REACH = OVERALL_RUN - STEM_REACH
BRANCH_SOCKET_REACH = 0.827 * INCH         # E, junction to branch face
TUBE_INSERTION = 0.665 * INCH              # B2 = B3, face to tube stop
STEM_SHOULDER_X = -(STEM_REACH - STEM_LENGTH)

# The catalogue gives port datums and maximum collar diameter. Its drawing and
# the listing photograph supply these approximate undimensioned contours.
ROOT_D = 11.2
PASSAGE_D = 4.35
SOCKET_PROFILE = [
    (0.0, ROOT_D / 2),
    (7.2, ROOT_D / 2),
    (8.0, 6.30),
    (8.8, 6.70),
    (9.0, 7.10),
    (10.0, 7.10),
    (10.3, COLLAR_D / 2),
    (17.1, COLLAR_D / 2),
    (17.6, 7.10),
    (18.5, 7.10),
    (18.8, 6.60),
    (19.2, 6.25),
    (19.45, 6.25),
    (19.55, 6.65),
    (20.75, 6.65),
    (RUN_SOCKET_REACH, 6.40),
]


def ports():
    """Full native fitting interfaces; female faces name resting collet faces."""
    return {
        "run_stem": {
            "position_mm": [-STEM_REACH, 0.0, 0.0],
            "outward_axis": [-1.0, 0.0, 0.0],
            "shoulder_mm": [STEM_SHOULDER_X, 0.0, 0.0],
            "kind": "male_stem", "diameter_mm": STEM_OD,
            "stem_length_mm": STEM_LENGTH,
        },
        "run_socket": {
            "position_mm": [RUN_SOCKET_REACH, 0.0, 0.0],
            "outward_axis": [1.0, 0.0, 0.0],
            "kind": "female_push_fit", "tube_od_mm": TUBE_OD,
            "insertion_depth_mm": TUBE_INSERTION,
            "tube_stop_mm": [RUN_SOCKET_REACH - TUBE_INSERTION, 0.0, 0.0],
        },
        "branch_socket": {
            "position_mm": [0.0, -BRANCH_SOCKET_REACH, 0.0],
            "outward_axis": [0.0, -1.0, 0.0],
            "kind": "female_push_fit", "tube_od_mm": TUBE_OD,
            "insertion_depth_mm": TUBE_INSERTION,
            "tube_stop_mm": [0.0, -(BRANCH_SOCKET_REACH - TUBE_INSERTION), 0.0],
        },
    }


def cylinder(radius, start, length, axis):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*axis))


def socket():
    """Socket envelope along +X, including the resting release-collet rim."""
    profile = [(0.0, 0.0), *SOCKET_PROFILE, (RUN_SOCKET_REACH, 0.0)]
    return (cq.Workplane("XY").polyline(profile).close()
            .revolve(360, (0, 0), (1, 0)).val())


def build():
    body = socket().fuse(socket().rotate((0, 0, 0), (0, 0, 1), -90))
    body = body.fuse(cylinder(ROOT_D / 2,
                             (STEM_SHOULDER_X, 0, 0), -STEM_SHOULDER_X,
                             (1, 0, 0)))
    stem = cylinder(STEM_OD / 2, (-STEM_REACH + 0.30, 0, 0),
                    STEM_LENGTH - 0.30, (1, 0, 0))
    tip = cq.Solid.makeCone(STEM_OD / 2 - 0.30, STEM_OD / 2, 0.30,
                            cq.Vector(-STEM_REACH, 0, 0), cq.Vector(1, 0, 0))
    body = body.fuse(stem).fuse(tip)
    # Water passage and two stepped tube sockets. Internal retainers and
    # elastomer seats are omitted; this is an assembly-layout reference.
    body = body.cut(cylinder(PASSAGE_D / 2,
                             (-STEM_REACH - .1, 0, 0),
                             OVERALL_RUN + .2, (1, 0, 0)))
    body = body.cut(cylinder(PASSAGE_D / 2,
                             (0, -BRANCH_SOCKET_REACH - .1, 0),
                             BRANCH_SOCKET_REACH + .2, (0, 1, 0)))
    body = body.cut(cylinder(TUBE_OD / 2,
                             (RUN_SOCKET_REACH - TUBE_INSERTION, 0, 0),
                             TUBE_INSERTION + .1, (1, 0, 0)))
    body = body.cut(cylinder(TUBE_OD / 2,
                             (0, -BRANCH_SOCKET_REACH - .1, 0),
                             TUBE_INSERTION + .1, (0, 1, 0)))
    return body.clean()


def main():
    solid = build()
    assembly = cq.Assembly(solid, name="neofit-stem-run-tee",
                           color=cq.Color(0.055, 0.060, 0.065))
    step_path = HERE / "neofit-stem-run-tee.step"
    # Standalone reference export; it has no enclosure build dependency.
    assembly.export(str(step_path))
    data = step_path.read_bytes()
    data = re.sub(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'",
                  b"'1970-01-01T00:00:00'", data)
    step_path.write_bytes(data)
    vertices, faces = solid.tessellate(0.06, math.radians(12))
    v = np.array([p.toTuple() for p in vertices], dtype=np.float32)
    f = np.array(faces, dtype=np.int32)
    np.savez_compressed(HERE / "neofit-stem-run-tee.npz", v=v, f=f)
    bb = solid.BoundingBox()
    report = {
        "valid": bool(solid.isValid()), "solids": len(solid.Solids()),
        "volume_mm3": solid.Volume(),
        "bounds_mm": [[bb.xmin, bb.ymin, bb.zmin],
                      [bb.xmax, bb.ymax, bb.zmax]],
        "mesh_vertices": len(v), "mesh_faces": len(f),
        "ports": ports(),
    }
    (HERE / "model-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
