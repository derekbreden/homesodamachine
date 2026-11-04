"""Rust fluid-topology document driver with scalar-provider compatibility.

Run: tools/cad-venv/bin/python hardware/topology/_fluid_topology_sync.py [--check]
"""
from dataclasses import asdict, dataclass
from pathlib import Path
import sys

_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools/docgen").is_dir())
for _path in (_repo / "tools", _repo / "hardware/scripts", _repo / "hardware/assembly",
              _repo / "hardware/manifold-layout",
              _repo / "hardware/printed-parts/enclosure/enclosure"):
    sys.path.insert(0, str(_path))
from _enclosure_datums import install
install()
import _facts
import _lines
import _scorecard
import manifold_layout as ml
from _cadq_export import note_read
from _rust_docs import evaluate as _evaluate, update as _update

note_read(_repo / "hardware/manifold-layout/enclosure_assembly.py")
for _source in _facts.sources():
    if Path(_source).suffix in (".py", ".rs", ".json", ".toml", ".lock", ".yaml", ".yml"):
        note_read(_repo / _source)

MANIFOLD = _here / "fluid-topology-manifold.mmd"
LIMBS = _here / "fluid-topology-limbs.mmd"
CARBONATOR = _here / "fluid-topology-carbonator.mmd"
TOPOLOGY = _here / "fluid-topology.md"


def _inputs():
    return {
        "facts_runs": list(_facts.read().runs),
        "segment_recipes": ml.SEGMENTS,
        "mouths": ml.MOUTHS,
        "barb_of": list(ml.BARB_OF),
        "fore_stubs": ml.FORE_STUBS,
        "fore_stub_lengths": {how: ml.fore_stub_length(*ends) for how, ends in ml.FORE_STUBS.items()},
        "lower_links": ml.lower_links(),
        "lower_lengths": {cid: ml.lower_link_length(cid) for cid in ml.LOWER_CONNECTIONS},
        "source_steps": {cid: ml.source_step(row) for cid, row in ml.SBENDS.items()},
        "quarter_length": ml.QUARTER_LEN,
        "runs": ml.RUNS,
        "made_as": _scorecard.MADE_AS,
        "made_up": _scorecard.MADE_UP,
        "stations": ml.P,
        "pumps": list(ml.PUMPS),
        "limbs": ml.LIMBS,
        "valves": list(_lines.VALVES),
        "purchased_tees": list(ml.PURCHASED_TEES),
        "pump_junctions": list(ml.PUMP_JUNCTIONS),
        "lower_connections": ml.LOWER_CONNECTIONS,
        "fore_stub_exposed": ml.FORE_STUB_EXPOSED,
    }


@dataclass
class Seg:
    id: str
    ends: tuple
    made: str
    length: float = None
    corners: int = 0
    developed: float = None
    status: str = "complete"
    missing: tuple = ()

    @property
    def label(self):
        return _evaluate("fluid-topology", {"segment": asdict(self)}, operation="segment_label")["exports"]["label"]


def _values():
    return _evaluate("fluid-topology", _inputs(), operation="values")["exports"]


def _interior(cid, how):
    return tuple(_evaluate("fluid-topology", {**_inputs(), "cid": cid, "how": how}, operation="interior")["exports"]["interior"])


def segments():
    return {name: Seg(**row) for name, row in _values()["segments"].items()}


def owed():
    return {name: tuple(ends) for name, ends in _values()["owed"].items()}


def limb_members():
    return {name: set(members) for name, members in _values()["limb_members"].items()}


def class_members():
    return {name: set(members) for name, members in _values()["class_members"].items()}


def manifold_variables(segs):
    inputs = {**_inputs(), "segments_override": [asdict(seg) for seg in segs.values()]}
    return _evaluate("fluid-topology", inputs, operation="values")["exports"]["manifold_variables"]


def limb_variables():
    return _values()["limb_variables"]


def main():
    if "--check" in sys.argv:
        result = _evaluate("fluid-topology", _inputs(), operation="check")
        print(result["stdout"], end="")
    else:
        result = _update("fluid-topology", _inputs())
    return result["exports"]["status"]


if __name__ == "__main__":
    raise SystemExit(main())
