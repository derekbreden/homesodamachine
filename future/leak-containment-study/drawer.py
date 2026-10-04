"""Front-removable containment drawer and a separate, fixed appliance load frame.

World coordinates follow geometry.py: appliance inside floor Z=0 and base Z=-6.
The appliance remains stationary during drawer withdrawal. These native solids
demonstrate packaging and collision clearances only; the frame's load capacity,
watertightness, probe retention and discharge capture are not qualified.
"""

from __future__ import annotations

import hashlib
import math
from functools import lru_cache

import cadquery as cq

import geometry as g

RIM_Z = -8.5
SLIDE_CLEARANCE = 0.5
WEB_THICKNESS = 3.5
FRAME_LIP_BOTTOM = -8.0
FRAME_LIP_TOP = -6.0
PAN_Y0, PAN_Y1 = -4.05, 480.95
REFERENCE_PARTS = g.REFERENCE_PARTS
FIXED_NAMES = {
    "load-frame", "vent-extension", "hose-clip-upper", "hose-clip-lower",
    "upper-slot-closure-envelope", "wet-sensor-internal-floor-01",
    "drawer-presence-switch-envelope",
}


def _parameters(added_height=8.0, air_gap=25.4, bend_radius=30.0,
                tube_od=9.525, tube_id=6.35, horizontal_lead=5.0):
    added_height = float(added_height)
    # An 8 mm envelope leaves 3.5 mm static wet depth and 1.8 mm above the
    # bare 1.7 mm band. It does not reserve production clip height or freeboard.
    if added_height < 8.0:
        raise ValueError("The drawer study requires added_height >= 8 mm")
    p = g._parameters("full", added_height-2.0, added_height-4.5,
                      air_gap, bend_radius, tube_od, tube_id, horizontal_lead)
    p.update(mode="drawer", added_height=added_height,
             slide_clearance_mm=SLIDE_CLEARANCE,
             moving_rim_z=RIM_Z,
             bearing_lip_bottom_z=FRAME_LIP_BOTTOM,
             bearing_lip_top_z=FRAME_LIP_TOP,
             frame_web_thickness_mm=WEB_THICKNESS)
    if abs(p["rim_z"]-RIM_Z) > 1e-7:
        raise ValueError("Drawer rim and load-frame clearance are inconsistent")
    return p


def _rectangles(p):
    x0, x1 = p["downcomer_x"]-25.0, 112.5
    outer = (x0, PAN_Y0, x1, PAN_Y1)
    inner = (x0+2, PAN_Y0+2, x1-2, PAN_Y1-2)
    return outer, inner


def _frame(p, outer):
    """U-shaped fixed frame, open at the front; rear web is behind the drawer."""
    x0, y0, x1, y1 = outer
    z0 = p["bottom_z"]
    # Keep the high front bezel 0.5 mm ahead of the fixed lip end faces.
    # Without this front setback it touches them even with ample rim clearance.
    lip_y0 = y0+SLIDE_CLEARANCE
    west_web = (x0-SLIDE_CLEARANCE-WEB_THICKNESS, lip_y0, z0,
                x0-SLIDE_CLEARANCE, y1+SLIDE_CLEARANCE, FRAME_LIP_TOP)
    east_web = (x1+SLIDE_CLEARANCE, lip_y0, z0,
                x1+SLIDE_CLEARANCE+WEB_THICKNESS,
                y1+SLIDE_CLEARANCE, FRAME_LIP_TOP)
    west_lip = (west_web[0], lip_y0, FRAME_LIP_BOTTOM,
                -99.5, y1+SLIDE_CLEARANCE, FRAME_LIP_TOP)
    east_lip = (99.5, lip_y0, FRAME_LIP_BOTTOM,
                east_web[3], y1+SLIDE_CLEARANCE, FRAME_LIP_TOP)
    rear = (west_web[0], y1+SLIDE_CLEARANCE, z0,
            east_web[3], y1+SLIDE_CLEARANCE+4.0, FRAME_LIP_TOP)
    frame = g._union([g._box(b) for b in
                      (west_web, east_web, west_lip, east_lip, rear)])
    # Without this opening the fixed west bearing lip receives the discharge
    # instead of the moving drawer below. Keep the appliance bearing strip
    # intact; the opening itself further limits any structural claim.
    drop_window = (p["downcomer_x"]-21.0, g.VENT[1]-35.0,
                   FRAME_LIP_BOTTOM-1, p["downcomer_x"]+21.0,
                   g.VENT[1]+35.0, FRAME_LIP_TOP+1)
    frame = frame.cut(g._box(drop_window)).clean()
    bearing = [(-107.5, lip_y0, FRAME_LIP_TOP, -99.5, y1, FRAME_LIP_TOP),
               (99.5, lip_y0, FRAME_LIP_TOP, 107.5, y1, FRAME_LIP_TOP)]
    return frame, dict(west_web=list(west_web), east_web=list(east_web),
                       west_lip=list(west_lip), east_lip=list(east_lip),
                       rear=list(rear), case_bearing_surfaces=bearing,
                       vent_drop_window_bounds=list(drop_window),
                       west_lip_free_span_mm=-107.5-west_web[3],
                       east_lip_free_span_mm=east_web[0]-107.5)


