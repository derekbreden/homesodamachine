#!/usr/bin/env python3
"""Extract the video's lightweight CAD from the repository's generated payloads.

Run with tools/cad-venv/bin/python. No CAD is rebuilt. The export retains mm and
the enclosure's Z-up frame, including the standalone cold core's placement.
"""
from __future__ import annotations

import hashlib
import gzip
import json
import shutil
import struct
import sys
import urllib.request
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"


def payload(relative: str):
    path = ROOT / relative
    blob = path.read_bytes()
    header_size = struct.unpack_from("<I", blob)[0]
    header = json.loads(blob[4:4 + header_size])
    data = memoryview(blob)[4 + header_size:]
    blob_sha = hashlib.sha256(blob).hexdigest()
    for entry in header["meshes"]:
        arrays = {}
        for key, dtype in (("pos", "<f4"), ("nrm", "<f4"), ("idx", "<u4")):
            offset, count = entry[key]
            arrays[key] = np.frombuffer(data, dtype=dtype, count=count, offset=offset).reshape((-1, 3)).copy()
        yield entry, arrays, blob_sha, header["src"]


def bounds(points):
    return np.round(np.vstack((points.min(axis=0), points.max(axis=0))), 3).tolist()


def group(name: str):
    if name.startswith("enclosure-"):
        return name
    if name.startswith("foam-"):
        return "insulation"
    if name.startswith("evap-"):
        return "evaporator"
    if name.startswith("reservoir-") or name.startswith(("float-a", "float-b", "reed-a", "reed-b")):
        return "flavor-reservoirs"
    if name.startswith(("carbonator", "endcap-", "float-rod-carb", "float-carb", "water-inlet-jet", "collet-", "prv-", "reed-carb", "reed-bridge")):
        return "carbonator"
    if name.startswith("display"):
        return "display"
    if name.startswith("funnel"):
        return "funnel"
    return "mechanical-context"


def export_mesh(entry, arrays, *, cold_core: bool, group_override=None):
    name = entry["name"]
    positions, normals, indices = arrays["pos"], arrays["nrm"], arrays["idx"]
    source_triangles = len(indices)
    if name.startswith("enclosure-"):
        target = 18000
    elif name.startswith("foam-"):
        target = 6500
    elif name == "evap-coil":
        target = 18000
    else:
        target = 4000
    if source_triangles > target:
        mesh = trimesh.Trimesh(vertices=positions, faces=indices, process=False)
        mesh.merge_vertices(digits_vertex=5)
        mesh = mesh.simplify_quadric_decimation(face_count=target, aggression=5)
        mesh = trimesh.graph.smooth_shade(mesh, angle=np.deg2rad(35), facet_minarea=20)
        positions = np.asarray(mesh.vertices)
        normals = np.asarray(mesh.vertex_normals)
        indices = np.asarray(mesh.faces)
    native_bounds = bounds(positions)
    if cold_core:
        # The native cold-core frame rotates +90 degrees about Z into the cabinet.
        positions = positions[:, [1, 0, 2]] * np.array([-1, 1, 1])
        positions += [0, 323.8, 20]
        normals = normals[:, [1, 0, 2]] * np.array([-1, 1, 1])
    return {
        "name": name,
        "group": group_override or group(name),
        "color": [round(float(c), 6) for c in entry["color"]],
        "positions": np.round(positions, 3).reshape(-1).tolist(),
        "normals": np.round(normals, 4).reshape(-1).tolist(),
        "indices": indices.reshape(-1).tolist(),
        "bounds": bounds(positions),
        "nativeBounds": native_bounds,
        "sourceTriangles": source_triangles,
        "triangles": int(len(indices)),
    }


def make_bundle(source, predicate, target, cold_core=False, frame="enclosure-z-up", group_override=None, clip_floor=None):
    meshes = []
    for entry, arrays, sha, source_key in payload(source):
        if predicate(entry["name"]):
            if clip_floor is not None:
                faces = arrays["idx"]
                faces = faces[np.all(arrays["pos"][faces, 2] >= clip_floor, axis=1)]
                if not len(faces):
                    continue
                used, inverse = np.unique(faces, return_inverse=True)
                arrays = {"pos": arrays["pos"][used], "nrm": arrays["nrm"][used], "idx": inverse.reshape((-1, 3))}
            item = export_mesh(entry, arrays, cold_core=cold_core, group_override=group_override)
            meshes.append(item)
            print(f'{target}: {item["name"]} {item["sourceTriangles"]:,} → {item["triangles"]:,}', flush=True)
    data = {
        "version": 1,
        "units": "mm",
        "frame": frame,
        "colorSpace": "linear-srgb",
        "source": source,
        "sourceSha256": sha,
        "sourceGeometryKey": source_key,
        "meshes": meshes,
    }
    path = ASSETS / target
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n")
    compressed = path.with_suffix(path.suffix + ".gz")
    compressed.write_bytes(gzip.compress(path.read_bytes(), compresslevel=9, mtime=0))
    all_points = np.concatenate([np.asarray(m["positions"]).reshape((-1, 3)) for m in meshes])
    return {"file": target, "compressedFile": compressed.name, "meshes": len(meshes), "triangles": sum(m["triangles"] for m in meshes), "bytes": path.stat().st_size, "compressedBytes": compressed.stat().st_size, "bounds": bounds(all_points), "sourceSha256": sha}


