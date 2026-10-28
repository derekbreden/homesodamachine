#!/usr/bin/env python3
"""Keep the Claude Code transcripts of archived sessions in iCloud Drive.

A session is offloaded once none of its files has been written for --hours
and the desktop app no longer shows it in the sidebar: the app has it
archived, or has no record of it. Its transcripts (the session's, its
subagents', and the copies Claude Code sets aside) and its spilled tool
results of 64 KB or more move into iCloud Drive under "Agent
transcripts/claude/projects", and a symlink takes each one's place. A copy
that iCloud reports uploaded, and that has also gone --hours without a write,
is evicted from this disk.

The desktop app reads a transcript only from a regular file, so it shows an
offloaded session's transcript as unavailable. The CLI reads and appends
through the symlinks, downloading an evicted copy. A session that is back in
the sidebar gets its files back on the next run.

The default dry run lists what would change; --apply does it. The hourly
launchd job described in transcript-offload.md runs it with --apply.
Requires the Python standard library and osascript.
"""

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

PROJECTS = Path.home() / ".claude" / "projects"
APP_SESSIONS = Path.home() / "Library" / "Application Support" / "Claude" / "claude-code-sessions"
MIRROR = (Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
          / "Agent transcripts" / "claude" / "projects")
LOCK = Path.home() / ".config" / "transcript-offload" / "lock"
MIN_BYTES = 64 * 1024
SF_DATALESS = 0x40000000  # st_flags bit of a file whose data lives only in iCloud
SESSION = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

# Evicts each listed path that iCloud reports uploaded; the rest stay pending.
EVICT_JS = r"""
ObjC.import('Foundation');
function run(argv) {
  const fm = $.NSFileManager.defaultManager;
  const paths = ObjC.unwrap($.NSString.stringWithContentsOfFileEncodingError(
      argv[0], $.NSUTF8StringEncoding, null)).split('\n').filter(Boolean);
  return paths.map(p => {
    const url = $.NSURL.fileURLWithPath(p), up = Ref();
    url.getResourceValueForKeyError(up, $.NSURLUbiquitousItemIsUploadedKey, null);
    if (ObjC.unwrap(up[0]) !== true) return 'pending\t' + p;
    return (fm.evictUbiquitousItemAtURLError(url, null) ? 'evicted' : 'failed') + '\t' + p;
  }).join('\n');
}
"""


def in_sidebar():
    """CLI session ids the desktop app lists unarchived, or None without records."""
    shown, records = set(), 0
    for p in APP_SESSIONS.glob("*/*/local_*.json"):
        try:
            record = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        records += 1
        if record.get("cliSessionId") and not record.get("isArchived"):
            shown.add(record["cliSessionId"])
    return shown if records else None


def sessions(project):
    """Each session in a project folder with every file that belongs to it."""
    groups = {}
    for entry in project.iterdir():
        m = SESSION.match(entry.name)
        if m:
            groups.setdefault(m.group(0), []).append(entry)
    for sid, entries in sorted(groups.items()):
        files = []
        for entry in entries:
            if entry.is_dir() and not entry.is_symlink():
                for dirpath, _, names in os.walk(entry):
                    files += [Path(dirpath) / n for n in names if n != ".DS_Store"]
            else:
                files.append(entry)
        yield sid, files


def last_write(path):
    """mtime of a file, or of the iCloud copy its symlink points to."""
    try:
        return path.stat().st_mtime
    except OSError:
        return path.lstat().st_mtime


def offloaded(path):
    return path.is_symlink() and Path(os.readlink(path)).is_relative_to(MIRROR)


def offloadable(path, project):
    if path.is_symlink() or not path.is_file():
        return False
    return ((".jsonl" in path.name or "tool-results" in path.relative_to(project).parts)
            and path.stat().st_size >= MIN_BYTES)


