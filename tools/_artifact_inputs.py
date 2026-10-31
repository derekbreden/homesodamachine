"""What each published member was made from, as `tools/bazel/graph.json` records it, and one
digest over those inputs' ids.

This is read on demand by publication. It starts no watcher and adds no hook. It reads the
index off disk.

A member's inputs are what its writers read, less what each of them writes, plus each writer's
own script. An intermediate that git does not hold and the pointer file does not name — the cold
core's handoff mesh, the box's facts — counts as its own writer's inputs.

A tracked input's id is its git blob id: the index's for the tree as committed, the bytes on
disk for what a cut on this disk read. A member the pointer file names is its line there. An
input that is not there is `-`.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent

EXTENDED_FLAGS = 0x4000
DIRECTORY = 0o040000


def _git_dir(root: Path) -> Path:
    """The directory holding this checkout's index: `.git`, or where a linked worktree's
    `.git` file points."""
    dot = root / ".git"
    if dot.is_file():
        text = dot.read_text().strip()
        if text.startswith("gitdir:"):
            return (root / text[len("gitdir:"):].strip()).resolve()
    return dot


def _read_index(data: bytes) -> dict | None:
    """`{path: blob id}` off an index file's bytes, or None for a layout this does not read.

    Versions 2 and 3 only. Version 4 compresses each path against the one before it, a split
    index keeps most entries in a second file, and a sparse index folds directories into one
    entry; each of those goes to git."""
    if data[:4] != b"DIRC" or len(data) < 32:
        return None
    version, count = struct.unpack_from(">II", data, 4)
    if version not in (2, 3):
        return None
    out, pos, end = {}, 12, len(data) - 20
    for _ in range(count):
        mode = struct.unpack_from(">I", data, pos + 24)[0]
        flags = struct.unpack_from(">H", data, pos + 60)[0]
        head = 64 if flags & EXTENDED_FLAGS else 62
        stop = data.index(b"\0", pos + head)
        if stop > end or mode == DIRECTORY:
            return None
        if (flags >> 12) & 3 == 0:
            path = data[pos + head:stop].decode("utf-8", "surrogateescape")
            out[path] = data[pos + 40:pos + 60].hex()
        pos += (head + (stop - pos - head) + 8) & ~7
    while pos + 8 <= end:
        if data[pos:pos + 4] in (b"link", b"sdir"):
            return None
        pos += 8 + struct.unpack_from(">I", data, pos + 4)[0]
    return out


def staged(root: Path) -> dict:
    """`{path: blob id}` for every file the index holds at stage 0."""
    try:
        got = _read_index((_git_dir(root) / "index").read_bytes())
    except (OSError, ValueError, struct.error):
        got = None
    if got is not None:
        return got
    listing = subprocess.run(["git", "-C", str(root), "--no-optional-locks", "ls-files",
                              "--stage", "-z"], capture_output=True)
    out = {}
    for row in listing.stdout.split(b"\0"):
        meta, _tab, path = row.partition(b"\t")
        fields = meta.split()
        if len(fields) == 3 and fields[2] == b"0":
            out[path.decode("utf-8", "surrogateescape")] = fields[1].decode()
    return out


def blob_id(path: Path) -> str:
    """The id git gives the bytes at `path`, or `-` where nothing is."""
    try:
        data = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
    except OSError:
        return "-"
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class Graph:
    """Each declared output's writers, and what each writer reads, off one `graph.json`."""

    def __init__(self, graph: dict):
        sys.path.insert(0, str(_TOOLS / "bazel"))
        import inventory

        self.writers, self.reads = {}, {}
        for gen, seen in inventory._split_generators(graph).items():
            writes = (set(seen.get("writes") or ())
                      | set(inventory.IMPLICIT_SOLIDS.get(gen, ())))
            for path in writes:
                self.writers.setdefault(path, []).append(gen)
            self.reads[gen] = frozenset(
                {path for path in seen.get("reads") or ()
                 if path not in writes and not inventory.build_inert(path)} | {gen})

    @classmethod
    def load(cls, root: Path) -> "Graph":
        return cls(json.loads((root / "tools" / "bazel" / "graph.json").read_text()))

    def inputs(self, rel: str) -> frozenset:
        """What the writers of `rel` read."""
        return frozenset().union(*(self.reads[gen] for gen in self.writers.get(rel, ())))

    def digest(self, rel: str, ident) -> str:
        """One sha256 over the ids of what `rel` was made from.

        `ident(path)` is an input's id, or None for an output nothing else names, whose own
        inputs then count in its place."""
        lines, seen, todo = set(), {rel}, list(self.inputs(rel))
        while todo:
            path = todo.pop()
            if path in seen:
                continue
            seen.add(path)
            got = ident(path)
            if got is None and path in self.writers:
                todo.extend(self.inputs(path))
                continue
            lines.add(f"{path}\t{got or '-'}")
        return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()


def committed(index: dict, lines: dict):
    """Ids for the tree as it is committed: the index's blob ids, then the pointer file's lines."""
    def ident(path):
        if path in index:
            return index[path]
        return lines.get(path)
    return ident


def on_disk(root: Path, index: dict, lines: dict, members: dict, graph: Graph):
    """Ids for what a cut on this disk read: the blob id of each tracked file's bytes here, and
    each member's digest as `members` holds it."""
    held = {}

    def ident(path):
        if path in index:
            if path not in held:
                held[path] = blob_id(root / path)
            return held[path]
        if path in lines or path in members:
            return members.get(path, "-")
        if path in graph.writers:
            return None
        if path not in held:
            held[path] = blob_id(root / path)
        return held[path]
    return ident
