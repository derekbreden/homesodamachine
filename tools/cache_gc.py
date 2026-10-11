#!/usr/bin/env python3
"""Delete scratch in the repository's .cache once it has gone untouched.

A unit is a top-level entry of .cache, or one job inside .cache/prints or
.cache/printer-control. Its age is the newest write of any file in it,
ignoring .DS_Store, which Finder writes into every folder it browses. Units
idle longer than --days are removed. The memo caches the build reads (meshes,
boxes, realized) and the printer tools' virtualenv are never removed.

The default dry run lists what would go; --apply deletes it. The private
six-hour launchd runner described in h2c-timelapse-gc.md runs it with --apply.
Requires only the Python standard library.
"""

import argparse
import os
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CONTAINERS = {"prints", "printer-control"}
KEEP = {"meshes", "boxes", "realized", "printer-control/venv"}


def newest_write(path):
    """Newest mtime under path, ignoring .DS_Store, and the bytes it holds."""
    if path.is_symlink() or not path.is_dir():
        st = path.lstat()
        return (0.0 if path.name == ".DS_Store" else st.st_mtime), st.st_size
    newest, size = 0.0, 0
    for dirpath, _, files in os.walk(path):
        for name in files:
            try:
                st = os.lstat(os.path.join(dirpath, name))
            except OSError:
                continue
            size += st.st_size
            if name != ".DS_Store":
                newest = max(newest, st.st_mtime)
    return newest, size


def units(cache):
    for entry in sorted(cache.iterdir()):
        if entry.name == ".DS_Store" or entry.name in KEEP:
            continue
        if entry.name in CONTAINERS and entry.is_dir() and not entry.is_symlink():
            for child in sorted(entry.iterdir()):
                rel = f"{entry.name}/{child.name}"
                if child.name != ".DS_Store" and rel not in KEEP:
                    yield rel, child
        else:
            yield entry.name, entry


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache", type=Path, default=ROOT / ".cache",
                   help="cache directory (default: the repository's .cache)")
    p.add_argument("--days", type=float, default=3.0,
                   help="remove units idle longer than this many days (default: 3)")
    p.add_argument("--apply", action="store_true",
                   help="delete; without it, only list")
    args = p.parse_args()

    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if not args.cache.is_dir():
        print(f"{stamp} :: {args.cache} does not exist")
        return 0
    cutoff = time.time() - args.days * 86400
    removed = kept = failed = 0
    freed = 0
    for rel, path in units(args.cache):
        newest, size = newest_write(path)
        if newest >= cutoff:
            kept += 1
            continue
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(newest)) if newest else "never"
        if args.apply:
            try:
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            except OSError as e:
                print(f"  failed        {when}  {size / 1e6:9.1f} MB  {rel}: {e}")
                failed += 1
                continue
        print(f"  {'deleted' if args.apply else 'would delete'}  {when}  {size / 1e6:9.1f} MB  {rel}")
        removed += 1
        freed += size
    verb = "freed" if args.apply else "would free"
    print(f"{stamp} :: .cache {verb} {freed / 1e9:.2f} GB in {removed} unit(s); "
          f"{kept} kept" + (f"; {failed} failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
