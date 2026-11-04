"""Scene records and fastening-based membership from the Rust composer."""
from collections import namedtuple
from pathlib import Path
import sys

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
sys.path.insert(0, str(_ROOT))
from hardware.wiring.installed._wiring_data import read as _read, plain

Scene = namedtuple("Scene", "id title roots inner flip also later cam up zoom look note without", defaults=(None,))
_definitions = _read("scene_definitions")
for _key, _value in _definitions.items():
    if _key == "SCENES":
        continue
    globals()[_key] = frozenset(_value) if _key == "BARE" else tuple(_value) if isinstance(_value, list) else _value


def _scene(row):
    data = dict(row)
    for key in ("roots", "also", "later", "cam", "up"):
        data[key] = tuple(data[key])
    if isinstance(data["inner"], list):
        data["inner"] = tuple(data["inner"])
    if data["flip"] is not None:
        data["flip"] = tuple(data["flip"])
    return Scene(**data)


SCENES = tuple(_scene(row) for row in _definitions["SCENES"])
SCENE_BY_ID = {scene.id: scene for scene in SCENES}
_COLD_CARD = _HW / "cold-core-layout/cold-core-assembly.scorecard.json"


def back_top_carried_names(): return frozenset(_read("scene_back_carried"))
def core_names(): return tuple(_read("scene_core_names"))
def inner_of(scene): return tuple(_read("scene_inner", {"scene": scene}))
def crossings(runs): return _read("scene_crossings", {"runs": runs})


def holders(assembly=None):
    return _read("scene_holders", {"tube_sites": getattr(assembly, "tube_anchor_sites", ())}, assembly=assembly)


def held_by(root, holder_map, stop=()):
    return set(_read("scene_held_by", {"root": root, "holders": holder_map, "stop": stop}))


def runs_for(bodies, runs, holder_map):
    return set(_read("scene_runs_for", {"bodies": bodies, "runs": runs, "holders": holder_map}))


def named(scene, runs, assembly=None):
    return _read("scene_named", {"scene": scene, "runs": runs,
                                "tube_sites": getattr(assembly, "tube_anchor_sites", ()),
                                "core_external_components": getattr(assembly, "core_external_components", ())}, assembly=assembly)
