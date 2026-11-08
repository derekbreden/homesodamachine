"""Parts the Rust kernel cuts (`tools/hsm/kernel`).

A part's Python module holds its numbers: it derives each one from the parts it closes on,
states its bounds and fills its README, as any generator does. Its program, beside it, cuts the
part's files from those numbers:

    said = _rust_part.cut(crate, name, numbers, part_dir)

writes `<name>.numbers.json` into `part_dir`, builds the program with cargo from the checkout's
`tools/hsm` workspace (the crate `tools/hsm/<crate>` names it), and runs it. The program writes
`<name>.step`, the model file beside it (`<name>.step.npz`), the payload (`<name>.step.mesh`)
and `<name>.stl`, and answers with what they hold (`hsm_kernel::part::write_part`). A program
that writes several file sets answers once for each, a line apiece, and this returns their files
and bodies together. `check(crate, name, numbers)` runs `<program> <numbers.json> --check`, which
measures the part and writes nothing, and returns its JSON; `run(crate, name, *args)` runs a
program with arguments of its own and returns what it printed. Each run says what the program
took: its seconds and the most memory it held.

A PART'S OWN RUN BEGINS HERE, before its module imports anything else:

    if __name__ == "__main__":
        import _rust_part
        _rust_part.start()

`start` starts the run's clock at the process's own start and defers CadQuery. The CAD lock
(`_run_lock`, as `_cadq_export` takes it for every other generator) is taken when CadQuery or OCP
loads, or before cargo and the program run in this process, so a run the part engine answers
that loads neither waits behind no OCCT build.

THE PART ENGINE RUNS THE PROGRAM WHERE `hsm` IS INSTALLED (`tools/hsm/README.md`, "Part runs").
`run` asks the daemon over its socket. The daemon keeps each run by the program's code and what
the run read, so a run it has seen answers with the files it kept, and cargo runs only for code
nothing has built. Its programs start in turn within a memory budget, under no CAD lock. Where no
`hsm` is installed, or `HSM_NO_ENGINE` is set, cargo and the program run here, and write the same
bytes.

CADQUERY IS DEFERRED, NOT REMOVED. A part's numbers come from modules that import CadQuery to
build other parts with, and the run itself uses none of it. So `start` puts a `cadquery` in
`sys.modules` that loads the first time a name is read off it. Two names don't load it, because
shared modules make them as they import: `cq.Color` (`_materials`) and `cq.Plane`
(`world_workplane`) make stand-ins that hold their arguments. A colour's is all OCCT keeps of
it, so a stand-in colour answers `toTuple`, `==` and `hash`, and `_materials.linear` its linear
RGB, bit for bit as OCCT would (`_occt_color`). If CadQuery does load, each stand-in becomes the
value it stands for, the same object, so a module holding one holds the real one.
Whenever OCP loads, through CadQuery or not, the loops over its collections end in Python
(`_cadq_export._end_ocp_loops_in_python`). A process that already holds a `cadquery`, the mesh
kernel's (`meshcad.activate`) among them, keeps it.

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
import importlib.machinery
import importlib.util
import json
import os
import pwd
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_READ_TARGETS: set = set()
_WRITE_TARGETS: set = set()
_ENGINE_SOCKET: str | None = None

#: Where this run's seconds start, on `time.perf_counter`'s clock: the process's own start, once
#: `start` has run.
_STARTED: float | None = None
_IMPORTED = time.time()
#: The run `start` began, which takes the CAD lock if CadQuery or OCP loads in it.
_LOCK_FOR: str | None = None


def start() -> None:
    """Begin a part's own run: the clock from the process's start, CadQuery deferred until
    something uses it, and the CAD lock when it does."""
    global _STARTED, _LOCK_FOR
    if _STARTED is not None:
        return
    _STARTED = time.perf_counter() - (time.time() - _process_start())
    if "cadquery" not in sys.modules and (spec := importlib.util.find_spec("cadquery")) is not None:
        cq = importlib.util.module_from_spec(spec)
        cq.__class__ = _Deferred
        sys.modules["cadquery"] = cq
    if "OCP.OCP" not in sys.modules:
        sys.meta_path.insert(0, _OCPFinder())
    entry = _entry()
    _LOCK_FOR = entry


def _lock() -> None:
    """The CAD lock, for a run `start` began, now that OCCT is loading in it."""
    if _STARTED is not None:
        from _run_lock import acquire
        acquire(_LOCK_FOR or 'python')


def _entry():
    """What this run is, named as `_cadq_export` names it: the entry script, from the root."""
    if sys.argv and sys.argv[0].endswith(".py"):
        entry = Path(sys.argv[0]).resolve()
        try:
            return entry.relative_to(ROOT).as_posix()
        except ValueError:
            return entry.name
    return None


def _process_start() -> float:
    """When this process began, on `time.time`'s clock, as the kernel keeps it; the time this
    module was imported where it keeps none."""
    try:
        if sys.platform == "darwin":
            import ctypes
            info = ctypes.create_string_buffer(136)              # struct proc_bsdinfo
            if ctypes.CDLL(None).proc_pidinfo(os.getpid(), 3, ctypes.c_uint64(0), info, 136) == 136:
                sec, usec = (int.from_bytes(info.raw[k:k + 8], "little") for k in (120, 128))
                return sec + usec / 1e6                          # pbi_start_tvsec, _tvusec
        elif sys.platform.startswith("linux"):
            with open("/proc/self/stat") as f:
                ticks = int(f.read().rpartition(")")[2].split()[19])   # starttime, since boot
            return time.time() - time.clock_gettime(time.CLOCK_BOOTTIME) + ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, AttributeError):
        pass
    return _IMPORTED


# --- CadQuery, deferred --------------------------------------------------------

#: What may be read off the deferred `cadquery` without loading it: what the import system and a
#: module's repr ask of any module.
_MODULE_NAMES = frozenset(("__name__", "__spec__", "__loader__", "__package__", "__file__",
                           "__cached__", "__class__"))


class _Deferred(types.ModuleType):
    """`cadquery` before anything has used it. `import cadquery` reads only its `__spec__`, and
    `Color` and `Plane` are the stand-ins' classes; any other name loads CadQuery into this same
    module."""

    def __getattribute__(self, name):
        if name in _MODULE_NAMES:
            return object.__getattribute__(self, name)
        if name in _STANDINS:
            return _STANDINS[name]
        _load()
        return getattr(self, name)


def _load() -> None:
    """CadQuery, loaded into the module that stood for it, and each stand-in made the value it
    stands for."""
    cq = sys.modules.get("cadquery")
    if type(cq) is _Deferred:
        _lock()
        cq.__class__ = types.ModuleType
        spec = cq.__spec__
        spec._initializing = True
        try:
            spec.loader.exec_module(cq)
        except BaseException:
            del sys.modules["cadquery"]
            raise
        finally:
            spec._initializing = False
    while _MADE:
        _MADE.pop()._become()


class _StandinClass(type):
    """`cq.Color` or `cq.Plane` while CadQuery is deferred: it makes stand-ins. Once CadQuery has
    loaded, the class a module kept makes the real ones and holds them."""

    def __call__(cls, *args, **kwargs):
        if type(sys.modules.get("cadquery")) is _Deferred:
            return super().__call__(*args, **kwargs)
        return cls._real()(*args, **kwargs)

    def __instancecheck__(cls, obj):
        if type(sys.modules.get("cadquery")) is _Deferred:
            return type.__instancecheck__(cls, obj)
        return isinstance(obj, cls._real())

    def __getattr__(cls, name):
        return getattr(cls._real(), name)

    def _real(cls):
        _load()
        return getattr(sys.modules["cadquery"], cls.__name__)


class _Standin(metaclass=_StandinClass):
    """A CadQuery value made while CadQuery is deferred: the arguments it was made with. Once
    CadQuery has loaded it is the value they make, in place."""

    def __init__(self, *args, **kwargs):
        self._made = (args, kwargs)
        _MADE.append(self)

    def _become(self):
        args, kwargs = vars(self).pop("_made")
        real = getattr(sys.modules["cadquery"], type(self).__name__)(*args, **kwargs)
        vars(self).update(vars(real))
        self.__class__ = type(real)

    def _now(self):
        _load()
        return self

    # Anything but its arguments is the real one's to answer.
    def __getattr__(self, name):
        if "_made" not in vars(self):
            raise AttributeError(name)
        return getattr(self._now(), name)

    def __eq__(self, other):
        return self._now() == other

    def __ne__(self, other):
        return self._now() != other

    def __hash__(self):
        return hash(self._now())

    def __repr__(self):
        args, kwargs = vars(self)["_made"]
        return f"<deferred cq.{type(self).__name__} {args} {kwargs}>"


class _ColorStandin(_Standin):
    """`cq.Color` while CadQuery is deferred. What OCCT keeps of a colour is arithmetic on the
    arguments it was made with (`_occt_color`), so it answers `toTuple`, `==` and `hash` as the
    real one does, without loading CadQuery for them."""

    def toTuple(self):
        import _occt_color
        rgba = _occt_color.rgba(*vars(self)["_made"])
        if rgba is None:
            return self._now().toTuple()
        return (*_occt_color.srgb(rgba[:3]), rgba[3])

    def __eq__(self, other):
        return self.toTuple() == other.toTuple()

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.toTuple())


_STANDINS = {name: _StandinClass(name, (base,), {"__module__": "cadquery", "__qualname__": name})
             for name, base in (("Color", _ColorStandin), ("Plane", _Standin))}
_MADE: list = []


class _OCPFinder:
    """Finds OCP's extension as the path finder does, so that once it has loaded, whatever loaded
    it, the loops over its collections end in Python."""

    def find_spec(self, name, path=None, target=None):
        if name != "OCP.OCP":
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path, target)
        if spec is not None:
            spec.loader = _EndingLoops(spec.loader)
        return spec


class _EndingLoops:
    """OCP's own loader, and `_cadq_export`'s patch on its loops once it has run."""

    def __init__(self, loader):
        self.loader = loader

    def create_module(self, spec):
        return self.loader.create_module(spec)

    def exec_module(self, module):
        _lock()
        self.loader.exec_module(module)
        export = sys.modules.get("_cadq_export")
        if export is None:
            import _cadq_export          # noqa: F401  its import ends them, now that OCP has loaded
        else:
            export._end_ocp_loops_in_python()


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
    from _build_data import request
    return set(request("compiled", path=str(dep_info), workspace=str(workspace)))


def _manifests(sources: set, crate: str, workspace: Path) -> set:
    from _build_data import request
    return set(request("manifests", sources=list(sources), crate=crate, workspace=str(workspace)))


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _workspace() -> Path:
    return Path(os.environ.get("HSM_WORKSPACE") or ROOT).resolve()


#: The kernel's rule (`tools/hsm/kernel/src/rule.rs`): mm, the chord's largest distance from the
#: curve; rad, the largest turn between two segments.
LINEAR, ANGULAR = 0.005, 0.05


def _src(payload: Path):
    from _build_data import read
    try:
        return read("header", payload).get("src")
    except ValueError:
        return None


def step(path) -> str:
    """Register Rust's verified STEP import plan and any retained payload."""
    from _build_data import request
    path = Path(path).resolve()
    result = request("step-input", path=str(path), root=str(ROOT), workspace=str(_workspace()),
                     linear=LINEAR, angular=ANGULAR)
    for source in result["reads"]:
        _READ_TARGETS.add(_relative(Path(source)))
    if result["tessellate"]:
        _tessellate(path, Path(result["cached"]), result["digest"])
    return result["name"]


