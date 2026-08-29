#!/usr/bin/env python3
"""_single_flight.py — one marker, one runner, and the marker that outlives its runner.

`.githooks/post-commit` fires two detached jobs on every commit, `publish_now.py` and
`checks_now.py`, and both want the same thing from a tree several sessions commit into at once:
many commits landing together produce one run against the newest tree, not one run each. Each
keeps a marker naming its own pid, drops it in `finally`, and stands down for a live holder.

THE MARKER OUTLIVES A RUNNER THAT IS KILLED. `finally` drops it when the process gets to run its
own unwinding, and a SIGKILL, a panic or a machine that sleeps hard is where it does not — after
which every later run reads a marker whose pid is gone and stands down for it, with nothing to
end the wait. Both jobs are detached under `nohup` into a log nobody opens, so there is no
failure to see: only a thing that quietly stops happening. A tree that stops reaching the site,
or a verdict on it that stops moving while every page goes on showing the last one.

That is not hypothetical. A read died at 23:14 on 2026-08-28 without unwinding, and the site
served that moment's verdict for the next fifty-seven commits.

So the marker is read, not merely tested for existence — the pid is in it for this one question.
The rule lives here once because it was written twice and only one copy asked the question.
"""

from __future__ import annotations

import os
from pathlib import Path


def holder(lock: Path) -> int:
    """The pid the marker names, or 0 where there is none to read."""
    try:
        return int(lock.read_text().strip())
    except (OSError, ValueError):
        return 0


def alive(pid: int) -> bool:
    """Whether that process is still on this machine."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True                 # alive, and not ours to signal
    return True


def take(lock: Path) -> tuple:
    """`(fd, cleared)` — the marker's open fd, and the dead pid whose marker was taken for it.

    `fd` is None while a live runner holds the marker, which is the caller's cue to ask for
    another pass and stand down. `cleared` is 0 unless a dead holder's marker was removed, so a
    caller says that in its own words rather than this saying it in one voice for both."""
    cleared = 0
    for _ in range(2):
        try:
            return os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY), cleared
        except FileExistsError:
            held = holder(lock)
            if alive(held):
                return None, cleared
            cleared = held
            lock.unlink(missing_ok=True)
    return None, cleared            # a live runner took it between the clear and the retry
