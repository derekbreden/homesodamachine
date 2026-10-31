"""Content digests and directory listings, each reused while its complete stat identity is
unchanged.

This is read on demand by publication. It starts no watcher and adds no hook.
The caches belong to the checkout, and an unreadable cache is simply cold.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

# A directory's stamp moves on the clock's tick, and an entry added within the tick of the last
# one leaves it where it was. A listing is kept only once its directory has been still this long.
SETTLED_NS = 2_000_000_000


def identity(path) -> list[int]:
    s = os.stat(path)
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def _load(path: Path) -> dict:
    try:
        entries = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return entries if isinstance(entries, dict) else {}


def _save(path: Path, entries: dict) -> None:
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.stem}-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(entries, stream, separators=(",", ":"))
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


class Digests:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / ".cache/cad-artifact-digests.json"
        self.entries = _load(self.path)
        self.dirty = False

    def digest(self, rel: str) -> str:
        path = f"{self.root}/{rel}"
        before = identity(path)
        held = self.entries.get(rel)
        if (isinstance(held, list) and len(held) == 2 and held[0] == before
                and isinstance(held[1], str) and len(held[1]) == 64):
            return held[1]
        # A producer can replace an artifact during the read. Only remember a
        # digest read from one stable file; a moving file remains owed next time.
        for _ in range(3):
            h = hashlib.sha256()
            with Path(path).open("rb") as source:
                for chunk in iter(lambda: source.read(1 << 20), b""):
                    h.update(chunk)
            after = identity(path)
            if before == after:
                digest = h.hexdigest()
                self.entries[rel] = [after, digest]
                self.dirty = True
                return digest
            before = after
        raise OSError(f"artifact kept changing while hashing: {path}")

    def save(self) -> None:
        if self.dirty:
            _save(self.path, self.entries)
            self.dirty = False


class Listings:
    """What each directory under the checkout holds, by repo-relative path."""

    def __init__(self, root: Path):
        self.root = root
        self.path = root / ".cache/cad-artifact-listings.json"
        self.entries = _load(self.path)
        self.read = set()
        self.dirty = False

    def listing(self, rel: str) -> tuple[list, list] | None:
        """The names of the directories and of the regular files directly in `rel`, links
        followed for neither, or None where `rel` cannot be read."""
        path = f"{self.root}/{rel}"
        try:
            before = identity(path)
            held = self.entries.get(rel)
            if isinstance(held, list) and len(held) == 3 and held[0] == before:
                self.read.add(rel)
                return held[1], held[2]
            dirs, files = [], []
            with os.scandir(path) as listing:
                for entry in listing:
                    if entry.is_dir(follow_symlinks=False):
                        dirs.append(entry.name)
                    elif entry.is_file(follow_symlinks=False):
                        files.append(entry.name)
            after = identity(path)
        except OSError:
            return None
        if before == after and time.time_ns() - after[4] > SETTLED_NS:
            self.entries[rel] = [after, dirs, files]
            self.read.add(rel)
            self.dirty = True
        return dirs, files

    def save(self) -> None:
        """Write what this pass read, and nothing it did not reach."""
        if self.dirty or self.read != set(self.entries):
            _save(self.path, {rel: self.entries[rel] for rel in self.read})
            self.dirty = False


def hashes(root: Path, paths: list[str]) -> dict[str, str]:
    cache = Digests(root)
    result = {rel: cache.digest(rel) for rel in paths}
    cache.save()
    return result
