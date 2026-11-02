"""The installation pictures' producer surfaces and illustration props.

Producer meshes keep their normals, face ranges and material colours. Only the
two faucet detail crops pass through the solid kernel, to close their cut ends.
These scene payloads serve pictures; they are not measurement models.
"""
from __future__ import annotations

import json
from pathlib import Path
import struct

import numpy as np

import _mesh_payload
import _rust_part
from _materials import linear


def _read(path):
    raw = Path(path).read_bytes()
    size = struct.unpack_from("<I", raw)[0]
    header = json.loads(raw[4:4 + size])
    data = memoryview(raw)[4 + size:]
    meshes = []
    for item in header["meshes"]:
        mesh = {key: value for key, value in item.items()
                if key not in ("pos", "nrm", "idx", "fac", "uv", "col")}
        for key in ("pos", "nrm", "idx", "fac", "uv", "col"):
            if key in item:
                offset, count = item[key]
                dtype = "<u4" if key in ("idx", "fac") else "<f4"
                mesh[key] = np.frombuffer(data, dtype=dtype, count=count, offset=offset)
        meshes.append(mesh)
    return meshes


def payloads(art, names, work):
    """Stage the requested named scenes beside the existing render job paths."""
    hardware = art.HARDWARE
    held = {}

    def source(path, keep=lambda name: True, *, move=None, color=None, rename=None):
        path = Path(path)
        if path not in held:
            held[path] = _read(path)
        selected = []
        for original in held[path]:
            name = original["name"].split("/")[0]
            if not keep(name):
                continue
            mesh = dict(original)
            if move is not None:
                mesh["pos"] = (mesh["pos"].reshape(-1, 3) + move).ravel()
            if color is not None:
                mesh["color"] = list(linear(color))
            if rename is not None:
                mesh["name"] = rename + original["name"][len(name):]
            selected.append(mesh)
        return selected

    faucet = hardware / "faucet-layout/faucet-assembly.step.mesh"
    crop_names = {"opening", "plate-sideways"} & set(names)
    if crop_names:
        selected = {"westbrass", "flavor_tube_pos_x", "flavor_tube_neg_x",
                    "flavor_umbilical_tube_pos_x", "flavor_umbilical_tube_neg_x",
                    "soda_umbilical_tube", "drain_tube", "display_signal_ribbon",
                    "under_counter_plate"}
        _mesh_payload.write(source(faucet, selected.__contains__), work / "faucet.mesh")

    # These modules supply dimensions and interface stations, not their CAD builders.
    fa = art._cad_art._load_faucet_module() if crop_names else None
    reg = art._load_regulator() if "regulator" in names else None
    colors = {name: list(linear(getattr(art, name))) for name in (
        "STONE", "CABINET", "CORAL", "STEEL", "WHITE_TUBE", "RED_TUBE",
        "BLUE_TUBE", "BLACK_PART", "BLACK_PART_LIT", "CONCENTRATE", "BOTTLE_PET",
        "FILTER_BODY", "FILTER_CAP", "CYLINDER", "CORDSET", "NUT_STEEL", "PLATE_STEEL")}
    numbers = {
        "scenes": list(names), "colors": colors,
        "box": [art.BOX_X0, art.BOX_X1, art.BOX_Y0, art.BOX_Y1],
        "clearances": [art.CLEAR_SIDE, art.CLEAR_BEHIND, art.CYLINDER_LANE],
        "cylinder": [art.CYLINDER_D, art.CYLINDER_H],
        "filter": [art.FILTER_D, art.FILTER_L], "tube_d": art.TUBE_D,
        "bottle": [art.BOTTLE_D, art.BOTTLE_H, art.BOTTLE_NECK_D, art.BOTTLE_NECK_H,
                   art.BOTTLE_TIP, art.BOTTLE_CLEARANCE, *art.FUNNEL_MOUTH, art.FUNNEL_BOUNDS[5]],
        "c13": {"station": [*art.C14_STATION, art.REAR_FACE_Y],
                "slip": art.C13_SLIP, "wall": art.C13_WALL,
                "body": art.C13_BODY_LEN, "nose": art.C13_NOSE_LEN,
                "boot": art.C13_BOOT_LEN, "boot_d": art.C13_BOOT_D,
                "cable_d": art.C13_CABLE_D,
                "mouth": [art._c14.MOUTH_W, art._c14.MOUTH_H, art._c14.MOUTH_TOP_R],
                "blades": art._c14.BLADE_STATIONS,
                "blade_size": [art._c14.BLADE_T, art._c14.BLADE_W]},
    }
    if fa is not None:
        numbers["faucet"] = {"payload": str(work / "faucet.mesh"),
                             "counter": [fa.countertop_bottom_z, fa.countertop_thickness,
                                         fa.countertop_hole_center_y, fa.hole_radius],
                             "shank_length": fa.shank_length,
                             "plate_x": art.PLATE_STANDOFF_X,
                             "washer_t": art.WASHER_T, "nut_h": art.NUT_H}
    if reg is not None:
        numbers["tether"] = {"mouth": reg.outlet()[0], "insert": art.TETHER_IN_MOUTH}
    path = work / "props.json"
    path.write_text(json.dumps(numbers, sort_keys=True) + "\n")
    _rust_part.run("tooling", "install-art-props", path, work)

    plumbing = art.PLUMBING_DIR / "out"
    plumbing_names = {"stop-open": "plumbing-valve-on", "stop-closed": "plumbing-valve-off",
                      "tee-before": "plumbing-pre-tee", "tee-after": "plumbing-tee-installed",
                      "kitchen-hose": "plumbing-valve-on"}
    shown = {}
    for name in names:
        meshes = _read(work / f"{name}.props.mesh")
        if name in ("cabinet-plan", "bottle-in-funnel", "nameplate", "the-back-face", "the-socket"):
            if name == "cabinet-plan":
                keep = lambda body: True
            elif name == "bottle-in-funnel":
                keep = lambda body: body != "funnel-cover"
            else:
                keep = lambda body: body in art.REAR_CHILDREN or body.startswith(art.REAR_RING_PREFIX)
            meshes += source(art.MACHINE_MESH, keep)
        elif name in plumbing_names:
            meshes += source(plumbing / f"{plumbing_names[name]}.step.mesh",
                             lambda body: body != "finished-wall")
        elif name == "kitchen-push":
            meshes += source(art.MODERN_DIR / "out/modern-water-on.step.mesh")
        elif name == "two-tees":
            meshes += source(hardware / "reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh",
                             move=(30., 0., 0.), color=art.BLACK_PART, rename="black-tee")
            # The pre-tee scene holds the same fully open adapter at (45,77,152).
            meshes += source(plumbing / "plumbing-pre-tee.step.mesh",
                             lambda body: body.startswith("tee-"), move=(-57., -77., -182.8))
        elif name == "regulator":
            meshes += source(art.REGULATOR_DIR / "taprite-3741-regulator.step.mesh")
        elif name == "collet-press":
            meshes += source(Path(f"{art.COLLET_PRESS}.mesh"), color=art.PRINTED)
        shown[name] = work / f"{name}.step.mesh"
        _mesh_payload.write(meshes, shown[name])
    return shown
