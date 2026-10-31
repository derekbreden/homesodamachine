"""The mesh kernel: CadQuery's API over Manifold meshes.

A generator runs unchanged on meshes when `activate()` runs before anything imports
cadquery:

    tools/cad-venv/bin/python hardware/scripts/meshcad/run.py <generator.py> [args]

`activate()` imports CadQuery's own shapes module ahead of its package, puts the mesh solids
under its Solid/Compound builders (`solids.install`), then lets the package import the rest:
Workplane, selectors and Sketch are CadQuery's own code, running on meshes. `importStep`
answers with a mesh (`imports.import_step`).

`cadquery.MESH` is True in such a process; `mesh_mode()` asks it.
"""

import importlib.util
import sys
from pathlib import Path


def mesh_mode():
    cq = sys.modules.get("cadquery")
    return bool(getattr(cq, "MESH", False))


def activate():
    """Import cadquery with the mesh kernel in place. Idempotent."""
    cq = sys.modules.get("cadquery")
    if cq is not None:
        if getattr(cq, "MESH", False):
            return cq
        raise RuntimeError("meshcad: cadquery was imported before the mesh kernel could take its place")
    spec = importlib.util.find_spec("cadquery")
    real = Path(spec.origin).parent
    spec = importlib.util.spec_from_file_location(
        "cadquery", real / "__init__.py", submodule_search_locations=[str(real)])
    cq = importlib.util.module_from_spec(spec)
    cq.MESH = True
    sys.modules["cadquery"] = cq
    try:
        import cadquery.occ_impl.shapes  # noqa: F401  CadQuery's classes, before its package binds them
        from . import solids
        solids.install()
        spec.loader.exec_module(cq)
        from . import imports
        imports.install(cq)
    except BaseException:
        sys.modules.pop("cadquery", None)
        raise
    return cq


def is_mesh(shape):
    """Whether `shape` (a shape or a Workplane) is held by the mesh kernel."""
    solids = sys.modules.get(__name__ + ".solids")
    if solids is None:
        return False
    if hasattr(shape, "vals"):
        return any(isinstance(v, solids.MeshShape) for v in shape.vals())
    return isinstance(shape, solids.MeshShape)


def arrays(shape):
    """(vertices, triangles) of a mesh shape's solids, side by side, as the kernel holds them."""
    import numpy as np
    from .write import _solids, _triangles
    V, T, base = [], [], 0
    for s in _solids(shape):
        v, t = _triangles(s)
        V.append(v)
        T.append(t + base)
        base += len(v)
    return np.concatenate(V), np.concatenate(T)


def manifold(shape):
    """One Manifold holding a mesh shape's solids, side by side, without a boolean."""
    import manifold3d as m3d
    from .solids import _meshes
    ms = _meshes(shape)
    return ms[0] if len(ms) == 1 else m3d.Manifold.compose(ms)


def model_bytes(shape):
    """A mesh shape as model-file bytes (`write.write_model`), face records and all."""
    from .write import _solids, model_bytes as _bytes
    return _bytes(_solids(shape))


def from_model(data):
    """The shape `model_bytes` wrote: one solid, or a compound of several."""
    from .imports import load_model
    from .solids import MeshCompound
    solids = load_model(data)
    return solids[0] if len(solids) == 1 else MeshCompound(solids)


def writer():
    """The kernel's file writers (`write`)."""
    from . import write
    return write


def toolchain():
    """The mesh kernel and the Manifold under it, named for a cache key: the kernel by the text
    of its own files, since any edit to them can move a triangle."""
    import hashlib
    from importlib.metadata import version
    h = hashlib.blake2b(digest_size=8)
    for f in sorted(Path(__file__).parent.glob("*.py")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return f"meshcad=={h.hexdigest()} manifold3d=={version('manifold3d')}"


def offset(shape, distance):
    """Every point within `distance` of the solid, joined round (`grow.offset`)."""
    from . import grow
    return grow.offset(shape, distance)


def prism(faces, vector):
    """The solid `faces` sweep along `vector`, as BRepPrimAPI_MakePrism sweeps a compound of
    them (`sweep.prism`)."""
    from . import sweep
    return sweep.prism(faces, vector)
