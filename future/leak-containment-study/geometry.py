"""Parametric, unqualified leak-containment proposal in the saved assembly frame.

Only proposal solids are returned. The saved appliance and upper pan are context,
not altered here. Coordinates and intersections refer to the saved STEP/facts;
they do not establish capture of real leaks, material suitability, or compliance.
All dimensions are mm. World Z=0 is the appliance's inside floor, Z=-6 its base.
"""

from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
STUDY_DIR = Path(__file__).resolve().parent
FACTS_PATH = STUDY_DIR / "context-source.facts.json"
STEP_PATH = STUDY_DIR / "context-source.step"
FACTS = json.loads(FACTS_PATH.read_text())
VENT = tuple(FACTS["card_ports"]["asse1022-assembly"]["vent-tip"]["pos"])
VENT_AXIS = tuple(FACTS["card_ports"]["asse1022-assembly"]["vent-tip"]["axis"])
if any(abs(a-b) > 1e-7 for a, b in zip(VENT_AXIS, (0, 0, -1))):
    raise ValueError("This study route requires the saved vent to point vertically down")
# Existing reference stub runs from the body underside to 2 mm below the barb.
# Its bored-on-barb section is an envelope, not a validated hose stretch model.
BARB_DIAMETER = 8.0
STUB_LENGTH = 10.5 + 33.0/2 - 33.0*math.sqrt(3)/4 + 2.0
BASE_Z = -6.0
CASE_TOP_Z = 355.0
APPLIANCE_TOP_Z = FACTS["bodies"]["funnel-cover"][5]
WEST_WALL_X = -107.5
INTERNAL_SENSOR_BOUNDS = (-97.5, 80.0, 0.0, -89.5, 130.0, 1.7)
REFERENCE_PARTS = {"wall-opening-extension", "air-gap-reference"}


def _box(bounds):
    x0, y0, z0, x1, y1, z1 = bounds
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def _rect_box(rect, z0, z1):
    x0, y0, x1, y1 = rect
    return _box((x0, y0, z0, x1, y1, z1))


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


@lru_cache(maxsize=1)
def _source_hash():
    return hashlib.sha256(STEP_PATH.read_bytes()).hexdigest()


