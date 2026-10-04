#!/usr/bin/env python3
"""Export a compact, named assembly context without rebuilding production CAD.

Run with tools/cad-venv/bin/python. The output is a gzip-compressed JSON list;
context.b64 contains those gzip bytes as base64 for a standalone Three.js page.
Small selected hardware bodies retain a matching viewer payload's coordinates
and faces; a stale payload is replaced with fine native STEP tessellation.
Case and outer-core bodies are tessellated from the same frozen STEP snapshot
with absolute chord deflection, preserving the BRep's openings and placement.
This display context is not the geometry used for native clearance acceptance.
"""

from __future__ import annotations

import argparse
import ast
import base64
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
import re
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSEMBLY = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
FACTS = ROOT / "hardware/manifold-layout/enclosure-assembly.facts.json"
SCORECARD = ROOT / "hardware/manifold-layout/enclosure-assembly.scorecard.json"
sys.path.insert(0, str(ROOT / "hardware/scripts"))

# The imported helper also serves production generators and takes their build
# mutex at import. This reader operates on frozen files and writes study files
# only; it must neither queue behind nor supersede an active production build.
os.environ["HSM_NO_BUILD_LOCK"] = "1"

# Every included surface is an actual named body, not an envelope or convex hull.
# Omitted internal core hardware remains available in the full source assembly.
CORE_BODIES = {
    "cold-core/foam-shell", "cold-core/foam-cap-top",
    "cold-core/foam-cap-lid-top", "cold-core/foam-cap-bottom",
    "cold-core/foam-cap-lid-bottom",
}
DISPLAY_BODIES = {"funnel-cover"}
OMITTED_CASE_BODIES = {
    "enclosure-front-top", "enclosure-pump-cap", "enclosure-pump-cartridge",
    "enclosure-tee-carrier-plate",
}
EXACT_BODIES = {
    "condenser+fan", "mq6-sensor", "asse-drip-pan", "moisture-plate",
    "pcba", "psu", "relay-1", "relay-2", "ground-stack", "c14-inlet",
    "thermal-fuse", "fuse-clamp", "water-split", "flow-regulator",
    "bulkhead-water", "bulkhead-carb", "bulkhead-flavor-a",
    "bulkhead-flavor-b", "keystone-jack",
}
EXACT_PREFIXES = ("compressor/", "asse1022-assembly/", "wago-")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_payload(raw: bytes) -> tuple[dict, bytes]:
    header_length = struct.unpack("<I", raw[:4])[0]
    header = json.loads(raw[4:4 + header_length])
    if header.get("v") != 3:
        raise ValueError("The assembly context requires a source-stamped v3 payload")
    return header, raw[4 + header_length:]


def stable_snapshot() -> tuple[bytes, bytes, dict, bytes]:
    """Hold stable STEP bytes; use its payload only when descent also agrees."""
    payload_path = Path(str(ASSEMBLY) + ".mesh")
    frozen = HERE / "context-source.step"
    if frozen.is_file():
        step, payload = frozen.read_bytes(), payload_path.read_bytes()
        header, blob = read_payload(payload)
        return step, payload, header, blob
    for _ in range(3):
        step_before = ASSEMBLY.stat()
        step = ASSEMBLY.read_bytes()
        payload = payload_path.read_bytes()
        step_after = ASSEMBLY.stat()
        header, blob = read_payload(payload)
        unchanged = ((step_before.st_mtime_ns, step_before.st_size)
                     == (step_after.st_mtime_ns, step_after.st_size))
        if unchanged and header.get("src") == digest(step):
            return step, payload, header, blob
    if unchanged:
        # A producer can leave a new STEP beside an old payload. The caller then
        # meshes ALL selected bodies from the frozen STEP, including hardware.
        return step, payload, header, blob
    raise RuntimeError("Production STEP is changing; no stable snapshot read")


def payload_arrays(mesh: dict, blob: bytes) -> tuple[np.ndarray, np.ndarray]:
    positions = np.frombuffer(blob, dtype="<f4", count=mesh["pos"][1],
                              offset=mesh["pos"][0]).reshape(-1, 3).copy()
    indices = np.frombuffer(blob, dtype="<u4", count=mesh["idx"][1],
                            offset=mesh["idx"][0]).reshape(-1, 3).copy()
    return positions, indices


