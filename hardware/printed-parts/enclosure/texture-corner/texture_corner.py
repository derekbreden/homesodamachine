"""Texture corner — two standing walls meeting at the box's own outside corner, textured
on the outside, printed the way the enclosure prints: STANDING, build axis up the wall.

Frame: the walls are the NORTH and EAST of a box whose interior lies to −X/−Y. The north
wall's outer face looks +Y, the east wall's looks +X, and they meet at a convex corner
rounded to `corner_r` — `enclosure.corner_round`, the anti-warp relief the box strikes on
every standing vertical. World +Z is height and the build axis; z = 0 is the bed.

WHY THIS EXISTS. A flat tile can only answer what a texture does on a TOP surface, where
relief is quantised in Z at the layer height. On a standing wall the same groove is drawn
by the nozzle in XY and carries no layer quantisation at all — it is as clean as the
nozzle draws. That is the condition the box's own walls are in, and no tile can show it.
This coupon is the other half of `../texture-tiles/`, and the two are meant to be held up
beside each other.

It also answers the question neither flat set can: WHAT A FLUTE DOES ROUND A CORNER. The
texture is sampled by ARC LENGTH along the wall's outer path, so it crosses the corner's
quarter turn without knowing the corner is there — no seam, no restart, constant spacing.

`wall` and `corner_r` are the enclosure's own, so what the coupon shows is what the box
can take: the deepest cut leaves `wall - texture_depth` behind, on the flat and round the
turn alike.

NOTHING ELSE MAY SPEND THAT SECTION. `wall - texture_depth` is 1.8 mm and the profile lays
two loops a side — 0.42 out, 0.45 in — so a groove floor still has all four, with 0.06 mm
to spare. Take anything more out of the far side and the two pairs of loops meet: the
slicer stops laying four walls and lays whatever fits, and the change in what it lays under
the groove reads THROUGH to the show face as a mark you can find with a fingertip. That is
why the label below stands PROUD of the inner face instead of being sunk into it — an
engraved one takes `label_depth` out of exactly the section the flute over it is standing
on.

Everything cut here is drawn in XY, so nothing overhangs — except as the warp tilts a
groove's side surface off vertical, which `cadlib/reeding.py` sizes to stay inside 45°.

An inner foot ramps 45° off the wall at the base: a 3 mm wall standing 50 mm on its own
edge is a warp risk, and the foot is on the INSIDE, where it costs the show face nothing.
The texture fades in over the same height, so the first layers go down as a clean solid
L and the band it leaves is the plain wall to read the textured one against.
"""

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
import reeding
from docgen import substitute_md

# --- The corner every variant is cut from ------------------------------------------

leg = 50.0                       # flat wall either side of the turn
corner_r = 12.0                  # = enclosure.corner_round
wall = 3.0                       # = enclosure.wall
height = 50.0
texture_depth = 1.2
grid_step = 0.3                  # sampling pitch, well under the 0.42 mm bead the box lays

foot = 5.0                       # inner ramp at the base, 45° since it is also its width
texture_rise = 5.0               # = foot: plain wall exactly where the foot backs it

label_height = 8.0
label_depth = 0.6

quarter_turn = math.pi * corner_r / 2.0
path_length = 2.0 * leg + quarter_turn


def _smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _outer_path():
    """The outer face's plan path sampled at uniform ARC LENGTH — leg, quarter turn, leg
    — as (arc length, point, outward normal). Sampling by arc length is what carries a
    flute round the corner at constant spacing."""
    count = int(round(path_length / grid_step)) + 1
    s = np.linspace(0.0, path_length, count)
    point = np.zeros((count, 2))
    normal = np.zeros((count, 2))

    north = s <= leg
    point[north] = np.column_stack([-(leg + corner_r) + s[north], np.zeros(north.sum())])
    normal[north] = (0.0, 1.0)

    turn = (s > leg) & (s < leg + quarter_turn)
    angle = math.pi / 2.0 * (1.0 - (s[turn] - leg) / quarter_turn)
    normal[turn] = np.column_stack([np.cos(angle), np.sin(angle)])
    point[turn] = np.array([-corner_r, -corner_r]) + corner_r * normal[turn]

    east = s >= leg + quarter_turn
    point[east] = np.column_stack([np.zeros(east.sum()),
                                   -corner_r - (s[east] - leg - quarter_turn)])
    normal[east] = (1.0, 0.0)
    return s, point, normal


def _label_mask(label, count, rows):
    """The label rasterised onto the inner face's own grid, centred on the north leg at
    mid-height, and STANDING PROUD of it. Read from inside the box, arc length runs left to
    right, so the glyphs go down unmirrored."""
    supersample = 3
    image = Image.new("L", (count * supersample, rows * supersample), 0)
    font = None
    for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Helvetica.ttc"):
        try:
            font = ImageFont.truetype(path, int(label_height / grid_step * supersample))
            break
        except OSError:
            continue
    ImageDraw.Draw(image).text(
        ((leg / 2.0) / grid_step * supersample,
         (height / 2.0) / grid_step * supersample),
        label, font=font or ImageFont.load_default(), fill=255, anchor="mm")
    grid = np.array(image.resize((count, rows), Image.LANCZOS)) > 110
    return grid.T[:, ::-1]


