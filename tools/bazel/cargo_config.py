#!/usr/bin/env python3
"""cargo_config.py — what in the Rust workspace's manifest and lock file can change a compiled program.

    python3 tools/bazel/cargo_config.py      writes tools/hsm/cargo-config.json

A step that runs a Rust program is made from the program's sources, the manifests of its crates,
and this file. It is the workspace manifest without its member list, and the lock file's external
packages: the compiler settings and the library versions every program is built with. Adding a
crate to the workspace changes the manifest's member list and the lock's workspace packages, and
neither of those is in this file, so no step reruns for it.
"""

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HSM = ROOT / "tools" / "hsm"
OUT = HSM / "cargo-config.json"


def config() -> dict:
    manifest = tomllib.loads((HSM / "Cargo.toml").read_text())
    manifest.get("workspace", {}).pop("members", None)
    lock = tomllib.loads((HSM / "Cargo.lock").read_text())
    external = [package for package in lock.get("package", []) if "source" in package]
    return {"manifest": manifest, "lock": {"version": lock.get("version"), "external": external}}


def main() -> int:
    text = json.dumps(config(), indent=1, sort_keys=True) + "\n"
    if not OUT.is_file() or OUT.read_text() != text:
        OUT.write_text(text)
    print(f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
