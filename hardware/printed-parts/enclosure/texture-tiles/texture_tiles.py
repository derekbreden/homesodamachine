"""Texture tiles — five 50 × 50 × 3 mm swatches, printed FLAT, one 50 × 50 face
textured and the other left plain.

Frame: the tile lies in the XY plane with +Z the build axis. z = 0 is the bed face and
z = `tile_z` is the show face. Every texture is a heightfield cut DOWN from the show
face, so the tile's bounding box is its stated 50 × 50 × 3 and the deepest cut still
leaves `tile_z - texture_depth` of solid under it.

The plain face is the bed face, so each tile carries its texture and the textured-PEI
finish it is being judged against on opposite sides of the same 3 mm.

Both faces are the same grid at `grid_step`, sides stitched between them, so a tile is
watertight by construction and the texture runs full-bleed to all four edges rather
than sitting in a border like a plaque.

WHAT A FLAT TILE CAN AND CANNOT ANSWER. Everything here is a TOP surface, quantised in
Z at the layer height — `texture_depth` is three layers at the enclosure's 0.4 mm. That
is the honest, hardest case, and the one the box's top and its 45° facet actually face.
It is NOT what these patterns look like on a vertical wall, where a cut of the same
shape is drawn by the nozzle in XY and carries no layer quantisation at all.

  * FLUTE    half-round grooves on one axis — linear, directional reeding.
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
from perlin import fbm

# --- The tile every swatch is cut from ---------------------------------------------

tile_side = 50.0
tile_z = 3.0
texture_depth = 1.2              # three layers at the enclosure's 0.4 mm
grid_step = 0.25                 # sampling pitch of both faces, well under the 0.8 nozzle

label_height = 6.0
label_depth = 0.6
label_inset = 6.0                # centre of the label, in from the tile's near edge

_ROOT2 = math.sqrt(2.0)
_ROOT3 = math.sqrt(3.0)


def _groove(u, pitch, width):
    """Half-round grooves `width` across on `pitch` centres, as a 0…1 depth fraction."""
    offset = (u + pitch / 2.0) % pitch - pitch / 2.0
    return np.sqrt(np.clip(1.0 - (offset / (width / 2.0)) ** 2, 0.0, None))


def _sites(spacing, jitter, seed):
    """Lattice points covering the tile and a margin around it, so cells at the edge are
    bounded by neighbours that exist rather than running out to infinity. `jitter` 0
    leaves the triangular lattice whose Voronoi cells are regular hexagons."""
    margin = spacing * 3.0
    rows = np.arange(-margin, tile_side + margin, spacing * _ROOT3 / 2.0)
    points = []
    for index, y in enumerate(rows):
        xs = np.arange(-margin + (index % 2) * spacing / 2.0, tile_side + margin, spacing)
        points.append(np.column_stack([xs, np.full_like(xs, y)]))
    points = np.vstack(points)
    if jitter:
        rng = np.random.default_rng(seed)
        points = points + rng.uniform(-jitter, jitter, points.shape) * spacing
    return points


# --- The five ----------------------------------------------------------------------

flute_pitch = 5.0
flute_width = 4.0

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


def _flute(x, y):
    return _groove(x, flute_pitch, flute_width)


def _cross(x, y):
    return np.maximum(_groove((x + y) / _ROOT2, cross_pitch, cross_width),
                      _groove((x - y) / _ROOT2, cross_pitch, cross_width))


def _hex(x, y):
    tree = cKDTree(_sites(hex_cell, 0.0, 0))
    near = tree.query(np.column_stack([x, y]), k=2)[0]
    to_boundary = (near[:, 1] - near[:, 0]) / 2.0
    return np.sqrt(np.clip(1.0 - (to_boundary / (hex_groove / 2.0)) ** 2, 0.0, None))


def _voronoi(x, y):
    sites = _sites(voronoi_cell, voronoi_jitter, perlin_seed)
    cell = cKDTree(sites).query(np.column_stack([x, y]), k=1)[1]
    levels = np.random.default_rng(perlin_seed).integers(0, voronoi_levels, len(sites))
    return levels[cell] / (voronoi_levels - 1.0)


def _perlin(x, y):
    field = fbm(np.column_stack([x, y, np.zeros_like(x)]),
                perlin_feature, perlin_octaves, perlin_persistence, perlin_seed)
    # Stretched onto its own extremes, not onto fbm's ±1 — the tile spends the whole of
    # `texture_depth` either way, so depth is not a variable between the five.
    return (field - field.min()) / np.ptp(field)


TILES = (("flute", _flute), ("cross", _cross), ("hex", _hex),
         ("voronoi", _voronoi), ("perlin", _perlin))


# --- Mesh --------------------------------------------------------------------------

def _label_mask(label, n):
    """The label rasterised onto the tile's own grid, MIRRORED in X — it is sunk into
    the bed face, and a tile is turned over to read it."""
    supersample = 4
    image = Image.new("L", (n * supersample, n * supersample), 0)
    font = None
    for path in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Helvetica.ttc"):
        try:
            font = ImageFont.truetype(path, int(label_height / grid_step * supersample))
            break
        except OSError:
            continue
    ImageDraw.Draw(image).text(
        (n * supersample / 2.0, (tile_side - label_inset) / grid_step * supersample),
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


def build_tile(cut_field, label):
    n = int(round(tile_side / grid_step)) + 1
    axis = np.linspace(0.0, tile_side, n)
    gx, gy = np.meshgrid(axis, axis)
    x, y = gx.ravel(), gy.ravel()

    cut = np.clip(cut_field(x, y), 0.0, 1.0)
    top = np.column_stack([x, y, tile_z - texture_depth * cut])
    bottom = np.column_stack([x, y, label_depth * _label_mask(label, n).ravel()])

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


def main():
    out_dir = _here.parent
    meshes = [(name, build_tile(field, name.upper())) for name, field in TILES]

    plate = []
    for index, (name, mesh) in enumerate(meshes):
        out = out_dir / f"texture-tile-{name}.stl"
        mesh.export(str(out))
        print(f"-> {out.name}  ({len(mesh.faces)} facets, "
              f"{'watertight' if mesh.is_watertight else 'NOT WATERTIGHT'})")
        row, column = divmod(index, plate_columns)
        in_row = min(plate_columns, len(meshes) - row * plate_columns)
        pitch = tile_side + plate_gap
        seat = mesh.copy()
        seat.apply_translation([(column - (in_row - 1) / 2.0) * pitch, row * pitch, 0.0])
        plate.append(seat)
    plate = trimesh.util.concatenate(plate)
    plate.apply_translation(-plate.bounds.mean(axis=0) * [1, 1, 0])
    plate.export(str(out_dir / "texture-tiles-plate.stl"))
    print(f"-> texture-tiles-plate.stl  ({plate.extents[0]:.1f} × "
          f"{plate.extents[1]:.1f} × {plate.extents[2]:.1f} mm)")

    substitute_md(out_dir / "README.md", variables={
        "TILE_SIDE": f"{tile_side:.4g} mm",
        "TILE_Z": f"{tile_z:.4g} mm",
        "TEXTURE_DEPTH": f"{texture_depth:.4g} mm",
        "FLOOR_LEFT": f"{tile_z - texture_depth:.4g} mm",
        "GRID_STEP": f"{grid_step:.4g} mm",
        "FLUTE_PITCH": f"{flute_pitch:.4g} mm",
        "CROSS_PITCH": f"{cross_pitch:.4g} mm",
        "HEX_CELL": f"{hex_cell:.4g} mm",
        "HEX_GROOVE": f"{hex_groove:.4g} mm",
        "VORONOI_CELL": f"{voronoi_cell:.4g} mm",
        "VORONOI_LEVELS": f"{voronoi_levels}",
        "VORONOI_STEP": f"{texture_depth / (voronoi_levels - 1):.4g} mm",
        "PERLIN_FEATURE": f"{perlin_feature:.4g} mm",
        "PLATE_X": f"{plate.extents[0]:.4g} mm",
        "PLATE_Y": f"{plate.extents[1]:.4g} mm",
    })
    print("-> README.md")


if __name__ == "__main__":
    main()
