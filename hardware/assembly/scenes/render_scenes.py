"""Named scene composition and viewer exports through Rust."""
from pathlib import Path
import sys

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
sys.path[:0] = [str(_ROOT), str(_HW / "scripts"), str(_HERE.parent)]
import _scenes
from hardware.wiring.installed._wiring_data import read as _read

GLB_DIR = _HERE.parent / "glb"
ASSEMBLY_MESH = _HW / "manifold-layout/enclosure-assembly.step.mesh"
CORE_MESH = _HW / "cold-core-layout/cold-core-assembly.step.mesh"


def numeric_spec(assembly):
    return _read("scene_numeric_spec", {"assembly": assembly})


def write_reference_glbs(assembly, output=GLB_DIR):
    import _machine_export
    spec = assembly if "views" in assembly else numeric_spec(assembly)
    output = Path(output)
    _machine_export.views(spec, output)
    return [Path(row["file"]) if "file" in row else output / (row["id"] + ".glb") for row in spec["views"]]


def write_glbs(assembly, require_core_payload=False):
    return write_reference_glbs(assembly)
