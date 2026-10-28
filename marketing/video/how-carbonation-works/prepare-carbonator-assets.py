#!/usr/bin/env python3
"""Export persistent full/cutaway hardware and the movable current ASA Aero float.

This reads existing STEP assemblies and writes only video assets. The pressure
hardware and its Boolean half sections share exact analytic source geometry.
Run with tools/cad-venv/bin/python; no hardware generator or print job is run.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
# This process reads STEP files and writes no hardware build outputs.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(ROOT / "hardware/scripts"))
sys.path.insert(0, str(ROOT / "hardware/cold-core-layout"))
from _cadq_export import import_assembly
import _mesh_payload
import _carbonator as carbonator
import _fittings as fittings
from _water_inlet_jet import JET_CAP_T, JET_PASSAGE_D

FLOOR = carbonator.interior_z[0]


def point(native):
    x, y, z = native.toTuple() if hasattr(native, "toTuple") else native
    return [-y, z - FLOOR, -x]


def direction(native):
    x, y, z = native.toTuple() if hasattr(native, "toTuple") else native
    return [-y, z, -x]


def rounded(values, precision=5):
    return np.round(np.asarray(values, dtype=float), precision).tolist()


def bbox(positions):
    return rounded(np.vstack((positions.min(axis=0), positions.max(axis=0))))


def role(name):
    if name == "carbonator-tube":
        return "pressure-shell"
    if name.startswith("endcap"):
        return "endcap"
    if name.startswith("carbonator-elbow"):
        return "port"
    if name.startswith("collet"):
        return "collet"
    if name.startswith("prv"):
        return "prv"
    if name == "water-inlet-jet-cap-nominal":
        return "jet-cap"
    if name == "float-rod-carb":
        return "float-guide"
    return "sensor"


def write_bundle(filename, found, source, section=False, float_local=False):
    # Finer than the viewer's layout tessellation for close views of the bore.
    _mesh_payload.ANGULAR_DEFLECTION = .12
    copies = _mesh_payload._mesh_all([shape for _, shape, _ in found], .025)
    meshes = []
    for (name, _shape, color), triangulated in zip(found, copies):
        p, n, indices, _faces = _mesh_payload._solid_arrays(triangulated)
        if not indices:
            continue
        p = np.asarray(p, dtype=float).reshape((-1, 3))
        n = np.asarray(n, dtype=float).reshape((-1, 3))
        q = np.stack((-p[:, 1], p[:, 2] - (14 if float_local else FLOOR), -p[:, 0]), axis=1)
        normal = np.stack((-n[:, 1], n[:, 2], -n[:, 0]), axis=1)
        faces = np.asarray(indices, dtype=np.uint32).reshape((-1, 3))
        cut_mask = np.all(np.abs(q[faces, 2]) < 1e-5, axis=1) if section else np.zeros(len(faces), dtype=bool)
        cut_faces = faces[cut_mask]
        from OCP.Quantity import Quantity_TypeOfColor
        rgb = list(color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB)) if color else [.4,.4,.4]
        meshes.append({
            "name": name, "group": "magnetic-float" if float_local else "carbonator-hardware",
            "role": ("float-body" if name == "float-aero" else "float-magnet") if float_local else role(name),
            "color": rounded(rgb, 6), "positions": rounded(q.reshape(-1), 5),
            "normals": rounded(normal.reshape(-1), 6), "indices": faces.reshape(-1).tolist(),
            "sectionFaceIndices": cut_faces.reshape(-1).tolist(),
            "sectionTriangleOrdinals": np.flatnonzero(cut_mask).tolist(),
            "bounds": bbox(q), "triangles": len(faces), "sectionTriangles": len(cut_faces),
        })
        print(f"{filename}: {name} {len(faces):,} triangles; {len(cut_faces):,} section-face triangles", flush=True)
    source_path = ROOT / source
    bundle = {
        "version": 1, "units": "mm", "frame": "float-magnet-centered-y-up" if float_local else "carbonator-local-y-up",
        "colorSpace": "linear-srgb", "source": source,
        "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "nativeMapping": ["-source.y", "source.z-14", "-source.x"] if float_local else ["-cc.y", f"cc.z-{FLOOR:.5f}", "-cc.x"],
        "section": {"keptHalfSpace": "local z <= 0", "plane": [0,0,-1,0], "cutFacesAreGeometry": True} if section else None,
        "meshes": meshes,
    }
    target = ASSETS / filename
    target.write_text(json.dumps(bundle, separators=(",", ":")) + "\n")
    compressed = target.with_suffix(target.suffix + ".gz")
    compressed.write_bytes(gzip.compress(target.read_bytes(), compresslevel=9, mtime=0))
    return {"file": filename, "compressedFile": compressed.name, "meshes": len(meshes),
            "triangles": sum(m["triangles"] for m in meshes), "bytes": target.stat().st_size,
            "compressedBytes": compressed.stat().st_size, "source": source, "sourceSha256": bundle["sourceSha256"]}


def lumen(name, incoming=True):
    c = np.asarray(carbonator.port_corner(name), dtype=float)
    up = np.asarray(carbonator.port_up(name), dtype=float)
    out = np.asarray(carbonator.port_out(name), dtype=float)
    mouth = c + out * fittings.ELBOW_LEG
    # This is the reference adapter's actual external stand-off, not a measured bore.
    collet_mouth = mouth + out * (13.5 + 5.0)
    tip = np.asarray(carbonator.port_male_tip(name), dtype=float)
    radius = 1.5  # A centerline fillet wholly inside the intersecting 6.35 mm model bores.
    points = [collet_mouth, mouth, c + out * radius]
    center = c + (out + up) * radius
    for theta in np.linspace(0, math.pi/2, 13)[1:]:
        points.append(center - up * radius * math.cos(theta) - out * radius * math.sin(theta))
    points.append(tip)
    if not incoming:
        points.reverse()
    return rounded([point(p) for p in points]), {
        "corner": rounded(point(c)), "maleTip": rounded(point(tip)),
        "elbowMouth": rounded(point(mouth)), "colletMouth": rounded(point(collet_mouth)),
        "up": rounded(direction(up)), "out": rounded(direction(out)),
    }


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    source = "hardware/cold-core-layout/cold-core-assembly.step"
    bodies = import_assembly(ROOT / source)
    selected = {
        "carbonator-tube", "endcap-bottom", "endcap-top", "float-rod-carb", "float-stop-carb-top",
        "carbonator-elbow-co2-in", "carbonator-elbow-carb-water-out", "carbonator-elbow-water-in", "carbonator-elbow-prv",
        "water-inlet-jet-cap-nominal", "collet-co2-in", "collet-carb-water-out", "collet-water-in",
        "prv-sv125", "prv-shroud", "reed-bridge", "reed-carb-1", "reed-carb-2", "probe-carbonator-ds18b20",
    }
    missing = selected - bodies.keys()
    if missing:
        raise ValueError(f"Missing current STEP parts: {sorted(missing)}")
    found = [(name, *bodies[name]) for name in sorted(selected)]
    bundles = [write_bundle("carbonator-hardware-full.json", found, source)]
    half_space = cq.Solid.makeBox(600, 1200, 1200, cq.Vector(0, -600, -600))
    half = []
    for name, shape, color in found:
        bounds = shape.BoundingBox()
        if bounds.xmax < -1e-7:
            continue
        cut = shape if bounds.xmin >= -1e-7 else shape.intersect(half_space)
        if len(cut.Solids()):
            half.append((name, cut, color))
    bundles.append(write_bundle("carbonator-hardware-section.json", half, source, section=True))
    float_source = "hardware/printed-parts/cold-core/magnetic-float/all-aero/assembly.step"
    float_bodies = import_assembly(ROOT / float_source)
    float_found = [(name, *float_bodies[name]) for name in ("float-aero", "RC62")]
    bundles.append(write_bundle("magnetic-float-cad.json", float_found, float_source, float_local=True))
    water, water_port = lumen("water-in")
    gas, gas_port = lumen("co2-in")
    outlet, outlet_port = lumen("carb-water-out", incoming=False)
    tip = np.asarray(carbonator.port_male_tip("water-in"), dtype=float)
    up = np.asarray(carbonator.port_up("water-in"), dtype=float)
    jet_exit = point(tip + up * JET_CAP_T)
    from _float_interface import magnet_above_waterline, diameter, height, bore_diameter, pocket_depth
    immersion = -magnet_above_waterline()
    data = {
        "units": "mm", "frame": "carbonator-local-y-up; inner floor y=0; axis x=z=0",
        "nativeColdCoreMapping": ["-cc.y", f"cc.z-{FLOOR:.5f}", "-cc.x"],
        "enclosureMapping": ["E.x", "E.z-64.7", "323.8-E.y"],
        "jetExit": rounded(jet_exit), "jetEntrance": rounded(point(tip)),
        "jetDiameter": JET_PASSAGE_D, "jetCapThickness": JET_CAP_T,
        "waterLumen": water, "gasLumen": gas, "outletLumen": outlet,
        "waterJetPassage": rounded([point(tip), jet_exit]),
        "lumenDiameter": fittings.ELBOW_BORE, "recommendedFluidRadius": 2.7,
        "gasExit": gas_port["maleTip"], "waterOutlet": outlet_port["maleTip"],
        "ports": {"water-in": water_port, "co2-in": gas_port, "carb-water-out": outlet_port},
        "vessel": {"outerRadius": carbonator.TUBE_OD/2, "innerRadius": carbonator.TUBE_ID/2,
                   "insideHeight": carbonator.interior_z[1]-FLOOR,
                   "tubeY": [-12.7,139.7], "bottomPlateY": [-6.35,0], "topPlateY": [127,133.35]},
        "guide": {"axisXZ": [-carbonator.ROD_XY[1],-carbonator.ROD_XY[0]], "diameter": carbonator.ROD_D,
                  "rangeY": [-carbonator.REGISTER_DEPTH,127+carbonator.REGISTER_DEPTH]},
        "float": {"asset": "magnetic-float-cad.json", "diameter": diameter, "height": height,
                  "guideBoreDiameter": bore_diameter, "pocketDepth": pocket_depth,
                  "localY": [-14,14], "magnetCenter": [0,0,0], "magnetCenterBelowWater": immersion,
                  "position": [-carbonator.ROD_XY[1],"level-8.766",-carbonator.ROD_XY[0]],
                  "freeboardAtSizingDensity": 14-immersion,
                  "material": {"bodyColor": "#d8d6cf", "bodyRoughness": .78, "bodyMetalness": 0,
                               "magnetColor": "#737d88", "magnetRoughness": .35, "magnetMetalness": .65}},
        "bundles": bundles,
        "notes": ["The same STEP shapes supply full hardware and exact Boolean half sections; all hardware needs no further coordinate rotation.",
                  "The half-space z<=0 passes through the port axes and sections the rod and float on the current sensing plane.",
                  "sectionFaceIndices is a flat vertex-index list of cut triangles; sectionTriangleOrdinals gives their face IDs in the original full index buffer.",
                  "Water and gas centerlines follow the layout elbow bores. The 6.35mm elbow bore is the repo's nominal layout placeholder, not a purchased-part measurement.",
                  "Reference collets model an external solid envelope without a flow bore. Fluid through that envelope is an explanatory overlay, not measured connector internals.",
                  "The float is the genuine current cylindrical 36 x 28 mm ASA Aero body with its enclosed coaxial RC62 ring. No external magnet puck belongs on its side.",
                  "The immersion offset is the repo's provisional 0.65 g/cc dry-foam buoyancy model; installed immersion requires calibration."],
    }
    (ASSETS / "carbonator-datums.json").write_text(json.dumps(data, indent=2) + "\n")
    manifest_path = ASSETS / "cad-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        manifest["carbonatorAnimation"] = {"datums": "carbonator-datums.json", "bundles": bundles}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"jetExit": data["jetExit"], "gasExit": data["gasExit"], "ports": data["ports"], "bundles": bundles}, indent=2))


if __name__ == "__main__":
    main()