def bounds(positions: np.ndarray) -> list[list[float]]:
    return [positions.min(axis=0).astype(float).tolist(),
            positions.max(axis=0).astype(float).tolist()]


def category(name: str) -> str:
    if name == "asse-drip-pan":
        return "upper-pan"
    if name in ("mq6-sensor", "moisture-plate"):
        return "sensor"
    if name.startswith(("enclosure-", "grip-cover-")):
        return "case"
    if name in CORE_BODIES:
        return "core"
    return "hardware"


def exact(name: str) -> bool:
    return (name in EXACT_BODIES or name in ("compressor", "asse1022-assembly")
            or name.startswith(EXACT_PREFIXES))


def include(name: str) -> bool:
    return (name not in OMITTED_CASE_BODIES
            and (exact(name) or name in CORE_BODIES or name in DISPLAY_BODIES
                 or category(name) == "case"))


def as_entry(name: str, positions: np.ndarray, indices: np.ndarray,
             color: list | None, rounded: bool = False) -> dict:
    # Rounding is restricted to coarsely tessellated display bodies. Exact
    # hardware retains every Float32 coordinate in the source payload unchanged.
    p = np.round(positions.astype(float), 4) if rounded else positions.astype(float)
    return {"name": name, "p": p.reshape(-1).tolist(),
            "i": indices.reshape(-1).astype(int).tolist(),
            "category": category(name), "color": color}


def split_vent_stub(placed: dict) -> dict:
    """Give the lowest ASSE solid a stable name for proposed replacement views."""
    import cadquery as cq
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box

    name = "asse1022-assembly"
    if name not in placed:
        raise RuntimeError("ASSE assembly missing from frozen STEP")
    shape, color = placed[name]
    solids = shape.Solids()
    measured = []
    for solid in solids:
        box = Bnd_Box()
        BRepBndLib.AddOptimal_s(solid.wrapped, box, False, False)
        measured.append((box.Get()[2], solid))
    measured.sort(key=lambda item: item[0])
    if len(measured) < 2 or measured[1][0] - measured[0][0] < 1:
        raise RuntimeError("Existing vent stub is not a uniquely lowest ASSE solid")
    result = dict(placed)
    del result[name]
    result[name + "/vent-stub"] = (measured[0][1], color)
    result[name + "/body"] = (cq.Compound.makeCompound([s for _, s in measured[1:]]), color)
    return result


