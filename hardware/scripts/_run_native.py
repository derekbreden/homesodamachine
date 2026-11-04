"""Load the native host runtime, bootstrapping through an installed hsm."""
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = Path(os.environ.get("HSM_WORKSPACE") or ROOT).resolve()
_library = None
_executable = None
_Callback = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p)


def _descriptors():
    entries = []
    for name in ("HSM_RUN_LEASE", "HSM_CAD_LEASE", "HSM_COMPILER_LEASE"):
        try:
            row = json.loads(os.environ.get(name, "null"))
            entries.extend(row["fds"] if name == "HSM_RUN_LEASE" else [row])
        except (TypeError, KeyError, ValueError):
            pass
    found = []
    for row in entries:
        try:
            os.fstat(row["fd"])
            found.append(row["fd"])
        except (OSError, KeyError, TypeError):
            pass
    return tuple(found)


def _candidate(binary):
    try:
        reply = subprocess.run([str(binary), "--runtime-info", str(WORKSPACE)],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        info = json.loads(reply.stdout) if reply.returncode == 0 else {}
        if info.get("abi") == 1 and info.get("source_match") and Path(info["library"]).is_file():
            return info
    except (OSError, ValueError, KeyError):
        pass
    return None


def _candidates():
    candidates = []
    try:
        receipt = json.loads((Path.home() / ".local/lib/hsm/runtime.json").read_text())
        candidates.append(Path(receipt["runner"]))
    except (OSError, ValueError, KeyError):
        pass
    candidates.append(WORKSPACE / "tools/hsm/target/release/hsm-run")
    return candidates


def _find(force=False):
    if not force:
        for binary in _candidates():
            if info := _candidate(binary):
                return info
    command = shutil.which("hsm")
    if command is None:
        command = WORKSPACE / "tools/hsm/target/release/hsm"
    if not Path(command).is_file():
        raise RuntimeError("The host runtime needs an installed hsm to bootstrap its native library")
    request = {"op": "run", "workspace": str(WORKSPACE), "root": str(WORKSPACE),
               "crate": "run-slots", "name": "hsm-run", "args": ["--bootstrap"]}
    reply = subprocess.run([str(command), "request", json.dumps(request)],
                           stdout=subprocess.PIPE, text=True, pass_fds=_descriptors())
    try:
        answer = json.loads(reply.stdout)
    except ValueError:
        answer = {}
    if not answer.get("ok"):
        raise RuntimeError(answer.get("error", "hsm could not bootstrap the native host runtime"))
    for binary in _candidates():
        if info := _candidate(binary):
            return info
    raise RuntimeError("hsm completed without a current native host runtime")


def _load():
    global _library, _executable
    if _library is None:
        info = _find()
        library = ctypes.CDLL(info["library"])
        if not hasattr(library, "hsm_run_request"):
            info = _find(force=True)
            library = ctypes.CDLL(info["library"])
        library.hsm_run_request.argtypes = [ctypes.c_char_p, _Callback]
        library.hsm_run_request.restype = ctypes.c_void_p
        library.hsm_run_free.argtypes = [ctypes.c_void_p]
        library.hsm_run_free.restype = None
        _library, _executable = library, Path(info["executable"])
    return _library


def executable():
    _load()
    return _executable


def read(op, data=None, *, directory=None, callback=None):
    library = _load()
    buffers, errors = [], []
    def invoke(raw):
        try:
            answer = {"value": callback(json.loads(raw))}
        except BaseException as error:
            errors.append(error)
            answer = {"error": str(error)}
        buffers[:] = [ctypes.create_string_buffer(json.dumps(answer).encode())]
        return ctypes.addressof(buffers[0])
    handler = _Callback(invoke) if callback is not None else _Callback()
    payload = {"root": str(ROOT), "directory": str(directory) if directory is not None else None,
               "op": op, "data": data or {},
               "environment": {name: os.environ.get(name) for name in ("HSM_RUN_LEASE", "HSM_CAD_LEASE", "HSM_COMPILER_LEASE", "HSM_RUN_BROKER", "HSM_RUN_PROFILE")}}
    pointer = library.hsm_run_request(json.dumps(payload).encode(), handler)
    try:
        reply = json.loads(ctypes.string_at(pointer))
    finally:
        library.hsm_run_free(pointer)
    if errors:
        raise errors[0]
    if "error" in reply:
        if reply.get("errno") is not None:
            raise OSError(reply["errno"], reply["error"])
        raise RuntimeError(reply["error"])
    return reply["value"]
