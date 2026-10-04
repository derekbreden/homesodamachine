#!/usr/bin/env python3
"""Build the proposal STEP files and a compact, exact-solid display pack.

Run with tools/cad-venv/bin/python. Production CAD is read, never regenerated.
The context exporter is separate because its frozen snapshot is a deliberate
review boundary. Native solids, rather than display triangles, set capacities.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import cadquery as cq

import geometry
import drawer
from pack_proposals import write_pack

HERE = Path(__file__).resolve().parent
PRESETS = {
    "local60": dict(mode="local", depth=60.0),
    "local100": dict(mode="local", depth=100.0),
    "full5": dict(mode="full", gap=3.0, depth=8.0),
    "full8": dict(mode="full", gap=6.0, depth=11.0),
    "full12": dict(mode="full", gap=10.0, depth=15.0),
    "full16": dict(mode="full", gap=14.0, depth=19.0),
}
DRAWER_PRESETS = {f"drawer{height}": dict(added_height=float(height)) for height in (8,10,12,16)}


def mesh(shape: cq.Shape, name: str, category: str) -> dict:
    # Thin hose curvature is visually smooth at this display tessellation. All
    # route/clearance and capacity decisions use native BReps, not these triangles.
    vertices, triangles = shape.tessellate(0.4, 0.4) if category in ("tube", "support") else shape.tessellate(0.18, 0.20)
    return dict(name=name, category=category,
                p=[round(c, 3) for v in vertices for c in v.toTuple()],
                i=[n for triangle in triangles for n in triangle])


def cached_water(data, key, description, step_hash):
    """Reuse a verified display void only when every wetted part is identical.

    The added internal floor witness is above the full-tray rim and outside the
    local collector. It therefore cannot change either saved water void.
    """
    if data["metadata"]["step_sha256"] != step_hash:
        raise ValueError("Cached water belongs to another frozen STEP")
    old = data["metadata"]["variants"][key]
    required = ("mode", "gap", "depth", "floor_thickness", "wall_thickness",
                "bottom_z", "innerfloor_z", "rim_z", "downcomer_x",
                "sensor_width", "sensor_thickness")
    if any(old["parameters"][p] != description["parameters"][p] for p in required):
        raise ValueError(f"{key}: wetted geometry parameters changed")
    for name, part in old["parts"].items():
        if name == "lower-collector" or name.startswith(("support-", "wet-sensor-envelope")):
            new = description["parts"][name]
            if any(abs(a-b) > 1e-6 for a,b in zip(part["bounds"],new["bounds"])) or abs(part["volume_mm3"]-new["volume_mm3"]) > 1e-6:
                raise ValueError(f"{key}: wetted part {name} changed")
    b = geometry.INTERNAL_SENSOR_BOUNDS
    for x0,y0,x1,y1 in description["basin_cavity_rectangles_xy"]:
        overlap = b[0]<x1 and b[3]>x0 and b[1]<y1 and b[4]>y0
        if overlap and b[2]<description["rim_z"] and b[5]>description["innerfloor_z"]:
            raise ValueError("Internal witness intersects cached water; recalculate")
    indices = old["mesh_indices"]
    water = next(data["meshes"][i] for i in indices if data["meshes"][i]["category"] == "water")
    description["capacity"] = old["capacity"]
    description["net_capacity_ml"] = old["net_capacity_ml"]
    description["capacity_reuse_scope"] = "Same frozen native STEP, identical wetted parts and parameters; added floor witness is outside water void."
    return water


def main(reuse_water=False):
    meshes, variants, fingerprints = [], {}, {}
    metadata = dict(schema=1, units="mm", variants=variants,
                    baseline=dict(case_height_mm=361, installed_height_mm=364,
                                  width_mm=215, with_upper_pan_width_mm=220.95,
                                  depth_mm=466.3, base_z=-6, top_z=355,
                                  mq6_bottom_z=3, required_side_gap_mm=40,
                                  upper_pan_capacity_ml=39.2))
    step_hash = hashlib.sha256(geometry.STEP_PATH.read_bytes()).hexdigest()
    geometry_hash = hashlib.sha256(Path(geometry.__file__).read_bytes()).hexdigest()
    drawer_hash = hashlib.sha256(Path(drawer.__file__).read_bytes()).hexdigest()
    facts_hash = hashlib.sha256(geometry.FACTS_PATH.read_bytes()).hexdigest()
    cache = json.loads(gzip.decompress((HERE/"proposals.json.gz").read_bytes())) if reuse_water else None
    for key, parameters in {**PRESETS, **DRAWER_PRESETS}.items():
        print(f"Building {key}", flush=True)
        is_drawer = key in DRAWER_PRESETS
        module = drawer if is_drawer else geometry
        parts = module.build_variant(**parameters)
        description = module.describe_variant(**parameters, include_saved_displacement=not reuse_water)
        description["construction"] = "front-drawer" if is_drawer else ("under-machine-pan" if parameters["mode"]=="full" else "side-collector")
        if description["saved_assembly"]["step_sha256"] != step_hash:
            raise RuntimeError("Saved production STEP changed during the study build")
        if description["saved_assembly"]["facts_sha256"] != facts_hash:
            raise RuntimeError("Saved assembly facts changed during the study build")
        checks = description["checks"]
        assert checks["all_parts_valid"] and checks["single_solid_parts"], key
        assert checks["tube_wall_after_relief_mm3"] < 1e-6, key
        assert checks["tube_clip_intersection_mm3"] < 1e-6, key
        if is_drawer:
            assert checks["max_withdrawal_clash_mm3"] < 1e-6, key
        water_data = cached_water(cache, key, description, step_hash) if reuse_water and not is_drawer else None
        if not reuse_water or is_drawer:
            parts["static-water-volume"] = module.water_shape(**parameters)
        description["mesh_indices"] = []
        for name, shape in parts.items():
            if name == "air-gap-reference":
                continue
            category = ("water" if name == "static-water-volume" else
                        "relief" if name in geometry.REFERENCE_PARTS else
                        "sensor" if name.startswith("wet-sensor") else
                        "frame" if name == "load-frame" else
                        "presence" if name.startswith("drawer-presence") else
                        "tube" if name == "vent-extension" else
                        "tray" if name == "lower-collector" else "support")
            data = mesh(shape, name, category)
            fingerprint = hashlib.sha256(json.dumps(data, separators=(",", ":")).encode()).hexdigest()
            if fingerprint not in fingerprints:
                fingerprints[fingerprint] = len(meshes)
                meshes.append(data)
            description["mesh_indices"].append(fingerprints[fingerprint])
        if water_data:
            fingerprint = hashlib.sha256(json.dumps(water_data, separators=(",", ":")).encode()).hexdigest()
            if fingerprint not in fingerprints:
                fingerprints[fingerprint] = len(meshes)
                meshes.append(water_data)
            description["mesh_indices"].append(fingerprints[fingerprint])
        p = description["parameters"]
        # Cabinet walls at least 40 mm from each side of the original case.
        # The aft receiver can occupy part of the west allowance but must fit.
        left_wall = min(-147.5, description["overall_bounds"][0])
        description["cabinet_width_with_side_gaps_mm"] = 147.5-left_wall
        variants[key] = description
        if key in ("full5", "local60", "local100", "full16", "drawer10", "drawer16"):
            module.proposal_assembly(**parameters).save(str(HERE/f"{key}-proposal.step"))
        print(f"  {p['installed_height_mm']:.1f} mm installed height; "
              f"{description['net_capacity_ml']:.1f} mL net at rim", flush=True)
    metadata["step_sha256"] = step_hash
    if hashlib.sha256(Path(geometry.__file__).read_bytes()).hexdigest() != geometry_hash:
        raise RuntimeError("Proposal source changed during the study build; rebuild")
    if hashlib.sha256(Path(drawer.__file__).read_bytes()).hexdigest() != drawer_hash:
        raise RuntimeError("Drawer source changed during the study build; rebuild")
    if hashlib.sha256(geometry.FACTS_PATH.read_bytes()).hexdigest() != facts_hash:
        raise RuntimeError("Saved assembly facts changed during the study build; rebuild")
    metadata["geometry_sha256"] = geometry_hash
    metadata["drawer_geometry_sha256"] = drawer_hash
    metadata["facts_sha256"] = facts_hash
    packed = gzip.compress(json.dumps(dict(meshes=meshes, metadata=metadata),
                                     separators=(",", ":")).encode(), mtime=0)
    (HERE/"proposals.json.gz").write_bytes(packed)
    binary_bytes = write_pack(dict(meshes=meshes, metadata=metadata))
    (HERE/"study-metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    validation = json.loads((HERE/"geometry-validation.json").read_text())
    validation.update(source_hash=step_hash, geometry_sha256=geometry_hash,
                      drawer_geometry_sha256=drawer_hash, facts_sha256=facts_hash,
                      variants=variants)
    validation["internal_floor_probe"] = dict(bounds=list(geometry.INTERNAL_SENSOR_BOUNDS),
        geometry_scope="Independent native Boolean review against 217 named bodies in the same frozen STEP found no positive-volume clash. Bare probe envelope only.")
    (HERE/"geometry-validation.json").write_text(json.dumps(validation, indent=2)+"\n")
    print(f"{len(meshes)} unique proposal meshes; {binary_bytes} binary gzip bytes", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse-water", action="store_true", help="Reuse the verified same-snapshot water mesh only after wetted geometry checks")
    main(parser.parse_args().reuse_water)
