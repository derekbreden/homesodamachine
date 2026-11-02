"""A producer's display surfaces carried beside its immutable fine model."""

from collections import Counter
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import zipfile

import numpy as np


def surfaces(model):
    """The explicitly bound payload, in the fine model's entry order, or None."""
    from .scene import document
    from .write import model_identity
    from _cadq_export import note_read
    import _mesh_payload

    model = Path(model)
    note_read(model)
    binding = (document(model) or {}).get("presentation")
    if binding is None:
        return None
    path = model.parent / binding["path"]
    note_read(path)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError(f"{model}: bound presentation does not match {path}")
    size, = struct.unpack("<I", raw[:4])
    header = json.loads(raw[4:4 + size])
    if header.get("v") not in _mesh_payload.DECODABLE:
        raise ValueError(f"{path}: unsupported presentation version")
    identities = model_identity(model)
    totals = Counter(name for name, _ in identities)
    ordinals = Counter()
    expected = []
    for name, _ in identities:
        ordinals[name] += 1
        expected.append(name if totals[name] == 1 else f"{name}/{ordinals[name]}")
    if [entry["name"] for entry in header["meshes"]] != expected:
        raise ValueError(f"{path}: presentation identities differ from {model}")
    blob = memoryview(raw)[4 + size:]
    result = []
    for entry in header["meshes"]:
        surface = {"name": entry["name"], "color": entry["color"]}
        for key, dtype in (("pos", "<f4"), ("nrm", "<f4"), ("idx", "<u4"), ("fac", "<u4")):
            offset, count = entry[key]
            surface[key] = np.frombuffer(blob, dtype=dtype, count=count, offset=offset)
        sources = _mesh_payload.aligned_face_sources(entry.get("face_sources"), len(surface["fac"]) // 2)
        if sources is not None:
            surface["face_sources"] = sources
        result.append(surface)
    return result


def carried(surface, matrix):
    """Place display arrays by the same affine map as their fine geometry."""
    matrix = np.asarray(matrix, dtype=float).reshape(3, 4)
    if np.array_equal(matrix, np.eye(3, 4)):
        return surface
    linear, offset = matrix[:, :3], matrix[:, 3]
    result = {**surface,
              "pos": (np.asarray(surface["pos"], float).reshape(-1, 3) @ linear.T + offset).ravel(),
              "nrm": (surface["nrm"] if np.array_equal(linear, np.eye(3)) else
                      (np.asarray(surface["nrm"], float).reshape(-1, 3) @ np.linalg.inv(linear)).ravel())}
    if np.linalg.det(linear) < 0:
        result["idx"] = np.asarray(surface["idx"]).reshape(-1, 3)[:, [0, 2, 1]].ravel()
    return result


def bind(model, payload):
    """Change only the fine archive's document; retain every other ZIP member's bytes."""
    from _cadq_export import note_read, note_write

    model, payload = Path(model), Path(payload)
    note_read(model)
    note_read(payload)
    with payload.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    binding = {"path": os.path.relpath(payload, model.parent), "sha256": digest}
    temporary = model.with_name(f".{model.name}.{os.getpid()}.tmp")
    try:
        with zipfile.ZipFile(model) as archive:
            has_document = "document.npy" in archive.namelist()
            document = (json.loads(np.load(io.BytesIO(archive.read("document.npy")),
                                          allow_pickle=False).tobytes()) if has_document else {})
            if document.get("presentation") == binding:
                return
            document["presentation"] = binding
            encoded = json.dumps(document, separators=(",", ":"), sort_keys=True).encode()
            value = io.BytesIO()
            np.save(value, np.frombuffer(encoded, dtype=np.uint8), allow_pickle=False)
            with zipfile.ZipFile(temporary, "w") as out:
                for info in archive.infolist():
                    held = copy.copy(info)
                    if info.filename == "document.npy":
                        out.writestr(held, value.getvalue())
                    else:
                        with archive.open(info) as source, out.open(held, "w") as destination:
                            shutil.copyfileobj(source, destination, length=1024 * 1024)
                if not has_document:
                    out.writestr(zipfile.ZipInfo("document.npy", (1980, 1, 1, 0, 0, 0)), value.getvalue())
        temporary.replace(model)
    finally:
        temporary.unlink(missing_ok=True)
    note_write(model)


def placed(instances, model):
    """Bind each selected producer surface to an already placed fine archive."""
    from .imports import load_model
    from .write import model_identity, shown_payload, write_payload
    from _payload_rules import LINEAR_DEFLECTION_RATIO

    selected = []
    for instance in instances:
        identity = model_identity(instance["model"])
        shown = surfaces(instance["model"])
        indices = set(instance["indices"]) if "indices" in instance else None
        for index, (name, color) in enumerate(identity):
            if indices is not None and index not in indices:
                continue
            name = instance.get("name", instance.get("prefix", "") + name)
            color = instance.get("color", color)
            surface = shown[index] if shown is not None else None
            if surface is not None and "transform" in instance:
                surface = carried(surface, instance["transform"])
            selected.append((name, color, surface))
    if selected and all(surface is not None for _name, _color, surface in selected):
        fine = model_identity(model)
        tolerance = None
    else:
        fine = load_model(model, snap=False)
        boxes = [solid.BoundingBox() for solid in fine]
        size = [max(getattr(b, axis + "max") for b in boxes) - min(getattr(b, axis + "min") for b in boxes)
                for axis in "xyz"]
        tolerance = sum(size) / 3. * LINEAR_DEFLECTION_RATIO
    totals = Counter(name for name, _, _ in selected)
    ordinals = Counter()
    meshes = []
    for solid, (name, color, surface) in zip(fine, selected, strict=True):
        ordinals[name] += 1
        name = name if totals[name] == 1 else f"{name}/{ordinals[name]}"
        meshes.append({**surface, "name": name, "color": color} if surface is not None
                      else shown_payload(solid, name, color, tolerance))
    payload = Path(model).with_name(Path(model).name.removesuffix(".npz") + ".mesh")
    write_payload(meshes, payload)
    bind(model, payload)
