#!/usr/bin/env python3
"""Materialize only the pump cartridge's STEP, printed STL and viewer payload.

The ordinary enclosure producer deliberately draws all six pieces and its aggregate before the
assembly runs.  That is the right reconciliation path and the wrong visual-iteration path for a
change confined to the removable pump cartridge.  This entry reads the already-declared Box,
calls the cartridge builder directly, and uses the same tessellation, flute rails and payload
cutter as the ordinary producer without drawing another enclosure piece or an assembly.

    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py

All three siblings are completed in a temporary directory and seated only after the printed STL
has passed the ordinary producer's own slicer-facing reading.  They seat STEP, STL, then payload:
an interruption may leave the first one or two current while the payload stays held, but the
publisher then sees no changed payload and defers instead of exposing a mixed triplet.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
import time
from pathlib import Path


_HERE = Path(__file__).resolve()
_ROOT = next(p for p in _HERE.parents if (p / "tools" / "docgen").is_dir())
_ENCLOSURE = _ROOT / "hardware" / "printed-parts" / "enclosure" / "enclosure"
_OUTPUT = _ENCLOSURE


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


def materialize(output: Path = _OUTPUT) -> dict:
    started = time.perf_counter()
    scripts = _ROOT / "hardware" / "scripts"
    for directory in (scripts, _ENCLOSURE):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    import _box_spec
    import enclosure as enc
    import flute_payload

    imported = time.perf_counter()
    box, bounds = _box_spec.read(
        enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate))
    enc.BOUNDS[:] = bounds
    described = time.perf_counter()

    # This is intentionally the direct builder and not build_pieces(): no other piece, shared
    # front half, slide report, aggregate or scorecard is realized along this path.
    piece = enc.build_pump_cartridge(box)
    built = time.perf_counter()

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    stem = "enclosure-pump-cartridge"
    with tempfile.TemporaryDirectory(prefix=f".{stem}-", dir=output) as directory:
        work = Path(directory)
        step = work / f"{stem}.step"
        stl = work / f"{stem}.stl"
        payload = work / f"{stem}.step.mesh"

        # export_assembly ordinarily writes a smooth viewer payload beside the STEP.  The final
        # payload here is the printed/fluted surface, so skip that redundant tessellation only;
        # the STEP still goes through the canonical atomic/canonicalized assembly exporter.
        held_skip = os.environ.get("HSM_SKIP_MESH_PAYLOAD")
        os.environ["HSM_SKIP_MESH_PAYLOAD"] = "1"
        try:
            enc.export_assembly(
                enc.one_body(piece, stem, enc.PIECE_COLORS["pump-cartridge"]), str(step))
        finally:
            if held_skip is None:
                os.environ.pop("HSM_SKIP_MESH_PAYLOAD", None)
            else:
                os.environ["HSM_SKIP_MESH_PAYLOAD"] = held_skip
        stepped = time.perf_counter()

        # These are the exact body tessellation, two cartridge-only rails and flute operation
        # used by enclosure._export_pieces for this name.
        body = enc._piece_mesh(piece.val())
        rails = [enc._pump_cartridge_side_flute_rail(box.outer),
                 enc._pump_cartridge_front_flute_rail(box.outer)]
        printed = enc._flute_skin.flute(
            body, rails, enc.flute_pitch(box.outer), enc.flute_depth, enc.flute_rise)
        printed.export(str(stl))

        # The ordinary producer reads the written file back exactly this way before accepting a
        # bed mesh.  Keep that existing safety reading; this path adds no persistent gate.
        written = enc.trimesh.load_mesh(str(stl))
        loose = enc._flute_skin.non_manifold_edges(written)
        if loose or not written.is_watertight:
            raise ValueError(
                f"{stl.name}: {loose} non-manifold edge(s), watertight="
                f"{written.is_watertight}, over {len(written.faces)} facets")
        printed_at = time.perf_counter()

        # cut() is the canonical printed-mesh reduction/creased-region writer.  It writes only
        # the sibling payload and stamps it with the SHA of this exact STEP.
        flute_payload.cut(step, stl)
        source_sha = flute_payload._mesh_payload.read_source(payload)
        step_sha = _sha256(step)
        if source_sha != step_sha:
            raise ValueError(
                f"{payload.name} names STEP {str(source_sha)[:12]}, expected {step_sha[:12]}")
        payload_at = time.perf_counter()

        siblings = (step, stl, payload)
        hashes = {path.name: _sha256(path) for path in siblings}
        moved = {path.name: _seat(path, output / path.name) for path in siblings}
        seated = time.perf_counter()

    timings = {
        "imports": imported - started,
        "box": described - imported,
        "solid": built - described,
        "step": stepped - built,
        "stl": printed_at - stepped,
        "payload": payload_at - printed_at,
        "seat": seated - payload_at,
        "total": seated - started,
    }
    print("pump cartridge only:")
    print("  " + "  ".join(f"{name} {seconds:.2f}s" for name, seconds in timings.items()))
    for name in (f"{stem}.step", f"{stem}.stl", f"{stem}.step.mesh"):
        print(f"  {'updated' if moved[name] else 'held':7s} "
              f"{name}: {hashes[name]}")
    print(f"  {len(written.faces):,} STL facets; payload src={step_sha}")
    return {"hashes": hashes, "timings": timings, "facets": len(written.faces),
            "payload_src": step_sha}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir", type=Path, default=_OUTPUT,
        help="destination for the three siblings (default: the enclosure artifact directory)")
    args = parser.parse_args(argv)
    materialize(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