def _adopt_fine_payload(path: Path, out: Path, digest: str) -> bool:
    from _build_data import request
    result = request("adopt-fine-payload", path=str(path), out=str(out), digest=digest,
                     linear=LINEAR, angular=ANGULAR)
    for source in result["reads"]:
        _READ_TARGETS.add(_relative(Path(source)))
    return result["adopted"]


def _tessellate(path: Path, out: Path, digest: str) -> None:
    """OCCT's mesh of each solid of each body of the STEP at `path`, one face range per B-rep
    face, as a payload whose `src` is `digest`. A body of several solids is `name/1`, `name/2`;
    a body with no name takes the STEP's."""
    import numpy as np
    import _cadq_export                  # the CAD lock
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.Quantity import Quantity_TypeOfColor
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
                     "color": list(color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))
                     if color is not None else None}
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


def _slots():
    import _run_slots
    return _run_slots


def _has_lease_environment():
    return any(os.environ.get(key) for key in ('HSM_RUN_LEASE', 'HSM_CAD_LEASE',
                                               'HSM_COMPILER_LEASE', 'HSM_RUN_BROKER'))


def program(crate: str, name: str) -> Path:
    """Build `tools/hsm/<crate>`'s program `name`, keep what it was compiled from, and return
    where it is."""
    workspace = Path(os.environ.get("HSM_WORKSPACE") or ROOT).resolve()
    manifest = workspace / "tools" / "hsm" / crate / "Cargo.toml"
    binary = workspace / "tools/hsm/target/release" / name
    receipt = workspace / ".cache/realized/compiled-programs" / crate / f"{name}.json"
    # Matching source bytes reuse the executable without entering Cargo's compiler queue.
    def fingerprints(inputs):
        try:
            values = {}
            for path in inputs:
                try:
                    values[path] = hashlib.sha256((workspace / path).read_bytes()).hexdigest()
                except FileNotFoundError:
                    values[path] = None
            return values
        except OSError:
            return None
    try:
        held = json.loads(receipt.read_text())
        if (held["sources"] == fingerprints(held["sources"]) and
                held["binary"] == hashlib.sha256(binary.read_bytes()).hexdigest()):
            _READ_TARGETS.update(held["sources"])
            return binary
    except (OSError, ValueError, KeyError, TypeError):
        pass
    # Cargo runs the `rustc` it finds on the PATH, and rustup keeps it beside cargo.
    cargo, target = _cargo(), workspace / "tools" / "hsm" / "target"
    env = {**os.environ, "HOME": str(_home()), "CARGO_TARGET_DIR": str(target),
           "PATH": os.pathsep.join([str(Path(cargo).parent), os.environ.get("PATH", "")])}
    _slots().acquire(_entry() or f'cargo:{crate}/{name}')
    subprocess.run(_slots().command([cargo, "build", "--release", "--locked", "--quiet",
                    "--manifest-path", str(manifest), "--bin", name]), check=True,
                   **_slots().subprocess_kwargs(env))
    metadata = dict(op="program-inputs", path=str(target / "release" / f"{name}.d"),
                    workspace=str(workspace), crate=crate)
    if (crate, name) == ("build-data", "build-data"):
        # This program supplies the metadata reader itself. Bootstrap it by a
        # direct command before its resident transport exists.
        reply = subprocess.run([str(target / "release" / name)], input=json.dumps(metadata),
                               stdout=subprocess.PIPE, text=True, check=True,
                               **_slots().subprocess_kwargs())
        inputs = json.loads(reply.stdout)
        if isinstance(inputs, dict) and "error" in inputs:
            raise ValueError(inputs["error"])
    else:
        from _build_data import request
        inputs = request("program-inputs", path=metadata["path"], workspace=str(workspace), crate=crate)
    _READ_TARGETS.update(inputs)
    sources = fingerprints(inputs)
    if sources is not None:
        receipt.parent.mkdir(parents=True, exist_ok=True)
        temporary = receipt.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps({"sources": sources,
                                        "binary": hashlib.sha256(binary.read_bytes()).hexdigest()}))
        os.replace(temporary, receipt)
    return target / "release" / name


