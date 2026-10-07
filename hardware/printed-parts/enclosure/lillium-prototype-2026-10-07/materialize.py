"""Restore the preserved Lillium prototype files without running active CAD."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEFAULT_OUTPUT = ROOT / ".cache/lillium-prototype-2026-10-07"
DELIVERABLES = (
    "enclosure-back-top.step",
    "enclosure-back-top.stl",
    "enclosure-back-top.step.mesh",
)


def manifest():
    return json.loads((HERE / "manifest.json").read_text())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_snapshot(name, record):
    packed = (HERE / record["snapshot"]).read_bytes()
    if digest(packed) != record["compressed_sha256"]:
        raise ValueError(f"Compressed snapshot differs: {name}")
    raw = gzip.decompress(packed)
    if len(raw) != record["bytes"] or digest(raw) != record["sha256"]:
        raise ValueError(f"Restored snapshot differs: {name}")
    return raw


def materialize(names=DELIVERABLES, output=DEFAULT_OUTPUT):
    records = manifest()["artifacts"]
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name in names:
        raw = read_snapshot(name, records[name])
        path = output / name
        if not path.exists() or digest(path.read_bytes()) != records[name]["sha256"]:
            path.write_bytes(raw)
        paths[name] = path
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Also restore the fixed fit fixtures and source archive")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    names = tuple(manifest()["artifacts"]) if args.all else DELIVERABLES
    for name, path in materialize(names, args.output_dir).items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
