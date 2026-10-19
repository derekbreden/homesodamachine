"""Print features read from a piece's mesh in its print frame.

Each declared feature names a selection of faces by orientation and by its place
on the part's own bounds. The values a project needs — layer bands, painted
facets, ribbon and fin volumes, review windows — come from the faces found. A
feature whose faces are missing, or whose measured extent leaves its declared
range, raises `FeatureMissing` with what was found.
"""
from __future__ import annotations

import math

import numpy as np

from _mesh import CHAMFER_NZ, box_mesh, component_labels, normals_areas

FIRST_LAYER = 0.20
LAYER = 0.24
RISE_PER_RADIUS = 1.0 - 0.5 / math.sqrt(1.25)   # chamfer rise / R, cadlib/overhang_round.transition
ARC_PER_RADIUS = 0.5 / math.sqrt(1.25)          # retained arc above the chamfer / R


class FeatureMissing(ValueError):
    pass


class Geometry:
    def __init__(self, triangles: np.ndarray, faces: np.ndarray):
        self.t = triangles
        self.faces = faces
        self.n, self.a = normals_areas(triangles)
        self.c = triangles.mean(axis=1)
        self.zlo = triangles[:, :, 2].min(axis=1)
        self.zhi = triangles[:, :, 2].max(axis=1)
        flat = triangles.reshape(-1, 3)
        self.low, self.high = flat.min(axis=0), flat.max(axis=0)

    def select(self, spec: dict) -> np.ndarray:
        n, c, mask = self.n, self.c, np.ones(len(self.t), bool)
        if "normal_z" in spec:
            low, high = spec["normal_z"]
            mask &= (n[:, 2] >= low) & (n[:, 2] <= high)
        for axis, key in ((0, "x"), (1, "y")):
            if f"abs_normal_{key}_max" in spec:
                mask &= np.abs(n[:, axis]) <= spec[f"abs_normal_{key}_max"]
            if f"normal_{key}_min" in spec:
                mask &= n[:, axis] >= spec[f"normal_{key}_min"]
            if f"normal_{key}_max" in spec:
                mask &= n[:, axis] <= spec[f"normal_{key}_max"]
        if "top_mm" in spec:
            mask &= c[:, 2] >= self.high[2] - spec["top_mm"]
        if "bottom_mm" in spec:
            mask &= c[:, 2] <= self.low[2] + spec["bottom_mm"]
        side_x = np.minimum(c[:, 0] - self.low[0], self.high[0] - c[:, 0])
        side_y = np.minimum(c[:, 1] - self.low[1], self.high[1] - c[:, 1])
        if "exterior_x_mm" in spec:
            mask &= side_x <= spec["exterior_x_mm"]
        if "exterior_y_mm" in spec:
            mask &= side_y <= spec["exterior_y_mm"]
        if "half" in spec:
            middle = (self.low[2] + self.high[2]) / 2.0
            mask &= (c[:, 2] < middle) if spec["half"] == "lower" else (c[:, 2] >= middle)
        return mask

    def components(self, mask: np.ndarray) -> list[np.ndarray]:
        index = np.flatnonzero(mask)
        if not len(index):
            return []
        labels = component_labels(self.faces[index])
        return [index[labels == label] for label in np.unique(labels)]


def _check(feature: dict, name: str, value: float, key: str):
    bounds = feature.get("expect", {}).get(key)
    if bounds is not None and not (bounds[0] <= value <= bounds[1]):
        raise FeatureMissing(f"{feature['name']}: {name} {value:.3f} is outside the declared {bounds}")


def _record(geo: Geometry, faces: np.ndarray) -> dict:
    points = geo.t[faces].reshape(-1, 3)
    return {"faces": int(len(faces)), "area_mm2": round(float(geo.a[faces].sum()), 3),
            "bounds_print_mm": [points.min(axis=0).round(3).tolist(), points.max(axis=0).round(3).tolist()]}


def fine_band(geo: Geometry, feature: dict) -> dict:
    """An inward/top show round: its complete print-Z span takes the fine layer height."""
    kept, records = [], []
    for members in geo.components(geo.select(feature["select"])):
        if geo.a[members].sum() < feature.get("min_component_area_mm2", 10.0):
            continue
        if geo.n[members, 2].max() < feature.get("rolls_to_normal_z", 0.0):
            continue
        kept.append(members)
        records.append(_record(geo, members))
    if not kept:
        raise FeatureMissing(f"{feature['name']}: no faces match {feature['select']}")
    faces = np.concatenate(kept)
    low, high = float(geo.zlo[faces].min()), float(geo.zhi[faces].max())
    _check(feature, "span height", high - low, "span_mm")
    _check(feature, "component count", len(kept), "components")
    _check(feature, "area", float(geo.a[faces].sum()), "area_mm2")
    return {"name": feature["name"], "kind": "fine_band", "span_print_z_mm": [low, high],
            "layer_height_mm": feature.get("layer_height_mm", 0.08), "components": records,
            "paint_faces": faces, "reason": feature["reason"]}