def coil_paths():
    sys.path.insert(0, str(ROOT / "hardware/cold-core-layout"))
    import _coil

    floor = _coil._carbonator_bottom_z + 12.7
    def to_local(point):
        x, y, z = point.toTuple() if hasattr(point, "toTuple") else point
        return [round(-y, 4), round(z - floor, 4), round(-x, 4)]
    wrap = [to_local(point) for point in _coil.wrap_points()]
    tails = {}
    for end in ["inlet", "outlet"]:
        wire = _coil.tail_form(end).wire()
        count = max(64, int(wire.Length() / 1.5))
        points = [to_local(wire.positionAt(i / count)) for i in range(count + 1)]
        tails[end] = list(reversed(points)) if end == "inlet" else points
    result = {
        "units": "mm", "frame": "three-y-up, radial center at origin, internal floor y=0",
        "nativeColdCoreMapping": ["-cc.y", f"cc.z-{floor:.4f}", "-cc.x"],
        "wraps": _coil.TOTAL_WRAPS, "nominalRadius": _coil.WIND_R,
        "tubeRadius": _coil.TUBE_R, "nativeFloorZ": floor,
        "lowY": _coil.evap_tail_low_z - floor, "highY": _coil.evap_tail_high_z - floor,
        "source": "hardware/cold-core-layout/_coil.py",
        "sourceSha256": hashlib.sha256((ROOT / "hardware/cold-core-layout/_coil.py").read_bytes()).hexdigest(),
        "wrapPoints": wrap, "inletPoints": tails["inlet"], "outletPoints": tails["outlet"],
        "flowPoints": tails["inlet"] + wrap[1:] + tails["outlet"][1:],
        "flowDirection": "inlet station through lower coil end, up 9.5 turns, through outlet tail",
    }
    (ASSETS / "coil-path.json").write_text(json.dumps(result, separators=(",", ":")) + "\n")
    return {"file": "coil-path.json", "wrapPoints": len(wrap), "inletPoints": len(tails["inlet"]), "outletPoints": len(tails["outlet"])}


