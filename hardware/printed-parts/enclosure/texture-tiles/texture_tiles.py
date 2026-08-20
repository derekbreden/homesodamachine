"""Texture tiles — five swatches at each of `tile_sides`, printed FLAT, one square face
textured and the other left plain.

Frame: the tile lies in the XY plane with +Z the build axis. z = 0 is the bed face and
z = `tile_z` is the show face. Every texture is a heightfield cut DOWN from the show
face, so the tile's bounding box is its stated 50 × 50 × 3 and the deepest cut still
leaves `tile_z - texture_depth` of solid under it.

The plain face is the bed face, so each tile carries its texture and the textured-PEI
finish it is being judged against on opposite sides of the same 3 mm.

Both faces are the same `grid_cells` × `grid_cells` grid with the sides stitched between
them, so a tile is watertight by construction and the texture runs full-bleed to all four
edges rather than sitting in a border like a plaque. The cell COUNT is what is held
constant across sizes, not the cell size: every size then samples finer than the 0.82 mm
the nozzle draws — so none loses a feature the printer could have made — and the triangle
budget, and the file, stay put as the tile grows.

The flute vocabulary — the grooves and the warps that bend them — is
`../../cadlib/reeding.py`, shared with the standing-wall coupon in `../texture-corner/`
so both provably lay down the SAME texture.

A PATTERN'S SCALE IS ABSOLUTE. `flute_pitch` is 5 mm on every tile. A bigger swatch is
more repeats of the same texture, not the same texture enlarged, which is the only way
two sizes answer the same question.

WHAT A FLAT TILE CAN AND CANNOT ANSWER. Everything here is a TOP surface, quantised in
Z at the layer height — `texture_depth` is three layers at the enclosure's 0.4 mm. That
is the honest, hardest case, and the one the box's top and its 45° facet actually face.
It is NOT what these patterns look like on a vertical wall, where a cut of the same
shape is drawn by the nozzle in XY and carries no layer quantisation at all.

  * FLUTE    half-round grooves on one axis — linear, directional reeding. The control
             the two warped ones are read against.
  * CHEVRON  the same grooves, their path warped by a rounded-apex triangle wave.
  * WAVE     the same grooves, warped by a sine — the quiet end of the same idea.
  * CROSS    the same grooves on both diagonals, deeper wins — a diamond knurl.
  * HEX      grooves along the cell boundaries of a triangular lattice's Voronoi
             diagram, which are regular hexagons.
  * VORONOI  jittered sites, each cell dropped to one of `voronoi_levels` depths and
             meeting its neighbours on a vertical step — Bambu's own voronoi fuzzy
             skin, in geometry, at a size you choose.
  * PERLIN   fractal Perlin, the continuous-grain end of the range.
"""

import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md
import reeding
from perlin import fbm

# --- The tile every swatch is cut from ---------------------------------------------

tile_sides = (50.0, 100.0)
tile_z = 3.0
texture_depth = 1.2              # three layers at the enclosure's 0.4 mm
grid_cells = 200                 # per side, per face — the step follows from the size

label_height = 6.0
label_depth = 0.6
label_inset = 6.0                # centre of the label, in from the tile's near edge

_ROOT2 = math.sqrt(2.0)
_ROOT3 = math.sqrt(3.0)


def _grid_step(side):
    return side / grid_cells


def _sites(spacing, jitter, seed, side):
    """Lattice points covering the tile and a margin around it, so cells at the edge are
    bounded by neighbours that exist rather than running out to infinity. `jitter` 0
    leaves the triangular lattice whose Voronoi cells are regular hexagons."""
    margin = spacing * 3.0
    rows = np.arange(-margin, side + margin, spacing * _ROOT3 / 2.0)
    points = []
    for index, y in enumerate(rows):
        xs = np.arange(-margin + (index % 2) * spacing / 2.0, side + margin, spacing)
        points.append(np.column_stack([xs, np.full_like(xs, y)]))
    points = np.vstack(points)
    if jitter:
        rng = np.random.default_rng(seed)
        points = points + rng.uniform(-jitter, jitter, points.shape) * spacing
    return points


# --- The five ----------------------------------------------------------------------

cross_pitch = 6.0
cross_width = 3.4

hex_cell = 8.0
hex_groove = 2.2

voronoi_cell = 7.0
voronoi_jitter = 0.34            # share of the spacing each site wanders
voronoi_levels = 4               # evenly spaced, so `texture_depth` puts each on a layer
                                 # boundary and no two cells round together

