"""Global single-flight lock for CAD builds: the newest build wins.

On start a build SIGTERMs any older live build holding the lock and takes it over;
the superseded build names who took it and exits 143. The lock is a pid file in the
OS temp dir; a stale file whose pid is dead is ignored.

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

_me = None


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
    sys.exit(143)


def _release():
    """Drop the lock on a normal exit — but only if we still hold it. A superseded
    build must not delete the lock its successor now owns."""
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
    # Only the main thread can install handlers; a generator imported off-thread
    # still gets the lock, just not the courtesy message.
    try:
        signal.signal(signal.SIGTERM, _on_signal)
        signal.signal(signal.SIGINT, _on_signal)
    except ValueError:
        pass
    atexit.register(_release)