def build_corner(field, label):
    s, base, normal = _outer_path()
    count = len(s)
    rows = int(round(height / grid_step)) + 1
    z = np.linspace(0.0, height, rows)
    across, along = np.meshgrid(s, z, indexing="ij")

    cut = np.clip(field(across.ravel(), along.ravel()), 0.0, 1.0).reshape(count, rows)
    cut *= _smoothstep(along / texture_rise)

    outer_in = texture_depth * cut
    # The label stands INTO the room, never out of the wall — see the module docstring.
    inner_in = (wall + np.clip(foot - along, 0.0, None)
                + label_depth * _label_mask(label, count, rows))

    def surface(inward):
        plan = base[:, None, :] - normal[:, None, :] * inward[:, :, None]
        return np.concatenate([plan, along[:, :, None]], axis=2).reshape(-1, 3)

    vertices = np.vstack([surface(outer_in), surface(inner_in)])

    def quads(a, b, c, d):
        return np.concatenate([np.stack([a, b, c], axis=-1),
                               np.stack([a, c, d], axis=-1)]).reshape(-1, 3)

    i, j = np.meshgrid(np.arange(count - 1), np.arange(rows - 1), indexing="ij")
    o = (i * rows + j).ravel()
    inner = count * rows
    # Outer looks out along +normal; inner looks the other way, so its quad runs the
    # other way round. Caps and ends close between the two.
    faces = [quads(o, o + 1, o + rows + 1, o + rows),
             quads(o + inner, o + inner + rows, o + inner + rows + 1, o + inner + 1)]

    k = np.arange(count - 1)
    top = k * rows + (rows - 1)
    faces.append(quads(top, top + inner, top + inner + rows, top + rows))
    bottom = k * rows
    faces.append(quads(bottom, bottom + rows, bottom + inner + rows, bottom + inner))

    m = np.arange(rows - 1)
    faces.append(quads(m, m + inner, m + inner + 1, m + 1))
    far = (count - 1) * rows + m
    faces.append(quads(far, far + 1, far + inner + 1, far + inner))

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.concatenate(faces), process=True)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


CORNERS = (("flute", reeding.straight), ("chevron", reeding.chevron),
           ("wave", reeding.wave))

plate_gap = 10.0


def main():
    out_dir = _here.parent
    meshes = [(name, build_corner(field, name.upper())) for name, field in CORNERS]

    plate = []
    pitch = leg + corner_r + plate_gap
    for index, (name, mesh) in enumerate(meshes):
        out = out_dir / f"texture-corner-{name}.stl"
        mesh.export(str(out))
        print(f"-> {out.name}  ({len(mesh.faces)} facets, "
              f"{'watertight' if mesh.is_watertight else 'NOT WATERTIGHT'}, "
              f"vol {mesh.volume / 1000.0:.1f} cm3)")
        seat = mesh.copy()
        seat.apply_translation([(index - 1) * pitch, 0.0, 0.0])
        plate.append(seat)
    plate = trimesh.util.concatenate(plate)
    plate.apply_translation(-plate.bounds.mean(axis=0) * [1, 1, 0])
    plate.export(str(out_dir / "texture-corners-plate.stl"))
    print(f"-> texture-corners-plate.stl  ({plate.extents[0]:.1f} × "
          f"{plate.extents[1]:.1f} × {plate.extents[2]:.1f} mm)")

    substitute_md(out_dir / "README.md", variables={
        "LEG": f"{leg:.4g} mm",
        "CORNER_R": f"{corner_r:.4g} mm",
        "WALL": f"{wall:.4g} mm",
        "HEIGHT": f"{height:.4g} mm",
        "TEXTURE_DEPTH": f"{texture_depth:.4g} mm",
        "WALL_LEFT": f"{wall - texture_depth:.4g} mm",
        "GRID_STEP": f"{grid_step:.4g} mm",
        "FOOT": f"{foot:.4g} mm",
        "PATH_LENGTH": f"{path_length:.4g} mm",
        "QUARTER_TURN": f"{quarter_turn:.4g} mm",
        "FLUTE_PITCH": f"{reeding.flute_pitch:.4g} mm",
        "CHEVRON_LIMB": f"{reeding.chevron_limb_deg():.3g}°",
        "WAVE_LIMB": f"{reeding.wave_limb_deg():.3g}°",
        "PLATE_X": f"{plate.extents[0]:.4g} mm",
        "PLATE_Y": f"{plate.extents[1]:.4g} mm",
    })
    print("-> README.md")


if __name__ == "__main__":
    main()