perlin_feature = 7.0
perlin_octaves = 4
perlin_persistence = 0.5
perlin_seed = 20260819


def _flute(x, y, side):
    return reeding.straight(x, y)


def _chevron(x, y, side):
    return reeding.chevron(x, y)


def _wave(x, y, side):
    return reeding.wave(x, y)


def _cross(x, y, side):
    return reeding.cross(x, y, cross_pitch, cross_width)


def _hex(x, y, side):
    tree = cKDTree(_sites(hex_cell, 0.0, 0, side))
    near = tree.query(np.column_stack([x, y]), k=2)[0]
    to_boundary = (near[:, 1] - near[:, 0]) / 2.0
    return np.sqrt(np.clip(1.0 - (to_boundary / (hex_groove / 2.0)) ** 2, 0.0, None))


def _voronoi(x, y, side):
    sites = _sites(voronoi_cell, voronoi_jitter, perlin_seed, side)
    cell = cKDTree(sites).query(np.column_stack([x, y]), k=1)[1]
    levels = np.random.default_rng(perlin_seed).integers(0, voronoi_levels, len(sites))
    return levels[cell] / (voronoi_levels - 1.0)


def _perlin(x, y, side):
    field = fbm(np.column_stack([x, y, np.zeros_like(x)]),
                perlin_feature, perlin_octaves, perlin_persistence, perlin_seed)
    # Stretched onto its own extremes, not onto fbm's ±1 — the tile spends the whole of
    # `texture_depth` either way, so depth is not a variable between the five.
    return (field - field.min()) / np.ptp(field)


# The three-way the warp question turns on leads, so `plate_columns` puts FLUTE,
# CHEVRON and WAVE in one row of the plate with nothing between them.
TILES = (("flute", _flute), ("chevron", _chevron), ("wave", _wave),
         ("cross", _cross), ("hex", _hex), ("voronoi", _voronoi), ("perlin", _perlin))


# --- Mesh --------------------------------------------------------------------------

def _label_mask(label, n, side):
    """The label rasterised onto the tile's own grid, MIRRORED in X — it is sunk into
    the bed face, and a tile is turned over to read it."""
    supersample = 4
    step = _grid_step(side)
    image = Image.new("L", (n * supersample, n * supersample), 0)
    font = None
    for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Helvetica.ttc"):
        try:
            font = ImageFont.truetype(path, int(label_height / step * supersample))
            break
        except OSError:
            continue
    ImageDraw.Draw(image).text(
        (n * supersample / 2.0, (side - label_inset) / step * supersample),
        label, font=font or ImageFont.load_default(), fill=255, anchor="mm")
    grid = np.array(image.resize((n, n), Image.LANCZOS)) > 110
    return grid[::-1, ::-1]


def _quad_strip(top_ring, bottom_ring):
    """A skirt between two vertex rings walked in the same order. The face normal comes
    out on the left of that walk seen from outside, so a ring is handed in reversed
    where the tile's own edge runs the other way."""
    a, b = top_ring[:-1], top_ring[1:]
    c, d = bottom_ring[1:], bottom_ring[:-1]
    return np.concatenate([np.stack([a, b, c], axis=-1), np.stack([a, c, d], axis=-1)])


def build_tile(cut_field, label, side):
    n = grid_cells + 1
    axis = np.linspace(0.0, side, n)
    gx, gy = np.meshgrid(axis, axis)
    x, y = gx.ravel(), gy.ravel()

    cut = np.clip(cut_field(x, y, side), 0.0, 1.0)
    top = np.column_stack([x, y, tile_z - texture_depth * cut])
    bottom = np.column_stack([x, y, label_depth * _label_mask(label, n, side).ravel()])

    rows, cols = np.meshgrid(np.arange(n - 1), np.arange(n - 1), indexing="ij")
    a = (rows * n + cols).ravel()
    b, c, d = a + 1, a + n + 1, a + n
    face = np.concatenate([np.stack([a, b, c], axis=-1), np.stack([a, c, d], axis=-1)])

    left = np.arange(n) * n
    right = left + (n - 1)
    near = np.arange(n)
    far = near + (n - 1) * n
    sides = np.concatenate([_quad_strip(ring, ring + n * n)
                            for ring in (left, right[::-1], near[::-1], far)])

    return trimesh.Trimesh(
        vertices=np.vstack([top, bottom]),
        faces=np.concatenate([face, face[:, ::-1] + n * n, sides]),
        process=True)


# --- Export ------------------------------------------------------------------------

