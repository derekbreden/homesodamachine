#!/usr/bin/env python3
"""push.py — land this session's commits on main without waiting for a human.

    tools/cad-venv/bin/python tools/push.py          (or plain python3; no imports outside stdlib)
    tools/cad-venv/bin/python tools/push.py --check   say what it would do, touch nothing

Six sessions commit into one checkout, so losing a push race is the resting state. The reconcile
is the same every time: fetch, work out whether what is held is already on the remote under
another hash, replay it if not, push again.

THE TWIN IS THE CASE THAT LOOKS LIKE A CONFLICT AND IS NOT. Two sessions commit the same
working-tree change and hold two hashes for one patch; one pushes, the other is rejected as
behind. Rebasing the loser onto the winner replays a patch already applied, and git either drops
it silently or stops on a conflict against its own content. The patch-id settles it: same patch,
already on the remote, so the local commit carries nothing the remote lacks and is dropped
rather than replayed.

NOTHING HERE TOUCHES THE SHARED WORKTREE. A rebase refuses against a dirty tree — for any file,
not just the ones it touches — and with several agents building, dirty is the resting state. A
replay happens in a detached worktree that shares no index and no checkout, and the only thing
done to this one is `reset --mixed` onto the ref that now holds the work: HEAD and the index
move, files are not read and not written, another session's uncommitted edits stand. A replay
that does not go cleanly is left alone and named; a wrong merge between two sessions is not
recoverable by the next push.

EXIT 0 WHEN THE WORK IS ON THE REMOTE, by whatever route, including when it was already there.
Non-zero only when it is not, which is the one thing the caller cannot find out later.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Main moves under a push while the push is being prepared, and the answer is to prepare it
# again against what is there now. Each attempt costs a fetch and a replay of a few commits, so
# the ceiling is low and the loop is not the slow part of anything.
ATTEMPTS = 6
REMOTE, BRANCH = "origin", "main"
WORKTREE = ".git/push-wt"


def git(*args: str, check: bool = True, cwd: Path | None = None) -> str:
    run = subprocess.run(["git", *args], cwd=str(cwd or ROOT),
                         capture_output=True, text=True)
    if check and run.returncode != 0:
        detail = (run.stderr or run.stdout).strip().splitlines()
        raise SystemExit(f"  git {' '.join(args)} did not answer: "
                         f"{detail[0] if detail else run.returncode}")
    return run.stdout.strip()


def ok(*args: str, cwd: Path | None = None) -> bool:
    return subprocess.run(["git", *args], cwd=str(cwd or ROOT),
                          capture_output=True, text=True).returncode == 0


ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip() or ".")


def patch_ids(rev_range: str) -> dict:
    """patch-id -> commit, for every commit in the range.

    `--stable` so the reading does not move with git's own hashing, and a commit whose patch is
    empty (a merge, or one that only moved the lock to bytes already there) answers with no id
    and is simply not a twin of anything."""
    out = {}
    for sha in git("rev-list", rev_range).split():
        show = subprocess.run(["git", "show", sha], cwd=str(ROOT),
                              capture_output=True, text=True).stdout
        pid = subprocess.run(["git", "patch-id", "--stable"], cwd=str(ROOT),
                             input=show, capture_output=True, text=True).stdout.split()
        if pid:
            out[pid[0]] = sha
    return out


def drop_worktree() -> None:
    ok("worktree", "remove", "--force", WORKTREE)
    ok("worktree", "prune")
    stale = ROOT / WORKTREE
    if stale.exists():
        shutil.rmtree(stale, ignore_errors=True)
        ok("worktree", "prune")


def land(check: bool) -> int:
    started = time.time()
    for attempt in range(1, ATTEMPTS + 1):
        git("fetch", "--quiet", REMOTE, BRANCH)
        upstream = f"{REMOTE}/{BRANCH}"
        ahead = git("rev-list", "--count", f"{upstream}..HEAD")
        behind = git("rev-list", "--count", f"HEAD..{upstream}")

        if ahead == "0" and behind == "0":
            print(f"  already on {upstream} — nothing to land ({time.time() - started:.1f}s)")
            return 0
        if ahead == "0":
            # Behind only: this session has nothing of its own out, and moving HEAD forward is
            # somebody else's business, not a push.
            print(f"  nothing of this session's to land; {behind} commit(s) behind {upstream}")
            return 0

        # THE TWIN READING, BEFORE ANY REPLAY. What is held locally and what arrived on the
        # remote are compared as patches, and a local commit whose patch is already there is
        # carrying nothing — the remote has the work under a different hash.
        mine = patch_ids(f"{upstream}..HEAD")
        theirs = patch_ids(f"HEAD..{upstream}") if behind != "0" else {}
        twins = {p: s for p, s in mine.items() if p in theirs}
        real = [s for p, s in mine.items() if p not in theirs]

        if twins and not real:
            for pid, sha in twins.items():
                print(f"  {sha[:8]} is already on {upstream} as {theirs[pid][:8]} "
                      f"— same patch, dropping the duplicate")
            if check:
                print("  --check: would reset to " + upstream)
                return 0
            # `--mixed`: HEAD and the index move to what the remote holds, the worktree is not
            # read and not written. Another session's uncommitted edits survive this untouched.
            git("reset", "--mixed", upstream)
            print(f"  landed — the work was already on {upstream} ({time.time() - started:.1f}s)")
            return 0

        if behind == "0":
            if check:
                print(f"  --check: would push {ahead} commit(s) fast-forward")
                return 0
            if ok("push", REMOTE, f"HEAD:{BRANCH}"):
                print(f"  landed {ahead} commit(s) ({time.time() - started:.1f}s)")
                return 0
            print(f"  push lost a race (attempt {attempt}/{ATTEMPTS}) — reading main again")
            continue

        if check:
            print(f"  --check: would replay {len(real)} commit(s) onto {upstream}"
                  + (f", dropping {len(twins)} twin(s)" if twins else ""))
            return 0

        # A REPLAY IN A TREE OF ITS OWN. cherry-pick does a real three-way merge, so a file that
        # moved on main since this commit was written is merged rather than overwritten — and it
        # happens in a checkout no other session shares, so the dirty state of this one is not
        # this operation's problem.
        for pid, sha in twins.items():
            print(f"  {sha[:8]} is already on {upstream} as {theirs[pid][:8]} — not replaying it")
        drop_worktree()
        git("worktree", "add", "--quiet", "--detach", WORKTREE, upstream)
        wt = ROOT / WORKTREE
        try:
            order = [s for s in reversed(git("rev-list", f"{upstream}..HEAD").split())
                     if s in real]
            picked = True
            for sha in order:
                if not ok("cherry-pick", "--allow-empty", "--keep-redundant-commits", sha, cwd=wt):
                    ok("cherry-pick", "--abort", cwd=wt)
                    print(f"  {sha[:8]} does not replay onto {upstream} cleanly.", file=sys.stderr)
                    print("  Left alone: a merge between two sessions is not this tool's to "
                          "guess. Resolve it and run again.", file=sys.stderr)
                    picked = False
                    break
            if not picked:
                return 1
            if ok("push", REMOTE, f"HEAD:{BRANCH}", cwd=wt):
                landed = git("rev-parse", "HEAD", cwd=wt)
                git("fetch", "--quiet", REMOTE, BRANCH)
                git("reset", "--mixed", landed)
                print(f"  landed {len(order)} commit(s) replayed onto {upstream} "
                      f"({time.time() - started:.1f}s)")
                return 0
            print(f"  push lost a race (attempt {attempt}/{ATTEMPTS}) — reading main again")
        finally:
            drop_worktree()

    print(f"  main moved under this push {ATTEMPTS} times running; the work is still local "
          f"and still committed.", file=sys.stderr)
    return 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="say what would happen and change nothing")
    args = ap.parse_args(argv)
    # A COMMIT MADE BY A REBASE IS NOT A COMMIT TO PUSH. `git rebase` runs the commit hooks for
    # each replayed commit, and pushing from inside one lands a branch mid-rewrite.
    for busy in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD"):
        if (ROOT / ".git" / busy).exists():
            print(f"  a {busy} is in progress — not pushing into the middle of it")
            return 0
    return land(args.check)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
