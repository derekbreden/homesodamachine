"""Floating, hand-adjustable tube organizer; dimensions in millimetres.

The puck is a candidate. The context contains proposed lower routing and
union positions, using the retained faucet's mounting and tube datums.
This script does not alter the production faucet assembly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "hardware/faucet-layout"))
import faucet_assembly as faucet

OD = 32.0
LENGTH = 10.0
TUBE_BORE = 6.55
DRAIN_BORE = 4.10
CABLE_BORE = 5.0
ENTRY = 0.40
OUTSIDE_EASE = 0.60
TOP_Z = -88.0
UNION_GAP_BELOW = 7.0
RIBBON_XY = (5.45, 11.50)

# Circumcentre of the three equal-diameter tube axes minimizes the round stock.
AX = faucet.union_x(+1)
BX = faucet.union_x(-1)
FY = faucet.flavor_tube_depth_lower
CX = (AX + BX) / 2
CY = ((AX - CX) ** 2 + FY ** 2 - CX ** 2) / (2 * FY)
BORES = (
    {"name": "S", "label": "Soda", "xy": (0.0, 0.0), "bore": TUBE_BORE, "tube_od": 6.35},
    {"name": "F1", "label": "Flavor A", "xy": (AX, FY), "bore": TUBE_BORE, "tube_od": 6.35},
    {"name": "F2", "label": "Flavor B", "xy": (BX, FY), "bore": TUBE_BORE, "tube_od": 6.35},
    {"name": "D", "label": "Drain", "xy": (0.0, faucet.drain_bypass_y), "bore": DRAIN_BORE, "tube_od": 4.0},
    {"name": "SIG", "label": "Loose signal cable", "xy": RIBBON_XY, "bore": CABLE_BORE},
)


def build_puck(*, length=LENGTH, tube_bore=TUBE_BORE, drain_bore=DRAIN_BORE):
    """One cylinder, four friction bores and a round cable clearance passage."""
    body = cq.Workplane("XY").circle(OD / 2).extrude(length)
    body = body.edges("%Circle").chamfer(OUTSIDE_EASE)
    for station in BORES:
        x, y = station["xy"][0] - CX, station["xy"][1] - CY
        diameter = CABLE_BORE if station["name"] == "SIG" else drain_bore if station["name"] == "D" else tube_bore
        r = diameter / 2
        # The cable gets a smaller entrance relief to preserve broad webs.
        entry = 0.20 if station["name"] == "SIG" else ENTRY
        bore = cq.Solid.makeCylinder(r, length + 2, cq.Vector(x, y, -1))
        bottom = cq.Solid.makeCone(r + entry, r, entry, cq.Vector(x, y, 0))
        top = cq.Solid.makeCone(r, r + entry, entry, cq.Vector(x, y, length-entry))
        body = body.cut(bore.fuse(bottom, top))
    return body.val().clean()


def installed_puck(puck):
    return puck.translate((CX, CY, TOP_Z - LENGTH))


def cylinder(xy, radius, bottom, top):
    return cq.Solid.makeCylinder(radius, top-bottom, cq.Vector(*xy, bottom))


def window(shape, bottom, top, width=180):
    shape = shape.val() if hasattr(shape, "val") else shape
    return shape.intersect(cq.Solid.makeBox(width, width, top-bottom,
                                         cq.Vector(-width/2, -width/2, bottom)))


def s_return(start, end, radius, after_z):
    """Two tangent circular arcs, entering and leaving vertically downward."""
    dx, dy = end[0]-start[0], end[1]-start[1]
    offset = math.hypot(dx, dy)
    angle = math.acos(1-offset/(2*radius))
    rise = 2*radius*math.sin(angle)
    ux, uy = dx/offset, dy/offset
    z0 = start[2]

    def world(p):
        return cq.Vector(start[0]+ux*p[0], start[1]+uy*p[0], z0+p[1])

    a_mid, a_end, tangent = faucet._arc_from_tangent(
        (0.0, 0.0), (0.0, -1.0), radius, angle, ccw=True)
    b_mid, b_end, _ = faucet._arc_from_tangent(a_end, tangent, radius, angle, ccw=False)
    edges = [cq.Edge.makeThreePointArc(world((0.0, 0.0)), world(a_mid), world(a_end)),
             cq.Edge.makeThreePointArc(world(a_end), world(b_mid), world(b_end))]
    finish = world(b_end)
    edges.append(cq.Edge.makeLine(finish, cq.Vector(end[0], end[1], after_z)))
    return cq.Wire.assembleEdges(edges), z0-rise


def swept_tube(path, xy, z, radius):
    return (cq.Workplane("XY").workplane(offset=z).center(*xy)
            .circle(radius).sweep(cq.Workplane(obj=path), transition="round").val())


def build_context(puck):
    """Native mounting stock, proposed straight grip and downstream unions.

    Cable continuation is represented only through the puck: the existing
    native cable drawing ends at Z=-50 and does not define this lower route.
    Foam is shown downstream of the white faucet's two staggered unions.
    """
    parts = [{"name": "organizer", "material": "organizer", "shape": installed_puck(puck)}]
    parts += [
        {"name": "countertop", "material": "counter", "shape": faucet.build_countertop().val()},
        {"name": "steel plate", "material": "steel", "shape": faucet.build_under_counter_plate().val()},
        {"name": "faucet shank", "material": "fixture", "shape": window(faucet.load_westbrass(), -50, 0)},
    ]
    union_b_top = TOP_Z-LENGTH-UNION_GAP_BELOW
    union_a_top = union_b_top-faucet.union_length
    union_foot = union_a_top-faucet.union_length
    bottom = union_foot-65
    foam_top = union_foot-max(faucet.gather_rise(+1), faucet.gather_rise(-1), faucet.drain_gather_rise)
    at_plate_z = faucet.under_counter_plate_bottom_z
    for sign, label in ((+1, "F1"), (-1, "F2")):
        union_top = union_a_top if sign > 0 else union_b_top
        tube_stop = union_top-faucet.union.INSERTION
        at_plate = (faucet.flavor_mount_x(sign), FY, at_plate_z)
        upper = faucet._flavor_tube(faucet._step_path(sign, tube_stop)).val().translate(at_plate)
        parts.append({"name": label+" upper tube", "material": "flavor", "shape": upper})
        fitting = faucet.build_flavor_union(sign).val().translate((0, 0, union_top-faucet.union_top_z(sign)))
        parts.append({"name": label+" union", "material": "union", "shape": fitting})
        start_z = tube_stop-faucet.union_gap
        # Use the retained R30 gather, with the straight upper and lower reaches extended.
        path = faucet._gather_path(sign, faucet.union_foot_z+(start_z-union_foot))
        tube = faucet._flavor_tube(path, start_z-union_foot).val().translate((faucet.union_x(sign), FY, union_foot))
        tube = window(tube, bottom, start_z)
        parts.append({"name": label+" lower tube", "material": "flavor", "shape": tube})
    parts.append({"name": "Soda tube", "material": "soda",
                  "shape": cylinder((0, 0), 6.35/2, bottom, -50)})

    # Drain reaches its parallel bypass axis before the organizer, rather than
    # keeping the existing later return through the proposed grip station.
    start_xy = (faucet._fi.drain_tube_x, faucet._fi.drain_tube_y)
    drain_upper_path, drain_straight_top = s_return(
        (*start_xy, faucet.mount_return_start_z), (0.0, faucet.drain_bypass_y),
        faucet.drain_bend_radius, union_foot)
    drain_upper = swept_tube(drain_upper_path, start_xy, faucet.mount_return_start_z, 2)
    lead = cylinder(start_xy, 2, faucet.mount_return_start_z, at_plate_z)
    drain_lower_path, _ = s_return((0.0, faucet.drain_bypass_y, union_foot),
                                  (0.0, faucet.drain_pack_y), faucet.drain_bend_radius, bottom)
    drain_lower = swept_tube(drain_lower_path, (0.0, faucet.drain_bypass_y), union_foot, 2)
    parts.append({"name": "Drain tube", "material": "drain", "shape": drain_upper.fuse(lead, drain_lower).clean()})
    foam = (cq.Workplane("XY").workplane(offset=bottom)
            .circle(faucet.foam_r).circle(6.35/2).extrude(foam_top-bottom).val())
    parts.append({"name": "Cold-line foam", "material": "foam", "shape": foam})
    cable = (cq.Workplane("XY").workplane(offset=TOP_Z-LENGTH-12)
             .center(*RIBBON_XY).rect(faucet.cable_width, faucet.cable_lane).extrude(LENGTH+24).val())
    parts.append({"name": "Loose cable passage", "material": "cable", "shape": cable})
    return parts, {"union_b_top_z": union_b_top, "union_a_top_z": union_a_top,
                   "union_foot_z": union_foot, "foam_top_z": foam_top,
                   "drain_parallel_from_z": drain_straight_top,
                   "plate_bottom_z": at_plate_z, "plate_to_organizer_mm": at_plate_z-TOP_Z,
                   "shank_bottom_to_organizer_mm": -50-TOP_Z}


def mesh(shape):
    vertices, faces = shape.tessellate(0.12, 0.18)
    return {"vertices": [round(c, 4) for v in vertices for c in v.toTuple()],
            "triangles": [i for face in faces for i in face]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--view-data", type=Path, help="Optional mesh JSON for the inline view")
    args = parser.parse_args()
    puck = build_puck()
    if not puck.isValid() or len(puck.Solids()) != 1:
        raise ValueError("Organizer must be one valid solid")
    cq.exporters.export(puck, str(HERE / "organizer.step"))
    cq.exporters.export(puck, str(HERE / "organizer.stl"), tolerance=0.05, angularTolerance=0.12)
    context, positions = build_context(puck)
    minimum_web = min(math.dist(a["xy"], b["xy"])-(a["bore"]+b["bore"])/2
                      for i, a in enumerate(BORES) for b in BORES[i+1:])
    minimum_wall = min(OD/2-math.dist((CX, CY), b["xy"])-b["bore"]/2 for b in BORES)
    facts = {"status": "candidate; physical sliding fit unqualified", "material": "PET-GF",
             "od_mm": OD, "length_mm": LENGTH, "center_xy": [CX, CY],
             "smooth_contact_length_mm": LENGTH-2*ENTRY,
             "bores": BORES, "nominal_diametral_clearance_mm": {
                 "quarter_inch": round(TUBE_BORE-6.35, 3), "drain": round(DRAIN_BORE-4.0, 3)},
             "outer_edge_chamfer_mm": OUTSIDE_EASE, "entry_chamfer_mm": ENTRY,
             "min_straight_bore_web_mm": round(minimum_web, 4),
             "min_straight_bore_outer_wall_mm": round(minimum_wall, 4),
             "native_faces": len(puck.Faces()), "native_edges": len(puck.Edges()),
             "solid_volume_mm3": round(puck.Volume(), 3), "installed": positions,
             "nominal_braided_od_mm": OD+2*faucet.sleeve_wall,
             "counter_hole_mm": faucet.countertop_hole_diameter,
             "context_limits": ["Proposed lower routing and union positions",
                                "Retained washer, nut and compression fitting are not modeled",
                                "Cable continuation shown only near the puck",
                                "No modeled jacket weave or physical compression measurement"],
             "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "faucet_source_sha256": hashlib.sha256(Path(faucet.__file__).read_bytes()).hexdigest(),
             "stl_sha256": hashlib.sha256((HERE/"organizer.stl").read_bytes()).hexdigest()}
    (HERE / "geometry.json").write_text(json.dumps(facts, indent=2)+"\n")
    if args.view_data:
        data = {"facts": facts, "puck": mesh(puck),
                "context": [{"name": p["name"], "material": p["material"], **mesh(p["shape"])} for p in context]}
        args.view_data.parent.mkdir(parents=True, exist_ok=True)
        args.view_data.write_text(json.dumps(data, separators=(",", ":")))
    print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