def transition_band(geo: Geometry, feature: dict) -> dict:
    """An expanding print-down round with its additive chamfer: six walls through its rise."""
    zone = geo.select(feature["select"])
    tolerance = feature.get("chamfer_normal_tolerance", 0.003)
    chamfer = zone & (np.abs(geo.n[:, 2] - CHAMFER_NZ) < tolerance)
    area = float(geo.a[chamfer].sum())
    if not chamfer.any():
        raise FeatureMissing(f"{feature['name']}: no 0.5:1 chamfer faces in {feature['select']}")
    _check(feature, "chamfer area", area, "chamfer_area_mm2")
    # The foot is the flat face the straight runs start from: the most chamfer area starts there.
    feet = np.round(geo.zlo[chamfer], 2)
    values, inverse = np.unique(feet, return_inverse=True)
    foot = float(values[np.argmax(np.bincount(inverse, weights=geo.a[chamfer]))])
    significant = chamfer & (geo.a >= 0.05)
    top = float(geo.zhi[significant].max())
    radius = feature["radius_mm"]
    measured = (top - foot) / RISE_PER_RADIUS
    if abs(measured / radius - 1.0) > feature.get("radius_tolerance", 0.1):
        raise FeatureMissing(f"{feature['name']}: the chamfer rises {top - foot:.3f} mm above its foot at "
                             f"print Z{foot:.3f}, an R{measured:.2f} transition against the declared R{radius:g}")
    low = float(geo.zlo[significant].min())
    high = top + ARC_PER_RADIUS * radius
    paint = zone & (geo.n[:, 2] < -0.02) & (geo.n[:, 2] > -0.999) & (geo.zhi >= low - 0.01) & (geo.zlo <= high + 0.01)
    return {"name": feature["name"], "kind": "transition_band", "span_print_z_mm": [low, high],
            "foot_print_z_mm": foot, "radius_mm": radius, "chamfer_area_mm2": area,
            "wall_loops": feature.get("wall_loops", 6), "paint_faces": np.flatnonzero(paint),
            "painted": _record(geo, np.flatnonzero(paint)), "reason": feature["reason"]}


