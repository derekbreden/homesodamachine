"""The Pour V3 faucet module, built from frozen complete machine parts.

Source factory meshes are immutable inputs; native
manufacturing frames are distinct from assembled display frames, and the
Industrial cover has an explicitly elastic seated display model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile

import cadquery as cq
import numpy as np
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
HW = ROOT / "hardware"
HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs/faucet"
ASSETS = ROOT / ".cache/the-pour-v3/faucet-assets"
FAUCET = HW / "printed-parts/faucet"
sys.path[:0] = [str(HW / "scripts"), str(HW / "printed-parts/cadlib"),
               str(FAUCET), str(FAUCET / "faucet-shell"), str(FAUCET / "industrial"),
               str(FAUCET / "umbilical-organizer"), str(FAUCET / "tube-collar")]
from print_mesh import print_mesh
from _cadq_export import export_assembly
import _mesh_payload

ROOT_POINT = (-80.0, 138.0, 146.0)
HYBRID_JOIN_Z = 67.5
LEVER_LOCAL_BAR_Y = 41.8
LEVER_PLACEMENT = (0.0, -42.5, 49.5)
BAR_RADIUS = 2.295520914102124
BAR_SPAN = 8.42
BAR_Z = LEVER_PLACEMENT[2] - 5.55 + BAR_RADIUS
BAR_Y = LEVER_PLACEMENT[1] + LEVER_LOCAL_BAR_Y
MOUNT_AXES = ((22.5, -2.0), (-22.5, -2.0), (0.0, -22.3))
SOURCE_PATHS = {
    "industrial-base": "hardware/printed-parts/faucet/industrial/industrial-shell-base.step",
    "sculpted-base": "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base.step",
    "tip": "hardware/printed-parts/faucet/faucet-shell/faucet-shell-tip.step",
    "cover-relaxed": "hardware/printed-parts/faucet/industrial/industrial-display-cover.step",
    "plate": "hardware/printed-parts/faucet/industrial/industrial-above-counter-plate.step",
    "gasket": "hardware/printed-parts/faucet/industrial/industrial-above-counter-gasket.step",
    "lever": "hardware/printed-parts/faucet/lever-replica/lever-replica.step",
    "organizer": "hardware/printed-parts/faucet/umbilical-organizer/umbilical-organizer.step",
    "thimble": "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring.step",
    "tube-collar": "hardware/printed-parts/faucet/tube-collar/tube-collar-carb.step",
    "donor": "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step",
}
EVIDENCE_PATHS = [
    "hardware/printed-parts/faucet/industrial/physical-acceptance.json",
    "hardware/printed-parts/faucet/industrial/geometry-check.json",
    "hardware/printed-parts/faucet/industrial/display-cover-check.json",
    "hardware/printed-parts/faucet/industrial/prints/2026-10-11-centered-mounting-review-mark2/geometry-review.json",
    "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",
    "hardware/printed-parts/faucet/lever-replica/contact-datums.json",
    "hardware/printed-parts/faucet/lever-replica/evidence/datums.json",
    "hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json",
    "hardware/printed-parts/faucet/tpu-o-ring/README.md",
    "hardware/printed-parts/faucet/tube-collar/tube_collar.py",
    "hardware/printed-parts/faucet/industrial/industrial_display_cover.py",
    "hardware/printed-parts/faucet/industrial/industrial_faucet.py",
    "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py",
    "hardware/printed-parts/faucet/refresh_print_project.py",
    "hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.py",
    "hardware/printed-parts/faucet/tpu-o-ring/tpu_o_ring.py",
    "hardware/printed-parts/faucet/lever-replica/lever_replica.py",
    "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass_reference.py",
    "hardware/printed-parts/gaskets.3mf",
    "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring-85A-6mm.3mf",
]
POSE_AUTHORITIES = {
    "FB": "hardware/printed-parts/faucet/refresh_print_project.py#PARTS",
    "FT": "hardware/printed-parts/faucet/refresh_print_project.py#PARTS",
    "FC": "hardware/printed-parts/faucet/refresh_print_project.py#PARTS",
    "FPD": "hardware/printed-parts/faucet/industrial/industrial_faucet.py#build_above_counter_plate; reference adaptation retains native plate-down direction",
    "FG": "hardware/printed-parts/gaskets.3mf; native plate-down direction",
    "FL": "hardware/printed-parts/faucet/lever-replica/lever_replica.py#print_pose",
    "FS": "hardware/printed-parts/faucet/tpu-o-ring/tpu_o_ring.py#build_o_ring; source cap-down axis",
    "FO": "hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.py#main",
    "TC": "hardware/printed-parts/faucet/tube-collar/tube_collar.py; source flat-face-down direction",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def matrix(point=(0, 0, 0), rot=(0, 0, 0)):
    result = np.eye(4)
    for axis, angle in enumerate(rot):
        if angle:
            result = trimesh.transformations.rotation_matrix(math.radians(angle), np.eye(3)[axis]) @ result
    result[:3, 3] = point
    return result


def transformed(shape, transform):
    """Rigid CAD transform with no spline conversion of source analytic faces."""
    return shape.moved(cq.Location(cq.Plane(
        origin=tuple(transform[:3, 3]), xDir=tuple(transform[:3, 0]),
        normal=tuple(transform[:3, 2]))))


def transformed_mesh(mesh, transform):
    result = mesh.copy()
    result.apply_transform(transform)
    return result


def capture_inputs():
    """Capture once; subsequent development uses exactly the captured bytes."""
    INPUTS.mkdir(parents=True, exist_ok=True)
    index = INPUTS / "sources.json"
    if index.exists():
        return json.loads(index.read_text())
    rows = {}
    for key, path in SOURCE_PATHS.items():
        source = ROOT / path
        for suffix in (".step", ".stl"):
            original = source.with_suffix(suffix)
            if not original.exists():
                continue
            data = original.read_bytes()
            destination = INPUTS / (key + suffix + ".gz")
            destination.write_bytes(gzip.compress(data, mtime=0))
            rows[key + suffix] = {"source": str(original.relative_to(ROOT)),
                "snapshot": str(destination.relative_to(HERE)), "sha256": sha(data),
                "snapshot_sha256": sha(destination.read_bytes())}
    lever_print = FAUCET / "lever-replica/lever-replica-side-down.stl"
    data = lever_print.read_bytes()
    destination = INPUTS / "lever-side-down.stl.gz"
    destination.write_bytes(gzip.compress(data, mtime=0))
    rows["lever-side-down.stl"] = {"source": str(lever_print.relative_to(ROOT)),
        "snapshot": str(destination.relative_to(HERE)), "sha256": sha(data),
        "snapshot_sha256": sha(destination.read_bytes())}
    evidence = [{"path": p, "sha256": sha((ROOT / p).read_bytes())}
                for p in EVIDENCE_PATHS if (ROOT / p).exists()]
    # The source's nominal seated model is distinct from the relaxed factory
    # mesh; this is the actual full-span elastic display pose, not a rigid fit.
    from industrial_display_cover import build_seated_display_cover
    seated = build_seated_display_cover().val()
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "cover-seated.step"
        cq.exporters.export(seated, str(path))
        data = path.read_bytes()
    destination = INPUTS / "cover-seated.step.gz"
    destination.write_bytes(gzip.compress(data, mtime=0))
    rows["cover-seated.step"] = {"source": "hardware/printed-parts/faucet/industrial/industrial_display_cover.py#build_seated_display_cover",
        "snapshot": str(destination.relative_to(HERE)), "sha256": sha(data),
        "snapshot_sha256": sha(destination.read_bytes()), "role": "nominal elastic seated display model"}
    data = print_mesh(seated).export(file_type="stl")
    destination = INPUTS / "cover-seated.stl.gz"
    destination.write_bytes(gzip.compress(data, mtime=0))
    rows["cover-seated.stl"] = {**rows["cover-seated.step"], "snapshot": str(destination.relative_to(HERE)),
        "sha256": sha(data), "snapshot_sha256": sha(destination.read_bytes())}
    record = {"schema": 1, "sources": rows, "authority_files": evidence,
        "scope": "Factory complete parts captured in canonical source frames. Seated cover is the source nominal elastic model. Adapted parts and their comparison scope are recorded separately."}
    index.write_text(json.dumps(record, indent=2) + "\n")
    return record


def source_bytes(key):
    record = capture_inputs()["sources"][key]
    return gzip.decompress((HERE / record["snapshot"]).read_bytes())


def source_shape(key):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "source.step"
        path.write_bytes(source_bytes(key + ".step"))
        return cq.importers.importStep(str(path)).val()


def source_mesh(key, shape=None):
    rows = capture_inputs()["sources"]
    if key + ".stl" in rows:
        return trimesh.load_mesh(io.BytesIO(source_bytes(key + ".stl")), file_type="stl", process=False)
    return print_mesh(shape if shape is not None else source_shape(key))


def triangle_keys(mesh, above_z=None):
    triangles = mesh.triangles.astype(np.float32)
    if above_z is not None:
        triangles = triangles[np.min(triangles[:, :, 2], axis=1) > above_z + 1e-4]
    # A facet's identity ignores vertex ordering but retains every float32
    # coordinate. This verifies actual unchanged triangles, not just distance.
    rows = []
    for triangle in triangles:
        order = np.lexsort((triangle[:, 2], triangle[:, 1], triangle[:, 0]))
        rows.append(triangle[order].tobytes())
    return set(rows)


def hybrid_base():
    industrial = source_shape("industrial-base")
    sculpted = source_shape("sculpted-base")
    left = industrial.intersect(box(-100, 0, -200, 100, -1, HYBRID_JOIN_Z + .2))
    right = sculpted.intersect(box(0, 100, -200, 100, -1, HYBRID_JOIN_Z + .2))
    upper = industrial.intersect(box(-100, 100, -200, 100, HYBRID_JOIN_Z, 400))
    shape = left.fuse(right, upper).clean()
    # Preserve the Sculpted factory mesh's flutes, absent from smooth STEP.
    im = source_mesh("industrial-base")
    sm = source_mesh("sculpted-base")
    # STL repeats vertices per face; the boolean engine needs connected index
    # topology. Position welding leaves the factory facet coordinates intact.
    im.merge_vertices()
    sm.merge_vertices()
    cutter = trimesh.creation.box(extents=(100, 300, HYBRID_JOIN_Z + 1))
    cutter.apply_translation((50, -50, (HYBRID_JOIN_Z - 1) / 2))
    retained = trimesh.boolean.difference([im, cutter], engine="manifold", check_volume=False)
    right_mesh = trimesh.boolean.intersection([sm, cutter], engine="manifold", check_volume=False)
    mesh = trimesh.boolean.union([retained, right_mesh], engine="manifold", check_volume=False)
    source_triangles = triangle_keys(im, HYBRID_JOIN_Z)
    retained_triangles = triangle_keys(mesh, HYBRID_JOIN_Z)
    proof = {"valid_one_solid": bool(shape.isValid() and len(shape.Solids()) == 1),
        "hybrid_half_plane": "X=0; Industrial X<0, Sculpted X>0 below Z67.5; complete Industrial upper remains",
        "stl_includes_exact_source_sculpted_flutes": True,
        "source_upper_facets": len(source_triangles),
        "missing_exact_source_upper_facets": len(source_triangles - retained_triangles),
        "mesh_watertight": bool(mesh.is_watertight), "mesh_winding_consistent": bool(mesh.is_winding_consistent),
        "source_upper_missing_cad_volume_mm3": float(upper.cut(shape).Volume()),
        "common_mounting_cavities": "Both source halves retain the same native plate sockets and donor envelope; only exterior style differs."
    }
    return shape, mesh, proof


def closed_hybrid_print_mesh(mesh, manufacturing_transform):
    """Resolve coincident planar half-join faces in final STL coordinates.

    The two source half meshes meet on canonical X=0. Their boolean contains
    opposing coplanar sheet faces whose coincident vertices merge on STL
    reload. Cancel their common planar area, retaining the legitimate exposed
    style step and every non-planar source facet. The analytic hybrid is
    unchanged. This treatment belongs only to this hybrid's center join.
    """
    import shapely
    from shapely.geometry import Polygon

    original = trimesh.load_mesh(io.BytesIO(mesh.export(file_type="stl")),
                                 file_type="stl", process=True)
    join_x = float(np.float32(manufacturing_transform[0, 3]))
    planar = ((np.ptp(original.triangles[:, :, 0], axis=1) < 1e-12)
              & (np.abs(original.triangles[:, 0, 0] - join_x) < 1e-9))
    regions = []
    for sign in (1, -1):
        faces = np.flatnonzero(planar & (original.face_normals[:, 0] * sign > .9)
                               & (original.area_faces > 1e-12))
        regions.append(shapely.union_all([
            Polygon(original.triangles[index, :, 1:]) for index in faces]))
    new_join = []
    for sign, region in ((1, regions[0].difference(regions[1])),
                         (-1, regions[1].difference(regions[0]))):
        for triangle in shapely.get_parts(shapely.constrained_delaunay_triangles(region)):
            yz = np.asarray(triangle.exterior.coords)[:3]
            xyz = np.c_[np.full(3, join_x), yz]
            if np.cross(xyz[1] - xyz[0], xyz[2] - xyz[0])[0] * sign < 0:
                xyz = xyz[[0, 2, 1]]
            new_join.append(xyz)
    triangles = np.concatenate([original.triangles[~planar], np.asarray(new_join)])
    resolved = trimesh.Trimesh(vertices=triangles.reshape(-1, 3),
                               faces=np.arange(len(triangles) * 3).reshape(-1, 3),
                               process=True)
    # Round the reconstructed join to the binary STL representation before
    # closing its one subprecision triangle at an existing contour edge.
    resolved = trimesh.load_mesh(io.BytesIO(resolved.export(file_type="stl")),
                                 file_type="stl", process=True)
    counts = np.bincount(resolved.edges_unique_inverse)
    boundary_ids = np.flatnonzero(counts == 1)
    sliver_area = 0.
    if len(boundary_ids):
        edges = resolved.edges_unique[boundary_ids]
        vertices = list(np.unique(edges))
        if len(edges) != 3 or len(vertices) != 3:
            raise ValueError("Hybrid join has an unexpected non-triangular export boundary")
        xyz = resolved.vertices[vertices]
        sliver_area = float(np.linalg.norm(np.cross(xyz[1] - xyz[0], xyz[2] - xyz[0])) / 2)
        if sliver_area > 3e-6 or np.max(np.abs(xyz[:, 0] - join_x)) > 1e-9:
            raise ValueError("Hybrid join boundary exceeds its bounded rounding-sliver scope")
        a, b = resolved.edges[np.flatnonzero(np.isin(resolved.edges_unique_inverse, boundary_ids))[0]]
        c = next(v for v in vertices if v not in (a, b))
        resolved.faces = np.vstack([resolved.faces, [b, a, c]])
    resolved = trimesh.load_mesh(io.BytesIO(resolved.export(file_type="stl")),
                                 file_type="stl", process=True)
    before_native = transformed_mesh(original, np.linalg.inv(manufacturing_transform))
    upper = np.flatnonzero(np.min(before_native.triangles[:, :, 2], axis=1) > HYBRID_JOIN_Z + 1e-4)
    upper_keys = triangle_keys(original.submesh([upper], append=True))
    counts = np.bincount(resolved.edges_unique_inverse)
    proof = {"scope": "Coplanar center-join STL reconstruction only; analytic CAD and non-planar source faces unchanged.",
        "watertight": bool(resolved.is_watertight),
        "winding_consistent": bool(resolved.is_winding_consistent),
        "body_count": int(resolved.body_count),
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
        "cancelled_opposed_join_area_mm2": float(regions[0].intersection(regions[1]).area),
        "rounding_sliver_area_mm2": sliver_area,
        "signed_volume_difference_mm3": float(resolved.volume - original.volume),
        "unchanged_original_manufacturing_upper_facets": len(upper_keys),
        "missing_original_manufacturing_upper_facets": len(upper_keys - triangle_keys(resolved))}
    if not proof["watertight"] or not proof["winding_consistent"] or proof["body_count"] != 1:
        raise ValueError("Hybrid join reconstruction did not produce its connected closed surface")
    return resolved, proof


def donor_bar():
    return cq.Solid.makeCylinder(BAR_RADIUS, BAR_SPAN,
        cq.Vector(-BAR_SPAN / 2, BAR_Y, BAR_Z), cq.Vector(1, 0, 0))


def donor_proxy():
    """Nominal donor envelope rooted in the actual circular mounting plate."""
    plate = source_shape("plate")
    core = source_shape("donor").intersect(box(-50, 50, -50, 50, -4, 80))
    # The current actual tube axis is +8.875; the dimensional donor reference
    # port is +8.750. Fill/re-cut this private stand-in only, same Ø10/depth20.
    old_port = cq.Solid.makeCylinder(5, 20, cq.Vector(0, 8.75, 19))
    new_port = cq.Solid.makeCylinder(5, 20.1, cq.Vector(0, 8.875, 19))
    core = core.fuse(old_port).cut(new_port).clean()
    bar = donor_bar()
    rod = cq.Solid.makeCylinder(1.2, BAR_Z - 38.8, cq.Vector(0, BAR_Y, 38.8))
    shape = plate.fuse(core, rod, bar).clean()
    return shape, {"valid_one_solid": bool(shape.isValid() and len(shape.Solids()) == 1),
        "adaptation": "Printed dimensional donor reference rooted into the source above-counter plate. Inactive shank ends at plate underside Z−4; above-counter envelope is retained. Port moved +0.125 mm in Y to source tube axis +8.875. Added nominal Ø2.4 plunger rod and observed-diameter transverse bar.",
        "bar_diameter_mm": 2 * BAR_RADIUS, "bar_span_mm": BAR_SPAN,
        "bar_center_mm": [0, BAR_Y, BAR_Z], "bar_axis": "+X",
        "retention_scope": "Source lever channel/ledges around nominal bar, source neck/tube bay and native M3 plate/base fastening. Modeled alignment only; physical friction, insertion, movement and load untested.",
        "plate_outer_pedestals_and_fastening_seats_unchanged": True}


def counter_gasket():
    """Source gasket with the three native M3-axis cabinet perforations."""
    source = source_shape("gasket")
    holes = [cq.Solid.makeCylinder(1.95, 2.2, cq.Vector(x, y, -6.1)) for x, y in MOUNT_AXES]
    shape = source.cut(*holes).clean()
    original_mesh = source_mesh("gasket")
    original_mesh.merge_vertices()
    cutters = [print_mesh(hole) for hole in holes]
    mesh = trimesh.boolean.difference([original_mesh, *cutters], engine="manifold", check_volume=False)
    notes = {"adaptation": "Three Ø3.9 through-perforations on the unchanged source plate/base M3 axes for the cabinet fastener stack; all other source gasket lands retain their geometry.",
        "source_axes_xy_mm": [list(a) for a in MOUNT_AXES], "through_diameter_mm": 3.9,
        "outer_stock_beyond_screw_holes_mm": min(29.5-math.hypot(x,y)-1.95 for x,y in MOUNT_AXES),
        "scope": "Two-millimetre source gasket with declared cabinet-joint perforations. Compression, sealing and load acceptance do not transfer to this unprinted stack."}
    return shape, mesh, notes


@dataclass
class Feature:
    id: str
    name: str
    native: cq.Shape
    native_mesh: trimesh.Trimesh
    print_rotation_deg: tuple = (0, 0, 0)
    local_assembly_matrix: np.ndarray = field(default_factory=lambda: np.eye(4))
    material: str = "PET-GF"
    source_keys: tuple = ()
    display_native: cq.Shape | None = None
    display_native_mesh: trimesh.Trimesh | None = None
    notes: dict = field(default_factory=dict)
    recipe: dict = field(default_factory=dict)
    volumes: list = field(default_factory=list)
    _resolved_print_mesh: trimesh.Trimesh | None = field(default=None, init=False, repr=False)

    def manufacturing_matrix(self):
        rotation = matrix(rot=self.print_rotation_deg)
        rotated = transformed_mesh(self.native_mesh, rotation)
        bounds = rotated.bounds
        rotation[:3, 3] = [-(bounds[0, 0] + bounds[1, 0])/2,
                           -(bounds[0, 1] + bounds[1, 1])/2, -bounds[0, 2]]
        return rotation

    @property
    def shape(self):
        return transformed(self.native, self.manufacturing_matrix())

    @property
    def mesh(self):
        manufacturing = self.manufacturing_matrix()
        mesh = transformed_mesh(self.native_mesh, manufacturing)
        if self.id == "FB":
            if self._resolved_print_mesh is None:
                self._resolved_print_mesh, proof = closed_hybrid_print_mesh(mesh, manufacturing)
                self.notes["style_comparison"]["binary_stl_join"] = proof
            return self._resolved_print_mesh
        return mesh

    def assembly_matrix(self, root=ROOT_POINT):
        return matrix(root) @ self.local_assembly_matrix @ np.linalg.inv(self.manufacturing_matrix())

    def assembly_shape(self, root=ROOT_POINT):
        shape = self.display_native if self.display_native is not None else self.native
        return transformed(shape, matrix(root) @ self.local_assembly_matrix)

    def assembly_mesh(self, root=ROOT_POINT):
        if self.id == "FB":
            return transformed_mesh(self.mesh, self.assembly_matrix(root))
        mesh = self.display_native_mesh if self.display_native_mesh is not None else self.native_mesh
        return transformed_mesh(mesh, matrix(root) @ self.local_assembly_matrix)


def build_faucet():
    capture_inputs()
    print("Building hybrid source foot", flush=True)
    hybrid, hm, hp = hybrid_base()
    donor, dp = donor_proxy()
    gasket, gm, gp = counter_gasket()
    tube = source_shape("tube-collar")
    solids = tube.Solids()
    tube_body = next(s for s in solids if abs(s.BoundingBox().ylen - 30) < 1e-6)
    tube_word = cq.Compound.makeCompound([s for s in solids if s is not tube_body])
    organizer_xy = (0, (7.85**2 + 17.125**2) / (2 * 17.125))
    organizer_bores = (("S", (0, 0), 6.65), ("F1", (7.85, 17.125), 6.65),
        ("F2", (-7.85, 17.125), 6.65), ("D", (0, 16.225), 4.4), ("SIG", (0, 21.4875), 5.4))
    baseline = {"initial_layer_height_mm": .20, "layer_height_mm": .24,
        "supports_enabled": True, "support_type": "tree(auto)", "support_style": "default",
        "support_top_z_distance": .45, "seam_gap": "15%", "wall_loops": 2}
    gasket_recipe = {"initial_layer_height_mm": .30, "layer_height_mm": .18,
        "supports_enabled": False, "wall_generator": "arachne", "wall_loops": 2,
        "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag",
        "bottom_shell_layers": 3, "top_shell_layers": 3,
        "wall_sequence": "inner wall/outer wall", "infill_wall_overlap": "15%",
        "nominal_nozzle_diameter_mm": .6, "material_hardness_shore_a": 85, "spiral_mode": False,
        "recipe_authority": "hardware/printed-parts/gaskets.3mf"}
    thimble_recipe = {**gasket_recipe, "wall_generator": "classic", "wall_loops": 1,
        "sparse_infill_density": "0%", "sparse_infill_pattern": "grid", "top_shell_layers": 0,
        "spiral_mode": True, "spiral_mode_smooth": True, "elefant_foot_compensation": 0,
        "recipe_authority": "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring-85A-6mm.3mf"}
    features = {
        "FB": Feature("FB", "Industrial / Sculpted hybrid full faucet body", hybrid, hm,
            print_rotation_deg=(-15, 0, 0), source_keys=("industrial-base", "sculpted-base"),
            notes={"style_comparison": hp, "scope": "Intentional hybrid reference foot. Both styles use one object-wide print generator; no production-faucet or matched independent-generator claim."},
            recipe={**baseline, "wall_generator": "arachne", "fine_bands_print_z_mm": [[13.4, 29.0], [55.16, 68.12]],
                "fine_layer_height_mm": .12, "foot_wall_loops": 6, "foot_infill_percent": 100}),
        "FT": Feature("FT", "Complete shared faucet tip", source_shape("tip"), source_mesh("tip"),
            print_rotation_deg=(-105, 0, 0), source_keys=("tip",), recipe=baseline.copy()),
        "FC": Feature("FC", "Complete Industrial elastic display cover", source_shape("cover-relaxed"), source_mesh("cover-relaxed"),
            print_rotation_deg=(-50, 0, 0), source_keys=("cover-relaxed", "cover-seated"),
            display_native=source_shape("cover-seated"), display_native_mesh=source_mesh("cover-seated"),
            notes={"display_pose": "Actual source nominal seated elastic model; the relaxed manufacturing body is separate and must elastically spread on installation.",
                   "no_rigid_print_mesh_to_seated_transform": True}, recipe=baseline.copy()),
        "FPD": Feature("FPD", "Source mounting plate with rooted nominal donor mate", donor, print_mesh(donor),
            source_keys=("plate", "donor"), notes=dp, recipe=baseline.copy()),
        "FG": Feature("FG", "Source above-counter gasket with native-axis fastener holes", gasket, gm,
            material="TPU", source_keys=("gasket",), notes=gp, recipe=gasket_recipe),
        "FL": Feature("FL", "Complete accepted scan-derived lever", source_shape("lever"), source_mesh("lever"),
            print_rotation_deg=(0, 90, 0), local_assembly_matrix=matrix(LEVER_PLACEMENT), source_keys=("lever", "lever-side-down"),
            notes={"assembly_alignment": "Modeled dimensional donor alignment; source measured installed transform is null. Lever source geometry is untouched.",
                   "local_to_faucet_matrix_mm": matrix(LEVER_PLACEMENT).tolist()}, recipe=baseline.copy()),
        "FS": Feature("FS", "Complete source TPU port thimble", source_shape("thimble"), source_mesh("thimble"),
            local_assembly_matrix=matrix((0, 8.875, 21.9)), material="TPU", source_keys=("thimble",),
            notes={"intentional_interference": {"port_radial_mm": .22, "tube_radial_mm": .1625},
                   "scope": "Source elastic sealing geometry on a printed nominal port. Physical seal, friction and capture are untested."},
            recipe=thimble_recipe),
        "FO": Feature("FO", "Complete source umbilical organizer", source_shape("organizer"), source_mesh("organizer"),
            local_assembly_matrix=matrix((*organizer_xy, -98)), source_keys=("organizer",),
            notes={"native_top_z_mm": -88, "bores": [{"id": k, "axis_faucet_xy_mm": list(xy), "diameter_or_slot_length_mm": d} for k, xy, d in organizer_bores],
                   "retention": "Source full organizer on actual tube bundle inside cabinet; final routing and tube-end capture belong to the counter module."}, recipe=baseline.copy()),
        "TC": Feature("TC", "Complete source SODA tube collar", tube, print_mesh(tube),
            print_rotation_deg=(180, 0, 0), local_assembly_matrix=matrix((0, 0, -99), (-90, 0, 0)),
            source_keys=("tube-collar",), notes={"flat_face_down": True,
                "scope": "Source Ø6.68 horizontal bore. PETG/0.2 nozzle calibration does not establish PET-GF bore behavior. Final closed-end tube routing retains the collar."},
            recipe={**baseline, "supports_enabled": False},
            volumes=[{"id": "TC-body", "shape": tube_body, "mesh": print_mesh(tube_body), "filament_slot": 1},
                     {"id": "TC-word", "shape": tube_word, "mesh": print_mesh(tube_word), "filament_slot": 2}]),
    }
    # Accepted lever manufacturing triangles are authoritative, rather than a
    # new CAD remesh. Inverse the exact source print pose to native local X/Y/Z.
    lp = source_mesh("lever-side-down")
    accepted_matrix = matrix((0, 0, 6.2), (0, 90, 0))
    features["FL"].native_mesh = transformed_mesh(lp, np.linalg.inv(accepted_matrix))
    return features


def check_faucet(features):
    fb, ft, fc, fpd, fl, fs = (features[k].assembly_shape((0, 0, 0)) for k in ("FB", "FT", "FC", "FPD", "FL", "FS"))
    pairs = {}
    for aid, bid, a, b in (("FB", "FT", fb, ft), ("FT", "FC", ft, fc), ("FB", "FPD", fb, fpd),
                          ("FL", "FB", fl, fb), ("FL", "FPD", fl, fpd), ("FS", "FPD", fs, fpd)):
        pairs[aid + "/" + bid] = float(a.intersect(b).Volume())
    lever = features["FL"].native
    local_bar = donor_bar().translate((0, -LEVER_PLACEMENT[1], -LEVER_PLACEMENT[2]))
    native_plate = source_shape("plate").intersect(box(-50, 50, -50, 50, -4.1, .000001))
    kept_plate = fpd.intersect(box(-50, 50, -50, 50, -4.1, .000001))
    return {"schema": 1, "status": "nominal geometry review; assembly unprinted", "root_mm": list(ROOT_POINT),
        "hybrid": features["FB"].notes["style_comparison"], "donor": features["FPD"].notes,
        "rigid_pair_overlap_mm3": pairs,
        "lever_bar_overlap_mm3": float(lever.intersect(local_bar).Volume()),
        "source_plate_stock_missing_below_z0_mm3": float(native_plate.cut(kept_plate).Volume()),
        "intentional_elastic_interference": {"FS/FPD": "TPU thimble Ø10.44 in nominal Ø10 port; expected undeformed overlap, not a rigid-clearance defect."},
        "counter_mounting_axes": [{"source_xy_mm": [x, y], "world_xy_mm": [ROOT_POINT[0]+x, ROOT_POINT[1]+y],
            "direction": "+Z", "source_clearance_diameter_mm": 3.9, "source_head_recess_diameter_mm": 6.15}
            for x, y in MOUNT_AXES],
        "below_counter_envelopes_mm": {k: features[k].assembly_mesh().bounds.tolist() for k in ("FO", "TC")},
        "counter_gasket_mounting_scope": features["FG"].notes,
        "scope": "Exact-source nominal CAD placement and current hybrid construction only. No physical insertion, friction, spring force, seal, loading or life claim. Counter/core integration and fastening hardware remain separately reviewed."}


def export_cache(features=None):
    features = features or build_faucet()
    ASSETS.mkdir(parents=True, exist_ok=True)
    rows, objects = [], []
    source_index = capture_inputs()
    for ident, feature in features.items():
        print("Export", ident, flush=True)
        step = ASSETS / (ident + ".step")
        stl = ASSETS / (ident + ".stl")
        cq.exporters.export(feature.shape, str(step))
        feature.mesh.export(stl)
        mfg = feature.manufacturing_matrix()
        row = {"id": ident, "name": feature.name, "material": feature.material,
            "step": str(step.relative_to(ROOT)), "step_sha256": sha(step.read_bytes()),
            "stl": str(stl.relative_to(ROOT)), "stl_sha256": sha(stl.read_bytes()),
            "manufacturing_frame": {"id": ident + "-native-print", "baked_into_meshes": True,
                "from_source_matrix_mm": mfg.tolist(), "authority": POSE_AUTHORITIES[ident]},
            "assembly_matrix_mm": feature.assembly_matrix().tolist(),
            "assembly_source_matrix_mm": (matrix(ROOT_POINT) @ feature.local_assembly_matrix).tolist(),
            "print_rotation_xyz_deg": list(feature.print_rotation_deg),
            "print_bounds_mm": feature.mesh.bounds.tolist(), "print_recipe": feature.recipe,
            "source_keys": list(feature.source_keys), "notes": feature.notes}
        if feature.material == "TPU":
            row["material_hardness_shore_a"] = 85
        volumes = []
        if feature.volumes:
            for volume in feature.volumes:
                vpath = ASSETS / (volume["id"] + ".stl")
                transformed_mesh(volume["mesh"], mfg).export(vpath)
                volumes.append({"id": volume["id"], "part_id": ident,
                    "stl": str(vpath.relative_to(ROOT)), "stl_sha256": sha(vpath.read_bytes()),
                    "transform_mm": np.eye(4).tolist(), "filament_slot": volume["filament_slot"], "region_overrides": {}})
        else:
            volumes.append({"id": ident, "part_id": ident, "stl": row["stl"], "stl_sha256": row["stl_sha256"],
                "transform_mm": np.eye(4).tolist(), "filament_slot": 1, "region_overrides": {}})
        cohort = ("TPU85A-spiral" if feature.recipe.get("spiral_mode") else "TPU85A") if feature.material == "TPU" else "colour" if feature.volumes else "rigid"
        recipe = feature.recipe
        overrides = {"layer_height": str(recipe["layer_height_mm"]),
            "enable_support": "1" if recipe["supports_enabled"] else "0"}
        for key in ("support_type", "support_style", "support_top_z_distance", "seam_gap", "wall_loops",
                    "wall_generator", "sparse_infill_density", "sparse_infill_pattern", "bottom_shell_layers",
                    "top_shell_layers", "wall_sequence", "infill_wall_overlap"):
            if key in recipe:
                overrides[key] = str(recipe[key])
        ranges = [{"min_z_mm": low, "max_z_mm": high,
            "options": {"layer_height": str(recipe["fine_layer_height_mm"])}}
            for low, high in recipe.get("fine_bands_print_z_mm", [])]
        modifiers = []
        if ident == "FB":
            modifiers.append({"id": "FB-native-continuous-foot", "subtype": "modifier_part",
                "bounds_mm": [[-30.5, -30.5, -.01], [30.5, 30.5, 14.01]], "transform_mm": mfg.tolist(),
                "options": {"wall_loops": "6", "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag"}})
        objects.append({"id": ident, "cohort": cohort, "manufacturing_frame": row["manufacturing_frame"],
            "volumes": volumes, "object_overrides": overrides, "layer_ranges": ranges, "modifiers": modifiers})
        if feature.display_native is not None:
            display_step = ASSETS / (ident + "-seated-display.step")
            display_stl = ASSETS / (ident + "-seated-display.stl")
            cq.exporters.export(feature.assembly_shape((0, 0, 0)), str(display_step))
            feature.assembly_mesh((0, 0, 0)).export(display_stl)
            row["seated_display"] = {"step": str(display_step.relative_to(ROOT)), "stl": str(display_stl.relative_to(ROOT)),
                "stl_sha256": sha(display_stl.read_bytes()), "scope": "Nominal source elastic seated model in faucet frame; separately meshed from relaxed manufacturing model."}
        rows.append(row)
    report = check_faucet(features)
    (HERE / "faucet-proof.json").write_text(json.dumps(report, indent=2) + "\n")
    cohorts = [
        {"id": "rigid", "global_overrides": {"initial_layer_print_height": ".20", "spiral_mode": "0"}},
        {"id": "colour", "global_overrides": {"initial_layer_print_height": ".20", "spiral_mode": "0"}},
        {"id": "TPU85A", "profile_source": "hardware/printed-parts/gaskets.3mf",
            "global_overrides": {"initial_layer_print_height": ".30", "spiral_mode": "0"}},
        {"id": "TPU85A-spiral", "profile_source": "hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring-85A-6mm.3mf",
            "global_overrides": {"initial_layer_print_height": ".30", "spiral_mode": "1", "spiral_mode_smooth": "1",
                "elefant_foot_compensation": "0", "z_direction_outwall_speed_continuous": "0"}},
    ]
    result = {"schema": 1, "title": "The Pour V3 complete faucet module", "root_mm": list(ROOT_POINT), "cohorts": cohorts,
        "parts": rows, "print_objects": objects, "source_snapshot_index": str((INPUTS / "sources.json").relative_to(ROOT)),
        "source_snapshot_index_sha256": sha((INPUTS / "sources.json").read_bytes()), "review": report}
    (HERE / "faucet-module.json").write_text(json.dumps(result, indent=2) + "\n")
    assembly = cq.Assembly(name="The Pour V3 complete faucet")
    payloads = []
    for feature in features.values():
        rgb = (.13, .145, .15) if feature.material != "TPU" else (.075, .08, .085)
        assembly.add(feature.assembly_shape(), name=feature.id, color=cq.Color(*rgb))
        mesh = feature.assembly_mesh()
        payloads.append({"name": feature.id, "color": list(rgb), "pos": mesh.triangles.reshape(-1).tolist(),
            "nrm": np.repeat(mesh.face_normals, 3, axis=0).reshape(-1).tolist(),
            "idx": list(range(len(mesh.faces)*3)), "fac": [0, len(mesh.faces)-1]})
    target = ASSETS / "faucet-complete.step"
    export_assembly(assembly, str(target))
    _mesh_payload.write(payloads, str(target) + ".mesh", src=_mesh_payload.source_digest(target))
    print(json.dumps(report, indent=2), flush=True)
    return result


if __name__ == "__main__":
    export_cache()
