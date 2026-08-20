"""Texture coupons — four samples of the enclosure's top-front corner, each carrying a
different surface treatment across all three surfaces that corner presents: a vertical
wall, the 45° display facet, and a flat top.

Frame: world +Z is height (up) and the build axis, world ±X is lateral (symmetric about
the X = 0 plane), world -Y is forward — the front wall stands at y = 0 and the coupon
runs back in +Y. Each coupon sits on the bed on its own z = 0 face, the orientation
`enclosure.py` prints its four quadrants in, so what a coupon shows is what the piece
will show.

The SHOW SURFACE is one folded band, read by arc length from the bed: the front wall up
`wall_rise`, the 45° facet across `facet_slope`, then the top back to `coupon_y`.
`_fold_at` returns that band's point, outward normal and tangent at any arc length, and
every treatment is struck against what it returns — so a treatment crosses both arrises
instead of stopping at one face. Bottom, back and both sides are left plain; the back
carries the engraved label.

Nothing on any coupon hangs steeper than the 45° the box's own reliefs are struck at,
so all four print with no support.

  * FLUTE — half-round flutes running ALONG the fold, wall to facet to top, arrayed
    across X in three pitch zones. Three cylinders per flute, mitred at each arris on
    the intersection of their own offset axes.
  * VEE — 90° V-grooves running ACROSS X, arrayed up the fold at one pitch, their depth
    ramped from `vee_depth_min` at -X to `vee_depth_max` at +X. On the 45° facet a 90° V
    resolves into one vertical flank and one horizontal flank — the two surfaces an FDM
    machine prints best.
  * FACET — no micro-texture. Sections lofted RULED between alternating valley and
    ridge stations, so wall, facet and top all break into `facet_pitch` planes standing
    `facet_rise` apart, and no surface on the coupon is a true plane.
  * NOISE — Perlin fBm displacement baked into the mesh. Sampled in WORLD space, so the
    grain runs continuously over both arrises rather than restarting per layer.
    Amplitude is zoned across X. Mesh only; there is no STEP of it.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_step, export_assembly
from _materials import WALL_COLORS, one_body
from docgen import substitute_md

C_COUPON = WALL_COLORS["front-top"]

# --- The block every coupon is cut from --------------------------------------------

coupon_x = 120.0                 # lateral, three 40 mm parameter zones
wall_rise = 18.0                 # vertical front wall, bed to the lower arris
facet_run = 26.0                 # the 45° facet's run in Y, and so its rise in Z
top_run = 30.0                   # flat top, upper arris to the back wall
coupon_y = facet_run + top_run
coupon_z = wall_rise + facet_run
facet_slope = facet_run * math.sqrt(2.0)
show_length = wall_rise + facet_slope + top_run

zone_count = 3
zone_x = coupon_x / zone_count

label_size = 9.0
label_depth = 1.2

_ROOT2 = math.sqrt(2.0)
_facet_normal = (0.0, -1.0 / _ROOT2, 1.0 / _ROOT2)
_facet_tangent = (0.0, 1.0 / _ROOT2, 1.0 / _ROOT2)


def _fold_at(s):
    """The show surface at arc length `s` from the bed: (point_yz, normal, tangent),
    each in world Y/Z with X free. The band runs wall → 45° facet → top."""
    if s <= wall_rise:
        return (0.0, s), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0)
    if s <= wall_rise + facet_slope:
        run = (s - wall_rise) / _ROOT2
        return (run, wall_rise + run), _facet_normal, _facet_tangent
    back = s - wall_rise - facet_slope
    return (facet_run + back, coupon_z), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)


def _zone_center_x(zone):
    return -coupon_x / 2.0 + zone_x * (zone + 0.5)


def build_block():
    """The plain coupon: the folded section extruded the full width."""
    section = [(0.0, 0.0),
               (0.0, wall_rise),
               (facet_run, coupon_z),
               (coupon_y, coupon_z),
               (coupon_y, 0.0)]
    return (cq.Workplane("YZ")
            .workplane(offset=-coupon_x / 2.0)
            .polyline(section)
            .close()
            .extrude(coupon_x))


def build_label_cut(label):
    """The coupon's name sunk into the back wall, reading from +Y. Drawn on the front-
    facing plane and turned about Z, so the glyphs are not mirrored on the face they
    land on."""
    glyphs = (cq.Workplane("XZ")
              .text(label, label_size, label_depth, combine=False)
              .val())
    return (glyphs
            .rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180.0)
            .translate(cq.Vector(0.0, coupon_y - label_depth, coupon_z / 2.0)))


# --- FLUTE -------------------------------------------------------------------------

flute_depth = 1.0                # inside the 3 mm wall's two-perimeter budget
flute_land = 0.25                # share of the pitch left flat between two flutes
flute_pitches = (4.0, 6.0, 9.0)


def _flute_radius(pitch):
    """The cutter radius that leaves a `flute_depth` groove `(1 - flute_land) * pitch`
    wide, from the chord of a circle cut at that depth."""
    half_width = (1.0 - flute_land) * pitch / 2.0
    return (half_width ** 2 + flute_depth ** 2) / (2.0 * flute_depth)


def _flute_cutters(x, pitch):
    """One flute: three cylinders, each offset `radius - flute_depth` OUTSIDE its own
    face, meeting on the intersections of their axes so the groove mitres round both
    arrises."""
    radius = _flute_radius(pitch)
    stand = radius - flute_depth
    lower_miter_z = wall_rise + stand * (_ROOT2 - 1.0)
    upper_miter_y = facet_run - stand * (_ROOT2 - 1.0)
    overlap = flute_depth

    wall = cq.Solid.makeCylinder(
        radius, lower_miter_z + overlap + radius,
        cq.Vector(x, -stand, -radius), cq.Vector(0, 0, 1))

    facet_axis_start = cq.Vector(
        x,
        -stand / _ROOT2 - overlap / _ROOT2,
        wall_rise + stand / _ROOT2 - overlap / _ROOT2)
    facet = cq.Solid.makeCylinder(
        radius, facet_slope + 2.0 * overlap,
        facet_axis_start, cq.Vector(*_facet_tangent))

    top = cq.Solid.makeCylinder(
        radius, coupon_y - upper_miter_y + overlap + radius,
        cq.Vector(x, upper_miter_y - overlap, coupon_z + stand), cq.Vector(0, 1, 0))

    return [wall, facet, top]


def build_flute_coupon():
    cutters = []
    for zone, pitch in enumerate(flute_pitches):
        center = _zone_center_x(zone)
        count = int(zone_x // pitch)
        span = (count - 1) * pitch
        for i in range(count):
            cutters += _flute_cutters(center - span / 2.0 + i * pitch, pitch)
    cutters.append(build_label_cut("FLUTE"))
    return cq.Workplane(obj=build_block().val().cut(*cutters))


# --- VEE ---------------------------------------------------------------------------

vee_pitch = 7.0
vee_depth_min = 0.8              # at -X
vee_depth_max = 2.4              # at +X
vee_margin = 0.6                 # how far the cutter stands outside the face


def _vee_section(s, depth):
    """A 90° V at arc length `s`, as the three world (y, z) corners of the prism that
    cuts it: apex `depth` under the surface, both flanks struck at 45°, opened
    `vee_margin` clear of the face."""
    (py, pz), normal, tangent = _fold_at(s)
    reach = depth + vee_margin
    apex = (py - normal[1] * depth, pz - normal[2] * depth)
    lip = (py + normal[1] * vee_margin, pz + normal[2] * vee_margin)
    return [(lip[0] + tangent[1] * reach, lip[1] + tangent[2] * reach),
            apex,
            (lip[0] - tangent[1] * reach, lip[1] - tangent[2] * reach)]


def _vee_cutter(s):
    """One full-width groove, lofted between its shallow end at -X and its deep end at
    +X so the depth ramps across the coupon."""
    return (cq.Workplane("YZ")
            .workplane(offset=-coupon_x / 2.0)
            .polyline(_vee_section(s, vee_depth_min)).close()
            .workplane(offset=coupon_x)
            .polyline(_vee_section(s, vee_depth_max)).close()
            .loft(ruled=True)
            .val())


def build_vee_coupon():
    count = int(show_length // vee_pitch)
    start = (show_length - (count - 1) * vee_pitch) / 2.0
    cutters = [_vee_cutter(start + i * vee_pitch) for i in range(count)]
    cutters.append(build_label_cut("VEE"))
    return cq.Workplane(obj=build_block().val().cut(*cutters))


# --- FACET -------------------------------------------------------------------------

facet_pitch = 15.0               # lateral run from one arris to the next
facet_rise = 1.2                 # how far a ridge stands out of the valleys either side


def _facet_stations():
    """Lateral stations as a share of the width, alternating valley and ridge. Both side
    faces are valleys, so the coupon keeps its stated width, and consecutive facets never
    share a slope — an arris that carries no slope change carries no light either."""
    count = int(round(coupon_x / facet_pitch))
    return [(i / count - 0.5, 0.0 if i % 2 == 0 else facet_rise)
            for i in range(count + 1)]


def _facet_section(offset):
    """The folded section pushed `offset` out along its own faces. Both arris corners land
    where the two offset planes meet; bed and back wall do not move."""
    arris = offset * (_ROOT2 - 1.0)
    return [(-offset, 0.0),
            (-offset, wall_rise + arris),
            (facet_run - arris, coupon_z + offset),
            (coupon_y, coupon_z + offset),
            (coupon_y, 0.0)]


def build_facet_coupon():
    stations = _facet_stations()
    wp = cq.Workplane("YZ").workplane(offset=stations[0][0] * coupon_x)
    for i, (station, offset) in enumerate(stations):
        if i:
            wp = wp.workplane(offset=(station - stations[i - 1][0]) * coupon_x)
        wp = wp.polyline(_facet_section(offset)).close()
    return cq.Workplane(obj=wp.loft(ruled=True).val().cut(build_label_cut("FACET")))


# --- NOISE -------------------------------------------------------------------------

noise_feature = 8.0              # mm per unit of noise, before octaves
noise_octaves = 4                # `fuzzy_skin_octaves`
noise_persistence = 0.5          # `fuzzy_skin_persistence`
noise_seed = 20260819
noise_edge = 0.012               # mm, plane membership tolerance after tessellation
noise_amplitudes = (0.2, 0.4, 0.7)   # peak, either side of `fuzzy_skin_thickness` 0.3
noise_taper = 5.0                # mm the amplitude dies over at every show-surface edge
noise_blend = 3.0                # mm of arc length the normal turns over at each arris
noise_max_edge = 0.7             # mm, triangle size the displacement is sampled on


def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _perlin3(points, permutation):
    """Classic 3D Perlin over an (n, 3) array, vectorised."""
    lattice = np.floor(points).astype(np.int64)
    frac = points - lattice
    cell = lattice & 255
    fade = _fade(frac)

    def hashed(dx, dy, dz):
        a = permutation[cell[:, 0] + dx]
        b = permutation[(a + cell[:, 1] + dy) & 511]
        return permutation[(b + cell[:, 2] + dz) & 511]

    def dot(h, dx, dy, dz):
        gx, gy, gz = frac[:, 0] - dx, frac[:, 1] - dy, frac[:, 2] - dz
        low = h & 15
        u = np.where(low < 8, gx, gy)
        v = np.where(low < 4, gy, np.where((low == 12) | (low == 14), gx, gz))
        return (np.where(low & 1 == 0, u, -u) + np.where(low & 2 == 0, v, -v))

    def lerp(a, b, t):
        return a + t * (b - a)

    corners = {(dx, dy, dz): dot(hashed(dx, dy, dz), dx, dy, dz)
               for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)}
    x0 = [lerp(corners[(0, dy, dz)], corners[(1, dy, dz)], fade[:, 0])
          for dy in (0, 1) for dz in (0, 1)]
    y0 = lerp(x0[0], x0[2], fade[:, 1])
    y1 = lerp(x0[1], x0[3], fade[:, 1])
    return lerp(y0, y1, fade[:, 2])


def _fbm(points):
    """Fractal Perlin at `noise_octaves` octaves, scaled so the field's own extreme
    reaches ±1 — an amplitude in mm is then the displacement it actually buys."""
    base = np.random.default_rng(noise_seed).permutation(256)
    permutation = np.concatenate([base, base])
    total = np.zeros(len(points))
    amplitude, frequency = 1.0, 1.0 / noise_feature
    for octave in range(noise_octaves):
        shift = 37.13 * (octave + 1)
        total += amplitude * _perlin3(points * frequency + shift, permutation)
        amplitude *= noise_persistence
        frequency *= 2.0
    return total / np.abs(total).max()


def _smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _show_surface_arc_length(vertices):
    """Arc length along the fold for each vertex, and a mask of the ones that sit on the
    show surface. Vertices off the band get an arbitrary length and a False mask."""
    y, z = vertices[:, 1], vertices[:, 2]
    on_wall = (np.abs(y) < noise_edge) & (z > -noise_edge) & (z < wall_rise + noise_edge)
    on_facet = ((np.abs(z - y - wall_rise) < noise_edge * _ROOT2)
                & (y > -noise_edge) & (y < facet_run + noise_edge))
    on_top = ((np.abs(z - coupon_z) < noise_edge)
              & (y > facet_run - noise_edge) & (y < coupon_y + noise_edge))
    arc = np.where(on_wall, z,
                   np.where(on_facet, wall_rise + np.clip(y, 0.0, facet_run) * _ROOT2,
                            wall_rise + facet_slope + (y - facet_run)))
    return arc, on_wall | on_facet | on_top


def _fold_normals(arc):
    """The show surface's outward normal at each arc length, turned smoothly through
    `noise_blend` either side of an arris so the grain crosses a corner without a seam."""
    normals = np.zeros((len(arc), 3))
    wall = np.array([0.0, -1.0, 0.0])
    facet = np.array(_facet_normal)
    top = np.array([0.0, 0.0, 1.0])
    lower, upper = wall_rise, wall_rise + facet_slope
    weight = _smoothstep((arc - (lower - noise_blend)) / (2.0 * noise_blend))[:, None]
    normals = wall * (1.0 - weight) + facet * weight
    weight = _smoothstep((arc - (upper - noise_blend)) / (2.0 * noise_blend))[:, None]
    normals = normals * (1.0 - weight) + top * weight
    return normals / np.linalg.norm(normals, axis=1)[:, None]


def _noise_amplitude(x):
    """Amplitude by lateral station: three plateaus with short ramps between them."""
    edges = []
    values = []
    for zone, amplitude in enumerate(noise_amplitudes):
        low = -coupon_x / 2.0 + zone * zone_x
        edges += [low + zone_x * 0.12, low + zone_x * 0.88]
        values += [amplitude, amplitude]
    return np.interp(x, edges, values)


def _noise_taper(x, arc):
    """A factor that dies at every edge of the show surface, so the displaced band meets
    the plain bottom, back and side faces on their own planes."""
    return (_smoothstep((coupon_x / 2.0 - np.abs(x)) / noise_taper)
            * _smoothstep(arc / noise_taper)
            * _smoothstep((show_length - arc) / noise_taper))


def build_noise_mesh(out_dir):
    base = out_dir / "_texture-coupon-noise-base.stl"
    plain = cq.Workplane(obj=build_block().val().cut(build_label_cut("NOISE")))
    cq.exporters.export(plain, str(base), exportType="STL",
                        tolerance=0.01, angularTolerance=0.1)
    mesh = trimesh.load(str(base), process=True)
    base.unlink()

    vertices, faces = trimesh.remesh.subdivide_to_size(
        mesh.vertices, mesh.faces, max_edge=noise_max_edge)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    vertices = mesh.vertices.copy()

    arc, on_show = _show_surface_arc_length(vertices)
    amplitude = (_noise_amplitude(vertices[:, 0])
                 * _noise_taper(vertices[:, 0], arc)
                 * on_show)
    vertices += (_fold_normals(arc) * (_fbm(vertices) * amplitude)[:, None])
    return trimesh.Trimesh(vertices=vertices, faces=mesh.faces, process=True)


# --- Export ------------------------------------------------------------------------

plate_gap = 12.0


def _as_mesh(shape, out_dir, name):
    path = out_dir / f"_{name}.stl"
    cq.exporters.export(shape, str(path), exportType="STL",
                        tolerance=0.01, angularTolerance=0.1)
    mesh = trimesh.load(str(path), process=True)
    path.unlink()
    return mesh


def main():
    out_dir = _here.parent
    solids = [("flute", build_flute_coupon()),
              ("vee", build_vee_coupon()),
              ("facet", build_facet_coupon())]

    assembled = cq.Assembly(name="texture-coupons")
    for index, (name, shape) in enumerate(solids):
        out = out_dir / f"texture-coupon-{name}.step"
        export_assembly(one_body(shape, out.stem, C_COUPON), str(out))
        print(f"-> {out.name}")
        assembled.add(shape, name=name, color=C_COUPON,
                      loc=cq.Location(cq.Vector(0, index * (coupon_y + plate_gap), 0)))
    export_assembly(assembled, str(out_dir / "texture-coupons.step"))
    print("-> texture-coupons.step")

    meshes = [(name, _as_mesh(shape, out_dir, name)) for name, shape in solids]
    meshes.append(("noise", build_noise_mesh(out_dir)))

    plate = []
    for index, (name, mesh) in enumerate(meshes):
        out = out_dir / f"texture-coupon-{name}.stl"
        mesh.export(str(out))
        print(f"-> {out.name}  ({len(mesh.faces)} facets, "
              f"{'watertight' if mesh.is_watertight else 'NOT WATERTIGHT'})")
        seat = mesh.copy()
        seat.apply_translation([
            ((index % 2) - 0.5) * (coupon_x + plate_gap),
            ((index // 2) - 0.5) * (coupon_y + plate_gap),
            0.0])
        plate.append(seat)
    plate = trimesh.util.concatenate(plate)
    plate.export(str(out_dir / "texture-coupons-plate.stl"))
    print(f"-> texture-coupons-plate.stl  ({plate.extents[0]:.1f} × "
          f"{plate.extents[1]:.1f} × {plate.extents[2]:.1f} mm)")

    substitute_md(out_dir / "README.md", variables={
        "COUPON_X": f"{coupon_x:.4g} mm",
        "COUPON_Y": f"{coupon_y:.4g} mm",
        "COUPON_Z": f"{coupon_z:.4g} mm",
        "WALL_RISE": f"{wall_rise:.4g} mm",
        "FACET_SLOPE": f"{facet_slope:.4g} mm",
        "TOP_RUN": f"{top_run:.4g} mm",
        "ZONE_X": f"{zone_x:.4g} mm",
        "FLUTE_PITCHES": " / ".join(f"{p:.4g}" for p in flute_pitches) + " mm",
        "FLUTE_DEPTH": f"{flute_depth:.4g} mm",
        "VEE_PITCH": f"{vee_pitch:.4g} mm",
        "VEE_DEPTH_MIN": f"{vee_depth_min:.4g} mm",
        "VEE_DEPTH_MAX": f"{vee_depth_max:.4g} mm",
        "FACET_PITCH": f"{facet_pitch:.4g} mm",
        "FACET_RISE": f"{facet_rise:.4g} mm",
        "NOISE_FEATURE": f"{noise_feature:.4g} mm",
        "NOISE_AMPLITUDES": " / ".join(f"{a:.4g}" for a in noise_amplitudes) + " mm",
        "PLATE_X": f"{plate.extents[0]:.4g} mm",
        "PLATE_Y": f"{plate.extents[1]:.4g} mm",
    })
    print("-> README.md")


if __name__ == "__main__":
    main()
