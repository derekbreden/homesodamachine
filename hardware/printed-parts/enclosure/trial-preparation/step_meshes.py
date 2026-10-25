#!/usr/bin/env python3
"""Print meshes for the parts whose generator writes only a STEP.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/step_meshes.py <part>.step [...]
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/step_meshes.py --check

Each STEP is read through XCAF as the bodies its generator wrote. A part of several bodies (a
label and its lettering) is fused into the one solid it prints as. The mesh is written beside
the STEP as `<part>.stl` by `cadlib/print_mesh.py`, at its absolute tolerance and read back the
way a slicer reads it. `step-meshes.json` binds every STL written here to the STEP digest it was
cut from; `prepare.py` refuses an STL whose STEP has moved since, and `--check` lists them.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
RECORD = HERE / "step-meshes.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return Path(path).resolve().relative_to(ROOT).as_posix()


def load() -> dict:
    return json.loads(RECORD.read_text()) if RECORD.is_file() else {
        "_": "STLs cut by step_meshes.py from the STEP beside each, bound by digest.", "meshes": {}}


def check() -> int:
    stale = 0
    for stl, row in sorted(load()["meshes"].items()):
        step, mesh = ROOT / row["step"], ROOT / stl
        state = ("missing STL" if not mesh.is_file() else "missing STEP" if not step.is_file()
                 else "STEP moved" if sha256(step) != row["step_sha256"]
                 else "STL changed" if sha256(mesh) != row["stl_sha256"] else "bound")
        stale += state != "bound"
        print(f"{state:12s} {stl}")
    return 1 if stale else 0


def export(steps: list[Path]) -> None:
    sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ROOT / "hardware/printed-parts/cadlib")]
    from _run_lock import acquire
    acquire(str(Path(__file__)))
    from _cadq_export import import_assembly
    from print_mesh import print_mesh_angle, print_mesh_tol, write_print_stl

    record = load()
    for step in steps:
        step = step.resolve()
        bodies = import_assembly(step)
        names = sorted(bodies)
        solids = [s for name in names for s in bodies[name][0].Solids()]
        if not solids:
            raise ValueError(f"{relative(step)} holds no solid")
        shape = solids[0] if len(solids) == 1 else solids[0].fuse(*solids[1:]).clean()
        stl = step.with_suffix(".stl")
        mesh = write_print_stl(shape, stl)
        low, high = mesh.bounds
        record["meshes"][relative(stl)] = {
            "step": relative(step), "step_sha256": sha256(step), "stl_sha256": sha256(stl),
            "bodies": names, "solids_fused": len(solids), "result_solids": len(shape.Solids()),
            "tolerance_mm": print_mesh_tol, "angle_rad": print_mesh_angle,
            "facets": int(len(mesh.faces)), "volume_mm3": round(float(mesh.volume), 3),
            "bounds_mm": [[round(float(v), 4) for v in low], [round(float(v), 4) for v in high]],
            "tool_sha256": sha256(Path(__file__)),
            "written_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        RECORD.write_text(json.dumps(record, indent=2) + "\n")
        size = [round(float(h - l), 2) for l, h in zip(low, high)]
        print(f"{relative(stl)}  {sha256(stl)[:12]}  from {sha256(step)[:12]}  {names}  "
              f"{len(mesh.faces)} facets  {mesh.volume:.1f} mm3  {size} mm", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("steps", nargs="*", type=Path)
    parser.add_argument("--check", action="store_true", help="list each bound STL against its STEP")
    args = parser.parse_args()
    if args.check:
        raise SystemExit(check())
    if not args.steps:
        parser.error("name one or more STEP files")
    export([ROOT / s if not s.is_absolute() else s for s in args.steps])


if __name__ == "__main__":
    main()
