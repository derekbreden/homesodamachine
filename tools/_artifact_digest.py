"""Content digests reused while a file's complete stat identity is unchanged.

This is read on demand by publication. It starts no watcher and adds no hook.
The cache belongs to the checkout, and an unreadable cache is simply cold.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path


def identity(path: Path) -> list[int]:
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


class Digests:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / ".cache/cad-artifact-digests.json"
        try:
            self.entries = json.loads(self.path.read_text())
            if not isinstance(self.entries, dict):
                self.entries = {}
        except (OSError, ValueError):
            self.entries = {}
        self.dirty = False

    def digest(self, path: Path) -> str:
        key = str(path.relative_to(self.root))
        before = identity(path)
        held = self.entries.get(key)
        if (isinstance(held, list) and len(held) == 2 and held[0] == before
                and isinstance(held[1], str) and len(held[1]) == 64):
            return held[1]
        # A producer can replace an artifact during the read. Only remember a
        # digest read from one stable file; a moving file remains owed next time.
        for _ in range(3):
            h = hashlib.sha256()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1 << 20), b""):
                    h.update(chunk)
            after = identity(path)
            if before == after:
                digest = h.hexdigest()
                self.entries[key] = [after, digest]
                self.dirty = True
                return digest
            before = after
        raise OSError(f"artifact kept changing while hashing: {path}")

    def save(self) -> None:
        if not self.dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".cad-digests-", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(self.entries, stream, separators=(",", ":"))
            os.replace(tmp, self.path)
            self.dirty = False
        finally:
            Path(tmp).unlink(missing_ok=True)


def hashes(root: Path, paths: list[str]) -> dict[str, str]:
    cache = Digests(root)
    result = {rel: cache.digest(root / rel) for rel in paths}
    cache.save()
    return result
