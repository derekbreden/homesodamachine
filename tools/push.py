#!/usr/bin/env python3
"""push.py — land this session's commits on main without waiting for a human, and bring the
shared tree up to main while at it.

    tools/cad-venv/bin/python tools/push.py          (or plain python3; no imports outside stdlib)
    tools/cad-venv/bin/python tools/push.py --check   say what it would do, touch nothing

Six sessions commit into one checkout, so losing a push race is the resting state. The reconcile
is the same every time: fetch, work out whether what is held is already on the remote under
another hash, replay it if not, push again. `.githooks/post-commit` runs this after every commit.
A clone whose hooks are not wired runs it by hand after committing; it lands HEAD on main from
whatever branch the checkout is on.

THE TWIN IS THE CASE THAT LOOKS LIKE A CONFLICT AND IS NOT. Two sessions commit the same
working-tree change and hold two hashes for one patch; one pushes, the other is rejected as
behind. Rebasing the loser onto the winner replays a patch already applied, and git either drops
it silently or stops on a conflict against its own content. The patch-id settles it: same patch,
already on the remote, so the local commit carries nothing the remote lacks and is dropped
rather than replayed.

NOTHING HERE REBASES THE SHARED WORKTREE, BECAUSE GIT WILL NOT. A rebase refuses against a dirty
tree — for any file, not just the ones it touches — and with several agents building, dirty is
the resting state. So a replay happens in a detached worktree that shares no index and no
checkout, with the lock's own merge driver (`tools/cad-artifacts/merge_lock.py`, written into
this clone's config here) folding two publishes into one where git would stop.

AND THEN THIS TREE IS BROUGHT UP TO WHAT LANDED, FILE BY FILE, because the tree is what every
session here reads and builds from. HEAD and the index move to the landed ref. Then each file
main moved is looked at on its own: one nobody here touched takes main's copy; one somebody
here changed — an edit in flight, or a commit that did not replay — is merged three ways in
place, and where that does not go cleanly the conflict markers are written into the file on the
disk, so every session sees the collision where it is and whoever owns the file resolves it and
commits. A binary, a file deleted on one side and changed on the other, a path added on both:
named and not touched. Nothing a session had in flight is overwritten with main's copy.

A COMMIT THAT DOES NOT REPLAY DISSOLVES INTO THE TREE. The replay stops at the first commit
that conflicts; what replayed before it lands. That commit and the ones after it leave the
branch (ORIG_HEAD keeps what HEAD was) and their changes stand uncommitted on this disk, marked
where they collide with main. The report names each collision: the file, the commit on main it
met, and the session that made that commit when its message names one. Resolve, commit the
files by name, and this runs again with the commit.

EXIT 0 WHEN THE WORK IS ON THE REMOTE, by whatever route, including when it was already there.
Non-zero only when it is not, which is the one thing the caller cannot find out later.
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Main moves under a push while the push is being prepared, and the answer is to prepare it
# again against what is there now. Each attempt costs a fetch and a replay of a few commits, so
# the ceiling is low and the loop is not the slow part of anything.
ATTEMPTS = 6
REMOTE, BRANCH = "origin", "main"

#: The replay tree, named for the process that prepares it.
WORKTREE = f".git/push-wt-{os.getpid()}"

#: The one file two publishes always meet on, and the driver `.gitattributes` names for it.
LOCK_REL = "hardware/cad-artifacts.lock.json"
DRIVER = "cadlock"

#: A HOOK HANDS DOWN THE CHECKOUT IT RAN IN, and these are how. Git exports them naming paths
#: against that checkout — `GIT_INDEX_FILE` is `.git/next-index-*.lock` under a pathspec commit
#: — and `worktree add` resolves them again from inside the tree it has just made, where `.git`
#: is a file. Every call below runs without them, so this lands the same by hand and from a
#: hook.
ENV = {k: v for k, v in os.environ.items()
       if k not in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE",
                    "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR", "GIT_PREFIX")}


def git(*args: str, check: bool = True, cwd: Path | None = None) -> str:
    run = subprocess.run(["git", *args], cwd=str(cwd or ROOT),
                         capture_output=True, text=True, env=ENV)
    if check and run.returncode != 0:
        detail = (run.stderr or run.stdout).strip().splitlines()
        raise SystemExit(f"  git {' '.join(args)} did not answer: "
                         f"{detail[0] if detail else run.returncode}")
    return run.stdout.strip()


def ok(*args: str, cwd: Path | None = None) -> bool:
    return subprocess.run(["git", *args], cwd=str(cwd or ROOT),
                          capture_output=True, text=True, env=ENV).returncode == 0


ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip() or ".")


def ensure_merge_driver() -> None:
    """The lock's merge driver, in this clone's config.

    `.gitattributes` can name a driver for a path but cannot carry its command; that lives in
    config, which no clone inherits. So every clone gets it the first time this runs there —
    a cloud checkout that commits and runs `tools/push.py` included — and a rebase by hand in
    that clone merges the lock the same way a replay here does."""
    script = ROOT / "tools" / "cad-artifacts" / "merge_lock.py"
    if not script.is_file():
        return
    want = f"python3 {shlex.quote(str(script))} %O %A %B"
    if git("config", "--get", f"merge.{DRIVER}.driver", check=False) != want:
        git("config", f"merge.{DRIVER}.driver", want)
        git("config", f"merge.{DRIVER}.name", "the CAD lock, merged by member")


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
    drop_abandoned()


def drop_abandoned() -> None:
    """Replay trees whose process is gone. `worktree prune` drops the entry once the directory
    is, so the directory is what goes here."""
    for tree in (ROOT / ".git").glob("push-wt-*"):
        name = tree.name.rsplit("-", 1)[-1]
        if not name.isdigit() or int(name) == os.getpid():
            continue
        try:
            os.kill(int(name), 0)
        except ProcessLookupError:
            shutil.rmtree(tree, ignore_errors=True)
            ok("worktree", "prune")
        except PermissionError:
            pass


# -- bringing this tree up to what landed -----------------------------------------------------

def tree_blobs(rev: str) -> dict:
    """path -> blob id for every file `rev` holds."""
    out = {}
    raw = subprocess.run(["git", "ls-tree", "-r", "-z", rev], cwd=str(ROOT),
                         capture_output=True, text=True, env=ENV).stdout
    for entry in raw.split("\0"):
        if entry:
            meta, _, path = entry.partition("\t")
            out[path] = meta.split()[2]
    return out


def disk_blobs(paths: list) -> dict:
    """path -> blob id for the files on this disk; None where there is no file."""
    present = [p for p in paths if (ROOT / p).is_file()]
    out = {p: None for p in paths}
    if present:
        ids = subprocess.run(["git", "hash-object", "--stdin-paths"], cwd=str(ROOT),
                             input="\n".join(present) + "\n", capture_output=True,
                             text=True, env=ENV).stdout.split()
        out.update(zip(present, ids))
    return out


def blob_bytes(blob: str) -> bytes:
    return subprocess.run(["git", "cat-file", "blob", blob], cwd=str(ROOT),
                          capture_output=True, env=ENV).stdout


def is_binary(a: str, b: str, path: str) -> bool:
    if git("check-attr", "merge", "--", path, check=False).endswith(": unset"):
        return True
    return git("diff", "--numstat", a, b, "--", path, check=False).startswith("-\t-")


def beat_by(base: str, landed: str, path: str) -> list:
    """The commits on main since `base` that moved `path`, newest first: hash, subject, when,
    and the session the commit names in a `Session:` trailer, if it names one."""
    fmt = "%h%x1f%s%x1f%ar%x1f%(trailers:key=Session,valueonly,separator=%x2C)"
    out = []
    for line in git("log", f"--format={fmt}", f"{base}..{landed}", "--", path,
                    check=False).splitlines():
        h, s, when, who = (line.split("\x1f") + [""] * 4)[:4]
        out.append((h, s, when, who.strip()))
    return out


def merge_in_place(path: str, base_blob: str, landed_blob: str, base: str, landed: str) -> str:
    """Main's change folded into the copy of `path` on this disk. `merged`, `marked` (conflict
    markers written into the file), or a reason it was left alone."""
    met = beat_by(base, landed, path)
    label = f"main {met[0][0]} {met[0][1]}" if met else "main"
    if path == LOCK_REL:
        try:
            sys.dont_write_bytecode = True     # no __pycache__ left in a clone by a push
            sys.path.insert(0, str(ROOT / "tools" / "cad-artifacts"))
            import merge_lock
            text, notes = merge_lock.merge_texts(
                blob_bytes(base_blob).decode(), blob_bytes(landed_blob).decode(),
                (ROOT / path).read_text())
            (ROOT / path).write_text(text)
            for note in notes:
                print(f"  {LOCK_REL}: {note}")
            return "merged"
        except Exception as exc:  # noqa: BLE001 — the text merge below then names it
            print(f"  {LOCK_REL}: the lock driver could not merge it ({exc})", file=sys.stderr)
    with tempfile.TemporaryDirectory() as d:
        base_file, main_file = Path(d) / "base", Path(d) / "main"
        base_file.write_bytes(blob_bytes(base_blob))
        main_file.write_bytes(blob_bytes(landed_blob))
        run = subprocess.run(["git", "merge-file", "-L", "this tree", "-L", "base", "-L", label,
                              str(ROOT / path), str(base_file), str(main_file)],
                             cwd=str(ROOT), capture_output=True, text=True, env=ENV)
    if run.returncode == 0:
        return "merged"
    if run.returncode > 0:
        return "marked"
    return f"could not be merged ({(run.stderr or run.stdout).strip()}); the copy here stands"


def bring_up(base: str, pre: str, landed: str, dry: bool) -> dict:
    """The files on this disk, brought to `landed` from a tree that stood at `pre` with edits
    in flight. Each path main moved since `base` is settled on its own; what main left alone
    is not touched, whatever this tree did to it."""
    tb, tp, tl = tree_blobs(base), tree_blobs(pre), tree_blobs(landed)
    main_moved = {p for p in set(tb) | set(tl) if tb.get(p) != tl.get(p)}
    here_moved = {p for p in set(tb) | set(tp) if tb.get(p) != tp.get(p)}
    in_flight = set(git("diff", "--name-only", pre, check=False).splitlines())
    paths = sorted(main_moved | here_moved | in_flight)
    disk = disk_blobs(paths)
    report = {"advanced": [], "merged": [], "marked": [], "named": [], "kept": []}
    for p in paths:
        w, l, b = disk[p], tl.get(p), tb.get(p)
        if w == l:
            continue
        if l == b:
            # Main left it alone; what differs here is this tree's own work, in flight or
            # dissolved from a commit that did not replay. It stays as it is.
            report["kept"].append(p)
            continue
        if w == b:
            # Nobody here touched it since the fork; main's copy takes its place.
            report["advanced"].append(p)
            if dry:
                continue
            if l is None:
                (ROOT / p).unlink(missing_ok=True)
            elif not ok("checkout", landed, "--", p):
                report["advanced"].pop()
                report["named"].append((p, "main's copy could not be checked out over it"))
            continue
        # Both sides moved it.
        if b is None and p not in tp and w is not None:
            report["named"].append((p, "added on main and on this disk; the copy here stands, "
                                       f"main's is `git show {landed[:8]}:{p}`"))
        elif l is None:
            report["named"].append((p, "deleted on main and changed here; the copy here stands"))
        elif w is None:
            report["named"].append((p, "changed on main and gone from this disk; "
                                       "`git checkout -- <path>` takes main's"))
        elif is_binary(base, landed, p):
            report["named"].append((p, "moved on main and here, and not text; the copy here "
                                       f"stands, main's is `git show {landed[:8]}:{p}`"))
        elif dry:
            report["merged"].append(p)
        else:
            outcome = merge_in_place(p, b, l, base, landed)
            if outcome in ("merged", "marked"):
                report[outcome].append(p)
            else:
                report["named"].append((p, outcome))
    return report


def settle(pre: str, landed: str, base: str, dissolved: list, dry: bool) -> None:
    """HEAD and the index to `landed`, and the files on this disk after them."""
    if not dry:
        git("reset", "--mixed", landed)
    rep = bring_up(base, pre, landed, dry)
    verb = "would bring" if dry else "brought"

    def few(paths):
        shown = ", ".join(paths[:8])
        return f": {shown}" + (f" (+{len(paths) - 8})" if len(paths) > 8 else "")

    if rep["advanced"]:
        print(f"  {verb} {len(rep['advanced'])} file(s) on this disk up to main{few(rep['advanced'])}")
    if rep["merged"]:
        print(f"  {verb} main's changes into {len(rep['merged'])} file(s) changed here"
              f"{few(rep['merged'])}")
    for p, why in rep["named"]:
        print(f"  left alone: {p} — {why}", file=sys.stderr)
    if rep["marked"]:
        print("  CONFLICT MARKERS are on this disk, in:", file=sys.stderr)
        for p in rep["marked"]:
            print(f"    {p}", file=sys.stderr)
            for h, s, when, who in beat_by(base, landed, p)[:3]:
                print(f"      met {h} {s} ({when})" + (f" — session {who}" if who else ""),
                      file=sys.stderr)
                if who:
                    print(f"        to ask them: SendMessage to \"{who}\" from a session here, "
                          f"<relay to=\"{who}\"> from the cloud", file=sys.stderr)
        print("    resolve them, then commit those files by name; this runs again with the "
              "commit.", file=sys.stderr)
    if dissolved:
        first = dissolved[0]
        files = sorted(set(git("diff", "--name-only", f"{first}^", pre, check=False).splitlines()))
        print(f"  {len(dissolved)} commit(s) did not replay and stand uncommitted on this disk "
              "now (ORIG_HEAD keeps what HEAD was):", file=sys.stderr)
        for sha in dissolved:
            print(f"    {sha[:8]} {git('log', '-1', '--format=%s', sha, check=False)}",
                  file=sys.stderr)
        print(f"    their files{few(files)}", file=sys.stderr)


# -- landing ----------------------------------------------------------------------------------

def land(check: bool) -> int:
    started = time.time()
    if not check:
        ensure_merge_driver()
    for attempt in range(1, ATTEMPTS + 1):
        git("fetch", "--quiet", REMOTE, BRANCH)
        upstream = f"{REMOTE}/{BRANCH}"
        pre = git("rev-parse", "HEAD")
        up = git("rev-parse", upstream)
        base = git("merge-base", pre, up)
        ahead = git("rev-list", "--count", f"{upstream}..HEAD")
        behind = git("rev-list", "--count", f"HEAD..{upstream}")

        if ahead == "0" and behind == "0":
            print(f"  already on {upstream} — nothing to land ({time.time() - started:.1f}s)")
            return 0
        if ahead == "0":
            # Behind only: nothing of this session's to push, and the tree comes up to main so
            # what every session here reads is what main holds.
            print(f"  nothing of this session's to land; {behind} commit(s) behind {upstream}")
            settle(pre, up, base, [], check)
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
            settle(pre, up, base, [], check)
            if not check:
                print(f"  landed — the work was already on {upstream} "
                      f"({time.time() - started:.1f}s)")
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
            settle(pre, up, base, [], True)
            return 0

        # A REPLAY IN A TREE OF ITS OWN. cherry-pick does a real three-way merge, so a file that
        # moved on main since this commit was written is merged rather than overwritten — and it
        # happens in a checkout no other session shares, so the dirty state of this one is not
        # this operation's problem. It stops at the first commit that does not go cleanly.
        for pid, sha in twins.items():
            print(f"  {sha[:8]} is already on {upstream} as {theirs[pid][:8]} — not replaying it")
        drop_worktree()
        git("worktree", "add", "--quiet", "--detach", WORKTREE, upstream)
        wt = ROOT / WORKTREE
        try:
            order = [s for s in reversed(git("rev-list", f"{upstream}..HEAD").split())
                     if s in real]
            dissolved = []
            for i, sha in enumerate(order):
                if not ok("cherry-pick", "--allow-empty", "--keep-redundant-commits", sha, cwd=wt):
                    ok("cherry-pick", "--abort", cwd=wt)
                    dissolved = order[i:]
                    break
            picked = order[:len(order) - len(dissolved)]
            landed = up
            if picked:
                if not ok("push", REMOTE, f"HEAD:{BRANCH}", cwd=wt):
                    print(f"  push lost a race (attempt {attempt}/{ATTEMPTS}) — reading main again")
                    continue
                landed = git("rev-parse", "HEAD", cwd=wt)
                git("fetch", "--quiet", REMOTE, BRANCH)
            settle(pre, landed, base, dissolved, False)
            if dissolved:
                print(f"  {dissolved[0][:8]} does not replay onto {upstream} cleanly; "
                      f"{len(picked)} of {len(order)} commit(s) landed and the rest is on this "
                      f"disk to resolve ({time.time() - started:.1f}s)", file=sys.stderr)
                return 1
            print(f"  landed {len(order)} commit(s) replayed onto {upstream} "
                  f"({time.time() - started:.1f}s)")
            return 0
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
