"""Connect the printed elbow pair with tapered cutaway webs. Run by hand.

The archived elbow mesh is the dimensional source. A web joins the legs where
their horizontal sections separate; another joins the two elbows. Attachment
necks are one nominal bead wide, with two-bead stock away from the part.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import manifold3d as md
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
import trimesh

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
Q = lambda name: f"{{{CORE}}}{name}"
WIDTH, NECK, OVERLAP, PITCH = 1.24, .62, .25, 23.


def archived_mesh(project):
    with zipfile.ZipFile(project) as z:
        root = ET.fromstring(z.read("3D/Objects/full_base_single_elbow.model"))
    mesh = root.find(f"{Q('resources')}/{Q('object')}/{Q('mesh')}")
    vertices = [[float(v.get(k)) for k in ("x", "y", "z")]
                for v in mesh.find(Q("vertices"))]
    faces = [[int(t.get(k)) for k in ("v1", "v2", "v3")]
             for t in mesh.find(Q("triangles"))]
    return trimesh.Trimesh(vertices, faces, process=True)


def solid(mesh):
    raw = md.Mesh64(np.asarray(mesh.vertices, dtype=np.float64),
                    np.asarray(mesh.faces, dtype=np.uint64))
    raw.merge()
    out = md.Manifold(raw)
    if out.status() != md.Error.NoError:
        raise ValueError(out.status())
    return out


def mesh_of(body):
    raw = body.to_mesh64()
    return trimesh.Trimesh(np.asarray(raw.vert_properties)[:, :3],
                           np.asarray(raw.tri_verts), process=True)


def sections(body, z):
    """Return each material island, retaining its bore holes."""
    loops = body.slice(z).to_polygons()
    positive, negative = [], []
    for loop in loops:
        p = Polygon(loop)
        signed = np.sum(loop[:, 0] * np.roll(loop[:, 1], -1)
                        - loop[:, 1] * np.roll(loop[:, 0], -1))
        (positive if signed > 0 else negative).append(p)
    stock = unary_union(positive).difference(unary_union(negative))
    return [p for p in getattr(stock, "geoms", [stock]) if not p.is_empty]


def tent(a, b, width=WIDTH, neck=NECK):
    """Eight-point plan: taper to a narrow neck at each attachment."""
    a, b = np.asarray(a), np.asarray(b)
    d = b - a
    length = np.linalg.norm(d)
    unit = d / length
    normal = np.array([-unit[1], unit[0]])
    shoulder = min(2., length / 3)
    stations = [(a, neck), (a + unit * shoulder, width),
                (b - unit * shoulder, width), (b, neck)]
    return np.array([p - normal * w / 2 for p, w in stations]
                    + [p + normal * w / 2 for p, w in reversed(stations)])


def loft(rings):
    vertices = np.vstack([np.c_[xy, np.full(len(xy), z)] for z, xy in rings])
    count = len(rings[0][1])
    faces = []
    for j in range(len(rings) - 1):
        for i in range(count):
            a, b = j * count + i, j * count + (i + 1) % count
            c, d = b + count, a + count
            faces.extend(((a, b, c), (a, c, d)))
    for i in range(1, count - 1):
        faces.extend(((0, i + 1, i),
                      ((len(rings)-1)*count, (len(rings)-1)*count+i,
                       (len(rings)-1)*count+i+1)))
    mesh = trimesh.Trimesh(vertices, faces, process=True)
    mesh.fix_normals()
    return solid(mesh)


def build(project, copies=2):
    if copies not in (1, 2):
        raise ValueError("This specimen supports one or two elbows")
    mesh = archived_mesh(project)
    body = solid(mesh)
    top = float(mesh.bounds[1, 2])
    calibration = sections(body, 10.)
    holes = [Polygon(r) for p in calibration for r in p.interiors]
    tube_hole = max(holes, key=lambda p: p.centroid.x)
    axis_intercept = (tube_hole.bounds[0] + tube_hole.bounds[2]) / 2 - 10.
    spine, legs = [], []
    # Closely spaced sections keep the attachment overlap on the curved mesh.
    heights = np.unique(np.r_[0., np.arange(.03, top - .005, .06), top - .002])
    for z in heights:
        islands = sorted(sections(body, max(.001, z)), key=lambda p: p.bounds[0])
        right = islands[-1]
        margin = min(.5, (right.bounds[2] - right.bounds[0]) / 4)
        x = np.clip(z + axis_intercept, right.bounds[0] + margin,
                    right.bounds[2] - margin)
        # The outside Y edge keeps the inter-elbow connection outside sockets.
        outline = Polygon(right.exterior)
        hit = outline.intersection(LineString([(x, -20), (x, 20)]))
        y = hit.bounds[3]
        spine.append((z, tent((x, y - OVERLAP), (x, PITCH - y + OVERLAP))))
        if len(islands) == 2:
            left, right = islands
            l = left.intersection(LineString([(-30, 0), (30, 0)]))
            r = right.intersection(LineString([(-30, 0), (30, 0)]))
            if not l.is_empty and not r.is_empty:
                legs.append((z, tent((l.bounds[2] - OVERLAP, 0),
                                     (r.bounds[0] + OVERLAP, 0))))
    webs = [loft(spine)] if copies == 2 else []
    if legs:
        # Start in the solid heel before its first split section, so a gap
        # cannot appear between the sampled split and a slicer's layer plane.
        legs.insert(0, (legs[0][0] - .18, legs[0][1]))
        fin = loft(legs)
        webs += [fin.translate((0, PITCH * i, 0)) for i in range(copies)]
    web = md.Manifold.batch_boolean(webs, md.OpType.Add)
    pair = md.Manifold.batch_boolean([body.translate((0, PITCH * i, 0))
                                      for i in range(copies)], md.OpType.Add)
    joined = pair + web
    if joined.status() != md.Error.NoError or len(joined.decompose()) != 1:
        raise ValueError("The webbed pair is not one connected solid")
    if (pair - joined).volume() > 1e-5:
        raise ValueError("An original elbow lost material")
    record = dict(web_width_mm=WIDTH, attachment_neck_mm=NECK,
                  surface_overlap_mm=OVERLAP, elbow_pitch_mm=PITCH, elbows=copies,
                  section_spacing_mm=.06,
                  leg_web_z_range_mm=[legs[0][0], legs[-1][0]],
                  original_pair_volume_mm3=pair.volume(),
                  combined_volume_mm3=joined.volume(),
                  added_volume_mm3=(joined - pair).volume(),
                  original_material_removed_mm3=(pair - joined).volume(),
                  mesh_connected_components=len(joined.decompose()),
                  scope="Geometric connectivity; stability, clean removal and string reduction require the printed result.")
    return mesh_of(joined), mesh_of(web - pair), record