def _components(p):
    outer, inner = _rectangles(p)
    floor, rim = p["innerfloor_z"], p["rim_z"]
    pan = g._rect_box(outer, p["bottom_z"], rim).cut(
        g._rect_box(inner, floor, rim+1)).clean()
    x0, y0, x1, y1 = outer
    # The front bezel is forward of every fixed bearing lip. Its back face
    # meets the pan's front face; there is no tall wall travelling under a lip.
    bezel = g._box((x0, y0-3, p["bottom_z"], x1, y0, 12.0))
    pan = pan.fuse(bezel).clean()
    # A rigid pull handle is shown as an envelope; no flexible latch or clip
    # mechanism is inferred by the geometry. Centre it on the appliance front.
    handle = g._union([
        g._box((-38, y0-23, -4, -30, y0-2.75, 4)),
        g._box((30, y0-23, -4, 38, y0-2.75, 4)),
        g._box((-38, y0-23, -4, 38, y0-15, 4)),
    ])
    pan = pan.fuse(handle).clean()
    frame, frame_bounds = _frame(p, outer)

    # Reuse the qualified scope of the existing proposal helpers, never the
    # saved appliance solids. g._components does not import the large STEP.
    existing_p = dict(p, mode="full")
    old_parts, *_ = g._components(existing_p)
    parts = {name: shape for name, shape in old_parts.items()
             if name not in ("lower-collector",) and
             not name.startswith(("support-", "wet-sensor-envelope"))}
    parts.update({"lower-collector": pan, "load-frame": frame})
    # These bare sensing bands reserve only the 8 x 1.7 mm strip. There are no
    # unshown holders or joints within the shallow lowest-height candidate.
    strips = [(x0+6, 15, x0+14, 460),
              (97, 15, 105, 460),
              (x0+18, 8, 94, 16),
              (x0+18, 462, 94, 470),
              (p["downcomer_x"]-4, g.VENT[1]-25,
               p["downcomer_x"]+4, g.VENT[1]+25)]
    bands = []
    for index, rect in enumerate(strips, 1):
        band = g._rect_box(rect, floor, floor+p["sensor_thickness"])
        parts[f"wet-sensor-envelope-{index:02d}"] = band
        bands.append(band)
    # Functional packaging envelopes, not a selected or approved switch. The
    # stationary detector remains clear of the bezel and withdrawal corridor.
    parts["drawer-presence-switch-envelope"] = g._box(
        (108.5, y0+0.5, -2, 115.5, y0+6.5, 6))
    parts["drawer-presence-target-envelope"] = g._box(
        (105.0, y0-4.0, -2, 111.0, y0-3.0, 6))
    water = g._rect_box(inner, floor, rim)
    gross = water.Volume()
    for band in bands:
        water = water.cut(band)
    water = water.clean()
    tube, path, samples, outlet = g._tube(p)
    return parts, water, gross, bands, path, samples, outlet, outer, inner, frame_bounds


