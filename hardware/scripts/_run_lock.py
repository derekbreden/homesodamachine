"""Global single-flight lock for CAD builds: the newest build wins, unless one that
answers the same question is already running.

On start a build SIGTERMs any older live build holding the lock and takes it over;
the superseded build names who took it and exits 143. The lock is a pid file in the
OS temp dir; a stale file whose pid is dead is ignored.

A build that finds a live holder of the SAME script, begun after the last edit to any
.py under hardware/, follows it instead: it prints what the holder prints and exits on
the holder's status, so a hand run and the watcher (or two agents) share one build
rather than killing each other to compute it twice. A holder that began before the
caller's own edit cannot answer for it and is superseded as before. Each build tees its
console to `build.<pid>.log` and writes its status to `build.<pid>.result` for whoever
follows; a holder that dies without one leaves the follower to build for itself.
HSM_NO_BUILD_ATTACH=1 opts out.

The scope is global — one CAD generator at a time across the whole repo — because
every generator contends for the same cores. A pileup is what makes a build take
minutes: the dev-server only supersedes the runs it spawned itself, so a watcher
rebuild, a hand run and a second agent's run all grind on together, each unaware of
the others. This lock is the one thing they all share.

HSM_BUILD_SOURCE labels a build in the messages ("dev-server", "pre-commit", else
"manual"). HSM_NO_BUILD_LOCK=1 opts out entirely, for tooling that imports a
generator's helpers without meaning to build.

HSM_BUILD_LOCK_PROTECT=1 marks a build that must not be superseded — the commit
gates, which run for minutes and would turn a stray watcher rebuild into a failed
commit. A build that finds a protected holder yields: it runs alongside rather than
killing it, which is the pre-lock behavior and only for as long as the gate runs.
"""

import atexit
import json
import os
import signal
import sys
import tempfile
import time
from pathlib import Path

LOCK_DIR = Path(tempfile.gettempdir()) / "hsm-cad-lock"
LOCK = LOCK_DIR / "build.json"        # the single global holder
BY = LOCK_DIR / "build.by.json"       # who superseded the victim, for its message

# How long a superseded build gets to stop on its own before it is SIGKILLed.
# CadQuery sits inside OCCT calls that ignore signals until they return, so the
# handler can lag; past this the machine matters more than the tidy exit.
GRACE_S = 5.0
POLL_S = 0.05

# Where a build tees its console so a later caller for the same script can read it.
def _log_of(pid: int) -> Path:
    return LOCK_DIR / f"build.{pid}.log"


def _result_of(pid: int) -> Path:
    return LOCK_DIR / f"build.{pid}.result"


# Anything under here that a generator reads. A build whose inputs changed after it
# started cannot answer for the caller's edit, so `_fresh_for` refuses to attach to it.
_HW = Path(__file__).resolve().parent.parent
_SKIP_DIRS = {"__pycache__", ".pio", "node_modules", ".git", "cad-venv", "pcb-venv"}

_me = None
_tee = None


class _Tee:
    """Write the console to the real stream and to the build's log, so a caller that
    attaches to this build sees exactly what it printed."""

    def __init__(self, stream, sink):
        self._stream, self._sink = stream, sink

    def write(self, s):
        n = self._stream.write(s)
        try:
            self._sink.write(s)
            self._sink.flush()
        except (OSError, ValueError):
            pass
        return n

    def flush(self):
        self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)


def _newest_input_mtime() -> float:
    """The newest mtime among the .py under hardware/ — the sources an edit lands in.
    A stat walk, no parsing. STEPs are left out on purpose: a generator writes them, so
    counting them would make every build look stale to the next one, and the .py edit
    that regenerates a STEP moves this number first anyway."""
    newest = 0.0
    for root, dirs, files in os.walk(_HW):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if not f.endswith(".py"):
                continue
            try:
                m = os.stat(os.path.join(root, f)).st_mtime
            except OSError:
                continue
            if m > newest:
                newest = m
    return newest


def _fresh_for(holder) -> bool:
    """Whether `holder` began after the last edit to anything it reads."""
    started = holder.get("started")
    if not started:
        return False
    return _newest_input_mtime() <= started


def _attach(holder) -> int:
    """Follow a live build of the same script to its end, printing what it prints.
    Returns its exit status, or None if it stopped without writing one."""
    pid = holder["pid"]
    log, result = _log_of(pid), _result_of(pid)
    print(f"[build] a {holder.get('source', '?')} build of this script is already running "
          f"(pid {pid}) — following it instead of starting a second one",
          file=sys.stderr, flush=True)
    pos = 0
    while True:
        try:
            with open(log, "r") as fh:
                fh.seek(pos)
                chunk = fh.read()
                pos = fh.tell()
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
        except OSError:
            pass
        code = _read(result)
        if code is not None:
            return code.get("code")
        if not _alive(pid):
            time.sleep(POLL_S)                  # let a last write and the result land
            code = _read(result)
            return code.get("code") if code else None
        time.sleep(POLL_S)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _who(holder) -> str:
    if not holder:
        return "a newer build"
    return f"{holder.get('source', '?')} ({holder.get('script', '?')})"


def _on_signal(_signum, _frame):
    """SIGTERM/SIGINT — usually a newer build taking the lock, but not always (a
    Ctrl-C, a `kill`). Only claim a supersede when the taker actually named us as its
    victim, so the message can be trusted. sys.exit (not os._exit) so the export
    helper's atomic-write cleanup still runs."""
    by = _read(BY)
    if by and _me and by.get("victim") == _me["pid"]:
        why = f"was superseded by {_who(by)}"
    else:
        why = "was terminated (not by a newer build)"
    print(f"[build] this build ({_who(_me)}) {why} — stopping", file=sys.stderr, flush=True)
    _record(143)
    sys.exit(143)


