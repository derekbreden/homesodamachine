"""The Sculpted base with the space under its mounting face filled down to the bed, in the CAD frame.

    make_union.py <faucet-shell-base.stl> <out.stl> <out.json>

The slicer reads the fill as part of the base, so it lays no support under the face and prints
the courses above it as ordinary inside courses. The sloped stage prints the fill's space itself."""
import json, sys, numpy as np, trimesh, manifold3d as m3
from shapely.geometry import Polygon
from shapely.ops import unary_union

TILT = np.radians(15.0)
S, C = np.sin(TILT), np.cos(TILT)
# CAD to plate: x' = x, y' = c y + s z, z' = -s y + c z.
R = np.array([[1, 0, 0], [0, C, S], [0, -S, C]], float)
SEMI = (29.0, 29.5)
EMBED = 0.05

def solid(vertices, faces):
    mesh = getattr(m3, "Mesh64", None)
    if mesh is not None:
        return m3.Manifold(mesh(vert_properties=np.asarray(vertices, np.float64), tri_verts=np.asarray(faces, np.uint64)))
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(vertices, np.float32), tri_verts=np.asarray(faces, np.uint32)))

def arrays(manifold):
    mesh = manifold.to_mesh64() if hasattr(manifold, "to_mesh64") else manifold.to_mesh()
    return np.asarray(mesh.vert_properties, float)[:, :3], np.asarray(mesh.tri_verts, np.int64)

def main():
    src, out, record = sys.argv[1:4]
    base = trimesh.load(src)
    assert base.is_watertight
    plate = base.vertices @ R.T
    bed = float(plate[:, 2].min())
    a = np.linspace(0, 2 * np.pi, 361)[:-1]
    ring = np.c_[SEMI[0] * np.cos(a), SEMI[1] * np.sin(a) * C]
    # The insert recesses stay open to the bed, so the fill seals no pocket.
    on = np.all(np.abs(base.vertices[base.faces][:, :, 2] - base.vertices[:, 2].min()) < 1e-6, axis=1)
    face = unary_union([Polygon(base.vertices[f][:, :2]) for f in base.faces[on]]).buffer(0)
    mouths = [Polygon(np.c_[np.array(h.coords)[:, 0], np.array(h.coords)[:, 1] * C]).buffer(0.02) for h in face.interiors if Polygon(h).area < 200.0]
    assert len(mouths) == 3, "expected three insert recess mouths"
    footprint = Polygon(ring).difference(unary_union(mouths))
    loops = [np.array(footprint.exterior.coords)[:-1]] + [np.array(h.coords)[:-1] for h in footprint.interiors]
    section = m3.CrossSection([l.tolist() for l in loops], m3.FillRule.EvenOdd)
    prism = m3.Manifold.extrude(section, 40.0).translate([0.0, 0.0, bed])
    # Under the face plane, a little inside the base. In the plate frame CAD z = 0 is s y' + c z' = 0.
    wedge = prism.trim_by_plane([0.0, -S, -C], -EMBED)
    turned = solid(plate, base.faces)
    union = turned + wedge
    assert union.status() == m3.Error.NoError and len(union.decompose()) == 1, "the filled base is not one closed body"
    v, f = arrays(union)
    for k in range(3):
        assert abs(v[:, k].min() - plate[:, k].min()) < 1e-5 and abs(v[:, k].max() - plate[:, k].max()) < 1e-5, ("bounds moved", k)
    # Back to CAD (R is orthonormal), with corners the cut left a hair apart made one corner.
    cad = np.round(v @ R, 5)
    _, first, index = np.unique(cad, axis=0, return_index=True, return_inverse=True)
    f = index[f]
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    result = trimesh.Trimesh(cad[first], f, process=False)
    assert result.is_watertight and result.is_winding_consistent, "the filled base is open"
    welded = np.unique(np.round(result.triangles.astype(np.float32).astype(np.float64).reshape(-1, 3) * 1e8).astype(np.int64), axis=0)
    assert len(welded) == len(result.vertices), "corners would weld in the preparer"
    result.export(out)
    json.dump({"purpose": "Records the fill under the Sculpted base's mounting face that the sloped stage prints.",
               "source": src, "triangles": int(len(result.faces)), "volume_mm3": float(result.volume),
               "base_volume_mm3": float(base.volume), "bed_plate_z_in_rotated_cad_mm": bed,
               "fill_embed_mm": EMBED, "rim_semi_axes_mm": SEMI, "tilt_degrees": 15.0}, open(record, "w"), indent=2)
    print("filled base", len(result.faces), "triangles; volume", round(result.volume, 1), "base", round(base.volume, 1), "bed", bed)

main()
