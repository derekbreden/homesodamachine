"""Describe two accessible sectors of the actual seat for native support slicing."""

import argparse
import json
from pathlib import Path

import numpy as np
import trimesh

from tip_geometry import CANONICAL_POINT, rotate_x
from tip_warp import BEARING_ANGLE, NORMAL_AGAIN, TipWarp

CENTRE = 4.024
ROOF_RADII = (12.05, 14.0)
RELEASE_HALF_ANGLE = 4.0
ENFORCEMENT_DEPTH = (-.72, .55)
PLUG_RADIUS = 11.8
PLUG_DEPTH = (-1.15, .38)
LEVEL_RECIPE_START = 65.96
COURSE_BANDS = [[.20, 30.20, .20]]


def sector(angles, radii, depths):
    inner, outer = radii
    low, high = depths
    section = np.array([[inner, low], [outer, low], [outer, high], [inner, high]])
    a = np.radians(angles)
    vertices = np.stack([
        np.cos(a)[:, None] * section[:, 0],
        CENTRE + np.sin(a)[:, None] * section[:, 0],
        np.broadcast_to(section[:, 1], (len(a), len(section))),
    ], axis=-1).reshape(-1, 3)
    faces = [(0, 2, 1), (0, 3, 2)]
    for step in range(len(a) - 1):
        for edge in range(len(section)):
            i = step * 4 + edge
            j = step * 4 + (edge + 1) % 4
            faces.extend([(i, j, j + 4), (i, j + 4, i + 4)])
    end = 4 * (len(a) - 1)
    faces.extend([(end, end + 1, end + 2), (end, end + 2, end + 3)])
    return vertices, np.array(faces)


def to_donor_seat(vertices, rotation, translation, warp):
    shoulder = vertices @ rotate_x(-BEARING_ANGLE).T + warp.shoulder_xyz
    shoulder[:, 2] = warp.inverse(shoulder[:, 1], shoulder[:, 2])
    return (shoulder - translation) @ rotation


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("warp", type=Path)
    cli.add_argument("output", type=Path)
    args = cli.parse_args()
    row = json.loads(args.warp.read_text())
    rotation = np.asarray(row["physical_rotation"])
    translation = np.asarray(row["physical_cad_to_plate_translation"])
    warp = TipWarp(tuple(rotation @ CANONICAL_POINT + translation))

    def write(name, role, verts, tris):
        solid = trimesh.Trimesh(to_donor_seat(verts, rotation, translation, warp), tris, process=False)
        if not solid.is_watertight:
            raise ValueError(f"{name} has an open support mesh")
        if solid.volume < 0:
            solid.invert()
        file = name.replace(" ", "-").lower() + ".stl"
        solid.export(args.output.parent / file)
        return {"name": name, "role": role, "stl": file}

    volumes = []
    for i, centre in enumerate((0., 180.), start=1):
        angles = np.linspace(centre + RELEASE_HALF_ANGLE, centre + 180. - RELEASE_HALF_ANGLE, 175)
        vertices, faces = sector(angles, ROOF_RADII, ENFORCEMENT_DEPTH)
        volumes.append(write(f"Shoulder roof sector {i}", "support_enforcer", vertices, faces))
        release_angles = np.linspace(centre - RELEASE_HALF_ANGLE, centre + RELEASE_HALF_ANGLE, 9)
        release_v, release_f = sector(release_angles, (11.72, 14.28), (-1., .74))
        volumes.append(write(f"Roof access slit {i}", "support_blocker", release_v, release_f))
    plug = trimesh.creation.cylinder(radius=PLUG_RADIUS, height=PLUG_DEPTH[1]-PLUG_DEPTH[0], sections=144)
    plug.apply_translation([0., CENTRE, sum(PLUG_DEPTH)/2])
    volumes.append(write("Mating plug keepout", "support_blocker", plug.vertices, plug.faces))
    settings = {"course_bands_mm": COURSE_BANDS, "native_nose_handoff_mm": NORMAL_AGAIN,
                "support_parts": volumes}
    args.output.write_text(json.dumps(settings, indent=2) + "\n")


if __name__ == "__main__":
    main()