def ceiling_inset(geo: Geometry, feature: dict, foot_z: float) -> dict:
    """The flat lifting ceiling at a transition's foot keeps tree contacts off its boundary strip."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    zone = geo.select(feature["select"])
    flat = zone & (geo.n[:, 2] < -0.999) & (np.abs(geo.c[:, 2] - foot_z) < 0.01)
    if not flat.any():
        raise FeatureMissing(f"{feature['name']}: no flat ceiling at print Z{foot_z:.3f}")
    region = unary_union([Polygon(p[:, :2]) for p in geo.t[flat]])
    _check(feature, "ceiling area", region.area, "area_mm2")
    permitted = region.buffer(-feature["inset_mm"])
    blocked = 0.0
    codes = {}

    def encode(points, depth=0):
        nonlocal blocked
        polygon = Polygon(points[:, :2])
        if permitted.covers(polygon):
            return "0"
        if not permitted.intersects(polygon) or depth == feature.get("paint_depth", 7):
            blocked += polygon.area
            return "8"
        a, b, c = points
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        return "".join(encode(np.array(q), depth + 1)
                       for q in ((a, ab, ca), (ab, b, bc), (bc, c, ca), (ab, bc, ca))) + "3"

    for index in np.flatnonzero(flat):
        code = encode(geo.t[index])
        if code != "0":
            codes[int(index)] = code
    return {"name": feature["name"], "kind": "ceiling_inset", "ceiling_print_z_mm": foot_z,
            "ceiling_area_mm2": float(region.area), "inset_mm": feature["inset_mm"],
            "blocked_area_mm2": blocked, "paint_codes": codes, "region": region,
            "reason": feature["reason"]}


def layer_index_below(z: float) -> int:
    """The last layer whose slicing plane lies below z (layers 1..; first 0.20, then 0.24)."""
    return int(math.floor((z - FIRST_LAYER + LAYER / 2) / LAYER))


def layer_mid(index: int) -> float:
    return FIRST_LAYER + LAYER * index - LAYER / 2 if index > 0 else FIRST_LAYER / 2


def groove_ribbons(geo: Geometry, feature: dict) -> dict:
    """Removable model ribbons standing in each sliding groove under its broad caught face."""
    zone = geo.select(feature["select"])
    catches = []
    for members in geo.components(zone & (geo.n[:, 2] < -0.999)):
        points = geo.t[members].reshape(-1, 3)
        low, high = points.min(axis=0), points.max(axis=0)
        size = high[:2] - low[:2]
        long_side, short_side = float(size.max()), float(size.min())
        if long_side < feature["min_length_mm"] or not (feature["width_mm"][0] <= short_side <= feature["width_mm"][1]):
            continue
        if geo.a[members].sum() < 0.85 * size[0] * size[1]:
            continue
        catches.append((members, low, high))
    _check(feature, "groove count", len(catches), "count")
    if not catches:
        raise FeatureMissing(f"{feature['name']}: no caught faces match {feature['select']}")
    up = np.flatnonzero(geo.n[:, 2] > 0.999)
    ribbons = []
    gap = feature.get("side_clearance_mm", 0.40)
    for number, (members, low, high) in enumerate(catches, 1):
        roof = float(np.median(geo.c[members, 2]))
        inside = ((geo.c[up, 0] > low[0] + 0.1) & (geo.c[up, 0] < high[0] - 0.1)
                  & (geo.c[up, 1] > low[1] + 0.1) & (geo.c[up, 1] < high[1] - 0.1)
                  & (geo.c[up, 2] < roof - 1.0) & (geo.c[up, 2] > roof - feature["max_depth_mm"]))
        if not inside.any():
            raise FeatureMissing(f"{feature['name']}: groove {number} has no floor within {feature['max_depth_mm']} mm")
        floors = up[inside]
        floor = float(geo.c[floors, 2].max())
        floor_area = float(geo.a[floors[np.abs(geo.c[floors, 2] - floor) < 0.01]].sum())
        if floor_area < 0.5 * float(geo.a[members].sum()):
            raise FeatureMissing(f"{feature['name']}: groove {number} floor covers {floor_area:.1f} mm2 under its caught face")
        first, last = layer_index_below(floor) + 2, layer_index_below(roof) - 2
        if last - first < 3:
            raise FeatureMissing(f"{feature['name']}: groove {number} is {roof - floor:.2f} mm tall")
        bottom, top = layer_mid(first) - 0.06, layer_mid(last) + 0.06
        box_low = [float(low[0] + gap), float(low[1] + gap), bottom]
        box_high = [float(high[0] - gap), float(high[1] - gap), top]
        ribbons.append({"number": number, "caught_face_print_z_mm": roof, "floor_print_z_mm": floor,
                        "caught_face": _record(geo, members), "box_print_mm": [box_low, box_high],
                        "layers": [first, last],
                        "gap_below_mm": round(layer_mid(first) - LAYER / 2 - floor, 3),
                        "gap_above_mm": round(roof - (layer_mid(last) + LAYER / 2), 3)})
    _check(feature, "total ribbon length", sum(max(r["box_print_mm"][1][0] - r["box_print_mm"][0][0],
                                                   r["box_print_mm"][1][1] - r["box_print_mm"][0][1]) for r in ribbons),
           "total_length_mm")
    return {"name": feature["name"], "kind": "groove_ribbons", "ribbons": ribbons,
            "paint_faces": np.concatenate([m for m, _, _ in catches]),
            "ribbon_settings": feature["ribbon_settings"], "reason": feature["reason"]}


def tie_windows(geo: Geometry, feature: dict) -> dict:
    """The room under each zip-tie channel roof: a rectangular print-down face one tie
    channel wide, inside the exterior skin, as a box from the roof down to its floor or the
    declared cavity depth."""
    zone = geo.select(feature.get("select", {}))
    up = np.flatnonzero(geo.n[:, 2] > 0.999)
    depth = feature["cavity_depth_mm"]
    widths = np.array(feature["channel_widths_mm"])
    windows = []
    for members in geo.components(zone & (geo.n[:, 2] < -0.999)):
        points = geo.t[members].reshape(-1, 3)
        low, high = points.min(axis=0), points.max(axis=0)
        size = high[:2] - low[:2]
        if np.min(np.abs(widths - size.min())) > feature.get("width_tolerance_mm", 0.06) or size.max() > feature["long_side_max_mm"]:
            continue
        if np.any(low[:2] < geo.low[:2] + 0.5) or np.any(high[:2] > geo.high[:2] - 0.5):
            continue
        if geo.a[members].sum() < 0.85 * size[0] * size[1]:
            continue
        roof = float(np.median(geo.c[members, 2]))
        if roof - geo.low[2] < depth:
            continue
        inside = ((geo.c[up, 0] > low[0]) & (geo.c[up, 0] < high[0]) & (geo.c[up, 1] > low[1]) & (geo.c[up, 1] < high[1])
                  & (geo.c[up, 2] < roof) & (geo.c[up, 2] >= roof - depth))
        floor = float(geo.c[up[inside], 2].max()) if inside.any() else roof - depth
        windows.append({"roof_print_z_mm": roof, "floor_print_z_mm": floor,
                        "box_print_mm": [[float(low[0]), float(low[1]), floor], [float(high[0]), float(high[1]), roof]],
                        "roof": _record(geo, members)})
    _check(feature, "window count", len(windows), "count")
    return {"name": feature["name"], "kind": "tie_windows", "windows": windows,
            "blockers": bool(feature.get("blockers", False)), "reason": feature["reason"]}


def edge_fins(geo: Geometry, feature: dict, ceiling: dict) -> dict:
    """Interrupted removable walls from the bed to a flat ceiling's exterior edge."""
    region = ceiling["region"]
    xs = np.array(region.exterior.coords if region.geom_type == "Polygon"
                  else [p for g in region.geoms for p in g.exterior.coords])
    fins = []
    width, overhang, gap = feature["wall_mm"], feature["outboard_mm"], feature["top_gap_mm"]
    top = ceiling["ceiling_print_z_mm"] - gap
    for side in (-1.0, 1.0):
        edge_x = xs[:, 0].max() if side > 0 else xs[:, 0].min()
        on_edge = xs[np.abs(xs[:, 0] - edge_x) < 0.05]
        if len(on_edge) < 2 or (side > 0) != (edge_x > (geo.low[0] + geo.high[0]) / 2):
            continue
        y0, y1 = float(on_edge[:, 1].min()) + feature["end_inset_mm"], float(on_edge[:, 1].max()) - feature["end_inset_mm"]
        length, segment, release = y1 - y0, feature["segment_mm"], feature["release_gap_mm"]
        count = max(1, int(round((length + release) / (segment + release))))
        actual = (length - (count - 1) * release) / count
        x_out = edge_x + side * overhang
        x_in = x_out - side * width
        for k in range(count):
            a = y0 + k * (actual + release)
            fin = {"side": side, "box_print_mm": [[min(x_in, x_out), a, 0.0], [max(x_in, x_out), a + actual, top]],
                   "blocker_print_mm": [[min(x_in, x_out) - 0.2, a - 0.2, top - 0.85],
                                        [max(x_in, x_out) + 0.2, a + actual + 0.2, ceiling["ceiling_print_z_mm"] + 0.85]]}
            if feature.get("foot_height_mm"):
                foot = (x_out + side * feature["foot_outboard_mm"], x_in - side * feature["foot_inboard_mm"])
                fin["foot_print_mm"] = [[min(foot), a, 0.0], [max(foot), a + actual, feature["foot_height_mm"]]]
            fins.append(fin)
    if not fins:
        raise FeatureMissing(f"{feature['name']}: no exterior ceiling edge found")
    return {"name": feature["name"], "kind": "edge_fins", "fins": fins, "reason": feature["reason"]}


