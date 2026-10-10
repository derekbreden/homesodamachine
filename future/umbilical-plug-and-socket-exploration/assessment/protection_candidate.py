"""Integral open cage for the guided umbilical boot: a geometric candidate.

The four fences are the parts of a round annulus which clear the full union-ring
cylinders. Their convex hull projects beyond all four bare tubes for broad planar
contact from any lateral direction. The corner openings still admit narrow objects.
No load, fatigue, print success or physical fitting result is inferred from this CAD.

Frame and tube guides are inherited from boot_concept.py: mating face y=0, positive
Y into the machine. The protected plug remains one printed body plus its tube key.
A short round collar attaches every fence without filling the existing internal cuts.
The matching socket keeps the original fluid stations, union float, release plane,
magnet/pogo seats, retainer and snap leaves.

Import guarded_plug(), guarded_socket() and fences() for native CadQuery solids.
Run with the repository CadQuery Python to regenerate protection-candidate.json;
--export-dir PATH additionally writes guard, guarded-plug and guarded-socket STEP.
This review is manual and is not attached to a build, edit, hook or print gate.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPLORATION = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "hardware").is_dir())
sys.path.insert(0, str(EXPLORATION))
import numpy as np
from scipy.spatial import ConvexHull
import umbilical as u
import boot_concept as b

GUARD_R = 17.0
GUARD_WALL = 2.6
RING_CLEARANCE = 0.25
RECEIVER_CLEARANCE = 0.25
RECEIVER_AXIAL_RELIEF = 1.0               # guard tips must not compete with the mating-face stop
TIP_LEAD = 2.0
TIP = b.STUB_Q + TIP_LEAD
ROOT_LENGTH = 6.0
ROOT_LEAD_LENGTH = 4.0
EDGE_RADIUS = 0.5
SOCKET_BODY_R = 22.2
SOCKET_FLANGE_R = SOCKET_BODY_R + 2.5


def _ring_radius(od):
    return (u.U.RING_D if od > 5 else u.D_RING) / 2


def _fence_prism(y0, y1, extra=0.0):
    """Expanded receiver negative when extra>0; every boundary has clearance."""
    outer = u.cyl(2 * (GUARD_R + extra), y0, y1)
    inner = u.cyl(2 * (GUARD_R - GUARD_WALL - extra), y0 - 0.1, y1 + 0.1)
    body = outer.cut(inner)
    for x, z, od in u.PORTS.values():
        body = body.cut(u.cyl(2 * (_ring_radius(od) + RING_CLEARANCE - extra),
                              y0 - 0.1, y1 + 0.1, x, z))
    return body.clean()


def sharp_fences():
    """Unrounded mathematical sectors, useful only for the upper-bound comparison."""
    return _fence_prism(-ROOT_LENGTH, TIP)


def fences():
    """Four fence sectors with rounded outer tips, joined by guarded_plug()."""
    raw = sharp_fences()
    edges = []
    for edge in raw.Edges():
        point, tangent = edge.startPoint(), edge.tangentAt(0)
        if abs(tangent.y) > .999 and abs(math.hypot(point.x, point.z) - GUARD_R) < .001:
            edges.append(edge)
    return u.cq.Workplane(obj=raw).newObject(edges).fillet(EDGE_RADIUS).val()


def collar_skin():
    """Add outside the existing nose stock; preserve all holes and seats inside it."""
    start = -(ROOT_LENGTH + ROOT_LEAD_LENGTH)
    straight = u.profile(u.PLUG_R, u.PLUG_F, start, -b.NOSE_CHAMFER_L + 0.01)
    lead = u.cq.Solid.makeLoft([
        u.profile_wire(u.PLUG_R, u.PLUG_F, -b.NOSE_CHAMFER_L),
        u.profile_wire(u.PLUG_R - .8, u.PLUG_F - .8, 0)])
    stock = straight.fuse(lead).clean()
    transition = u.cq.Solid.makeLoft([
        u.profile_wire(u.PLUG_R, u.PLUG_F, start),
        u.cq.Wire.makeCircle(GUARD_R, u._v(0, -ROOT_LENGTH, 0), u._v(0, 1, 0))])
    outer = transition.fuse(u.cyl(2 * GUARD_R, -ROOT_LENGTH, 0)).clean()
    return outer.cut(stock).clean()


def guarded_plug():
    """One printed guided boot body with four integral fences and round roots."""
    return b.plug().fuse(collar_skin()).fuse(fences()).clean()


def receiver_slots():
    return _fence_prism(0, TIP + RECEIVER_AXIAL_RELIEF, RECEIVER_CLEARANCE)


def receiver_cup():
    """Circle-receiving cup with the saved 36-degree roof and short top flat.

    profile(r,r) contains the full circle r. The flat limits the roof height and
    bridge length; a fully pointed teardrop would leave less than 1 mm top stock.
    This is a printing intent, not a sliced or physical support-free result.
    """
    r = GUARD_R + RECEIVER_CLEARANCE
    return u.profile(r, r, u.FACE - .1, 0)


@contextmanager
def _socket_dimensions():
    """Scoped evaluation of the saved socket's size parameters; always restore them."""
    original = u.BODY_R, u.FLANGE_R
    u.BODY_R, u.FLANGE_R = SOCKET_BODY_R, SOCKET_FLANGE_R
    try:
        yield
    finally:
        u.BODY_R, u.FLANGE_R = original


