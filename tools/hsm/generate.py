"""The part engine's Python generator worker: declared staging, execution and document carry.

The engine invokes this with the checkout's CAD interpreter. The shared action
plan supplies the inputs and outputs; geometry stays in the existing generator
and its Rust program. The enrolled dependency slice uses completed producer blobs;
other actions remain with the normal build.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
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
ENROLLED = frozenset(("water-inlet-jet-fixture", "elbow-cradle", "funnel-mold"))


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
    actions, _ = action_plan()
    ordered, visited = [], set()

    def visit(name):
        if name in visited:
            return
        if name not in ENROLLED:
            raise ValueError("Generator action is not enrolled in the engine slice: " + name)
        if name not in actions:
            raise ValueError("No declared generator action: " + name)
        action = actions[name]
        if action["node_runtimes"] or action["support_inputs"]:
            raise ValueError("Node and support actions still require the normal build: " + name)
        for dependency in action["dependencies"]:
            visit(dependency)
        visited.add(name)
        ordered.append(describe_action(name, action))

    visit(target)
    return {"version": 2, "target": target, "actions": ordered}


def describe_action(target, action):
    rewritten = sorted(set(action["docs"]))
    for name in rewritten:
        if Path(name).suffix not in _SPLICE and not _whole_rewritten(name):
            raise ValueError("No document carry for " + name)
    inputs = []
    for name in sorted(set(action["reads"]) | set(action["optional"]) | set(SUPPORT)):
        path = ROOT / relative(name)
        mode = "pysrc" if name in action["stripped"] else "raw"
        producer = action["producers"].get(name)
        if producer and producer != target:
            # The engine binds this hash after this request completes the producer.
            inputs.append({"path": name, "mode": mode, "producer": producer})
            continue
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
    return {"version": 2, "target": target, "generators": action["generators"],
            "entrypoints": action["entrypoints"], "dependencies": action["dependencies"],
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


def validate(recipe, root, *, sources_only=False):
    for row in recipe["inputs"]:
        if sources_only and "producer" in row:
            continue
        path = root / relative(row["path"])
        digest = (hashlib.sha256(source_bytes(path, row["mode"])).hexdigest()
                  if path.is_file() else None)
        if digest != row["sha256"]:
            raise ValueError("Generator input changed: " + row["path"])


def execute(recipe, scratch, socket, blobs):
    stage, out = scratch / "stage", scratch / "out"
    stage.mkdir(); out.mkdir()
    for row in recipe["inputs"]:
        if row["sha256"] is None:
            continue
        if "producer" in row:
            if row["mode"] != "raw" or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
                raise ValueError("Invalid completed producer input: " + row["path"])
            source = blobs / row["sha256"]
        else:
            source = ROOT / relative(row["path"])
        dest = stage / row["path"]
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
    env = dict(os.environ, HSM_WORKSPACE=str(ROOT), HSM_REPO_ROOT=str(stage),
                      HSM_INPUT_DIGEST=digest.hexdigest()[:32], HSM_SOCKET=socket,
                      HSM_GENERATOR_READS=str(reads_log))
    if recipe["payload"]:
        env.pop("HSM_SKIP_MESH_PAYLOAD", None)
    import _run_slots
    # BUILD starts each script in a separate interpreter. Modules, globals and main
    # guards cannot leak between co-writers, while their staged files remain shared.
    for argv in recipe["entrypoints"]:
        subprocess.run([sys.executable, *argv], cwd=stage, check=True,
                       **_run_slots.subprocess_kwargs(env))
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
    validate(recipe, ROOT, sources_only=True)
    result = {"runtime_reads": bindings, "nested_runs": nested, "keepable": keepable,
              "verified_run_lease": bool(_run_slots.current()),
              "entrypoints": recipe["entrypoints"], "separate_interpreters": True,
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
        execute(json.loads(Path(args[0]).read_text()), Path(args[1]), args[2], Path(args[3]))
    elif mode == "place":
        data = json.loads(Path(args[0]).read_text())
        validate(data["recipe"], ROOT, sources_only=True)
        place(data["recipe"], Path(args[1]), Path(args[2]), data["files"])
    else:
        raise ValueError("Unknown generator worker operation: " + mode)
