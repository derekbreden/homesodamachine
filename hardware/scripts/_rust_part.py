"""Parts the Rust kernel cuts (`tools/hsm/kernel`).

A part's Python module holds its numbers: it derives each one from the parts it closes on,
states its bounds and fills its README, as any generator does. Its program, beside it, cuts the
part's files from those numbers:

    said = _rust_part.cut("refrigeration", "fuse-clamp", numbers, part_dir)

writes `<name>.numbers.json` into `part_dir`, builds the program with cargo from the checkout's
`tools/hsm` workspace (the crate `tools/hsm/<crate>` names it), and runs it. The program writes
`<name>.step`, the model file beside it (`<name>.step.npz`), the payload (`<name>.step.mesh`)
and `<name>.stl`, and answers with what they hold (`hsm_kernel::part::write_part`). A program
that writes several file sets answers once for each, a line apiece, and this returns their files
and bodies together. `program(crate, name)` builds a program and returns its path, for a run
with arguments of its own.

A program runs from the checkout's root, and reads a STEP its numbers name by that path:

    "westbrass": _rust_part.step(WESTBRASS_STEP),

`step` returns the STEP's path from the root once a payload cut from it is on disk for
`hsm_kernel::import::step` to read. For a STEP of B-rep faces that is OCCT's mesh of each solid
of each body at the kernel's rule, cut once into `.cache/hsm/import/<SHA-256>.step.mesh` under
the CAD lock. A STEP of triangles is read through the payload its writer cut beside it.

THE TRACE SEES PYTHON, NOT CARGO. What rustc compiled into the program is in the dep-info file
cargo writes beside it. Those sources under this checkout, with the manifests and the lockfile
that chose them, are kept in `_READ_TARGETS`, and the files the program wrote in
`_WRITE_TARGETS`; `tools/bazel/trace_inputs.py` takes both at the end of a run.

CARGO BUILDS FROM THE CHECKOUT, NOT FROM AN ACTION'S COPY OF IT, into the checkout's own target
directory, `tools/hsm/target`. A Bazel action names its checkout in `HSM_WORKSPACE`, and the
sources there are the ones it declared; building from a copy at a new path each time would
compile the kernel again each time. And cargo judges a crate fresh by its files' times, under a
name that is the same from every checkout, so a target directory two checkouts share links one
checkout's kernel into the other's program. The directory is the checkout's own whatever
`CARGO_TARGET_DIR` says.
"""
from __future__ import annotations

import hashlib
import json
import os
import pwd
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_READ_TARGETS: set = set()
_WRITE_TARGETS: set = set()


def _home() -> Path:
    return Path(os.environ.get("HOME") or pwd.getpwuid(os.getuid()).pw_dir)


def _cargo() -> str:
    """`cargo` on the PATH, else where rustup puts it: Homebrew's rustup on a Mac, `~/.cargo`."""
    for found in (shutil.which("cargo"), "/opt/homebrew/opt/rustup/bin/cargo",
                  str(_home() / ".cargo" / "bin" / "cargo")):
        if found and Path(found).is_file():
            return found
    raise SystemExit("_rust_part: cargo is not installed (https://rustup.rs)")


def _compiled(dep_info: Path, workspace: Path) -> set:
    """The files under `workspace` rustc compiled into a program, as its dep-info file names
    them: one make rule, a space inside a path written `\\ `."""
    rule = dep_info.read_text().split("\n\n")[0].replace("\\\n", " ")
    _program, _, deps = rule.partition(": ")
    out = set()
    for dep in deps.replace("\\ ", "\0").split():
        try:
            out.add(Path(dep.replace("\0", " ")).resolve().relative_to(workspace).as_posix())
        except ValueError:
            pass
    return out


def _manifests(sources: set, crate: str, workspace: Path) -> set:
    """The lockfile, the workspace's manifest, and the manifest of each package a source is
    compiled in: the nearest `Cargo.toml` above it, or the crate's for a program kept beside its
    part."""
    out = {"tools/hsm/Cargo.toml", "tools/hsm/Cargo.lock", f"tools/hsm/{crate}/Cargo.toml"}
    for src in sources:
        parts = src.split("/")
        for n in range(len(parts) - 1, 2, -1):
            if parts[:2] == ["tools", "hsm"] and (workspace / "/".join(parts[:n]) / "Cargo.toml").is_file():
                out.add("/".join(parts[:n]) + "/Cargo.toml")
                break
    return out


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _workspace() -> Path:
    return Path(os.environ.get("HSM_WORKSPACE") or ROOT).resolve()


#: The kernel's rule (`tools/hsm/kernel/src/rule.rs`): mm, the chord's largest distance from the
#: curve; rad, the largest turn between two segments.
LINEAR, ANGULAR = 0.005, 0.05


def _src(payload: Path):
    """The `src` a payload's header names, or None."""
    try:
        with open(payload, "rb") as f:
            return json.loads(f.read(int.from_bytes(f.read(4), "little"))).get("src")
    except (OSError, ValueError):
        return None