def offload(path, project):
    """Move a file into the mirror and leave a symlink to it; never overwrite."""
    dst = MIRROR / project.name / path.relative_to(project)
    if dst.exists() or dst.is_symlink():
        dst = dst.with_name(f"{dst.stem}.{time.strftime('%Y%m%d-%H%M%S')}{dst.suffix}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.rename(path, dst)
    os.symlink(dst, path)


def restore(link):
    """Put a local copy of the mirror file in the symlink's place, then drop the mirror file."""
    target = Path(os.readlink(link))
    tmp = link.with_name(f".{link.name}.restore")
    shutil.copyfile(target, tmp)  # downloads an evicted copy
    copied = tmp.stat().st_size
    st = target.stat()
    os.utime(tmp, (st.st_atime, st.st_mtime))
    os.rename(tmp, link)
    if target.stat().st_size > copied:  # appended through the symlink meanwhile
        with open(target, "rb") as src, open(link, "ab") as dst:
            src.seek(copied)
            shutil.copyfileobj(src, dst)
    target.unlink()
    return copied


def resident(cutoff):
    """Mirror files still held on this disk that have gone the idle time unwritten."""
    for dirpath, _, names in os.walk(MIRROR):
        for name in names:
            p = Path(dirpath) / name
            st = p.lstat()
            if st.st_blocks and not st.st_flags & SF_DATALESS and st.st_mtime < cutoff:
                yield p, st.st_blocks * 512


def evict(paths):
    with tempfile.NamedTemporaryFile("w", suffix=".txt") as listing:
        listing.write("\n".join(str(p) for p in paths))
        listing.flush()
        out = subprocess.run(["osascript", "-l", "JavaScript", "-e", EVICT_JS, listing.name],
                             capture_output=True, text=True, check=True).stdout
    return dict(line.split("\t", 1)[::-1] for line in out.splitlines() if "\t" in line)


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hours", type=float, default=24.0,
                   help="offload archived sessions idle longer than this many hours (default: 24)")
    p.add_argument("--apply", action="store_true",
                   help="move, restore and evict; without it, only list")
    args = p.parse_args()

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock = open(LOCK, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} :: another offload is running")
        return 0

    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cutoff = time.time() - args.hours * 3600
    shown = in_sidebar()
    if shown is None:
        print(f"{stamp} :: no desktop app session records under {APP_SESSIONS}; nothing moved")
        return 1
    moved = moved_bytes = restored = restored_bytes = idle = active = sidebar = failed = 0
    for project in sorted(d for d in PROJECTS.iterdir() if d.is_dir() and not d.is_symlink()):
        for sid, files in sessions(project):
            if sid in shown:
                sidebar += 1
                back = [f for f in files if offloaded(f)]
                for f in back:
                    if not args.apply:
                        restored += 1
                        continue
                    try:
                        restored_bytes += restore(f)
                        restored += 1
                    except OSError as e:
                        print(f"  failed  {f}: {e}")
                        failed += 1
                if back:
                    print(f"  {'restored' if args.apply else 'would restore'}  "
                          f"{len(back):4d} file(s)  {project.name}/{sid}")
                continue
            newest = max(map(last_write, files), default=0)
            if newest >= cutoff:
                active += 1
                continue
            todo = [f for f in files if offloadable(f, project)]
            if not todo:
                continue
            sizes = [f.stat().st_size for f in todo]
            idle += 1
            if args.apply:
                done = []
                for f, n in zip(todo, sizes):
                    try:
                        offload(f, project)
                        done.append(n)
                    except OSError as e:
                        print(f"  failed  {f}: {e}")
                        failed += 1
                sizes = done
            when = time.strftime("%Y-%m-%d %H:%M", time.localtime(newest))
            print(f"  {'moved' if args.apply else 'would move'}  {when}  "
                  f"{sum(sizes) / 1e6:9.1f} MB  {len(sizes):4d} file(s)  {project.name}/{sid}")
            moved += len(sizes)
            moved_bytes += sum(sizes)

    held = dict(resident(cutoff)) if MIRROR.is_dir() else {}
    evicted = evicted_bytes = pending = 0
    if args.apply and held:
        try:
            outcomes = evict(held)
        except subprocess.CalledProcessError as e:
            print(f"  eviction failed: {e.stderr.strip()}")
            outcomes, failed = {}, failed + 1
        for path, outcome in outcomes.items():
            if outcome == "evicted":
                evicted += 1
                evicted_bytes += held[Path(path)]
            elif outcome == "pending":
                pending += 1
            else:
                print(f"  failed to evict  {path}")
                failed += 1

    if args.apply:
        tail = (f"restored {restored_bytes / 1e9:.2f} GB in {restored} file(s); "
                f"evicted {evicted_bytes / 1e9:.2f} GB in {evicted} file(s), "
                f"{pending} awaiting upload")
    else:
        tail = (f"would restore {restored} file(s); {sum(held.values()) / 1e9:.2f} GB in "
                f"{len(held)} iCloud file(s) to evict once uploaded")
    print(f"{stamp} :: transcripts {'moved' if args.apply else 'would move'} "
          f"{moved_bytes / 1e9:.2f} GB in {moved} file(s) from {idle} session(s); {tail}; "
          f"{sidebar} in the sidebar, {active} other(s) written within {args.hours:g} h"
          + (f"; {failed} failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
