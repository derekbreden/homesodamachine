"""Native CAD admission, with inherited heavy-run and CAD flock leases.

Every native run enters the host's shared heavy-run slots, then the single CAD
lease. HSM_NO_BUILD_LOCK never grants admission: only a validated inherited CAD
descriptor skips taking a second lease. The legacy build.json remains visible to
watchers and older worktrees, and its live holders are waited out without a timeout
that starts another CAD process alongside them. Parent launchers pass both leases
to their children, so a child never queues behind its own parent.
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


def _asked(name: str) -> bool:
    """Whether an environment flag was actually asked for.

    NOT A TRUTHINESS TEST ON THE RAW VALUE. `HSM_BUILD_SUPERSEDE=0` reads as yes to `bool()`,
    and what a caller means by writing `0` is no — twice now that has been one session killing
    another's build while deliberately trying not to."""
    return (os.environ.get(name) or "").strip().lower() not in ("", "0", "no", "false", "off")


def _unlocked_of(pid: int) -> Path:
    """Where a build running under `HSM_NO_BUILD_LOCK` records itself. `acquire` writes it
    on the way out and `_live_builds` reads it."""
    return LOCK_DIR / f"unlocked.{pid}.json"

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


def _newest_input_mtime(root=None) -> float:
    """The newest mtime among the .py under hardware/ — the sources an edit lands in.
    A stat walk, no parsing. STEPs are left out on purpose: a generator writes them, so
    counting them would make every build look stale to the next one, and the .py edit
    that regenerates a STEP moves this number first anyway."""
    newest = 0.0
    for root, dirs, files in os.walk(Path(root) / 'hardware' if root else _HW):
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
    return _newest_input_mtime(holder.get('root')) <= started


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
        if not _holder_active(holder):
            time.sleep(POLL_S)                  # let a last write and the result land
            code = _read(result)
            return code.get("code") if code else None
        time.sleep(POLL_S)


def _alive(pid: int) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
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


# How long a watcher rebuild waits for a hand or agent run before it stops waiting. Long
# enough for the slowest generator, bounded so a hung holder cannot stall the cascade.
WAIT_S = 900.0


def _deliberate(holder) -> bool:
    """Whether this build is work someone is waiting on. A watcher rebuild is not: it
    fires again on the next save, and its result is a refresh rather than an answer."""
    return not str(holder.get("source", "")).startswith("dev-server")


def _who(holder) -> str:
    if not holder:
        return "a newer build"
    return f"{holder.get('source', '?')} ({holder.get('script', '?')})"


def _age(holder) -> str:
    """How long the holder has held the machine, for the message that starts a wait.

    A WAITER CANNOT SIZE ITS WAIT FROM A PID. What it is queued behind is the rest of one
    generator's run, so the holder's age is the only figure that separates a wait about to
    end from one just begun — and without it a queue behind a long build reads as a hang.
    That reading is what routes an agent around this lock and onto the same cores it exists
    to keep clear."""
    started = holder.get("started")
    if not started:
        return "age unknown"
    secs = max(0.0, time.time() - started)
    return f"{secs:.0f}s in" if secs < 90 else f"{secs // 60:.0f}m{secs % 60:02.0f}s in"


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
    """Drop the log, result and unlocked marker of every build whose pid is gone."""
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
        for p in LOCK_DIR.glob("unlocked.*.json"):
            try:
                pid = int(p.name.split(".")[1])
            except (IndexError, ValueError):
                continue
            if not _alive(pid):
                try:
                    p.unlink()
                except OSError:
                    pass
    except OSError:
        pass


def _live_builds(exclude_pid: int = None) -> list:
    """Every CAD build running right now: the lock's holder, and each build that opted out
    and recorded itself. A build that opted out takes no lock, so the two are counted from
    different files."""
    out = {}
    holder = _read(LOCK)
    if holder and _alive(holder.get("pid", -1)):
        out[holder["pid"]] = holder
    try:
        for p in LOCK_DIR.glob("unlocked.*.json"):
            rec = _read(p)
            if rec and _alive(rec.get("pid", -1)):
                out[rec["pid"]] = rec
    except OSError:
        pass
    out.pop(exclude_pid, None)
    return sorted(out.values(), key=lambda r: r.get("started", 0.0))


