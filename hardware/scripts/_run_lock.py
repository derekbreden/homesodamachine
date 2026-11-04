"""Native CAD admission with Python stream and interpreter callbacks."""
import atexit
import os
from pathlib import Path
import signal
import sys
import tempfile
from _run_native import read as _native
import _run_slots as slots

LOCK_DIR = Path(tempfile.gettempdir()) / "hsm-cad-lock"
LOCK = LOCK_DIR / "build.json"
BY = LOCK_DIR / "build.by.json"
_HW = Path(__file__).resolve().parent.parent
_me = _tee = None


def _call(op, data=None):
    return slots._consume(_native(op, {"lock_dir": str(LOCK_DIR), **(data or {})},
                                  directory=slots._directory, callback=slots._output))


_constants = _call("cad_constants")
GRACE_S, POLL_S, WAIT_S = _constants["grace"], _constants["poll"], _constants["wait"]


def _asked(name): return _call("cad_asked", {"name": name})
def _unlocked_of(pid): return Path(_call("cad_path", {"kind": "unlocked", "pid": pid}))
def _log_of(pid): return Path(_call("cad_path", {"kind": "log", "pid": pid}))
def _result_of(pid): return Path(_call("cad_path", {"kind": "result", "pid": pid}))
def _newest_input_mtime(root=None): return _call("cad_newest", {"workspace": str(root) if root is not None else None})
def _fresh_for(holder): return _call("cad_fresh", {"holder": holder})
def _attach(holder): return _call("cad_attach", {"holder": holder})
def _alive(pid): return _call("cad_alive", {"pid": pid})
def _read(path): return _call("cad_read", {"path": str(path)})
def _deliberate(holder): return _call("cad_deliberate", {"holder": holder})
def _who(holder): return _call("cad_who", {"holder": holder})
def _age(holder): return _call("cad_age", {"holder": holder})
def _record(code): return _call("cad_record", {"code": code})
def _sweep(): return _call("cad_sweep")
def _live_builds(exclude_pid=None): return _call("cad_live", {"exclude": exclude_pid})
def _drop_unlocked(pid): return _call("cad_drop_unlocked", {"pid": pid})
def _release(): return _call("cad_release_legacy")
def _holder_active(holder): return _call("cad_holder_active", {"holder": holder})
def wait_legacy(): return _call("cad_wait_legacy")


def _running_unlocked(script, source):
    if _call("cad_running_unlocked", {"script": script, "source": source}):
        atexit.register(_drop_unlocked, os.getpid())


def _on_signal(_signum, _frame):
    sys.exit(_call("cad_signal"))


class _Tee:
    def __init__(self, stream, sink):
        self._stream, self._sink = stream, sink

    def write(self, text):
        result = self._stream.write(text)
        try:
            self._sink.write(text)
            self._sink.flush()
        except (OSError, ValueError):
            pass
        return result

    def flush(self):
        self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)


def release():
    global _me
    _call("cad_release")
    _me = None


def acquire(script, source=None, root=None):
    global _me, _tee
    result = _call("cad_acquire", {"script": script, "source": source,
                                   "workspace": str(Path(root).resolve()) if root is not None else None})
    if "exit" in result:
        sys.exit(result["exit"])
    if result.get("tee") is None:
        return
    _me = result["identity"]
    try:
        _tee = open(result["tee"], "w")
        sys.stdout, sys.stderr = _Tee(sys.stdout, _tee), _Tee(sys.stderr, _tee)
    except OSError:
        _tee = None
    try:
        signal.signal(signal.SIGTERM, _on_signal)
        signal.signal(signal.SIGINT, _on_signal)
    except ValueError:
        pass
    previous_hook = sys.excepthook
    def hook(exc_type, exc, traceback):
        _record(1)
        previous_hook(exc_type, exc, traceback)
    sys.excepthook = hook
    real_exit = sys.exit
    def exit(code=0):
        _call("cad_exit_record", {"code": code})
        real_exit(code)
    sys.exit = exit
    atexit.register(release)
