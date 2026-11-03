#!/usr/bin/env python3
"""Materialize selected enclosure pieces: STEP, printed STL and viewer payload each.

This entry reads the already-declared Box and sends each selected numeric recipe to the
ordinary enclosure Rust part program. Rust writes the structural model, STEP and printed STL;
the shared Rust print writer checks that STL and writes its viewer payload. Selection does not
construct another enclosure piece or the assembled machine.

    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py
    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py --pieces pump-retainer
    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py --pieces pump-retainer front-top
    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py --pieces back-top
    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py --pieces front-bottom back-bottom front-top back-top

Each selected piece is completed in temporary files and seated after its printed STL passes the
existing slicer-facing reading. STEP, STL, fine model and any STL source records seat before the
STEP-bound payload. The publisher sees the changed payload only after its current siblings.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib
import json
import hashlib
import os
import shutil
import struct
import sys
import tempfile
import time
from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "tools" / "docgen").is_dir())
_ENCLOSURE = _ROOT / "hardware" / "printed-parts" / "enclosure" / "enclosure"
_OUTPUT = _ENCLOSURE
_BOXES = (
    _ROOT / "hardware" / "manifold-layout" / "enclosure-box.json",
    _ROOT / "bazel-bin" / "out" / "enclosure-box" / "hardware" / "manifold-layout"
    / "enclosure-box.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _seat(source: Path, target: Path) -> bool:
    """Seat one completed sibling, leaving an identical target's mtime alone."""
    if target.is_file() and _sha256(source) == _sha256(target):
        return False
    os.replace(source, target)
    return True


def _declared_box(box_spec, enc):
    """The first existing declared Box this source can read, with its path.

    A carried Box may trail a source checkpoint while the most recent completed producer output
    remains in bazel-bin.  Shape/schema validation belongs to `_box_spec.read`; this path never
    runs the placement producer to repair an old document.
    """
    refused = []
    for path in _BOXES:
        try:
            box, bounds = box_spec.read(
                enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=path)
            return box, bounds, path
        except (FileNotFoundError, ValueError) as error:
            refused.append(f"{path.relative_to(_ROOT)}: {error}")
    raise ValueError("no existing enclosure-box declaration matches this source:\n  "
                     + "\n  ".join(refused))


# The retainer has smooth functional faces; quadrant show faces take the outer flutes.
DEFAULT_PIECES = ("pump-retainer", "front-top")
PIECES = (*DEFAULT_PIECES, "back-top", "front-bottom", "back-bottom")


def _builder(enc, name):
    """The selected part's current scalar recipe and existing Rust program."""
    builders = {
        "pump-retainer": ("_enclosure_pump_retainer", "enclosure-pump-retainer", "numbers"),
        "front-top": ("_enclosure_front_top", "enclosure-front-top", "print_numbers"),
        "back-top": ("_enclosure_back_top", "enclosure-back-top", "print_numbers"),
        "front-bottom": ("_enclosure_front_bottom", "enclosure-front-bottom", "print_numbers"),
        "back-bottom": ("_enclosure_panel", "enclosure-panel", "print_numbers"),
    }
    if name not in builders:
        raise ValueError(f"{name!r} is not supported; this path stands {PIECES}")
    module, program, recipe = builders[name]
    return program, getattr(importlib.import_module(module), recipe)


@contextmanager
def _staging(output, stem):
    """Build under the checkout and seat from the destination's own filesystem."""
    with tempfile.TemporaryDirectory(prefix=f".{stem}-", dir=output) as directory:
        seated = Path(directory)
        if seated.resolve().is_relative_to(_ROOT):
            yield seated, seated
        else:
            cache = _ROOT / "tmp" / "materialize-enclosure"
            cache.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=f"{stem}-", dir=cache) as work:
                yield Path(work), seated


def _payload_source(path):
    with path.open("rb") as stream:
        length, = struct.unpack("<I", stream.read(4))
        return json.loads(stream.read(length)).get("src")


def _materialize_piece(enc, box, name, output: Path, started: float) -> dict:
    import _rust_part
    from _rust_enclosure_presentation import print_payload

    program, recipe = _builder(enc, name)
    numbers = recipe(enc, box)
    described = time.perf_counter()
    stem = f"enclosure-{name}"
    with _staging(output, stem) as (work, seated_work):
        _rust_part.cut("enclosure-shell", program, numbers, work)
        built = time.perf_counter()
        step = work / f"{stem}.step"
        stl = work / f"{stem}.stl"
        model = work / f"{stem}.step.npz"
        payload = work / f"{stem}.step.mesh"
        # This entry checks every selected print, including the relaxed retainer.
        # The public triplet's presentation stays bound to its exact STEP bytes.
        printed = print_payload(step, check_print=True, source=step,
                                identity=(stem, numbers["color"]))
        source_sha = _payload_source(payload)
        step_sha = _sha256(step)
        if source_sha != step_sha:
            raise ValueError(
                f"{payload.name} names STEP {str(source_sha)[:12]}, expected {step_sha[:12]}")
        payload_at = time.perf_counter()

        sources = stl.with_name(stl.name + ".sources.json")
        siblings = [step, stl, model]
        if sources.is_file():
            siblings.append(sources)
        siblings.append(payload)
        hashes = {path.name: _sha256(path) for path in siblings}
        if work != seated_work:
            for path in siblings:
                shutil.copyfile(path, seated_work / path.name)
        moved = {path.name: _seat(seated_work / path.name, output / path.name)
                 for path in siblings}
        for path in siblings:
            target = (output / path.name).resolve()
            if target.is_relative_to(_ROOT):
                _rust_part._WRITE_TARGETS.add(target.relative_to(_ROOT).as_posix())
        seated = time.perf_counter()

    timings = {"numbers": described-started, "cut": built-described,
               "payload": payload_at-built, "seat": seated-payload_at,
               "total": seated-started}
    print(f"{stem}:")
    print("  " + "  ".join(f"{phase} {seconds:.2f}s" for phase, seconds in timings.items()))
    for filename in hashes:
        print(f"  {'updated' if moved[filename] else 'held':7s} "
              f"{filename}: {hashes[filename]}")
    print(f"  {printed['printed_triangles']:,} STL facets; payload src={step_sha}")
    return {"hashes": hashes, "timings": timings,
            "facets": printed["printed_triangles"], "payload_src": step_sha}


def materialize(output: Path = _OUTPUT, pieces: tuple[str, ...] = DEFAULT_PIECES) -> dict:
    started = time.perf_counter()
    scripts = _ROOT / "hardware" / "scripts"
    for directory in (scripts, _ENCLOSURE):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    import _enclosure_datums
    enc = _enclosure_datums.load()
    import _box_spec

    box, bounds, box_path = _declared_box(_box_spec, enc)
    enc.BOUNDS[:] = bounds
    enc._last_box[0] = box
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    print("selected enclosure pieces:")
    print(f"  box {_sha256(box_path)}  {box_path.relative_to(_ROOT)}")
    return {name: _materialize_piece(enc, box, name, output, time.perf_counter())
            for name in pieces}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir", type=Path, default=_OUTPUT,
        help="destination for the piece files (default: the enclosure artifact directory)")
    parser.add_argument(
        "--pieces", nargs="+", choices=PIECES, default=list(DEFAULT_PIECES),
        help="which pump-bay pieces to stand (default: retainer and front-top)")
    args = parser.parse_args(argv)
    materialize(args.output_dir, tuple(args.pieces))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