def build_variant(added_height=8.0, air_gap=25.4, bend_radius=30.0,
                  tube_od=9.525, tube_id=6.35, horizontal_lead=5.0):
    """Named fixed/moving physical proposal solids plus labelled references."""
    p = _parameters(added_height, air_gap, bend_radius, tube_od,
                    tube_id, horizontal_lead)
    return _components(p)[0]


def water_shape(added_height=8.0, air_gap=25.4, bend_radius=30.0,
                tube_od=9.525, tube_id=6.35, horizontal_lead=5.0):
    """Exact static void at the lowest flood crest, minus moving probe bodies.

    The complete cavity is below the stationary appliance and below the fixed
    frame's bearing lips. No appliance STEP subtraction is needed or performed.
    The resulting volume has zero freeboard and is not a guaranteed leak reserve.
    """
    p = _parameters(added_height, air_gap, bend_radius, tube_od,
                    tube_id, horizontal_lead)
    return _components(p)[1]


def _role(name):
    if name in REFERENCE_PARTS:
        return "reference"
    return "fixed" if name in FIXED_NAMES else "moving"


def _withdrawal_checks(parts):
    moving = [(name, shape) for name, shape in parts.items() if _role(name) == "moving"]
    fixed = [(name, shape) for name, shape in parts.items() if _role(name) == "fixed"]
    samples = (0.0, 0.5, 5.0, 25.0, 100.0, 250.0, 485.0, 500.0)
    clashes = []
    closest = math.inf
    for travel in samples:
        for moving_name, shape in moving:
            translated = shape.translate((0, -travel, 0))
            for fixed_name, stationary in fixed:
                if not g._overlaps_bbox(g.bounds(translated), g.bounds(stationary)):
                    continue
                volume = translated.intersect(stationary).Volume()
                if volume > 1e-6:
                    clashes.append(dict(travel_mm=travel, moving=moving_name,
                                        fixed=fixed_name, volume_mm3=volume))
        # Native distance is meaningful specifically for the drawer-to-frame
        # gap; the pan's front bezel meets the lip's Y plane at closed position
        # but remains 0.5 mm below its underside wherever their XY overlap.
        closest = min(closest, parts["lower-collector"].translate(
            (0, -travel, 0)).distance(parts["load-frame"]))
    return dict(withdrawal_samples_mm=list(samples), withdrawal_clashes=clashes,
                max_withdrawal_clash_mm3=max([c["volume_mm3"] for c in clashes], default=0.0),
                drawer_frame_min_sampled_distance_mm=closest,
                required_travel_for_complete_release_mm=485.0)


