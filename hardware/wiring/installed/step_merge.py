"""Rust STEP and payload append operations, preserving physical arrays."""
from pathlib import Path
from ._wiring_data import read as _read


def base_document(text): return _read("step_base", {"text": text})
def records(text): return {number: body for number, body in _read("step_records", {"text": text})}
def refs(body): return _read("step_refs", {"text": body})
def root(rec, name=None): return tuple(_read("step_root", {"records": list(rec.items()), "name": name}))
def _wiring(name): return _read("step_wiring", {"name": name})
def _digest(path): return _read("file_digest", {"path": str(Path(path).resolve())})


def _payload_merge(host, wires, src):
    return tuple(_read("step_payload_merge", {"host": str(Path(host).resolve()),
                       "wire": str(Path(wires).resolve()), "src": src}))


def install(host, wire_step, verify_retained=False, *, wire_model=None):
    return _read("step_install", {"host": str(Path(host).resolve()), "wire_step": str(Path(wire_step).resolve()),
                                 "verify_retained": verify_retained,
                                 "wire_model": str(Path(wire_model).resolve()) if wire_model is not None else None})
