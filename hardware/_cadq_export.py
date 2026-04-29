"""Atomic STEP / Assembly export helpers.

Concurrent runs targeting the same output file do not corrupt it: each call
writes to a unique temp file alongside the target and then renames atomically
via os.replace (POSIX-atomic rename). When two processes race — e.g. an agent
running the script directly while the dev server's watcher rebuilds the same
script — both produce complete files, last writer wins, and no consumer ever
observes a half-written .step.

Usage from any generate_step_cadquery.py:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
    )
    from _cadq_export import export_step          # for cq workplanes / solids
    from _cadq_export import save_assembly        # for cq.Assembly objects

    export_step(model, str(out_path))
    save_assembly(assy, str(out_path))
"""

import filecmp
import os
import re
import tempfile
from pathlib import Path

# STEP files embed a wall-clock timestamp in the FILE_NAME header. Without
# normalization, every run produces different bytes for identical source —
# which churns git status and burns agent tokens chasing a non-change.
_STEP_TIMESTAMP_RE = re.compile(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'")
_STEP_CANONICAL_TIMESTAMP = b"'1970-01-01T00:00:00'"


def _canonicalize_step(path):
    with open(path, "rb") as f:
        data = f.read()
    new_data = _STEP_TIMESTAMP_RE.sub(_STEP_CANONICAL_TIMESTAMP, data, count=1)
    if new_data != data:
        with open(path, "wb") as f:
            f.write(new_data)


def _atomic_write(target_path, write_fn):
    target = Path(target_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=target.suffix,
        dir=str(target.parent),
    )
    os.close(fd)
    # mkstemp creates files at 0600; restore umask-default so rename
    # produces a normal 0644 file rather than a private one.
    umask = os.umask(0)
    os.umask(umask)
    os.chmod(tmp, 0o666 & ~umask)
    try:
        write_fn(tmp)
        if target.suffix == ".step":
            _canonicalize_step(tmp)
        # No-change short-circuit: if the canonicalized output matches the
        # existing target byte-for-byte, leave the target's mtime alone and
        # leave git status clean. Only rename when content actually changed.
        if target.exists() and filecmp.cmp(tmp, str(target), shallow=False):
            os.unlink(tmp)
            return
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def export_step(model, target_path):
    """cq.exporters.export with atomic write."""
    import cadquery as cq
    _atomic_write(target_path, lambda p: cq.exporters.export(model, p))


def save_assembly(assembly, target_path):
    """cq.Assembly.save with atomic write."""
    _atomic_write(target_path, lambda p: assembly.save(p))
