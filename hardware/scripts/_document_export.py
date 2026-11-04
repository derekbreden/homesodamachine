"""Python writer callbacks for Rust's stable atomic PDF and DXF exports."""

import os
from pathlib import Path

from _rust_data import request

_ROOT = Path(__file__).resolve().parents[2]
_WRITE_TARGETS = set()


def _request(op, **fields):
    return request("documents", "hsm-documents", {"op": op, **fields})


def _pid_alive(pid):
    return _request("pid-alive", pid=pid)


def _canonicalize_dxf_classes_section(data):
    return bytes(_request("canonicalize-bytes", kind="classes", bytes=list(data)))


def _canonicalize_dxf(path):
    _request("canonicalize", kind="dxf", path=str(Path(path).resolve()))


def _canonicalize_pdf(path):
    _request("canonicalize", kind="pdf", path=str(Path(path).resolve()))


def _current_umask():
    mask = os.umask(0)
    os.umask(mask)
    return mask


def _make_sibling_tempfile(target):
    return _request("prepare", path=str(Path(target).resolve()), pid=os.getpid(), mode=0o666 & ~_current_umask())


def _unlink_if_exists(path):
    _request("unlink", path=str(Path(path).absolute()))


def _sweep_orphan_temps(target):
    _request("sweep", path=str(Path(target).resolve()))


def _matches_existing_target(temporary, target):
    return _request("matches", temporary=str(Path(temporary).resolve()), path=str(Path(target).resolve()))


def atomic_write(target_path, write_fn, *, canonicalize=None):
    """Invoke a Python writer; Rust prepares, normalizes and places its file."""
    target = Path(target_path).resolve()
    try:
        _WRITE_TARGETS.add(target.relative_to(_ROOT).as_posix())
    except ValueError:
        pass
    temporary = _make_sibling_tempfile(target)
    try:
        write_fn(temporary)
        if canonicalize is not None:
            canonicalize(temporary)
        return _request("finish", temporary=temporary, path=str(target), canonicalize=canonicalize is None)
    except BaseException:
        _unlink_if_exists(temporary)
        raise


def export_dxf(source, target_path):
    atomic_write(target_path, lambda path: source.saveas(path))


def export_pdf(build, target_path):
    atomic_write(target_path, build)