def _union(shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.clean()


def _parameters(mode, gap, depth, air_gap, bend_radius, tube_od, tube_id, horizontal_lead):
    if mode not in ("full", "local"):
        raise ValueError("mode must be full or local")
    depth = (8.0 if mode == "full" else 60.0) if depth is None else float(depth)
    if gap < 0 or depth <= 1.7 or air_gap <= 0:
        raise ValueError("gap >= 0, depth > 1.7, and air_gap > 0 required")
    if not (0 < tube_id < tube_od) or bend_radius < tube_od * 2:
        raise ValueError("positive tube wall and bend_radius >= 2*OD required")
    if horizontal_lead < 0:
        raise ValueError("horizontal_lead >= 0 required")
    p = dict(mode=mode, gap=float(gap), depth=depth, air_gap=float(air_gap),
             bend_radius=float(bend_radius), tube_od=float(tube_od),
             tube_id=float(tube_id), floor_thickness=2.0, wall_thickness=2.0,
             sensor_width=8.0, sensor_thickness=1.7)
    p["horizontal_lead"] = float(horizontal_lead)
    p["bottom_z"] = BASE_Z-2-gap if mode == "full" else BASE_Z
    p["innerfloor_z"] = p["bottom_z"]+2
    p["rim_z"] = p["innerfloor_z"]+depth
    p["added_z"] = 2+gap if mode == "full" else 0.0
    p["case_height_mm"] = CASE_TOP_Z-BASE_Z+p["added_z"]
    p["installed_height_mm"] = APPLIANCE_TOP_Z-BASE_Z+p["added_z"]
    p["global_height"] = p["case_height_mm"]  # Compatibility field: case height.
    p["downcomer_x"] = VENT[0]-2*bend_radius-horizontal_lead
    p["outlet_z"] = p["rim_z"]+air_gap
    if p["outlet_z"] >= VENT[2]-2*bend_radius-20:
        raise ValueError("receiver/outlet too high for the modeled two-bend route")
    return p


def _basin(p):
    """Return connected outer/cavity rectangles and their water outline."""
    cx, cy = p["downcomer_x"], VENT[1]
    if p["mode"] == "local":
        # Beside the appliance: the original base remains on its mounting plane.
        outer = [(cx-25, cy-60, cx+25, cy+60)]
        cavities = [(cx-23, cy-58, cx+23, cy+58)]
        outline = [(cx-23, cy-58), (cx+23, cy-58),
                   (cx+23, cy+58), (cx-23, cy+58)]
    else:
        main = (-112.5, -4.05, 112.5, 480.95)
        ear = (cx-25, cy-40, -108.0, cy+40)
        outer = [main, ear]
        # Bridge overlaps both cavities and removes the wall between them.
        cavities = [(-110.5, -2.05, 110.5, 478.95),
                    (cx-23, cy-38, -110.0, cy+38),
                    (cx-23, cy-38, -108.5, cy+38)]
        outline = [(-110.5, -2.05), (110.5, -2.05), (110.5, 478.95),
                   (-110.5, 478.95), (-110.5, cy+38), (cx-23, cy+38),
                   (cx-23, cy-38), (-110.5, cy-38)]
    return outer, cavities, outline


def _tube(p):
    x, y, z = VENT
    r = p["bend_radius"]
    a = (x-r, y, z-r)
    b = (a[0]-p["horizontal_lead"], y, a[2])
    c = (b[0]-r, y, b[2]-r)
    d = (c[0], y, p["outlet_z"])
    mid1 = (x-r+r/math.sqrt(2), y, z-r/math.sqrt(2))
    mid2 = (b[0]-r/math.sqrt(2), y, b[2]-r+r/math.sqrt(2))
    v = cq.Vector
    edges = [cq.Edge.makeThreePointArc(v(VENT), v(mid1), v(a))]
    if p["horizontal_lead"] > 0:
        edges.append(cq.Edge.makeLine(v(a), v(b)))
    edges += [cq.Edge.makeThreePointArc(v(b), v(mid2), v(c)),
             cq.Edge.makeLine(v(c), v(d))]
    wire = cq.Wire.assembleEdges(edges)
    profile = cq.Workplane(cq.Plane(origin=VENT, normal=(0, 0, -1)))
    tube = profile.circle(p["tube_od"]/2).circle(p["tube_id"]/2).sweep(
        cq.Workplane().newObject([wire]), isFrenet=True).val()
    upstream = (x, y, z+STUB_LENGTH)
    sleeve = cq.Solid.makeCylinder(p["tube_od"]/2, STUB_LENGTH,
                 cq.Vector(VENT), cq.Vector(0, 0, 1)).cut(
             cq.Solid.makeCylinder(BARB_DIAMETER/2, STUB_LENGTH,
                 cq.Vector(VENT), cq.Vector(0, 0, 1)))
    tube = tube.fuse(sleeve).clean()
    samples = [list(upstream)]
    for i in range(17):
        t = math.pi/2*i/16
        samples.append([x-r+r*math.cos(t), y, z-r*math.sin(t)])
    samples.append(list(b))
    for i in range(1, 17):
        t = math.pi/2*i/16
        samples.append([b[0]-r*math.sin(t), y, b[2]-r+r*math.cos(t)])
    samples.append(list(d))
    path = [dict(kind="line", start=list(upstream), end=list(VENT),
                 role="replacement sleeve over existing brass barb"),
            dict(kind="arc", start=list(VENT), mid=list(mid1), end=list(a),
                 center=[x-r, y, z], radius=r),
            dict(kind="line", start=list(a), end=list(b)),
            dict(kind="arc", start=list(b), mid=list(mid2), end=list(c),
                 center=[b[0], y, b[2]-r], radius=r),
            dict(kind="line", start=list(c), end=list(d))]
    return tube, path, samples, d


def _clip(p, center_z):
    """Open half-saddle with an integral arm/plate; screw detail is a proposal."""
    x, y = p["downcomer_x"], VENT[1]
    inner = p["tube_od"]/2+.30
    outer = inner+2
    ring = cq.Workplane("XY").workplane(offset=center_z-5).center(x, y).circle(
        outer).circle(inner).extrude(10).val()
    ring = ring.cut(_box((x-outer-1, y-outer-1, center_z-6,
                         x, y+outer+1, center_z+6)))
    arm = _box((x+outer-.5, y-4, center_z-1.5,
                WEST_WALL_X-1, y+4, center_z+1.5))
    plate = _box((WEST_WALL_X-2, y-8, center_z-12.5,
                 WEST_WALL_X, y+8, center_z+12.5))
    clip = _union([ring, arm, plate])
    holes = []
    for dz in (-8, 8):
        hole = cq.Solid.makeCylinder(1.7, 12,
              cq.Vector(WEST_WALL_X-3, y, center_z+dz), cq.Vector(1, 0, 0))
        clip = clip.cut(hole)
        holes.append(hole)
    return clip.clean(), holes


def _components(p):
    outer, cavities, outline = _basin(p)
    floor, rim = p["innerfloor_z"], p["rim_z"]
    pan = _union([_rect_box(r, p["bottom_z"], rim) for r in outer])
    cutter = _union([_rect_box(r, floor, rim+1) for r in cavities])
    pan = pan.cut(cutter).clean()
    water = _union([_rect_box(r, floor, rim) for r in cavities])
    tube, path, samples, outlet = _tube(p)
    parts = {"lower-collector": pan, "vent-extension": tube}
    supports = []
    bands = []
    if p["mode"] == "full":
        stations = [(x, y) for x, y, *_ in FACTS["box"]["floor_bosses"]]
        stations += [(x, y) for x in (-60, 60) for y in (285, 433)]
        if p["gap"] > 0:
            for i, (x, y) in enumerate(stations, 1):
                support = _box((x-11, y-6, floor, x+11, y+6, BASE_Z))
                parts[f"support-{i:02d}"] = support
                supports.append(support)
        sensor_rects = [(-105, 15, -97, 460), (97, 15, 105, 460),
                        (-94, 8, 94, 16), (-94, 462, 94, 470)]
    else:
        sensor_rects = []
    sensor_rects.append((p["downcomer_x"]-4, VENT[1]-25,
                         p["downcomer_x"]+4, VENT[1]+25))
    for i, rect in enumerate(sensor_rects, 1):
        band = _rect_box(rect, floor, floor+p["sensor_thickness"])
        parts[f"wet-sensor-envelope-{i:02d}"] = band
        bands.append(band)
    internal_band = _box(INTERNAL_SENSOR_BOUNDS)
    parts["wet-sensor-internal-floor-01"] = internal_band
    bands.append(internal_band)
    upper_z = 200.0
    lower_z = max(95.0, p["outlet_z"]+20)
    for tag, height in (("upper", upper_z), ("lower", lower_z)):
        clip, _ = _clip(p, height)
        parts[f"hose-clip-{tag}"] = clip
    # The old rectangular upper-pan opening is retained. This cutter extends it
    # downwards where an R30 tube exits; it is not a claim about existing clearance.
    opening = FACTS["box"]["west_ports"][0]
    old_z0 = opening[2]-opening[4]/2
    half = p["tube_od"]/2+.75
    relief = _box((WEST_WALL_X-1, VENT[1]-half, VENT[2]-p["bend_radius"]-half,
                   -97.5, VENT[1]+half, old_z0+1))
    parts["wall-opening-extension"] = relief
    # Infill is flush inside the existing nine-mm wall. Fixing/sealing is not
    # designed here; subtract the new notch to preserve the proposed tube opening.
    _, old_y, old_z, old_width, old_height, _ = opening
    blank = _box((WEST_WALL_X, old_y-old_width/2+.25, old_z-old_height/2+.25,
                   -98.5, old_y+old_width/2-.25, old_z+old_height/2-.25))
    parts["upper-slot-closure-envelope"] = blank.cut(relief).clean()
    parts["air-gap-reference"] = cq.Solid.makeCylinder(p["tube_od"]/2,
            p["air_gap"], cq.Vector(outlet[0], outlet[1], rim), cq.Vector(0, 0, 1))
    return parts, water, supports, bands, path, samples, outlet, outline, cavities


def build_variant(mode="full", gap=3.0, depth=None, air_gap=25.4,
                  bend_radius=30.0, tube_od=9.525, tube_id=6.35, horizontal_lead=5.0):
    """Return named proposal cq.Shape solids, including two labeled references.

    Full default: added height 5 mm, wet depth 8 mm, flood crest Z=-1 mm.
    Local default: 60 mm wet depth beside the chassis, added height 0 mm.
    Tube attachment, material, bend capability, clips and wet probes need design
    qualification. air_gap=25.4 is a review assumption, not an approved requirement.
    """
    p = _parameters(mode, gap, depth, air_gap, bend_radius, tube_od, tube_id, horizontal_lead)
    return _components(p)[0]


@lru_cache(maxsize=1)
def _saved_solids():
    # A read-only STEP import, independent of changing production generators.
    return tuple(cq.importers.importStep(str(STEP_PATH)).val().Solids())


def _overlaps_bbox(a, b):
    return all(a[i] < b[i+3]+1e-6 and b[i] < a[i+3]+1e-6 for i in range(3))


def _displacement(water, supports, bands, saved):
    gross = water.Volume()
    remaining = water
    installed = 0.0
    if saved:
        wb = bounds(water)
        for solid in _saved_solids():
            if not _overlaps_bbox(wb, bounds(solid)):
                continue
            before = remaining.Volume()
            remaining = remaining.cut(solid)
            installed += max(0.0, before-remaining.Volume())
    support = sensor = 0.0
    for shapes, label in ((supports, "support"), (bands, "sensor")):
        amount = 0.0
        for shape in shapes:
            before = remaining.Volume()
            remaining = remaining.cut(shape)
            amount += max(0.0, before-remaining.Volume())
        if label == "support":
            support = amount
        else:
            sensor = amount
    # Isolated voids in an appliance slab are not hydraulically connected basin
    # reserve. The main underbase/ear void is the largest connected component.
    components = remaining.Solids()
    connected = max(components, key=lambda shape: shape.Volume())
    excluded = max(0.0, remaining.Volume()-connected.Volume())
    remaining = connected
    capacity = dict(gross_ml=gross/1000, appliance_displacement_ml=installed/1000,
                support_displacement_ml=support/1000, sensor_displacement_ml=sensor/1000,
                excluded_disconnected_void_ml=excluded/1000,
                void_components_before_filter=len(components),
                net_capacity_ml=remaining.Volume()/1000,
                method="saved STEP solid subtraction" if saved else "proposal solids only; appliance not subtracted")
    return capacity, remaining


@lru_cache(maxsize=32)
def _capacity_and_water(parameter_items, saved):
    p = dict(parameter_items)
    _, water, supports, bands, *_ = _components(p)
    return _displacement(water, supports, bands, saved)


def water_shape(mode="full", gap=3.0, depth=None, air_gap=25.4,
                bend_radius=30.0, tube_od=9.525, tube_id=6.35, horizontal_lead=5.0):
    """Max-rim static water void, with saved appliance/supports/probes removed.

    This is a review volume with zero freeboard, not a flow simulation or leak
    capture claim. It shares the exact capacity calculation with describe_variant.
    """
    p = _parameters(mode, gap, depth, air_gap, bend_radius, tube_od, tube_id, horizontal_lead)
    return _capacity_and_water(tuple(p.items()), True)[1]


def describe_variant(mode="full", gap=3.0, depth=None, air_gap=25.4,
                     bend_radius=30.0, tube_od=9.525, tube_id=6.35,
                     horizontal_lead=5.0, include_saved_displacement=True):
    """JSON-serializable frame, route, cavities, capacity and geometric checks."""
    p = _parameters(mode, gap, depth, air_gap, bend_radius, tube_od, tube_id, horizontal_lead)
    parts, water, supports, bands, path, samples, outlet, outline, cavities = _components(p)
    capacity = _capacity_and_water(tuple(p.items()), include_saved_displacement)[0]
    physical = [v for k, v in parts.items() if k not in REFERENCE_PARTS]
    physical_bounds = bounds(cq.Compound.makeCompound(physical))
    overall = [min(-107.5, physical_bounds[0]), min(5, physical_bounds[1]),
               min(BASE_Z, physical_bounds[2]), max(107.5, physical_bounds[3]),
               max(471.9000001, physical_bounds[4]), max(APPLIANCE_TOP_Z, physical_bounds[5])]
    opening = FACTS["box"]["west_ports"][0]
    _, y, z, width, height, _ = opening
    wall = _box((WEST_WALL_X, y-width/2-5, z-height/2-40,
                 -98.5, y+width/2+5, z+height/2+10))
    old_cut = _box((WEST_WALL_X-1, y-width/2, z-height/2,
                    -97.5, y+width/2, z+height/2))
    relieved_wall = wall.cut(old_cut).cut(parts["wall-opening-extension"])
    tube = parts["vent-extension"]
    checks = dict(all_parts_valid=all(s.isValid() for s in parts.values()),
                  single_solid_parts=all(len(s.Solids()) == 1 for s in parts.values()),
                  tube_wall_after_relief_mm3=tube.intersect(relieved_wall).Volume(),
                  tube_clip_intersection_mm3=sum(tube.intersect(parts[k]).Volume()
                      for k in ("hose-clip-upper", "hose-clip-lower")),
                  tube_to_coldcore_bbox_clearance_mm=tube.distance(
                      _box(FACTS["bodies"]["foam-assembly"])),
                  underbase_sensor_clearance_mm=p["gap"]-1.7 if mode == "full" else None,
                  mq6_static_crest_margin_mm=3-p["rim_z"] if mode == "full" else None)
    return dict(parameters=p, saved_assembly=dict(step=str(STEP_PATH.relative_to(ROOT)),
                facts=str(FACTS_PATH.relative_to(ROOT)), facts_step_signature=FACTS["step"],
                facts_sources_signature=FACTS["sources"],
                step_sha256=_source_hash(),
                facts_sha256=hashlib.sha256(FACTS_PATH.read_bytes()).hexdigest(),
                freshness="Frozen STEP and refreshed facts agree in the study context provenance; source-tree freshness is a separate scope."),
                source_hash=_source_hash(),
                case_height_mm=p["case_height_mm"], installed_height_mm=p["installed_height_mm"],
                bounds=physical_bounds, overall_bounds=overall,
                overall_width_mm=overall[3]-overall[0], overall_depth_mm=overall[4]-overall[1],
                basin_outline_xy=[list(v) for v in outline], innerfloor_z=p["innerfloor_z"],
                rim_z=p["rim_z"], basin_cavity_rectangles_xy=[list(v) for v in cavities],
                support_bounds=[bounds(s) for s in supports],
                sensor_bounds=[bounds(s) for s in bands], tube_path=path,
                collector_sensor_bounds=[bounds(v) for k, v in parts.items()
                    if k.startswith("wet-sensor-envelope")],
                internal_floor_sensor_bounds=[list(INTERNAL_SENSOR_BOUNDS)],
                sensor_purposes=dict(internal_floor="Witness water on the existing base before it exits; location does not establish that every leak reaches this band.",
                    collector="Witness water captured below the chassis or ASSE outlet; location alone does not establish detection delay."),
                tube_centerline_samples=samples, tube_outlet_xyz=list(outlet),
                vent_connection_scope=dict(datum="open end of existing clear-PVC telltale stub",
                    source="hardware/reference/asse1022-assembly/asse1022_assembly.py:109",
                    reach_past_brass_barb_mm=2.0, brass_barb_diameter_mm=8.0,
                    upstream_sleeve_length_mm=STUB_LENGTH, sleeve_bore_diameter_mm=BARB_DIAMETER,
                    joint="Continuous replacement hose over the existing brass barb; upstream sleeve replaces the saved PVC stub. No hose-to-hose coupler. The drawn 8 mm sleeve bore and transition to 6.35 mm are envelopes; attachment and local stretch are unqualified."),
                shell_relief_bounds=bounds(parts["wall-opening-extension"]),
                nominal_base_silhouette=dict(bounds=[-107.5, 5, 107.5, 471.9],
                    corner_radius=12, purpose="viewer silhouette only; capacity uses STEP solids"),
                parts={k:dict(bounds=bounds(v), valid=v.isValid(), volume_mm3=v.Volume(),
                               role="reference" if k in REFERENCE_PARTS else "proposal")
                       for k, v in parts.items()}, capacity=capacity,
                net_capacity_ml=capacity["net_capacity_ml"], checks=checks,
                capacity_scope="Maximum level, static, zero freeboard; no detection-delay, tilt or splash allowance",
                review_limits=["No real-water capture or shutoff acceptance is inferred.",
                  "Local collector receives only the modeled ASSE vent route; other leaks can escape.",
                  "The full shallow tray does not establish capture of high side exits or tolerance of tilt.",
                  "25.4 mm air gap is a review assumption; requirements and installed outlet need confirmation.",
                  "Tube joint, materials, bend capability, clips and sensor electronics are not qualified.",
                  "Sensor envelopes have no additional clip plastic beneath the appliance.",
                  "The saved assembly upper pan is context only and must be omitted for the proposed route.",
                  "The saved PVC vent stub is replaced by the proposed continuous hose sleeve.",
                  "The original upper-pan slot receives a flush closure envelope; its fixing and sealing remain unresolved.",
                  "Wet-probe adhesive or retention detail remains unresolved; bare envelopes reserve only 1.7 mm height.",
                  "Datums come from frozen refreshed facts; capacity subtracts actual frozen STEP solids. Production source-tree state is outside this review boundary.",
                  "Wall relief and two 3.4 mm clip-mount holes per clip are proposed production changes."])


def proposal_assembly(mode="full", **kwargs):
    """STEP assembly of physical proposals only, without appliance or cutters."""
    assembly = cq.Assembly(name=f"leak-containment-{mode}-proposal")
    for name, shape in build_variant(mode=mode, **kwargs).items():
        if name not in REFERENCE_PARTS:
            assembly.add(shape, name=name)
    return assembly
