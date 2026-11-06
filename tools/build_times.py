#!/usr/bin/env python3
"""build_times.py — puts each full build's time on the site.

    python3 tools/build_times.py            add new full builds to the site's list, commit if it moved
    python3 tools/build_times.py --check    print the full builds Bazel's records hold, touch nothing

A full build is `bazel build //:everything`. Bazel keeps a profile of every command in its output
base (`.bazelrc` sets how many) and names each command's targets and failure in its server log.
This reads those two records after the fact, so it adds nothing to a build. Each full build
becomes one row of `web/public/build-times.json`: when it started, how long it took, how many
steps it reran, and whether it finished. /settings shows the rows.

`.githooks/post-commit` starts it after every commit. It commits only when a full build is new.
"""

from __future__ import annotations

import argparse
import fcntl
import getpass
import gzip
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = "web/public/build-times.json"
OUT = ROOT / REL
LOCK = ROOT / ".cache" / "build-times.lock"
MSG = "build times: the full builds Bazel's records hold"
TARGET = "//:everything"
KEEP = 200

COMMAND = re.compile(r"GrpcServerImpl\.executeCommand\] \[(.*)\]\s*$")
BUILD_ID = re.compile(r"Build identifier: ([0-9a-f-]{36})")
EXIT = re.compile(r"Exit status was DetailedExitCode\{exitCode=([A-Z_]+)")


def output_base() -> Path:
    """Bazel names a workspace's output base by the MD5 of its path."""
    digest = hashlib.md5(str(ROOT).encode()).hexdigest()
    return Path.home() / "Library/Caches/bazel" / f"_bazel_{getpass.getuser()}" / digest


def commands(base: Path) -> dict[str, dict]:
    """Each build's targets and exit, by build id, from the server's logs."""
    found: dict[str, dict] = {}
    for log in sorted(base.glob("java.log.*")):
        args, current = None, None
        try:
            lines = log.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if m := COMMAND.search(line):
                args, current = m.group(1).split(", "), None
            elif (m := BUILD_ID.search(line)) and args:
                current = m.group(1)
                tail = args[next((i for i, a in enumerate(args) if a.startswith("--client_cwd=")), 0) + 1:]
                found[current] = {"command": args[0],
                                  "targets": [a for a in tail if not a.startswith("-")],
                                  "exit": "SUCCESS"}
            elif (m := EXIT.search(line)) and current:
                found[current]["exit"] = m.group(1)
    return found


def profile(path: Path) -> dict | None:
    """When a command started, how long it ran, and the steps it ran. None while it is written."""
    try:
        data = json.load(gzip.open(path))
    except (OSError, EOFError, ValueError):
        return None
    events = [e for e in data.get("traceEvents", []) if "ts" in e]
    if not events:
        return None
    start = min(e["ts"] for e in events)
    end = max(e["ts"] + e.get("dur", 0) for e in events)
    steps = sorted({e["name"].removeprefix("Executing genrule //:") for e in events
                    if e.get("cat") == "action processing"
                    and str(e.get("name", "")).startswith("Executing genrule //:")})
    other = data.get("otherData", {})
    return {"id": other.get("build_id"), "started": other.get("date"),
            "seconds": round((end - start) / 1e6, 1), "ran": steps}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def step_count(commit: str) -> int | None:
    text = git("show", f"{commit}:BUILD.bazel")
    return text.count("genrule(") or None


def full_builds() -> list[dict]:
    base = output_base()
    if not base.is_dir():
        return []
    logged = commands(base)
    rows = []
    for path in base.glob("command-*.profile.gz"):
        if path.is_symlink():
            continue
        got = profile(path)
        if not got or not got["id"]:
            continue
        cmd = logged.get(got["id"])
        if not cmd or cmd["command"] != "build" or TARGET not in cmd["targets"]:
            continue
        commit = git("log", "-1", "--format=%h", f"--before={got['started']}", "HEAD")
        rows.append({"id": got["id"], "started": got["started"], "commit": commit,
                     "seconds": got["seconds"], "reran": len(got["ran"]),
                     "steps": step_count(commit) if commit else None,
                     "finished": cmd["exit"] == "SUCCESS"})
    return rows


def merged(rows: list[dict]) -> dict:
    try:
        have = json.loads(OUT.read_text())["builds"]
    except (OSError, ValueError, KeyError, TypeError):
        have = []
    by_id = {b["id"]: b for b in have}
    for row in rows:
        by_id.setdefault(row["id"], row)
    builds = sorted(by_id.values(), key=lambda b: b["started"])[-KEEP:]
    return {"builds": builds}


def committed() -> bool:
    """Whether HEAD already carries the file as it is on disk."""
    if subprocess.run(["git", "ls-files", "--error-unmatch", REL], cwd=ROOT,
                      capture_output=True).returncode != 0:
        return False
    return subprocess.run(["git", "diff", "--quiet", "HEAD", "--", REL], cwd=ROOT).returncode == 0


def land() -> int:
    """`--only` keeps the commit to this file whatever else the tree holds; `--no-verify` skips
    the pre-commit re-derive, which has nothing to say about a reading. The index is shared with
    every session and with `publish_now.py`, so three tries."""
    for attempt in range(3):
        git("add", REL)
        if subprocess.run(["git", "commit", "--no-verify", "--only", REL, "-m", MSG],
                          cwd=ROOT, capture_output=True).returncode == 0:
            return 0
        time.sleep(1.5 * (attempt + 1))
    print("  build times did not commit; the next commit's run tries again", file=sys.stderr)
    return 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.check:
        for row in sorted(full_builds(), key=lambda b: b["started"]):
            print(f"  {row['started']}  {row['seconds']:>7.1f} s  reran {row['reran']}"
                  f"{'' if row['finished'] else '  (failed)'}")
        return 0

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "w") as held:
        try:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        document = merged(full_builds())
        text = json.dumps(document, indent=2) + "\n"
        try:
            same = OUT.read_text() == text
        except OSError:
            same = False
        if same and committed():
            return 0
        if not same:
            OUT.write_text(text)
        return land()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