def _record(code) -> None:
    """Write this build's exit status where a follower reads it. The first status
    written stands: the signal and exception paths report before `_release` runs."""
    if not _me:
        return
    try:
        p = _result_of(_me["pid"])
        if not p.exists():
            p.write_text(json.dumps({"code": code}))
    except OSError:
        pass


def _sweep() -> None:
    """Drop the log and result of every build whose pid is gone."""
    try:
        for p in LOCK_DIR.glob("build.*.log"):
            try:
                pid = int(p.name.split(".")[1])
            except (IndexError, ValueError):
                continue
            if not _alive(pid):
                for q in (p, _result_of(pid)):
                    try:
                        q.unlink()
                    except OSError:
                        pass
    except OSError:
        pass


def _release():
    """Drop the lock on a normal exit — but only if we still hold it. A superseded
    build must not delete the lock its successor now owns. The status lands first."""
    _record(0)
    cur = _read(LOCK)
    if cur and _me and cur.get("pid") == _me["pid"]:
        for p in (LOCK, BY):
            try:
                p.unlink()
            except OSError:
                pass


def acquire(script: str, source: str = None) -> None:
    """Become the only running CAD build, superseding whoever holds the lock."""
    global _me
    if os.environ.get("HSM_NO_BUILD_LOCK") or _me is not None:
        return
    source = source or os.environ.get("HSM_BUILD_SOURCE") or "manual"
    protect = bool(os.environ.get("HSM_BUILD_LOCK_PROTECT"))
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    _me = {"pid": os.getpid(), "source": source, "script": script,
           "started": time.time(), "protected": protect}

    prev = _read(LOCK)
    if prev and prev.get("pid") != _me["pid"] and _alive(prev["pid"]) and prev.get("protected"):
        # A commit gate holds the lock. Killing it would fail the commit, so run
        # alongside it instead — and take no lock, so we supersede nobody either.
        print(f"[build] yielding to the protected build (pid {prev['pid']}, {_who(prev)}) "
              f"— running alongside it", file=sys.stderr, flush=True)
        _me = None
        return

    # A live build of the same script, begun after the last edit to anything it reads,
    # is already computing this caller's answer: follow it and exit on its status. A
    # staler holder, another script, or a follow that fails falls through to the
    # supersede below. HSM_NO_BUILD_ATTACH=1 opts out.
    if (prev and prev.get("pid") != _me["pid"] and _alive(prev["pid"])
            and prev.get("script") == script and not os.environ.get("HSM_NO_BUILD_ATTACH")):
        try:
            if _fresh_for(prev):
                code = _attach(prev)
                if code is not None:
                    _me = None
                    sys.exit(code)
                print("[build] the build we were following stopped without a result "
                      "— building here instead", file=sys.stderr, flush=True)
        except SystemExit:
            raise
        except Exception as e:                  # never let the shortcut break a build
            print(f"[build] could not follow the running build ({e}) — building here instead",
                  file=sys.stderr, flush=True)

    if prev and prev.get("pid") != _me["pid"] and _alive(prev["pid"]):
        print(f"[build] superseding the active build (pid {prev['pid']}, {_who(prev)}) "
              f"— sending SIGTERM", file=sys.stderr, flush=True)
        try:
            BY.write_text(json.dumps({**_me, "victim": prev["pid"]}))
        except OSError:
            pass
        try:
            os.kill(prev["pid"], signal.SIGTERM)
        except OSError:
            pass
        until = time.monotonic() + GRACE_S
        while _alive(prev["pid"]) and time.monotonic() < until:
            time.sleep(POLL_S)
        if _alive(prev["pid"]):
            print(f"[build] pid {prev['pid']} did not stop within {GRACE_S:g}s — SIGKILL",
                  file=sys.stderr, flush=True)
            try:
                os.kill(prev["pid"], signal.SIGKILL)
            except OSError:
                pass
    else:
        try:
            BY.unlink()
        except OSError:
            pass

    LOCK.write_text(json.dumps(_me))
    _sweep()
    # Tee the console into this build's log, so a later caller for the same script reads
    # what it printed. A sink that will not open leaves the streams untouched.
    global _tee
    try:
        _tee = open(_log_of(_me["pid"]), "w")
        sys.stdout = _Tee(sys.stdout, _tee)
        sys.stderr = _Tee(sys.stderr, _tee)
    except OSError:
        _tee = None
    # Only the main thread can install handlers; a generator imported off-thread
    # still gets the lock, just not the courtesy message.
    try:
        signal.signal(signal.SIGTERM, _on_signal)
        signal.signal(signal.SIGINT, _on_signal)
    except ValueError:
        pass
    # What a follower reads as this build's status. `sys.excepthook` never sees SystemExit
    # and `atexit` cannot read a pending exit code, so the two deliberate exits report for
    # themselves: an unhandled exception through the hook, `sys.exit` through the wrapper.
    # A generator that ends a build by raising SystemExit directly bypasses both and lands
    # on `_release`'s 0 — end them with `sys.exit(...)`.
    _prev_hook = sys.excepthook

    def _hook(exc_type, exc, tb):
        _record(1)
        _prev_hook(exc_type, exc, tb)

    sys.excepthook = _hook

    _real_exit = sys.exit

    def _exit(code=0):
        _record(1 if isinstance(code, str) else (code or 0))
        _real_exit(code)

    sys.exit = _exit
    atexit.register(_release)