def guarded_socket():
    """Wider saved socket with cage channels, existing leaves and roofed cup."""
    with _socket_dimensions():
        stock = u.socket()
    return stock.cut(receiver_cup()).cut(receiver_slots()).clean()


def guarded_coupon():
    """Matching 6 mm wall coupon for the widened snap-in receiver."""
    with _socket_dimensions():
        return u.coupon()


def guarded_receiver_wall():
    with _socket_dimensions():
        return u.wall_patch()


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _support_review(guard):
    vertices, _ = guard.tessellate(.003, .02)
    points = np.unique(np.asarray([(v.x, v.z) for v in vertices]), axis=0)
    hull = points[ConvexHull(points).vertices]
    angles = np.linspace(0, 2 * math.pi, 36000, endpoint=False)
    normals = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    tubes = np.array([[x, z, od / 2] for x, z, od in u.PORTS.values()])
    tube_support = np.max(tubes[:, :2] @ normals.T + tubes[:, 2:3], axis=0)
    guard_support = np.max(hull @ normals.T, axis=0)
    margins = guard_support - tube_support
    i = int(np.argmin(margins))
    return {
        "sampled_lateral_normals": len(angles),
        "minimum_planar_obstacle_lead_mm": float(margins[i]),
        "minimum_at_normal_degrees": float(angles[i] * 180 / math.pi),
        "guard_radial_diameter_mm": float(2 * max(np.linalg.norm(points, axis=1))),
        "method": "Native cage tessellation projected to X/Z; convex-hull support compared with exact circular tube support. Broad planar lateral obstacles only.",
        "scope": "Nominal rigid-body geometry. Open corner slots admit narrow protrusions. This does not rate impact, stiffness, fatigue, print variation or permanent tube alignment.",
    }