def step(path) -> str:
    """The STEP at `path` named from the root, once a payload cut from it is on disk."""
    path = Path(path).resolve()
    name = _relative(path)
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    _READ_TARGETS.add(name)
    if b"meshcad tessellated" in data[:200]:
        beside = path.with_name(path.name + ".mesh")
        if _src(beside) != digest:
            raise SystemExit(f"_rust_part: {name} is triangles, and the payload beside it was not "
                             "cut from it; its own generator cuts both")
        _READ_TARGETS.add(_relative(beside))
        return name
    cached = _workspace() / ".cache" / "hsm" / "import" / f"{digest}.step.mesh"
    if not cached.is_file():
        _tessellate(path, cached, digest)
    return name


def _tessellate(path: Path, out: Path, digest: str) -> None:
    """OCCT's mesh of each solid of each body of the STEP at `path`, one face range per B-rep
    face, as a payload whose `src` is `digest`. A body of several solids is `name/1`, `name/2`;
    a body with no name takes the STEP's."""
    import numpy as np
    import _cadq_export                  # the CAD lock
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    entries, blob = [], bytearray()
    for body, (shape, color) in sorted(_cadq_export.import_assembly(path).items()):
        body, solids = body or path.name.removesuffix(".step"), shape.Solids()
        for k, solid in enumerate(solids, 1):
            BRepMesh_IncrementalMesh(solid.wrapped, LINEAR, False, ANGULAR, True)
            pos, idx, fac = [], [], []
            faces = TopExp_Explorer(solid.wrapped, TopAbs_FACE)
            while faces.More():
                face = TopoDS.Face_s(faces.Current())
                faces.Next()
                loc = TopLoc_Location()
                tri = BRep_Tool.Triangulation_s(face, loc)
                if tri is None or tri.NbTriangles() == 0:
                    continue
                trsf, flip, base, first = loc.Transformation(), face.Orientation() == TopAbs_REVERSED, len(pos), len(idx)
                pos += [tri.Node(i).Transformed(trsf).Coord() for i in range(1, tri.NbNodes() + 1)]
                for i in range(1, tri.NbTriangles() + 1):
                    a, b, c = (base + n - 1 for n in tri.Triangle(i).Get())
                    idx.append((a, c, b) if flip else (a, b, c))
                fac += [first, len(idx) - 1]
            if not idx:
                continue
            p, t = np.asarray(pos, np.float64), np.asarray(idx, np.int64)
            n, area = np.zeros_like(p), np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
            for j in range(3):
                np.add.at(n, t[:, j], area)
            n /= np.maximum(np.linalg.norm(n, axis=1), 1e-30)[:, None]
            entry = {"name": body if len(solids) == 1 else f"{body}/{k}",
                     "color": list(color.toTuple()[:3]) if color is not None else None}
            for key, arr in (("pos", p.astype("<f4")), ("nrm", n.astype("<f4")),
                             ("idx", t.astype("<u4")), ("fac", np.asarray(fac, "<u4"))):
                entry[key] = [len(blob), arr.size]
                blob += arr.tobytes()
            entries.append(entry)
    head = json.dumps({"v": 3, "meshes": entries, "src": digest}, separators=(",", ":")).encode()
    head += b" " * (-(len(head) + 4) % 4)
    # A sandboxed action reads the cache and cannot write it; the program then says what is missing.
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        temp = out.with_name(f".{out.name}.{os.getpid()}")
        temp.write_bytes(len(head).to_bytes(4, "little") + head + bytes(blob))
        os.replace(temp, out)
    except OSError:
        pass


def program(crate: str, name: str) -> Path:
    """Build `tools/hsm/<crate>`'s program `name`, keep what it was compiled from, and return
    where it is."""
    workspace = Path(os.environ.get("HSM_WORKSPACE") or ROOT).resolve()
    manifest = workspace / "tools" / "hsm" / crate / "Cargo.toml"
    # Cargo runs the `rustc` it finds on the PATH, and rustup keeps it beside cargo.
    cargo, target = _cargo(), workspace / "tools" / "hsm" / "target"
    env = {**os.environ, "HOME": str(_home()), "CARGO_TARGET_DIR": str(target),
           "PATH": os.pathsep.join([str(Path(cargo).parent), os.environ.get("PATH", "")])}
    subprocess.run([cargo, "build", "--release", "--locked", "--quiet",
                    "--manifest-path", str(manifest), "--bin", name], check=True, env=env)
    sources = _compiled(target / "release" / f"{name}.d", workspace)
    _READ_TARGETS.update(sources | _manifests(sources, crate, workspace))
    return target / "release" / name


def cut(crate: str, name: str, numbers: dict, part_dir) -> dict:
    """Write `numbers`, build `tools/hsm/<crate>`'s program `name` and run it into `part_dir`,
    and return what it says it wrote."""
    part_dir = Path(part_dir)
    numbers_path = part_dir / f"{name}.numbers.json"
    text = json.dumps(numbers, indent=1, sort_keys=True) + "\n"
    if not numbers_path.is_file() or numbers_path.read_text() != text:
        numbers_path.write_text(text)
    _WRITE_TARGETS.add(_relative(numbers_path))

    run = subprocess.run([str(program(crate, name)), str(numbers_path.resolve()), str(part_dir.resolve())],
                         check=True, stdout=subprocess.PIPE, text=True, cwd=ROOT)
    said = {"files": [], "bodies": []}
    for line in run.stdout.splitlines():
        if line.strip():
            each = json.loads(line)
            said["files"] += each["files"]
            said["bodies"] += each["bodies"]
    _WRITE_TARGETS.update(_relative(part_dir / f) for f in said["files"])
    return said
