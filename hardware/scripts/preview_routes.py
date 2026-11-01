#!/usr/bin/env python3
r"""Build hollow route tubes with hsm-kernel and replace them in an exported scene.

    python3 hardware/scripts/preview_routes.py --routes routes.json \
        --scene context.step.mesh --output .cache/routes.step.mesh --contacts

The JSON is keyed by route ID. Each route supplies segments, od_mm and id_mm;
segments are line/arc points_mm or Bezier control_points_mm. The context is an
explicit exported snapshot. Only the supplied tube bodies are replaced.

Build the program once with:
    CARGO_BUILD_JOBS=2 cargo build --release --locked --manifest-path tools/hsm/Cargo.toml \
        -p hsm-kernel --example route-preview

This command starts no CadQuery process, takes no CAD lock, and writes no
production export. It uses the program in this checkout unless --kernel-bin
names another built copy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
ARRAYS = ("pos", "nrm", "idx", "fac")


def read_payload(raw):
    if len(raw) < 4:
        raise ValueError("payload has no header")
    size = struct.unpack_from("<I", raw)[0]
    if size > len(raw) - 4:
        raise ValueError("payload header extends past its file")
    header = json.loads(raw[4:4 + size])
    if header.get("v") not in (2, 3):
        raise ValueError("unsupported payload version")
    return header, raw[4 + size:]


def splice(context, tubes, routes_digest, context_digest, rule):
    old, old_blob = read_payload(context)
    new, new_blob = read_payload(tubes)
    names = {row["name"] for row in new["meshes"]}
    if len(names) != len(new["meshes"]):
        raise ValueError("the tube program returned duplicate names")
    previous = {}
    for row in old["meshes"]:
        name = row["name"].split("/")[-1]
        if name in names:
            if name in previous:
                raise ValueError(f"context contains more than one {name}")
            previous[name] = row
    if names - previous.keys():
        raise ValueError("context has no tube named " + ", ".join(sorted(names - previous.keys())))
    meshes, blob = [], bytearray()

    def append(row, data):
        row = dict(row)
        for key in ARRAYS:
            offset, count = row[key]
            if offset < 0 or count < 0 or offset + count * 4 > len(data):
                raise ValueError(f"{row['name']} has an invalid {key} array")
            row[key] = [len(blob), count]
            blob.extend(data[offset:offset + count * 4])
        meshes.append(row)

    for row in old["meshes"]:
        if row["name"].split("/")[-1] not in names:
            append(row, old_blob)
    for row in new["meshes"]:
        before = previous[row["name"]]
        append({**row, "name": before["name"], "color": before.get("color", row.get("color"))}, new_blob)
    header = {"v": 3, "meshes": meshes, "preview": {
        "context_sha256": context_digest, "routes_sha256": routes_digest,
        "tube_linear_mm": rule["linear_mm"], "tube_angular_rad": rule["angular_rad"]}}
    head = json.dumps(header, separators=(",", ":")).encode()
    head += b" " * ((-(len(head) + 4)) % 4)
    return struct.pack("<I", len(head)) + head + blob, [previous[n]["name"] for n in sorted(names)]


def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--routes", required=True, type=Path)
    parser.add_argument("--scene", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--kernel-bin", type=Path,
                        default=ROOT / "tools/hsm/target/release/examples/route-preview")
    parser.add_argument("--contacts", action="store_true", help="query every changed tube against the context with hsm")
    parser.add_argument("--id-mm", type=float, help="explicit bore diameter for routes whose JSON omits id_mm")
    args = parser.parse_args()
    routes, scene, output = args.routes.resolve(), args.scene.resolve(), args.output.resolve()
    if output in (routes, scene, args.kernel_bin.resolve()):
        parser.error("the output must differ from every input")
    if not args.kernel_bin.is_file():
        parser.error("route-preview is not built; see the build command above, or use --kernel-bin")
    route_bytes, context = routes.read_bytes(), scene.read_bytes()
    routes_file_digest = hashlib.sha256(route_bytes).hexdigest()
    if args.id_mm is not None:
        specifications = json.loads(route_bytes)
        for route in specifications.values():
            route.setdefault("id_mm", args.id_mm)
        route_bytes = json.dumps(specifications, sort_keys=True, separators=(",", ":")).encode()
    routes_digest = hashlib.sha256(route_bytes).hexdigest()
    context_digest = hashlib.sha256(context).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="route-preview-", dir=output.parent) as scratch:
        scratch = Path(scratch)
        snapshot = scratch / "routes.json"
        snapshot.write_bytes(route_bytes)
        tubes = scratch / "tubes.step.mesh"
        cut_start = time.monotonic()
        cut = subprocess.run([str(args.kernel_bin.resolve()), str(snapshot), str(tubes)],
                             text=True, capture_output=True, check=True)
        cut_wall = time.monotonic() - cut_start
        kernel = json.loads(cut.stdout)
        payload, names = splice(context, tubes.read_bytes(), routes_digest, context_digest, kernel)
        staged = scratch / "scene.step.mesh"
        staged.write_bytes(payload)
        os.replace(staged, output)
    kernel.pop("payload", None)
    report = {"scene": str(output), "context": str(scene), "context_sha256": context_digest,
              "routes_file_sha256": routes_file_digest, "routes_sha256": routes_digest,
              "payload_sha256": hashlib.sha256(payload).hexdigest(),
              "replaced": names, "kernel_process_wall_seconds": cut_wall, "kernel": kernel}
    if args.contacts:
        report["contacts"] = {}
        for name in names:
            result = subprocess.run(["hsm", "--root", str(ROOT), "--scene", str(output),
                                     "move", name, "--by", "0", "0", "0"],
                                    text=True, capture_output=True, check=True)
            answer = json.loads(result.stdout)
            if not answer.get("ok"):
                raise ValueError(answer.get("error", "hsm query failed"))
            report["contacts"][name] = answer
    report["elapsed_seconds"] = time.monotonic() - started
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.stderr or str(error)) from None
