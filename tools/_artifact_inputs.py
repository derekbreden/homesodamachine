"""Python object types for native published-member input and Git identities."""
from pathlib import Path
import json
import sys

_TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(_TOOLS.parent / "hardware/scripts"))
from _build_data import request

EXTENDED_FLAGS = 0x4000
DIRECTORY = 0o040000


def _git_dir(root: Path) -> Path:
    return Path(request("artifact-git-dir", root=str(root)))


def _read_index(data: bytes) -> dict | None:
    return request("artifact-index", bytes=list(data))


def staged(root: Path) -> dict:
    return request("artifact-staged", root=str(root))


def blob_id(path: Path) -> str:
    return request("artifact-blob", path=str(path))


class Graph:
    def __init__(self, graph: dict):
        sys.path.insert(0, str(_TOOLS / "bazel"))
        import inventory
        record = request("artifact-graph", graph=graph, config=dict(
            generator_order=list(graph), implicit_solids=inventory.IMPLICIT_SOLIDS, inert_suffixes=inventory.BUILD_INERT_SUFFIXES,
            inert_basenames=list(inventory.BUILD_INERT_BASENAMES)))
        self.writers = record["writers"]
        self.reads = {name: frozenset(paths) for name, paths in record["reads"].items()}

    @classmethod
    def load(cls, root: Path) -> "Graph":
        return cls(json.loads((root / "tools/bazel/graph.json").read_text()))

    def _wire(self):
        return dict(writers=self.writers, reads={name: list(paths) for name, paths in self.reads.items()})

    def inputs(self, rel: str) -> frozenset:
        return frozenset(request("artifact-inputs", graph=self._wire(), path=rel))

    def digest(self, rel: str, ident) -> str:
        if isinstance(ident, _Identity):
            return request("artifact-digest", graph=self._wire(), path=rel, identity=ident.spec, id=ident.id)
        return request("artifact-digest", graph=self._wire(), path=rel,
                       callback=lambda query: ident(query["path"]))


class _Identity:
    def __init__(self, spec, graph=None):
        self.spec, self.graph = spec, graph
        self.id = request("artifact-identity-id")

    def __call__(self, path):
        return request("artifact-ident", path=path, identity=self.spec, id=self.id,
                       writers=self.graph.writers if self.graph is not None else {})


def committed(index: dict, lines: dict):
    return _Identity(dict(kind="committed", index=index, lines=lines))


def on_disk(root: Path, index: dict, lines: dict, members: dict, graph: Graph):
    return _Identity(dict(kind="on_disk", root=str(root), index=index, lines=lines, members=members), graph)
