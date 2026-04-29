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

import os
import tempfile
from pathlib import Path


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