def box_part(box_low, box_high):
    return box_mesh(box_low, box_high)


def closing_schedule(tops, finest=0.08, coarsest_fine=0.16):
    """Layer ranges that put a layer top exactly on each face height in `tops`.

    The schedule starts 0.20 mm and continues in 0.24 mm layers. A face height off that
    grid takes equal fine layers from the grid top below it (one step further down when
    the remainder is under `finest`). Fine ranges within one ordinary layer of each
    other join at their finest height when their joined span divides evenly by it.
    """
    ranges, level = [], FIRST_LAYER
    targets = sorted(set(round(t, 4) for t in tops))
    for top in targets:
        if top <= level + 1e-6:
            if abs(top - level) > 1e-6:
                raise ValueError(f"face at {top} mm lies below the scheduled layer top {level} mm")
            continue
        steps = math.floor((top - level) / LAYER + 1e-9)
        start = level + steps * LAYER
        if abs(top - start) < 1e-6:
            level = top
            continue
        if top - start < finest - 1e-6:
            start -= LAYER
        count = math.ceil((top - start) / coarsest_fine - 1e-9)
        height = (top - start) / count
        if height < finest - 1e-6 or start < FIRST_LAYER - 1e-6:
            raise ValueError(f"no layer schedule closes {top} mm")
        ranges.append([round(start, 4), round(top, 4), round(height, 4)])
        level = top
    joined = []
    for low, high, height in ranges:
        if joined and low - joined[-1][1] <= LAYER + 1e-6:
            finest_height = min(height, joined[-1][2])
            start = joined[-1][0]
            inside = [t for t in targets if start < t <= high + 1e-6]
            if all(abs((t - start) / finest_height - round((t - start) / finest_height)) < 1e-6 for t in inside):
                joined[-1] = [start, high, finest_height]
                continue
        joined.append([low, high, height])
    return joined
