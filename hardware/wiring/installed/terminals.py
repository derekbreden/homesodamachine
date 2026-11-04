"""Typed attachments supplied by the Rust installed-wiring resolver."""
from pathlib import Path
from .model import Terminal
from ._model_input import Body as ModelBody, Solid as ModelSolid, components
from ._wiring_data import read as _read, body_record, solid_record, scene_record

ROOT = Path(__file__).resolve().parents[3]
HW = ROOT / "hardware"


def bounds(shape):
    lower, upper = _read("terminal_bounds", {"body": body_record(shape)})
    return tuple(lower), tuple(upper)


def solids(shape):
    if isinstance(shape, ModelBody):
        return shape.solids
    if getattr(shape, "model_arrays", None) is not None:
        vertices, triangles, _faces, _records = shape.model_arrays()
        return components(vertices, triangles)
    return shape.Solids()


def volume(shape):
    return shape.volume_mm3 if isinstance(shape, ModelSolid) else shape.Volume()


def centre(shape):
    return tuple(_read("terminal_centre", {"body": body_record(shape)}))


def _turn_matrix(turns):
    return tuple(tuple(row) for row in _read("terminal_turns", {"turns": turns}))


def carbonator_bond_datums(ea):
    return _read("terminal_bond", ea=ea)


class Attachments:
    def __init__(self, scene, ea):
        self._source_scene = scene
        self.ea = ea
        self.frames = {}
        self._apply(_read("terminal_init", {"scene": scene_record(scene)}))

    def _apply(self, state):
        self._state = state
        self.terminals = {name: Terminal(**{**row, "point": tuple(row["point"]), "outward": tuple(row["outward"])})
                          for name, row in state["terminals"].items()}
        self.frame_checks = state["frame_checks"]
        self.parts = state["parts"]
        self.fuse_leads = state["fuse_leads"]
        self.passages = state["passages"]
        self.pcb_reference = state["pcb_reference"]
        self.scene = {name: self._source_scene[source][0]
                      for name, source in state["source_names"].items()}

    def part(self, name):
        key = _read("terminal_part_name", {"state": self._state, "name": name})
        return self.scene[key]

    def put(self, id, part, point, outward, kind, basis, status="modeled", pin=""):
        self._apply(_read("terminal_put", {"state": self._state, "id": id, "part": part,
                   "point": point, "outward": outward, "kind": kind, "basis": basis,
                   "status": status, "pin": pin}))
        return self.terminals[id]

    def station(self, spec):
        return tuple(_read("terminal_station", {"state": self._state, "spec": spec}))

    def frame(self, part, reference, turns=()):
        result = _read("terminal_frame", {"state": self._state, "part": part,
                        "reference": str(reference), "turns": turns}, ea=self.ea)
        self._apply(result["state"])
        def carry(point, axis):
            return tuple(tuple(row) for row in _read("terminal_carry", {"pose": result["pose"],
                                                            "point": point, "axis": axis}))
        self.frames[(part, str(reference), str(turns))] = carry
        return carry

    def resolve(self):
        self._apply(_read("terminal_resolve", {"state": self._state}, ea=self.ea))
        return self.terminals

    def _stage(self, stage):
        self._apply(_read("terminal_stage", {"state": self._state, "stage": stage}, ea=self.ea))

    def board(self): self._stage("board")
    def valves(self): self._stage("valves")
    def wagos(self): self._stage("wagos")
    def power(self): self._stage("power")
    def pump_motors(self): self._stage("pump_motors")
    def sensors(self): self._stage("sensors")
    def boundaries(self): self._stage("boundaries")
    def cable_passages(self): self._stage("cable_passages")

    def record(self):
        return self._state["terminals"]