plate_gap = 8.0
plate_columns = 3
# The H2C's bed is 330 × 320, but the LEFT extruder reaches x 0…325 and the right x
# 25…330 — the band the plate draws as "left nozzle only". A single-filament plate is
# held to the left extruder's reach, less a margin it is not worth printing into.
bed_usable_x = 325.0
bed_usable_y = 320.0
plate_margin = 10.0


def _seated(meshes, side):
    """The set laid out `plate_columns` wide, rows centred on each other, about the
    origin — or None where that arrangement wants more bed than there is."""
    pitch = side + plate_gap
    seated = []
    for index, (_, mesh) in enumerate(meshes):
        row, column = divmod(index, plate_columns)
        in_row = min(plate_columns, len(meshes) - row * plate_columns)
        seat = mesh.copy()
        seat.apply_translation([(column - (in_row - 1) / 2.0) * pitch, row * pitch, 0.0])
        seated.append(seat)
    plate = trimesh.util.concatenate(seated)
    plate.apply_translation(-plate.bounds.mean(axis=0) * [1, 1, 0])
    fits = (plate.extents[0] <= bed_usable_x - 2 * plate_margin
            and plate.extents[1] <= bed_usable_y - 2 * plate_margin)
    return plate, fits


def main():
    out_dir = _here.parent
    plates = {}
    for side in tile_sides:
        meshes = [(name, build_tile(field, name.upper(), side)) for name, field in TILES]
        for name, mesh in meshes:
            out = out_dir / f"texture-tile-{side:g}-{name}.stl"
            mesh.export(str(out))
            print(f"-> {out.name}  ({len(mesh.faces)} facets, "
                  f"{'watertight' if mesh.is_watertight else 'NOT WATERTIGHT'})")
        plate, fits = _seated(meshes, side)
        plates[side] = (plate, fits)
        if fits:
            out = out_dir / f"texture-tiles-{side:g}-plate.stl"
            plate.export(str(out))
            print(f"-> {out.name}  ({plate.extents[0]:.1f} × {plate.extents[1]:.1f} mm)")
        else:
            print(f"   no {side:g} mm plate: {len(meshes)} of them want "
                  f"{plate.extents[0]:.0f} × {plate.extents[1]:.0f} mm, and the left "
                  f"extruder reaches {bed_usable_x:.0f} × {bed_usable_y:.0f}. "
                  f"Import them and arrange, or print them in batches.")

    substitute_md(out_dir / "README.md", variables={
        "TILE_SIDES": " and ".join(f"{s:g}" for s in tile_sides) + " mm",
        "TILE_Z": f"{tile_z:.4g} mm",
        "TEXTURE_DEPTH": f"{texture_depth:.4g} mm",
        "FLOOR_LEFT": f"{tile_z - texture_depth:.4g} mm",
        "GRID_CELLS": f"{grid_cells}",
        "GRID_STEP_50": f"{_grid_step(50.0):.4g} mm",
        "GRID_STEP_100": f"{_grid_step(100.0):.4g} mm",
        "FLUTE_PITCH": f"{reeding.flute_pitch:.4g} mm",
        "WARP_AMPLITUDE": f"{reeding.warp_amplitude:.4g} mm",
        "WARP_WAVELENGTH": f"{reeding.warp_wavelength:.4g} mm",
        "CHEVRON_LIMB": f"{reeding.chevron_limb_deg():.3g}°",
        "WAVE_LIMB": f"{reeding.wave_limb_deg():.3g}°",
        "CROSS_PITCH": f"{cross_pitch:.4g} mm",
        "HEX_CELL": f"{hex_cell:.4g} mm",
        "HEX_GROOVE": f"{hex_groove:.4g} mm",
        "VORONOI_CELL": f"{voronoi_cell:.4g} mm",
        "VORONOI_LEVELS": f"{voronoi_levels}",
        "VORONOI_STEP": f"{texture_depth / (voronoi_levels - 1):.4g} mm",
        "PERLIN_FEATURE": f"{perlin_feature:.4g} mm",
        "PLATE_50_X": f"{plates[50.0][0].extents[0]:.4g} mm",
        "PLATE_50_Y": f"{plates[50.0][0].extents[1]:.4g} mm",
        "PLATE_100_X": f"{plates[100.0][0].extents[0]:.4g} mm",
        "PLATE_100_Y": f"{plates[100.0][0].extents[1]:.4g} mm",
        "BED_USABLE_X": f"{bed_usable_x:.4g} mm",
    })
    print("-> README.md")


if __name__ == "__main__":
    main()