def _socket() -> str:
    """The installed build's endpoint, unless `HSM_SOCKET` names another."""
    if os.environ.get("HSM_SOCKET"):
        return os.environ["HSM_SOCKET"]
    global _ENGINE_SOCKET
    if _ENGINE_SOCKET is None:
        _ENGINE_SOCKET = f"/tmp/hsm-{os.getuid()}/engine.sock"
        if hsm := _hsm():
            said = subprocess.run([hsm, "endpoint"], capture_output=True, text=True,
                                  env={**os.environ, "HOME": str(_home())})
            if said.returncode == 0:
                _ENGINE_SOCKET = json.loads(said.stdout)["socket"]
    return _ENGINE_SOCKET


def _hsm():
    """`hsm` on the PATH, else where `cargo install --root ~/.local` puts it; None where neither."""
    for found in (shutil.which("hsm"), str(_home() / ".local" / "bin" / "hsm")):
        if found and Path(found).is_file():
            return found
    return None


def _ask(request: dict, attach_lease=True):
    """The daemon's answer to one request, or None where nothing listens."""
    import socket
    import array
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(_socket())
            metadata, descriptors = _slots().wire() if attach_lease and _has_lease_environment() else (None, ())
            if descriptors:
                request = {**request, '_lease': metadata}
            payload = json.dumps(request).encode() + b"\n"
            if descriptors:
                sent = s.sendmsg([payload], [(socket.SOL_SOCKET, socket.SCM_RIGHTS,
                                             array.array('i', descriptors))])
                if sent < len(payload):
                    s.sendall(payload[sent:])
            else:
                s.sendall(payload)
            reply = bytearray()
            while not reply.endswith(b"\n"):
                chunk = s.recv(1 << 20)
                if not chunk:
                    break
                reply += chunk
    except (FileNotFoundError, ConnectionRefusedError):
        return None
    return json.loads(reply) if reply.strip() else None


