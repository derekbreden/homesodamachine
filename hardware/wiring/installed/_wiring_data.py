"""Type and raw-provider transport for the Rust installed-wiring programs."""
from dataclasses import asdict
import importlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "hardware/scripts"), str(ROOT / "hardware/manifold-layout"),
               str(ROOT / "hardware/cold-core-layout"), str(ROOT / "hardware/printed-parts/cold-core"),
               str(ROOT / "hardware/printed-parts/enclosure/enclosure"), str(ROOT / "tools")]
import _rust_part
from _rust_data import request
from _rust_objects import NativeProxy


def _class_has(value, name):
    return any(name in vars(cls) for cls in type(value).__mro__)


def plain(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, NativeProxy) and value._tag["$native"]["kind"] in ("dict", "list", "tuple", "set"):
        return plain(value._invoke("snapshot"))
    if _class_has(value, "__dataclass_fields__"):
        return plain(asdict(value))
    if _class_has(value, "_asdict"):
        return plain(value._asdict())
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [plain(item) for item in value]
    if _class_has(value, "tolist"):
        return plain(value.tolist())
    if _class_has(value, "toTuple"):
        row = value.toTuple()
        if len(row) == 4:
            from _materials import linear
            return {"$linear": linear(value)}
        return plain(row)
    raise TypeError(f"{type(value).__name__} is not a raw wiring provider value")


def body_record(body):
    if _class_has(body, "__dataclass_fields__"):
        return plain(body)
    if hasattr(body, "model_arrays"):
        from ._model_input import components
        vertices, triangles, _faces, _records = body.model_arrays()
        return {"solids": plain(components(vertices, triangles))}
    # A manual caller may hand over a native model as its measurement provider.
    return {"solids": [solid_record(solid) for solid in body.Solids()]}


def solid_record(solid):
    if _class_has(solid, "__dataclass_fields__"):
        return plain(solid)
    box = solid.BoundingBox()
    return {"lower": [box.xmin, box.ymin, box.zmin],
            "upper": [box.xmax, box.ymax, box.zmax], "volume_mm3": solid.Volume()}


def scene_record(scene):
    return {name: body_record(row[0]) for name, row in scene.items()}


def provider(ea=None, assembly=None):
    def provide(query):
        kind = query["kind"]
        if kind == "get":
            value = ea if query["base"] == "ea" else importlib.import_module(query["base"])
            for name in query["path"].split("."):
                value = getattr(value, name)
            if "args" in query:
                value = value(*query["args"], **query.get("kwargs", {}))
            return plain(value)
        if kind == "reference_bounds":
            from ._model_input import reference_bounds
            return plain(reference_bounds(Path(query["path"]), query["rotation"]))
        if kind == "valve_reference":
            return str(getattr(ea.ml, "VALVE_STEP", ROOT / "hardware/reference/beduan-solenoid/beduan-solenoid.step"))
        if kind == "fixed_wiring_passages":
            import _box_spec
            enc = ea._enc
            box, _bounds = _box_spec.read(enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate),
                                          path=ROOT / "hardware/manifold-layout/enclosure-box.json")
            return plain(enc._fixed_pump_mount.wiring_passages(enc, box))
        if kind == "measure":
            import _assembly_model
            return plain(_assembly_model.measure(query["instances"], query.get("queries", []),
                                                  component_names=query.get("component_names", [])))
        if kind == "step":
            return _rust_part.step(Path(query["path"]))
        if kind == "cut":
            return _rust_part.cut(query["crate"], query["name"], query["numbers"], Path(query["output"]),
                                   numbers_name=query["numbers_name"])
        if kind == "append_wiring":
            import _machine_export
            return _machine_export.append_wiring(query["host"], query["wire_step"],
                                                 wire_model=query.get("wire_model"))
        if kind == "module_files":
            from ._model_input import QUERY_SOURCES
            return [*[str(module.__file__) for module in tuple(sys.modules.values())
                       if getattr(module, "__file__", None) and str(module.__file__).endswith(".py")],
                    *map(str, QUERY_SOURCES)]
        if kind == "compiled_sources":
            return list(_rust_part._READ_TARGETS)
        if kind == "code_digest":
            from _realized import code_digest
            return code_digest(Path(query["path"]))
        if kind == "scene_inputs":
            import _scorecard
            import enclosure_assembly
            import _cold_core_interface
            import manifold_layout
            import above_core
            return plain({"mounts": _scorecard.mounts(assembly), "rides": _scorecard.RIDES,
                          "cap_anchors": _cold_core_interface.cap_anchors,
                          "tube_anchor_sites": enclosure_assembly.TUBE_ANCHOR_SITES,
                          "equipment": above_core.core_equipment_names(),
                          "manifold": {"pumps": manifold_layout.PUMPS, "segments": manifold_layout.SEGMENTS,
                                       "barb_of": manifold_layout.BARB_OF, "fore_stubs": manifold_layout.FORE_STUBS,
                                       "lower_ids": list(manifold_layout.lower_links())}})
        raise ValueError(f"Unknown raw wiring provider {kind}")
    return provide


def read(op, data=None, *, ea=None, assembly=None, callback=None):
    for name in ("connector-map.json", "bundle-routes.json", "route-overrides.json"):
        _rust_part._READ_TARGETS.add("hardware/wiring/installed/" + name)
    return request("assembly-docs", "wiring-data", {"root": str(ROOT), "op": op, "data": plain(data or {})},
                   callback=callback or provider(ea, assembly))
