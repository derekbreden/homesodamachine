#!/usr/bin/env python3
"""worktree.py — a git worktree whose files are clones of the main checkout's.

    python3 tools/worktree.py -b codex/fan-pair .cache/fan-pair/worktree main
    python3 tools/worktree.py --detach /private/tmp/hsm-check HEAD

The arguments are `git worktree add`'s. Each tracked file of the new worktree is an APFS clone
of the main checkout's copy, sharing its disk blocks until one side writes, and git writes only
the files that differ from the commit the worktree stands on. The memo caches the build reads
(realized, meshes, boxes) are cloned as well. Their keys name the code, the inputs and the
kernel, never the checkout, so the worktree's first build reads back what the main checkout
already drew.

A worktree made this way costs almost no disk until something in it changes. A clone keeps its
blocks when the main checkout's copy changes, so a worktree left standing grows toward a full
copy; `git worktree remove` takes it away. `du` counts a clone at full size, so free space is
what shows a worktree's cost.

tools/cad-venv is not cloned. The commit hook runs publish_now.py with the committing checkout's
venv, and in a worktree with none that run publishes nothing. Build in a worktree with the main
checkout's tools/cad-venv/bin/python.

Requires macOS and the Python standard library. A file that will not clone is left to git.
"""

import ctypes
import os
import stat
import subprocess
import sys
import time

CACHES = (b"realized", b"meshes", b"boxes")
CLONE_NOFOLLOW = 0x0001
VALUED = {"-b", "-B", "--reason"}  # the `git worktree add` options that take the next argument

libc = ctypes.CDLL(None, use_errno=True)
libc.clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32]


def clone(src: bytes, dst: bytes) -> bool:
    """APFS-clone a file, or a directory and everything under it; False where it will not."""
    return libc.clonefile(src, dst, CLONE_NOFOLLOW) == 0


def git(*args, cwd=None) -> bytes:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True).stdout


def path_of(argv) -> bytes:
    """The <path> among `git worktree add`'s arguments: its first one that is not an option."""
    rest = iter(argv)
    for arg in rest:
        if arg == "--":
            return os.fsencode(next(rest))
        if arg in VALUED:
            next(rest, None)
        elif not arg.startswith("-"):
            return os.fsencode(arg)
    raise SystemExit("worktree.py: no <path> among the arguments")


def main(argv) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    wt = os.path.abspath(path_of(argv))
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    source = os.path.dirname(common)
    added = subprocess.run(["git", "worktree", "add", "--no-checkout", *argv])
    if added.returncode:
        return added.returncode
    start = time.monotonic()

    cloned, made = 0, set()
    for entry in git("ls-tree", "-r", "-z", "--full-tree", "HEAD", cwd=wt).split(b"\0"):
        meta, _, path = entry.partition(b"\t")
        if meta.split(b" ", 1)[0] not in (b"100644", b"100755"):
            continue
        src = os.path.join(source, path)
        try:
            if not stat.S_ISREG(os.lstat(src).st_mode):
                continue
        except OSError:
            continue
        dst = os.path.join(wt, path)
        parent = os.path.dirname(dst)
        if parent not in made:
            os.makedirs(parent, exist_ok=True)
            made.add(parent)
        cloned += clone(src, dst)

    # The index takes the commit, a refresh finds the clones that already match it, and the
    # reset writes the rest: files the main checkout holds changed, or does not hold.
    git("read-tree", "HEAD", cwd=wt)
    subprocess.run(["git", "update-index", "-q", "--ignore-missing", "--refresh"],
                   cwd=wt, capture_output=True)
    written = sum(1 for p in git("diff-files", "--name-only", "-z", cwd=wt).split(b"\0") if p)
    git("reset", "-q", "--hard", cwd=wt)

    caches = []
    for name in CACHES:
        src = os.path.join(source, b".cache", name)
        dst = os.path.join(wt, b".cache", name)
        if os.path.isdir(src) and not os.path.lexists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if clone(src, dst):
                caches.append(name.decode())

    print(f"{os.fsdecode(wt)}: {cloned} files cloned from {os.fsdecode(source)}, "
          f"{written} written by git; caches cloned: {', '.join(caches) or 'none'} "
          f"({time.monotonic() - start:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