def _engine(crate: str, name: str, args) -> dict | None:
    """What the part engine says of the run, or None where it does not run it: no `hsm`
    installed, an `hsm` from before part runs, or `HSM_NO_ENGINE` set."""
    if (os.environ.get("HSM_NO_ENGINE") or "").strip().lower() not in ("", "0", "no", "false", "off"):
        return None
    request = {"op": "run", "workspace": str(_workspace()), "root": str(ROOT.resolve()),
               "crate": crate, "name": name, "args": [str(a) for a in args]}
    for attempt in (0, 1):
        if _has_lease_environment() and _slots().pass_fds():
            capability = _ask({'op': 'ping'}, attach_lease=False)
            if capability and capability.get('result', {}).get('run_slots') != 1:
                return None                 # an older daemon must not book a nested lease
        answer = _ask(request)
        if answer is not None and answer.get("ok"):
            return answer["result"]
        # A daemon from before part runs reads `run` as an op it doesn't know.
        if answer is not None and "unknown variant `run`" not in answer.get("error", ""):
            raise SystemExit(f"_rust_part: {name}: {answer.get('error')}")
        hsm = _hsm()
        if attempt or hsm is None:
            return None
        # Start the installed build on the endpoint it named. A live incompatible service stays.
        env = {**os.environ, "HOME": str(_home())}
        for key in ('HSM_RUN_LEASE', 'HSM_CAD_LEASE', 'HSM_COMPILER_LEASE',
                    'HSM_RUN_BROKER', 'HSM_RUN_PROFILE'):
            env.pop(key, None)               # a detached daemon never retains this run's lease
        cmd = [hsm, "--socket", _socket(), "status"]
        if subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env).returncode:
            return None
    return None


