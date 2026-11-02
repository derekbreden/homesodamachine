"""The part engine's Python generator worker: declared staging, execution and document carry.

The engine invokes this with the checkout's CAD interpreter. The shared action
plan supplies the inputs and outputs; geometry stays in the existing generator
and its Rust program. Actions with producer dependencies remain with the normal
build until the engine's dependency caller is connected.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools/bazel"), str(ROOT / "hardware/scripts")]
from gen_build import action_plan
from pysrc import same_code, stripped
from sync_tree import _SPLICE, _whole_rewritten, carried

SUPPORT = ("tools/hsm/generate.py", "tools/bazel/gen_build.py", "tools/bazel/inventory.py",
           "tools/bazel/pysrc.py", "tools/bazel/sync_tree.py", "tools/_artifact_inputs.py",
           "tools/cad-artifacts/pack.py", "tools/cad-requirements.txt")


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def relative(name):
    path = Path(name)
    if path.is_absolute() or not path.parts or any(p in ("..", ".") for p in path.parts):
        raise ValueError("Generator paths are relative to their declared root: " + name)
    return path


def source_bytes(path, mode):
    raw = path.read_bytes()
    if mode == "pysrc":
        try:
            result = stripped(raw)
        except SyntaxError:
            return raw
        if not same_code(raw, result):
            raise ValueError("Comment stripping changes code: " + str(path))
        return result
    return raw


def describe(target):
    if target != "water-inlet-jet-fixture":
        raise ValueError("The generator-action slice currently supports water-inlet-jet-fixture")
    actions, _ = action_plan()
    if target not in actions:
        raise ValueError("No declared generator action: " + target)
    action = actions[target]
    if action["dependencies"]:
        raise ValueError("Generator dependencies still require the normal build: "
                         + ", ".join(action["dependencies"]))
    if action["node_runtimes"]:
        raise ValueError("Node runtimes still require the normal build")
    rewritten = sorted(set(action["docs"]))
    for name in rewritten:
        if Path(name).suffix not in _SPLICE and not _whole_rewritten(name):
            raise ValueError("No document carry for " + name)
    inputs = []
    for name in sorted(set(action["reads"]) | set(action["optional"]) | set(SUPPORT)):
        path = ROOT / relative(name)
        mode = "pysrc" if name in action["stripped"] else "raw"
        if not path.is_file():
            if name not in action["optional"]:
                raise FileNotFoundError(path)
            digest = None
        else:
            digest = hashlib.sha256(source_bytes(path, mode)).hexdigest()
        inputs.append({"path": name, "mode": mode, "sha256": digest})
    packages = {}
    for line in (ROOT / "tools/cad-requirements.txt").read_text().splitlines():
        if match := re.fullmatch(r"([A-Za-z0-9_.-]+)==[^\s]+", line):
            name = match[1]
            try:
                packages[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                packages[name] = None
    return {"version": 1, "target": target, "generators": action["generators"],
            "inputs": inputs, "outputs": sorted(action["solids"] + action["docs"]),
            "rewritten": rewritten, "payload": any(p.endswith(".step.mesh") for p in action["solids"]),
            "runtime": {"python": sys.version, "executable_sha256": sha(sys.executable),
                        "platform": sys.platform, "packages": packages}}


def clone(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform == "darwin":
        done = subprocess.run(["/bin/cp", "-c", str(source), str(destination)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if done.returncode == 0:
            return
    shutil.copyfile(source, destination)


def validate(recipe, root):
    for row in recipe["inputs"]:
        path = root / relative(row["path"])
        digest = (hashlib.sha256(source_bytes(path, row["mode"])).hexdigest()
                  if path.is_file() else None)
        if digest != row["sha256"]:
            raise ValueError("Generator input changed: " + row["path"])


def execute(recipe, scratch, socket):
    stage, out = scratch / "stage", scratch / "out"
    stage.mkdir(); out.mkdir()
    for row in recipe["inputs"]:
        if row["sha256"] is None:
            continue
        source, dest = ROOT / relative(row["path"]), stage / row["path"]
        if row["mode"] == "pysrc":
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(source_bytes(source, row["mode"]))
        else:
            clone(source, dest)
    validate(recipe, stage)
    # Native memo stores remain the checkout's existing stores, as in a normal action.
    (stage / ".cache").symlink_to(ROOT / ".cache", target_is_directory=True)
    digest = hashlib.sha256()
    for row in recipe["inputs"]:
        path = stage / row["path"]
        if path.is_file() and path.suffix in (".step", ".dxf", ".stl"):
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1 << 20), b""):
                    digest.update(chunk)
    reads_log = scratch / "nested-reads.jsonl"
    os.environ.update(HSM_WORKSPACE=str(ROOT), HSM_REPO_ROOT=str(stage),
                      HSM_INPUT_DIGEST=digest.hexdigest()[:32], HSM_SOCKET=socket,
                      HSM_GENERATOR_READS=str(reads_log))
    if recipe["payload"]:
        os.environ.pop("HSM_SKIP_MESH_PAYLOAD", None)
    os.chdir(stage)
    # Match the normal action's script entry, including its existing main guard.
    sys.path[:0] = [str(stage / "hardware/scripts")]
    for name in recipe["generators"]:
        sys.argv = [name]
        sys.path.insert(0, str((stage / name).parent))
        runpy.run_path(str(stage / name), run_name="__main__")
        sys.path.pop(0)
    nested = [json.loads(line) for line in reads_log.read_text().splitlines()] if reads_log.exists() else []
    bound = {row["path"]: row["sha256"] for row in recipe["inputs"]}
    external, bindings, keepable = {}, [], True
    for run in nested:
        for base, name, expected in run["reads"]:
            path = ((Path(run[base]) / name) if base in ("root", "workspace") else Path(name))
            path = path.resolve()
            if path.is_relative_to(stage):
                rel = path.relative_to(stage).as_posix()
                if rel in recipe["outputs"]:
                    role = "output"
                elif rel in bound and bound[rel] == expected:
                    role = "input"
                else:
                    role = "unbound"; keepable = False
                if not path.is_file() or sha(path) != expected:
                    keepable = False
                bindings.append({"base": role, "path": rel, "sha256": expected})
            else:
                role = "workspace" if path.is_relative_to(ROOT) else "/"
                name = path.relative_to(ROOT).as_posix() if role == "workspace" else str(path)
                external[role, name] = expected
                bindings.append({"base": role, "path": name, "sha256": expected})
                if not path.is_file() or sha(path) != expected:
                    keepable = False
    for name in recipe["outputs"]:
        clone(stage / relative(name), out / name)
    validate(recipe, ROOT)
    import _run_slots
    result = {"runtime_reads": bindings, "nested_runs": nested, "keepable": keepable,
              "verified_run_lease": bool(_run_slots.current()),
              "native_loaded": "OCP.OCP" in sys.modules,
              "external_reads": [[base, name, digest] for (base, name), digest in sorted(external.items())]}
    (scratch / "receipt.json").write_text(json.dumps(result))


def place(recipe, blobs, output, files):
    """Use the normal carry's authored scopes; the engine places every other blob."""
    for name, digest in files:
        if name not in recipe["rewritten"]:
            continue
        path, source = output / relative(name), blobs / digest
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in _SPLICE and path.is_file():
            text = path.read_text()
            result = carried(source.read_text(), text, path.suffix)
            if result != text:
                path.write_text(result)
        elif not path.is_file() or sha(path) != digest:
            clone(source, path)


if __name__ == "__main__":
    mode, *args = sys.argv[1:]
    if mode == "describe":
        print(json.dumps(describe(args[0]), sort_keys=True))
    elif mode == "execute":
        execute(json.loads(Path(args[0]).read_text()), Path(args[1]), args[2])
    elif mode == "place":
        data = json.loads(Path(args[0]).read_text())
        validate(data["recipe"], ROOT)
        place(data["recipe"], Path(args[1]), Path(args[2]), data["files"])
    else:
        raise ValueError("Unknown generator worker operation: " + mode)