def review():
    guard, plug, socket = fences(), guarded_plug(), guarded_socket()
    wall = guarded_receiver_wall()
    baseline = b.plug()
    protected_addition = plug.cut(baseline)
    record = {
        "schema": 1,
        "reviewed_local_date": "2026-10-09",
        "status": "geometric protection candidate; not a print or functional qualification",
        "sources_sha256": {str(p.relative_to(ROOT)): _sha(p) for p in [Path(__file__).resolve(), EXPLORATION / "umbilical.py", EXPLORATION / "boot_concept.py", Path(u.U.__file__), Path(u.P.__file__)]},
        "parameters_mm": {
            "counter_hole_diameter": u.COUNTER_HOLE,
            "guard_outer_diameter": 2 * GUARD_R,
            "guard_inner_diameter": 2 * (GUARD_R - GUARD_WALL),
            "nominal_annulus_radial_stock": GUARD_WALL,
            "union_ring_clearance": RING_CLEARANCE,
            "socket_clearance": RECEIVER_CLEARANCE,
            "guard_tip_axial_relief": RECEIVER_AXIAL_RELIEF,
            "guard_projection": TIP,
            "quarter_tube_projection": b.STUB_Q,
            "drain_tube_projection": b.STUB_D,
            "tip_lead_over_quarter_tubes": TIP_LEAD,
            "root_collar_length": ROOT_LENGTH,
            "root_lead_length": ROOT_LEAD_LENGTH,
            "root_maximum_radial_growth_per_axial_mm": .5,
            "outer_wing_edge_radius": EDGE_RADIUS,
            "socket_body_radius": SOCKET_BODY_R,
            "socket_flange_radius": SOCKET_FLANGE_R,
            "counter_radial_clearance": u.COUNTER_HOLE / 2 - GUARD_R,
        },
        "closed_shell_bounds_mm": {
            "present_layout_without_wall_or_clearance": 2 * u.R_AXIS + u.U.RING_D,
            "three_quarter_rings_optimally_repacked_without_wall_or_clearance": u.U.RING_D * (1 + 2 / math.sqrt(3)),
            "three_quarter_rings_with_1_mm_wall_0_25_mm_clearance": u.U.RING_D * (1 + 2 / math.sqrt(3)) + 2 * (RING_CLEARANCE + 1.0),
            "scope": "First bound is for present coplanar axes. Second/third bound use three equal non-overlapping disks; the fourth union and fluid/electrical geometry add requirements. No claim about all staggered connector architectures.",
            "ring_band_length": u.U.RING_LEN,
            "between_ring_waist_length": u.U.BARREL_LEN,
            "ring_in_waist_nominal_axial_slack": u.U.BARREL_LEN - u.U.RING_LEN,
            "independent_union_float": u.NOSE_AIR + u.U.COLLET_TRAVEL,
        },
        "removable_cap_bound_mm": {
            "diameter_for_stub_envelope_plus_1_5_wall_0_25_clearance": 2 * (u.R_AXIS + 6.35 / 2 + 1.5 + .25),
            "scope": "A removable cap covers bare stubs only; attachment to the Ø34 boot and protection during coupling need separate design.",
        },
        "lateral_protection": _support_review(guard),
        "sharp_cusp_upper_bound_lateral_protection": _support_review(sharp_fences()),
        "native_solids": {
            "fence_count_before_joining_boot": len(guard.Solids()),
            "guard_valid": guard.isValid(),
            "protected_plug_solid_count": len(plug.Solids()),
            "protected_plug_valid": plug.isValid(),
            "modified_socket_solid_count": len(socket.Solids()),
            "modified_socket_valid": socket.isValid(),
            "matching_receiver_wall_solid_count": len(wall.Solids()),
            "matching_receiver_wall_valid": wall.isValid(),
            "added_printed_volume_mm3": protected_addition.Volume(),
            "new_separate_parts": 0,
            "new_moving_parts": 0,
            "new_wetted_joints": 0,
        },
        "roots": [
            {"fence_index": i, "existing_boot_common_volume_mm3": s.intersect(baseline).Volume(),
             "collar_common_volume_mm3": s.intersect(collar_skin()).Volume()}
            for i, s in enumerate(guard.Solids())
        ],
        "intersections_mm3": {
            "mated_protected_plug_socket": plug.intersect(socket).Volume(),
            "socket_receiver_wall": socket.intersect(wall).Volume(),
            "addition_key": protected_addition.intersect(b.key()).Volume(),
            "addition_fluid_guides": {},
            "addition_tubes": {},
            "addition_hardware": {},
            "addition_unions": {},
            "release_plate_bearing_stock_removed": {},
            "rigid_plug_outside_counter_bore": plug.cut(u.cyl(u.COUNTER_HOLE, b.ENTRY - .1, TIP + .1)).Volume(),
            "insertion_steps": {},
        },
        "cup_mm": {
            "radius": GUARD_R + RECEIVER_CLEARANCE,
            "top_flat_z": GUARD_R + RECEIVER_CLEARANCE,
            "top_bridge_length": 2 * u.profile_corners(GUARD_R + RECEIVER_CLEARANCE, GUARD_R + RECEIVER_CLEARANCE)[2],
            "top_outer_stock": u.BODY_F - (GUARD_R + RECEIVER_CLEARANCE),
            "snap_clearance_slot_inner_x": SOCKET_BODY_R - 1.5 - 1.9,
            "cup_to_snap_clearance_slot_stock_at_x_axis": SOCKET_BODY_R - 1.5 - 1.9 - (GUARD_R + RECEIVER_CLEARANCE),
            "scope": "Roof angle, snap leaf thickness and deflection gap inherited from the socket. Socket/receiver widened 2.4 mm in total to preserve 1.55 mm cup-to-slit stock. Top bridge and fence/support orientation are not print qualified.",
        },
        "confined_space_mm": {
            "boot_body_length": b.TOTAL_L if hasattr(b, 'TOTAL_L') else -b.ENTRY,
            "inserted_body_length": -u.FACE,
            "seated_body_outside_wall": -b.ENTRY + u.FACE,
            "bare_tube_initial_approach_stroke": -u.FACE + b.STUB_Q,
            "guard_initial_approach_stroke": -u.FACE + TIP,
            "bare_tube_rigid_axial_approach_envelope": -b.ENTRY + b.STUB_Q,
            "guard_rigid_axial_approach_envelope": -b.ENTRY + TIP,
            "scope": "Rigid axial approach only; excludes bundle bend, hands and installation obstructions.",
        },
        "limits": [
            "The open cage shields broad plane contact; narrow objects can enter its corner windows and insertion face.",
            "Guard and receiver remain exploratory. The saved trial is the unguarded boot; no new print has been sliced or launched.",
            "The 4 mm union envelope and release geometry remain provisional; its clearance cuts require the selected part's actual envelope.",
            "The longer guard adds 2 mm approach stroke; it does not shorten the 98 mm boot or establish acceptable confined-space UX.",
            "Socket/frame outer width is 2.4 mm greater than the saved baseline; the matching coupon is modeled but integration and printing are unqualified.",
            "The rounded 1 mm outer tip feature has only about 0.52 mm nominal broad-plane lead; actual extrusion, stiffness and handling must establish whether that margin is useful.",
        ],
    }
    intersections = record["intersections_mm3"]
    saved_socket = u.socket()
    for name, (x, z, od) in u.PORTS.items():
        d = b.GUIDE_Q if od > 5 else b.GUIDE_D
        guide = u.cyl(d, b.GUIDE_START, .1, x, z)
        intersections["addition_fluid_guides"][name] = protected_addition.intersect(guide).Volume()
        tube = u.cyl(od, b.GUIDE_START, b.tip(name), x, z)
        intersections["addition_tubes"][name] = protected_addition.intersect(tube).Volume()
        collet_d = u.U.COLLET_D if od > 5 else 8.0
        collet_bore = u.U.COLLET_BORE if od > 5 else u.HOLE_D
        bearing = u.cyl(collet_d, u.RELEASE - .01, u.RELEASE + .01, x, z).cut(
            u.cyl(collet_bore, u.RELEASE - .02, u.RELEASE + .02, x, z))
        intersections["release_plate_bearing_stock_removed"][name] = saved_socket.intersect(bearing).cut(socket).Volume()
        if od > 5:
            union = u.U.build_jg_pp0408w().val().located(u.union_location(x, z, u.COLLET_Q))
        else:
            union = u.auc44m(x, z, u.DRAIN_STOP - u.D_L + 1.8)
        intersections["addition_unions"][name] = {
            "mated": protected_addition.intersect(union).Volume(),
            "forward_1_835_mm": protected_addition.intersect(union.translate((0, -(u.NOSE_AIR + u.U.COLLET_TRAVEL), 0))).Volume(),
        }
    hardware = u.pogo_hardware(+1) + [(f"magnet-{i}", s) for i, (_, s) in enumerate(u.bars(+1))]
    hardware += [("pogo", u.P.build_male().val().located(u.pogo_location(+1)))]
    for name, shape in hardware:
        intersections["addition_hardware"][name] = protected_addition.intersect(shape).Volume()
    for dy in (-(-u.FACE + TIP), -34, -26.3, -13.04, -9.8, -2, 0):
        # The receiver also clears the whole guard in its enlarged entrance cup.
        intersections["insertion_steps"][str(dy)] = plug.translate((0, dy, 0)).intersect(socket).Volume()
    record["union_sweep_argument"] = "Every cage sector is cut outside the maximum full-ring cylinders along its complete positive-Y length; axial translation and independent union float therefore cannot bring a ring into the cage at these fixed axes. This conservative sweep also excludes thicker collets only if the actual selected parts remain within the ring envelope."
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", type=Path)
    args = parser.parse_args()
    record = review()
    destination = HERE / "protection-candidate.json"
    destination.write_text(json.dumps(record, indent=2) + "\n")
    if args.export_dir:
        args.export_dir.mkdir(parents=True, exist_ok=True)
        for name, shape in (("open-guard", fences()), ("guarded-plug", guarded_plug()), ("guarded-socket", guarded_socket()), ("guarded-coupon", guarded_coupon())):
            u.cq.exporters.export(shape, str(args.export_dir / (name + ".step")))
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