def run(crate: str, name: str, *args) -> str:
    """Build `tools/hsm/<crate>`'s program `name`, run it from the root with `args`, and return
    what it printed. Says what the run took: its seconds and the most memory it held, or that the
    part engine kept it."""
    said = _engine(crate, name, args)
    if said is not None:
        _READ_TARGETS.update(said["sources"])
        if receipt := os.environ.get("HSM_GENERATOR_READS"):
            with open(receipt, "a") as stream:
                stream.write(json.dumps({"root": str(ROOT.resolve()),
                    "workspace": str(_workspace()), "reads": said["reads"],
                    "key": said["key"], "code": said["code"], "hit": said["hit"]}) + "\n")
        sys.stderr.write(said["stderr"])
        took = ("kept" if said["hit"] else
                f"{said['program_seconds']:.2f} s, {said['peak_bytes'] / 2 ** 20:.0f} MB at its peak")
        print(f"   {name}: {took}")
        return said["stdout"]
    _slots().acquire(_entry() or f'part:{crate}/{name}')
    cmd = [str(program(crate, name)), *map(str, args)]
    began = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, cwd=ROOT,
                            **_slots().subprocess_kwargs())
    out = proc.stdout.read()
    proc.stdout.close()
    _pid, status, usage = os.wait4(proc.pid, 0)
    proc.returncode = os.waitstatus_to_exitcode(status)
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, cmd, out)
    peak = usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)    # bytes, or KiB
    print(f"   {name}: {time.perf_counter() - began:.2f} s, {peak / 2 ** 20:.0f} MB at its peak")
    return out


def check(crate: str, name: str, numbers: dict):
    """What `tools/hsm/<crate>`'s program `name` measures of the part `numbers` make, writing
    nothing: `<program> <numbers.json> --check`, with the numbers in a file of their own."""
    import tempfile
    from _rust_data import json_default
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{name}.numbers.json"
        path.write_text(json.dumps(numbers, indent=1, sort_keys=True, default=json_default) + "\n")
        return json.loads(run(crate, name, path, "--check"))


def cut(crate: str, name: str, numbers: dict, part_dir, *, numbers_name: str | None = None) -> dict:
    """Write `numbers`, build `tools/hsm/<crate>`'s program `name` and run it into `part_dir`,
    and return what it says it wrote. `results` retains each complete JSON record, alongside
    the aggregated `files` and `bodies`. `numbers_name` sets the numbers file's stem; by default
    it is the program's `name`."""
    part_dir = Path(part_dir)
    numbers_path = part_dir / f"{name if numbers_name is None else numbers_name}.numbers.json"
    from _rust_data import json_default
    text = json.dumps(numbers, indent=1, sort_keys=True, default=json_default) + "\n"
    if not numbers_path.is_file() or numbers_path.read_text() != text:
        numbers_path.write_text(text)
    _WRITE_TARGETS.add(_relative(numbers_path))

    said = {"files": [], "bodies": [], "results": []}
    for line in run(crate, name, numbers_path.resolve(), part_dir.resolve()).splitlines():
        if line.strip():
            each = json.loads(line)
            said["files"] += each["files"]
            said["bodies"] += each["bodies"]
            said["results"].append(each)
    wrote = {_relative(numbers_path)} | {_relative(part_dir / f) for f in said["files"]}
    _WRITE_TARGETS.update(wrote)
    # A run `start` did not begin tells `_cadq_export` what it wrote.
    if _STARTED is None and (export := sys.modules.get("_cadq_export")) is not None:
        for path in sorted(wrote):
            export.note_write(ROOT / path)
    return said
