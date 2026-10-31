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

    run = subprocess.run([str(program(crate, name)), str(numbers_path), str(part_dir)],
                         check=True, stdout=subprocess.PIPE, text=True)
    said = {"files": [], "bodies": []}
    for line in run.stdout.splitlines():
        if line.strip():
            each = json.loads(line)
            said["files"] += each["files"]
            said["bodies"] += each["bodies"]
    _WRITE_TARGETS.update(_relative(part_dir / f) for f in said["files"])
    return said
