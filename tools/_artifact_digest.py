"""Python cache object interfaces for native artifact hashes and listings."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hardware/scripts"))
from _build_data import request

SETTLED_NS = 2_000_000_000


def _io(op, **fields):
    try:
        return request(op, **fields)
    except ValueError as error:
        raise OSError(str(error)) from error


def identity(path) -> list[int]:
    return _io("artifact-stat", path=str(path))


def _load(path: Path) -> dict:
    return request("artifact-cache-load", path=str(path))


def _save(path: Path, entries: dict) -> None:
    _io("artifact-cache-save-file", path=str(path), entries=entries)


class Digests:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / ".cache/cad-artifact-digests.json"
        self._id = request("artifact-cache-new", root=str(root), listings=False)

    @property
    def entries(self):
        return request("artifact-cache-get", id=self._id)["entries"]

    @property
    def dirty(self):
        return request("artifact-cache-get", id=self._id)["dirty"]

    def digest(self, rel: str) -> str:
        return _io("artifact-cache-digest", id=self._id, path=rel)

    def save(self) -> None:
        _io("artifact-cache-save", id=self._id)


class Listings:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / ".cache/cad-artifact-listings.json"
        self._id = request("artifact-cache-new", root=str(root), listings=True)

    @property
    def entries(self):
        return request("artifact-cache-get", id=self._id)["entries"]

    @property
    def dirty(self):
        return request("artifact-cache-get", id=self._id)["dirty"]

    @property
    def read(self):
        return set(request("artifact-cache-get", id=self._id)["read"])

    def listing(self, rel: str) -> tuple[list, list] | None:
        result = request("artifact-cache-listing", id=self._id, path=rel)
        return tuple(result) if result is not None else None

    def save(self) -> None:
        _io("artifact-cache-save", id=self._id)


def hashes(root: Path, paths: list[str]) -> dict[str, str]:
    return _io("artifact-hashes", root=str(root), paths=list(paths))
