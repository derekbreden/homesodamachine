"""The interpreter every CAD action boots, without the visualisation toolkit it never draws with.

`cadquery.occ_impl.shapes` imports `vtkmodules` and `OCP.IVtkOCC` at module level to serve one
method — `Shape.toVtkPolyData`, which puts a solid on a VTK pipeline for an interactive viewer.
Nothing in this tree calls it. The triangles this repo does want come from `OCP.BRepMesh`
through `_meshes._tessellate`, and the pictures come from a browser reading those triangles.

WHAT THAT IMPORT COSTS IS NOT THE POINT AT WHICH IT IS PAID. One action pays 12 s of the 15 s
`import cadquery` takes and carries 145 MB it never reads; a whole-graph build is 85 such
actions on 8 cores, so the toolkit is loaded 85 times and stands 8 deep in RAM at once. On an
8 GB box that is the difference between a build that runs and a build that swaps.

Blocking it is a meta-path finder rather than a `sys.modules` stub, because the names arrive as
a PACKAGE — `from vtkmodules.vtkIOXML import ...` walks `vtkmodules.__path__`, and a plain
module object handed back for a package fails inside the import machinery instead of at the
name. The finder answers for the whole subtree and hands back a module whose every attribute is
a fresh class, which is enough for the `from X import Y` lines cadquery runs at import time and
would raise on any real use — so a caller that does reach for VTK is told, rather than served a
silent stand-in.

`site` imports this file at interpreter startup from anywhere on `sys.path`, before any script
runs, which is the only place a shim can sit when 95 files reach for `cadquery` themselves.
"""

import importlib.abc
import importlib.machinery
import sys
import types

_BLOCKED = frozenset({"OCP.IVtkOCC", "OCP.IVtkVTK"})
_BLOCKED_ROOTS = frozenset({"vtk", "vtkmodules"})


class _Absent(types.ModuleType):
    __path__: list = []

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return type(name, (), {})


class _NoVtk(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in _BLOCKED or fullname.split(".")[0] in _BLOCKED_ROOTS:
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        return _Absent(spec.name)

    def exec_module(self, module):
        pass


if not sys.modules.get("vtkmodules"):
    sys.meta_path.insert(0, _NoVtk())
