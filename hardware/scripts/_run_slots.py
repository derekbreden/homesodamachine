"""Host-wide leases and descriptor protocols supplied by the native Rust runtime."""
import array
import atexit
import json
import os
from pathlib import Path
import socket
import sys
from _run_native import read as _native

RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV = 'HSM_RUN_LEASE', 'HSM_CAD_LEASE', 'HSM_COMPILER_LEASE', 'HSM_RUN_BROKER'
_directory = None
_run = _cad = _compiler = _broker = None
_broker_checked = False
_used = False
_WIRE_LIMIT = 16384


class TimingLeaseError(RuntimeError):
    pass


class InheritanceError(RuntimeError):
    pass


class Lease:
    def __init__(self, entries, kind, inherited=False):
        self.entries, self.kind, self.inherited = entries, kind, inherited

    def close(self):
        _call("lease_close", {"kind": self.kind, "entries": self.entries})
        self.entries = []


def _consume(reply):
    global _run, _cad, _compiler, _broker, _broker_checked, _used
    _used = True
    for name, value in reply["environment"].items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    for kind, row in reply["leases"].items():
        key = {"run": "_run", "cad": "_cad", "compiler": "_compiler"}[kind]
        value = globals()[key]
        if row is None:
            if value is not None:
                value.entries = []
            globals()[key] = None
        elif value is None or value.entries != row["entries"]:
            if value is not None:
                value.entries = []
            globals()[key] = Lease(row["entries"], kind, row["inherited"])
    _broker_checked = reply.get("checked", False)
    if reply["broker"] is not None and (_broker is None or _broker._id != reply["broker"]["id"]):
        _broker = Broker._restore(reply["broker"])
    return reply["result"]


def _output(query):
    stream = sys.stdout if query["call"] == "stdout" else sys.stderr
    stream.write(query["text"])
    stream.flush()


def _call(op, data=None):
    try:
        return _consume(_native(op, data, directory=_directory, callback=_output))
    except RuntimeError as error:
        message = str(error)
        if message.startswith("timing: "):
            raise TimingLeaseError(message.removeprefix("timing: ")) from error
        if message.startswith("inheritance: "):
            raise InheritanceError(message.removeprefix("inheritance: ")) from error
        if op in ("count", "set_count"):
            raise ValueError(message) from error
        raise


def directory(): return Path(_call("directory"))
def _defaults(): return _call("defaults")
def capacity(): return _call("capacity")
def count(): return _call("count")
def set_count(value): return _call("set_count", {"value": value})
def _path(kind, slot=None): return Path(_call("path", {"kind": kind, "slot": slot}))
def _read_fd(fd): return _call("read_fd", {"fd": fd})
def _write_fd(fd, value): return _call("write_fd", {"fd": fd, "value": value})
def _open(path): return _call("open", {"path": str(path)})
def _valid(entry, kind): return _call("valid", {"entry": entry, "kind": kind})
def _export(lease): return _call("export", {"entries": lease.entries, "kind": lease.kind})
def _env_lease(kind):
    _call("env_lease", {"kind": kind})
    return {"run": _run, "cad": _cad, "compiler": _compiler}[kind]


def wire():
    metadata, descriptors = _call("wire")
    return metadata, tuple(descriptors)


def adopt(metadata, fds): return _call("adopt", {"metadata": metadata, "fds": list(fds)})


def _send(peer, value, fds=()):
    def primitive(query):
        if query["call"] == "sendmsg":
            ancillary = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array('i', query["fds"]))] if query["fds"] else []
            return peer.sendmsg([bytes(query["bytes"])], ancillary)
        peer.sendall(bytes(query["bytes"]))
    try:
        return _native("socket_send", {"value": value, "fds": list(fds)}, directory=_directory, callback=primitive)
    except RuntimeError as error:
        raise ValueError(str(error)) from error


def _receive(peer, limit=_WIRE_LIMIT):
    def primitive(query):
        if query["call"] == "gettimeout":
            return peer.gettimeout()
        if query["call"] == "settimeout":
            return peer.settimeout(query["value"])
        chunk, ancillary, flags, _address = peer.recvmsg(query["bytes"], query["space"])
        return {"bytes": list(chunk), "ancillary": [[level, kind, list(value)] for level, kind, value in ancillary], "flags": flags}
    try:
        value, fds = _native("socket_receive", {"limit": limit}, directory=_directory, callback=primitive)
    except RuntimeError as error:
        raise ValueError(str(error)) from error
    return value, fds


def _from_broker(): return _call("from_broker")
def current():
    _call("current", {"kind": "run"})
    return _run

def current_cad():
    _call("current", {"kind": "cad"})
    return _cad

def current_compiler():
    _call("current", {"kind": "compiler"})
    return _compiler

def _expects_parent(): return _call("expects_parent")
def host_pressure(): return tuple(_call("pressure"))
def acquire(key=None, timing=False):
    _call("acquire", {"key": key, "timing": timing})
    return _run

def acquire_cad():
    _call("acquire_cad")
    return _cad

def acquire_compiler():
    _call("acquire_compiler")
    return _compiler

def release(): return _call("release")
def release_cad(): return _call("release_cad")
def pass_fds(): return wire()[1]
def broker_config(workspace): return _call("broker_config", {"workspace": str(Path(workspace).resolve())})


class Broker:
    def __init__(self, config=None):
        row = _call("broker_new", {"config": config})
        self._id, self.path, self.closed = row["id"], Path(row["path"]), False
        self.token = row.get("token")

    @classmethod
    def _restore(cls, row):
        obj = cls.__new__(cls)
        obj._id, obj.path, obj.closed = row["id"], Path(row["path"]), False
        obj.token = row.get("token")
        return obj

    def close(self):
        _call("broker_close", {"id": self._id})
        self.closed = True


def child_env(env=None, broker=True): return _call("child_env", {"environment": env, "broker": broker})
def subprocess_kwargs(env=None): return {"env": child_env(env), "pass_fds": pass_fds()}
def command(argv, key=None): return _call("command", {"python": sys.executable, "root": str(Path(__file__).resolve().parents[2]), "argv": list(map(str, argv)), "key": key})
def ensure_cli(key):
    if current():
        return acquire(key)
    os.execv(sys.executable, command([sys.executable, *sys.argv], key))


def _finish():
    if not _used:
        return
    if _broker:
        _broker.close()
    release()


atexit.register(_finish)