def native_context(placed: dict, names: list[str], colors: dict,
                   linear_mm: float, angle_rad: float) -> tuple[list[dict], list[dict]]:
    """Absolute OCCT tessellation of copies; never a convex-hull substitution."""
    import _mesh_payload
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    from OCP.BRepTools import BRepTools
    import fast_simplification
    import trimesh
    from OCP.Quantity import Quantity_TypeOfColor

    entries, records = [], []
    for name in names:
        shape, _ = placed[name]
        color = colors.get(name)
        if placed[name][1] is not None:
            color = list(placed[name][1].wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))
        actual_linear = 0.02 if exact(name) else linear_mm
        actual_angle = 0.15 if exact(name) else angle_rad
        native_box = Bnd_Box()
        BRepBndLib.AddOptimal_s(shape.wrapped, native_box, False, False)
        low_x, low_y, low_z, high_x, high_y, high_z = native_box.Get()
        # Copies prevent triangulation from changing the imported shapes used
        # for analytic bounding boxes or a later coarser tessellation attempt.
        copy = BRepBuilderAPI_Copy(shape.wrapped).Shape()
        BRepTools.Clean_s(copy)
        BRepMesh_IncrementalMesh(copy, actual_linear, False, actual_angle, True)
        p, _normals, i, _faces = _mesh_payload._solid_arrays(copy)
        p = np.asarray(p, dtype=float).reshape(-1, 3)
        i = np.asarray(i, dtype=np.uint32).reshape(-1, 3)
        if not len(i):
            raise RuntimeError(f"No tessellation for selected source body {name}")
        original_triangles = len(i)
        original_vertices = len(p)
        # Native tessellation emits separate vertices for every analytic face.
        # Weld matching rounded positions, then collapse coplanar redundancy
        # with the library's lossless mode. No target-count reduction is used,
        # and open boundaries are protected rather than bridged or filled.
        before_euler = None
        if exact(name):
            # Native faces duplicate identical world coordinates. Reindexing
            # those duplicates changes no vertex position or triangle geometry.
            # It is not a surface reduction and introduces no rounding.
            unique, inverse = np.unique(p, axis=0, return_inverse=True)
            reindexed = inverse[i]
            if not np.array_equal(unique[reindexed], p[i]):
                raise AssertionError(f"Exact reindex changed geometry: {name}")
            p, i = unique, reindexed
            reduction = "none; identical coordinates reindexed without rounding or triangle changes"
        else:
            mesh = trimesh.Trimesh(np.round(p, 4), i, process=True)
            mesh.merge_vertices(digits_vertex=4)
            before_euler = mesh.euler_number
            p, i = fast_simplification.simplify(
                mesh.vertices, mesh.faces, lossless=True, preserve_border=True)
            reduced = trimesh.Trimesh(p, i, process=False)
            if reduced.euler_number != before_euler:
                p, i = mesh.vertices, mesh.faces
                reduction = "welded-native-tessellation; topology-changing reduction rejected"
            else:
                reduction = "lossless coplanar reduction with protected open boundaries"
        entries.append(as_entry(name, p, i, color, rounded=not exact(name)))
        records.append({"name": name, "method": "saved-step-absolute-tessellation",
                        "native_bounds_mm": [[low_x, low_y, low_z],
                                             [high_x, high_y, high_z]],
                        "preview_bounds_mm": bounds(p),
                        "vertices": len(p), "triangles": len(i),
                        "native_tessellation_triangles": original_triangles,
                        "native_tessellation_vertices": original_vertices,
                        "reduction": reduction,
                        "euler_characteristic": None if before_euler is None else int(before_euler),
                        "linear_deflection_mm": actual_linear,
                        "angular_deflection_rad": actual_angle,
                        "coordinate_rounding_mm": 0 if exact(name) else 0.0001})
    return entries, records


def file_code_digest(raw: bytes) -> str:
    """The same code digest as _realized, evaluated on frozen artifact bytes."""
    try:
        form = ast.dump(ast.parse(raw)).encode()
    except (SyntaxError, ValueError):
        form = raw
    return hashlib.blake2b(form, digest_size=16).hexdigest()


def tree_state(facts_bytes: bytes, card_bytes: bytes, step_bytes: bytes) -> dict:
    import _facts
    f = _facts.Facts(json.loads(facts_bytes), json.loads(card_bytes))
    changed = subprocess.check_output(
        ["git", "diff", "HEAD", "--name-only"], cwd=ROOT, text=True).splitlines()
    source_names = set(_facts.sources())
    return {
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "facts_source_digest": f._f.get("sources"),
        "current_traced_source_digest": _facts.source_digest(),
        "facts_agrees_with_current_sources": f.agrees_with_sources(),
        "facts_agrees_with_saved_step": f._f.get("step") == file_code_digest(step_bytes),
        "facts_agrees_with_saved_scorecard": f._f.get("card") == file_code_digest(card_bytes),
        "changed_traced_inputs": sorted(source_names.intersection(changed)),
        "scope": "Saved STEP/payload snapshot; concurrent source edits are not regenerated.",
    }


def validate(entries: list[dict]) -> None:
    names = set()
    for entry in entries:
        name = entry["name"]
        if name in names:
            raise AssertionError(f"Duplicate body name: {name}")
        names.add(name)
        p = np.asarray(entry["p"], dtype=float).reshape(-1, 3)
        i = np.asarray(entry["i"], dtype=np.int64).reshape(-1, 3)
        if not np.isfinite(p).all() or not len(i):
            raise AssertionError(f"Invalid positions or missing triangles: {name}")
        if i.min() < 0 or i.max() >= len(p):
            raise AssertionError(f"Out-of-range triangle index: {name}")
        if entry["category"] not in ("case", "core", "hardware", "upper-pan", "sensor"):
            raise AssertionError(f"Unknown display category: {name}")