@lru_cache(maxsize=16)
def _description(parameter_items):
    p = dict(parameter_items)
    parts, water, gross, bands, path, samples, outlet, outer, inner, frame = _components(p)
    physical = [shape for name, shape in parts.items() if _role(name) != "reference"]
    physical_bounds = g.bounds(cq.Compound.makeCompound(physical))
    overall = [min(-107.5, physical_bounds[0]), min(5, physical_bounds[1]),
               min(g.BASE_Z, physical_bounds[2]), max(107.5, physical_bounds[3]),
               max(471.9000001, physical_bounds[4]), max(g.APPLIANCE_TOP_Z, physical_bounds[5])]
    x0, y0, x1, y1 = inner
    checks = dict(all_parts_valid=all(shape.isValid() for shape in parts.values()),
                  single_solid_parts=all(len(shape.Solids()) == 1 for shape in parts.values()),
                  tube_clip_intersection_mm3=sum(parts["vent-extension"].intersect(parts[name]).Volume()
                      for name in ("hose-clip-upper", "hose-clip-lower")),
                  bearing_to_rim_clearance_mm=FRAME_LIP_BOTTOM-p["rim_z"],
                  side_web_to_pan_clearance_mm=SLIDE_CLEARANCE,
                  sensor_to_rim_clearance_mm=p["depth"]-p["sensor_thickness"],
                  underbase_sensor_clearance_mm=g.BASE_Z-(p["innerfloor_z"]+p["sensor_thickness"]),
                  mq6_static_crest_margin_mm=3-p["rim_z"],
                  full_water_void_below_appliance_mm=g.BASE_Z-p["rim_z"],
                  flood_crest_air_gap_mm=outlet[2]-p["rim_z"])
    checks["tube_to_frame_drop_window_edge_height_mm"] = outlet[2]-FRAME_LIP_TOP
    checks["vent_centreline_through_frame_window"] = (
        frame["vent_drop_window_bounds"][0] < outlet[0] < frame["vent_drop_window_bounds"][3]
        and frame["vent_drop_window_bounds"][1] < outlet[1] < frame["vent_drop_window_bounds"][4])
    checks.update(_withdrawal_checks(parts))
    # Match the existing relief check without importing the appliance STEP.
    _, oy, oz, ow, oh, _ = g.FACTS["box"]["west_ports"][0]
    wall = g._box((g.WEST_WALL_X, oy-ow/2-5, oz-oh/2-40,
                   -98.5, oy+ow/2+5, oz+oh/2+10))
    old_cut = g._box((g.WEST_WALL_X-1, oy-ow/2, oz-oh/2,
                     -97.5, oy+ow/2, oz+oh/2))
    checks["tube_wall_after_relief_mm3"] = parts["vent-extension"].intersect(
        wall.cut(old_cut).cut(parts["wall-opening-extension"])).Volume()
    capacity = dict(gross_ml=gross/1000, appliance_displacement_ml=0.0,
                    support_displacement_ml=0.0,
                    sensor_displacement_ml=(gross-water.Volume())/1000,
                    net_capacity_ml=water.Volume()/1000,
                    excluded_disconnected_void_ml=0.0,
                    void_components_before_filter=len(water.Solids()),
                    method="native drawer cavity minus five moving probe envelopes; cavity is entirely below appliance and frame lips")
    return dict(parameters=p, source_hash=g._source_hash(),
                saved_assembly=dict(step=str(g.STEP_PATH.relative_to(g.ROOT)),
                    facts=str(g.FACTS_PATH.relative_to(g.ROOT)),
                    facts_step_signature=g.FACTS["step"],
                    facts_sources_signature=g.FACTS["sources"],
                    step_sha256=g._source_hash(),
                    facts_sha256=hashlib.sha256(g.FACTS_PATH.read_bytes()).hexdigest(),
                    freshness="Frozen appliance datums only; no STEP import or appliance-solid clash audit is performed by this module."),
                case_height_mm=p["case_height_mm"], installed_height_mm=p["installed_height_mm"],
                bounds=physical_bounds, overall_bounds=overall,
                overall_width_mm=overall[3]-overall[0], overall_depth_mm=overall[4]-overall[1],
                basin_outline_xy=[[x0,y0], [x1,y0], [x1,y1], [x0,y1]],
                innerfloor_z=p["innerfloor_z"], rim_z=p["rim_z"],
                basin_cavity_rectangles_xy=[list(inner)],
                support_bounds=[g.bounds(parts["load-frame"])],
                sensor_bounds=[g.bounds(band) for band in bands]+[list(g.INTERNAL_SENSOR_BOUNDS)],
                collector_sensor_bounds=[g.bounds(band) for band in bands],
                internal_floor_sensor_bounds=[list(g.INTERNAL_SENSOR_BOUNDS)],
                sensor_purposes=dict(internal_floor="Fixed witness on existing appliance floor; not all-leak detection proof.",
                    collector="Moving bare strips in the removable drawer; hardwired quick disconnect and retention unresolved.",
                    drawer_presence="Fixed switch and moving target envelopes indicate an inhibit requirement; no selected component or safety qualification."),
                tube_path=path, tube_centerline_samples=samples,
                tube_outlet_xyz=list(outlet),
                shell_relief_bounds=g.bounds(parts["wall-opening-extension"]),
                nominal_base_silhouette=dict(bounds=[-107.5,5,107.5,471.9], corner_radius=12),
                frame=frame, moving_parts=[name for name in parts if _role(name)=="moving"],
                fixed_parts=[name for name in parts if _role(name)=="fixed"],
                removal=dict(direction=[0,-1,0], maximum_display_travel_mm=500,
                    complete_release_travel_mm=485,
                    full_outlet_od_catch_until_travel_mm=inner[3]-outlet[1]-p["tube_od"]/2,
                    outlet_centre_inside_until_travel_mm=inner[3]-outlet[1],
                    conservative_catch_display_limit_mm=95.5,
                    slide_support="Drawer bottom rests and slides directly on the cabinet floor; no skid, bearing or suspension clearance is reserved.",
                    operating_state="Water supply and dispensing inhibited before withdrawal; drawer-presence detection, hose purge/drain, hardwired sensor disconnect and latch are unresolved.",
                    scope="Straight native-geometry translation samples; no deformation, tolerances, water motion or saved-appliance STEP intersection check."),
                parts={name:dict(bounds=g.bounds(shape), valid=shape.isValid(),
                    volume_mm3=shape.Volume(), role=_role(name)) for name,shape in parts.items()},
                capacity=capacity, net_capacity_ml=capacity["net_capacity_ml"], checks=checks,
                capacity_scope="Maximum static level at lowest flood crest, zero freeboard; volume is not a detection-delay, tilt or splash allowance.",
                review_limits=[
                    "Separate fixed U-frame carries the appliance; the drawer carries only retained water and its probes.",
                    "The 2 mm bearing lip, 3.5 mm webs and approximately 61 mm west free span are packaging geometry; load capacity, deflection and cabinet fastening are unqualified.",
                    "The 0.5 mm clearances are geometric assumptions, not tolerance or friction acceptance.",
                    "Drawer bottom rests and slides on the cabinet floor; no skid allowance or floor-flatness acceptance is included.",
                    "The rectangular west bay remains full depth to pass beneath stationary side bearing lips during withdrawal.",
                    "A 42 x 70 mm hole through the fixed west bearing lip leaves the vent drop path open; its capture and splash behavior are unqualified.",
                    "The drawn outlet is 25.4 mm above the drawer flood crest and 22.9 mm above the surrounding dry frame lip; approved installed air-gap requirements remain unresolved.",
                    "The drawer rim is 2.5 mm below the appliance base; leak capture around base edges needs real-water qualification.",
                    "Sensor bodies are bare 8 x 1.7 mm envelopes; retention, wiring and quick-disconnect volume are unresolved.",
                    "No water can be safely dispensed with the receiving drawer removed; withdrawal needs a fail-safe operating inhibit and drain/purge procedure.",
                    "The 25.4 mm air gap, R30 hose bends, attachment, clip fixing and slot closure retain the existing study's unqualified review scope.",
                    "Stationary tube outlet remains over the cabinet when the drawer is withdrawn; no alternative discharge receiver is drawn.",
                    "A shallow drawer does not establish usable containment under tilt or splash.",
                    "Frame, tray, handle and presence-switch envelopes are not production drawings or a print-ready assembly.",
                ])


def describe_variant(added_height=8.0, air_gap=25.4, bend_radius=30.0,
                     tube_od=9.525, tube_id=6.35, horizontal_lead=5.0,
                     include_saved_displacement=False):
    """Geometry, static capacity, motion groups and native withdrawal checks.

    include_saved_displacement is accepted for builder compatibility; all drawer
    water is below the appliance so no large saved-STEP import is performed.
    """
    p = _parameters(added_height, air_gap, bend_radius, tube_od,
                    tube_id, horizontal_lead)
    return _description(tuple(p.items()))


def proposal_assembly(**kwargs):
    assembly = cq.Assembly(name="front-removable-containment-drawer-proposal")
    for name, shape in build_variant(**kwargs).items():
        if name not in REFERENCE_PARTS:
            assembly.add(shape, name=name)
    return assembly