def faucet_assets():
    names = {"westbrass", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x", "lever",
             "above_counter_plate", "above_counter_gasket", "shell_base", "shell_tip",
             "faucet-display-cover-seated", "faucet_display", "faucet_display_screen"}
    bundle = make_bundle("hardware/faucet-layout/faucet-assembly.step.mesh", lambda n: n in names,
                         "faucet-cad.json", frame="faucet-z-up", group_override="faucet", clip_floor=-.2)
    datums = {
        "units": "mm", "frame": "faucet native, countertop z=0; forward is -Y",
        "threeYUpMapping": ["F.x", "F.z", "-F.y"],
        "waterOutlet": [0, -133.9967220, 180.3887434],
        "flavorOutlet": [-3.175, -138.6377220, 184.2857434],
        "exitDirection": [0, -0.6427876097, -0.7660444431],
        "waterIllustrativeSpeedMmS": 900, "flavorIllustrativeSpeedMmS": 750,
        "leverPivot": [0, 0, 46], "leverPourRotationRadians": .23,
        "suggestedGlass": {"baseCenter": [0, -196, .4], "height": 86.45, "outerRimRadius": 38.15, "liquidLevel": 68},
        "screen": {"mesh": "faucet_display_screen", "texture": "faucet-display-flavor1.png", "u": "(F.x+8.875)/17.75", "v": "(F.z-200.580)/25.483", "imageSize": [172,320]},
        "source": "Current faucet CAD and marketing/video/one-less-errand/studio/stage.py",
        "note": "Outlet stations and tangent are CAD-based; pour speeds and glass are illustrative shot staging.",
    }
    (ASSETS / "faucet-datums.json").write_text(json.dumps(datums, indent=2) + "\n")
    import re
    from PIL import Image
    source = (ROOT / "firmware/src_faucet/images/flavor1_faucet.h").read_text()
    body = source[source.index("{")+1:source.rindex("}")]
    words = np.asarray([int(v,16) for v in re.findall(r"0x([0-9a-fA-F]{4})", body)], dtype=np.uint16)
    assert len(words) == 172*320
    rgb = np.stack((((words >> 11) & 31)*255/31, ((words >> 5) & 63)*255/63, (words & 31)*255/31), axis=1)
    Image.fromarray(np.rint(rgb).astype(np.uint8).reshape((320,172,3))).save(ASSETS / "faucet-display-flavor1.png")
    return bundle


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    exterior = {
        "enclosure-front-bottom", "enclosure-front-top", "enclosure-back-bottom", "enclosure-back-top",
        "display/1", "display/2", "display-cover", "display-gasket", "funnel", "funnel-cover", "funnel-frame",
        "compressor/1", "compressor/2", "condenser+fan", "psu", "pump-a-head", "pump-a-boss", "pump-a-motor",
        "pump-b-head", "pump-b-boss", "pump-b-motor", "c14-inlet", "pcba",
    }
    bundles = [make_bundle("hardware/manifold-layout/enclosure-assembly.step.mesh", lambda n: n in exterior, "enclosure-cad.json")]
    core_predicate = lambda n: (n.startswith(("foam-", "carbonator-", "endcap-", "float-rod-", "float-", "reservoir-", "evap-", "collet-", "prv-", "reed-"))
                                or n in {"water-inlet-jet-cap-nominal", "probe-carbonator-ds18b20", "probe-coil-ds18s20"})
    bundles.append(make_bundle("hardware/cold-core-layout/cold-core-assembly.step.mesh", core_predicate, "cold-core-cad.json", cold_core=True))
    bundles.append(faucet_assets())
    coil = coil_paths()
    for name in ["wordmark.svg", "wordmark-reverse.svg", "wordmark-stacked.svg", "mark.svg", "mark-white.svg", "mark-blue.svg"]:
        shutil.copyfile(ROOT / "web/public/brand" / name, ASSETS / name)
    shutil.copyfile(ROOT / "brand/palette.json", ASSETS / "palette.json")
    fonts = {
        "Archivo-latin-variable.woff2": "https://fonts.gstatic.com/s/archivo/v25/k3kPo8UDI-1M0wlSV9XAw6lQkqWY8Q82sLydOxI.woff2",
        "IBMPlexMono-latin-regular.woff2": "https://fonts.gstatic.com/s/ibmplexmono/v20/-F63fjptAgt5VM-kVkqdyU8n1i8q1w.woff2",
    }
    for name, url in fonts.items():
        if not (ASSETS / name).exists():
            urllib.request.urlretrieve(url, ASSETS / name)
    license_sources = {
        "Archivo-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/OFL.txt",
        "IBMPlexMono-OFL.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/OFL.txt",
    }
    for name, url in license_sources.items():
        if not (ASSETS / name).exists():
            urllib.request.urlretrieve(url, ASSETS / name)
    manifest = {
        "units": "mm", "nativeFrame": "X-right, Y-rear, Z-up; enclosure assembly",
        "threeYUpMapping": ["E.x", "E.z", "-E.y"],
        "carbonator": {"axisXY": [0, 323.8], "tubeBottomZ": 52, "tubeTopZ": 204.4, "insideFloorZ": 64.7, "insideCeilingZ": 191.7, "outerRadius": 63.5},
        "coldCoreToEnclosure": {"matrixRowMajor": [0,-1,0,0,1,0,0,323.8,0,0,1,20,0,0,0,1]},
        "bundles": bundles,
        "coilPath": coil,
        "faucetDatums": "faucet-datums.json",
        "fonts": fonts,
        "licenses": license_sources,
        "notes": ["Enclosure and cold-core position/normal arrays share the enclosure frame; do not apply coldCoreToEnclosure twice. Faucet geometry uses its own mounting-axis frame.", "CAD display meshes use conservative quadric simplification for video; source design geometry is unchanged.", "Color triples are linear-sRGB and should be passed directly to THREE.Color without another sRGB-to-linear conversion.", "The standalone cold-core payload supplies the coil; the enclosure bundle does not duplicate its embedded cold core.", "Compressed bundles are the committed sources; plain JSON files are local working copies."]
    }
    (ASSETS / "cad-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["bundles"], indent=2))


if __name__ == "__main__":
    main()