def _running_unlocked(script: str, source: str) -> None:
    """Record this opted-out build, and name what its opting out costs while other builds
    are on the machine: it supersedes none of them, none of them can follow it, and every
    one of them is on the same cores. Silent when it is the only build running, which is
    when opting out costs nothing."""
    pid = os.getpid()
    rec = {"pid": pid, "source": source, "script": script, "started": time.time()}
    try:
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        _sweep()
        _unlocked_of(pid).write_text(json.dumps(rec))
        atexit.register(_drop_unlocked, pid)
    except OSError:
        pass
    others = _live_builds(exclude_pid=pid)
    if not others:
        return
    who = ", ".join(f"{_who(o)} pid {o['pid']}" for o in others)
    print(f"[build] running unlocked (HSM_NO_BUILD_LOCK) beside {len(others)} live "
          f"build{'s' if len(others) > 1 else ''}: {who} — this build supersedes none of "
          f"them, none of them can follow it, and all of them are on the same cores",
          file=sys.stderr, flush=True)


def _drop_unlocked(pid: int) -> None:
    try:
        _unlocked_of(pid).unlink()
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


def release():
    """Release this process's native admission, retaining any parent's descriptors."""
    global _me
    from _run_slots import release_cad
    release_cad()
    _release()
    _me = None


def _holder_active(holder):
    if holder.get('run_slots'):
        import _run_slots
        import fcntl
        fd = os.open(_run_slots._path('cad'), os.O_RDWR | os.O_CREAT, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            return False
        finally:
            os.close(fd)
    return _alive(holder.get('pid', -1))


def wait_legacy():
    """Drain an older PID-only CAD holder before reserving the shared root capacity."""
    import _run_slots
    if _run_slots.current_cad() is not None:
        return
    announced = None
    while True:
        holder = _read(LOCK)
        if not holder or holder.get('run_slots') or holder.get('pid') == os.getpid() or not _alive(holder.get('pid', -1)):
            return
        if announced != holder.get('pid'):
            print(f"[build] waiting for legacy native CAD pid {holder['pid']} before admission",
                  file=sys.stderr, flush=True)
            announced = holder.get('pid')
        time.sleep(POLL_S)


def acquire(script: str, source: str = None, root=None) -> None:
    """Enter shared heavy admission and become the sole native CAD owner."""
    global _me
    if _me is not None:
        return
    import _run_slots as slots
    if slots.current() is None:
        wait_legacy()
    slots.acquire(script)
    if slots.current_cad() is not None:
        return                              # the parent's verified lease; keep its build.json
    source = source or os.environ.get("HSM_BUILD_SOURCE") or "manual"
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    identity = {"pid": os.getpid(), "source": source, "script": script,
                "root": str(Path(root).resolve() if root else _HW.parent), "started": time.time(),
                "run_slots": 1,
                "protected": _asked("HSM_BUILD_LOCK_PROTECT")}
    announced = None
    while True:
        previous = _read(LOCK)
        if previous and previous.get("pid") != os.getpid() and _holder_active(previous):
            if (previous.get("script") == script and previous.get("root") == identity["root"]
                    and not os.environ.get("HSM_NO_BUILD_ATTACH") and _fresh_for(previous)):
                code = _attach(previous)
                if code is not None:
                    sys.exit(code)
                continue
            if not previous.get('run_slots'):
                if announced != previous.get("pid"):
                    print(f"[build] waiting for native CAD pid {previous['pid']} "
                          f"({_who(previous)}, {_age(previous)})", file=sys.stderr, flush=True)
                    announced = previous.get("pid")
                time.sleep(POLL_S)
                continue
        slots.acquire_cad()
        # A legacy caller cannot see flock; recheck its visible ownership before publishing ours.
        previous = _read(LOCK)
        if previous and not previous.get('run_slots') and previous.get("pid") != os.getpid() and _alive(previous.get("pid", -1)):
            slots.release_cad()
            continue
        break
    _me = identity
    temporary = LOCK.with_name(f".build.{os.getpid()}.json")
    temporary.write_text(json.dumps(_me))
    os.replace(temporary, LOCK)
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
    # `raise SystemExit` reaches neither.
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
    atexit.register(release)