def source_body_accounting(entries: list[dict], payload_names) -> dict:
    """Report source solids behind grouped and split native display bodies."""
    def base(name):
        if name.startswith("asse1022-assembly/"):
            return "asse1022-assembly"
        return re.sub(r"/\d+$", "", name)

    included = {base(entry["name"]) for entry in entries}
    names = list(payload_names)
    return {
        "omitted_payload_bodies": sorted(name for name in names if base(name) not in included),
        "merged_source_solid_names": {
            source: sorted(name for name in names if base(name) == source and name != source)
            for source in sorted(included)
            if any(base(name) == source and name != source for name in names)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-base64-bytes", type=int, default=780000)
    parser.add_argument("--linear-mm", type=float, default=0.3)
    parser.add_argument("--angle-rad", type=float, default=0.5)
    args = parser.parse_args()
    step, payload, header, blob = stable_snapshot()
    frozen_facts = HERE / "context-source.facts.json"
    facts_bytes = (frozen_facts if frozen_facts.is_file() else FACTS).read_bytes()
    card_bytes = SCORECARD.read_bytes()
    saved_facts = json.loads(facts_bytes)
    current_tree = tree_state(facts_bytes, card_bytes, step)
    payload_meshes = {m["name"]: m for m in header["meshes"]}
    exact_entries, exact_records = [], []
    colors = {}
    matching_payload = header.get("src") == digest(step)
    for m in header["meshes"]:
        name = m["name"]
        colors[name] = m.get("color")
        # The ASSE compound is always read natively to give its existing stub
        # the same stable name in matched and stale-payload situations.
        if not exact(name) or not matching_payload or name.startswith("asse1022-assembly"):
            continue
        p, i = payload_arrays(m, blob)
        exact_entries.append(as_entry(name, p, i, colors[name]))
        exact_records.append({"name": name, "method": "saved-payload-unmodified",
                              "preview_bounds_mm": bounds(p),
                              "vertices": len(p), "triangles": len(i),
                              "coordinate_rounding_mm": 0})

    from _cadq_export import import_assembly
    # Study-native checks can read this ignored file and compare its digest to
    # provenance, even when a production build later refreshes the assembly.
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "context-source.step").write_bytes(step)
    (HERE / "context-source.facts.json").write_bytes(facts_bytes)
    with tempfile.TemporaryDirectory(prefix="hsm-leak-context-") as temp:
        frozen = Path(temp) / "assembly-snapshot.step"
        frozen.write_bytes(step)
        print("Reading frozen saved STEP for case/core context", flush=True)
        placed = split_vent_stub(import_assembly(frozen))
        native_names = sorted(n for n in placed if include(n)
                              and (not exact(n) or not matching_payload
                                   or n.startswith("asse1022-assembly/")))
        missing = [n for n in CORE_BODIES if n not in placed]
        if missing:
            raise RuntimeError(f"Selected core bodies missing from saved STEP: {missing}")
        attempts = []
        # This changes tessellation density only. Each attempt starts from the
        # same actual BRep, including its holes, cavities and assembly poses.
        for linear in (args.linear_mm, 0.5, 0.8, 1.2):
            preview, native_records = native_context(
                placed, native_names, colors, linear, args.angle_rad)
            entries = sorted(exact_entries + preview, key=lambda x: x["name"])
            validate(entries)
            raw = json.dumps(entries, separators=(",", ":"), allow_nan=False).encode()
            compressed = gzip.compress(raw, compresslevel=9, mtime=0)
            encoded = base64.b64encode(compressed)
            attempts.append({"linear_mm": linear, "base64_bytes": len(encoded),
                             "triangles": sum(len(e["i"]) // 3 for e in entries)})
            print(f"{linear:g} mm: {len(encoded):,} base64 bytes", flush=True)
            if len(encoded) <= args.max_base64_bytes:
                break
        else:
            raise RuntimeError(f"No context within size budget: {attempts}")

    # All production inputs have already been frozen. Outputs belong only to
    # this study; no production generator, export or publishing path is called.
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "context.json.gz").write_bytes(compressed)
    (HERE / "context.b64").write_bytes(encoded)
    nominal = saved_facts["box"]["outer"]
    provenance = {
        "schema": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "units": "millimetres", "coordinate_frame": "saved assembly world coordinates; Z up",
        "sources": {
            "step": {"path": str(ASSEMBLY.relative_to(ROOT)), "sha256": digest(step),
                     "bytes": len(step), "study_snapshot": "context-source.step"},
            "payload": {"path": str(ASSEMBLY.relative_to(ROOT)) + ".mesh",
                        "sha256": digest(payload), "bytes": len(payload),
                        "src_sha256": header.get("src"), "version": header.get("v")},
            "facts": {"path": str(FACTS.relative_to(ROOT)), "sha256": digest(facts_bytes),
                      "study_snapshot": "context-source.facts.json"},
            "scorecard": {"path": str(SCORECARD.relative_to(ROOT)), "sha256": digest(card_bytes)},
        },
        "snapshot_step_payload_descent_agrees": header.get("src") == digest(step),
        "payload_used_for_geometry": matching_payload,
        "tree_at_capture": current_tree,
        "reference_datums": {
            "source": "saved facts; their freshness is reported separately",
            "nominal_outer_bounds_mm": [[nominal[0], nominal[2], nominal[4]],
                                         [nominal[1], nominal[3], nominal[5]]],
            "nominal_dimensions_mm": [nominal[1] - nominal[0], nominal[3] - nominal[2],
                                       nominal[5] - nominal[4]],
            "interior_floor_z_mm": saved_facts["box"]["inner"][4],
            "underside_z_mm": nominal[4],
            "mq6_saved_geometry_bounds_mm": next(
                r["preview_bounds_mm"] for r in exact_records + native_records if r["name"] == "mq6-sensor"),
            "installed_funnel_cover_native_bounds_mm": next(
                r["native_bounds_mm"] for r in native_records if r["name"] == "funnel-cover"),
        },
        "display_geometry": {
            "method": ("Unmodified matching hardware payload plus absolute STEP tessellation of case/outer core."
                       if matching_payload else
                       "Payload stale: all selected geometry tessellated from frozen STEP; hardware uses 0.02 mm / 0.15 rad without surface reduction or coordinate rounding."),
            "convex_hulls": False, "proxy_envelopes": False,
            "normals": "Recompute from indexed triangles in the viewer.",
            "case_show_surface": "Smooth saved STEP BRep; mesh-only decorative flutes are omitted.",
            "source_body_split": {"asse1022-assembly": ["asse1022-assembly/body", "asse1022-assembly/vent-stub"],
                                  "method": "Existing uniquely lowest native ASSE solid is named vent-stub; remaining native solids remain grouped."},
            "validation_scope": "Display context only; use saved native BReps for geometric clearance checks.",
            "tessellation_scope": "Requested OCCT chord deflection is not a measured Hausdorff error bound.",
            "attempts": attempts,
            "included_categories": dict(Counter(e["category"] for e in entries)),
            "omissions_scope": "Front-top, pump cartridge/cap and tee-carrier plate omitted for compact cutaway visibility; floor/rear routing surfaces and outer core retained, internal core equipment omitted.",
            "omitted_case_bodies": sorted(OMITTED_CASE_BODIES),
            **source_body_accounting(entries, payload_meshes),
            "bodies": sorted(exact_records + native_records, key=lambda x: x["name"]),
        },
        "outputs": {
            "context.json.gz": {"sha256": digest(compressed), "bytes": len(compressed),
                                "decompressed_json_bytes": len(raw)},
            "context.b64": {"sha256": digest(encoded), "bytes": len(encoded)},
            "body_count": len(entries),
            "triangles": sum(len(e["i"]) // 3 for e in entries),
        },
    }
    (HERE / "context-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Wrote {len(entries)} named bodies; {len(encoded):,} embedded bytes", flush=True)


if __name__ == "__main__":
    main()
