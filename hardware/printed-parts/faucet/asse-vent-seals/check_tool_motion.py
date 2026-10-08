"""Native assembly-motion witness for the consumer faucet vent-seal tool.

No production solids are changed. The casing witness is the native circular
neck minus build_vent_cavity and the actual female socket cutter. It retains
the material of the bottom outlet as a conservative extra obstruction. A
concentric annular envelope bounds the sleeve at every rotational position;
sampled native poses additionally check the complete tool and real tubes.
"""

from __future__ import annotations

import hashlib
import argparse
import ast
import json
import math
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
REPO = next(path for path in HERE.parents
            if (path / "hardware").is_dir() and (path / "tools").is_dir())
sys.path[:0] = [str(FAUCET), str(FAUCET / "faucet-shell"),
               str(REPO / "hardware" / "faucet-layout")]

import cadquery as cq
import faucet_paths as p
import faucet_shell as f
import vent_seals as v
import faucet_assembly as a


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_paths():
    return {"checker": Path(__file__), "tool_generator": Path(v.__file__),
            "paths": Path(p.__file__), "shell": Path(f.__file__),
            "assembly": Path(a.__file__), "interface": FAUCET / "_faucet_interface.py",
            "plate": FAUCET / "above-counter-plate" / "above_counter_plate.py",
            "gasket": FAUCET / "above-counter-gasket" / "above_counter_gasket.py"}


def volume(shape):
    return sum(s.Volume() for s in shape.Solids())


def circular_solid(kind, od, sign=1):
    wire = p.path_wire(kind, sign=sign, end_s=(None if kind == "drain"
                                             else p.CONVERGE_START_S))
    start = wire.Edges()[0].startPoint()
    plane = cq.Plane(origin=start, xDir=(1, 0, 0), normal=(0, 0, 1))
    return cq.Workplane(plane).circle(od/2).sweep(cq.Workplane(obj=wire),
                                               transition="round").val()


def soda_solid():
    start = p.arc_point(0)
    arc_end = p.arc_point(p.TOTAL_ANGLE)
    end = (arc_end[0], arc_end[1]-p.TIP_LENGTH*math.sin(p.TOTAL_ANGLE),
           arc_end[2]+p.TIP_LENGTH*math.cos(p.TOTAL_ANGLE))
    edges = [cq.Edge.makeLine(cq.Vector(0, p.WATER_Y, -6.2), cq.Vector(*start)),
             cq.Edge.makeThreePointArc(cq.Vector(*start),
                 cq.Vector(*p.arc_point(p.TOTAL_ANGLE/2)), cq.Vector(*arc_end)),
             cq.Edge.makeLine(cq.Vector(*arc_end), cq.Vector(*end))]
    wire = cq.Wire.assembleEdges(edges)
    return (cq.Workplane("XY", origin=(0, p.WATER_Y, -6.2)).circle(p.WATER_OD/2)
            .sweep(cq.Workplane(obj=wire), transition="round").val())


def peeled_wire(x):
    a = p.JOINT_ANGLE + p.SPREAD_END_S/p.WATER_RADIUS
    b = p.JOINT_ANGLE + p.CONVERGE_START_S/p.WATER_RADIUS
    points = [cq.Vector(*p.arc_point(q, x, v.WIRE_N)) for q in (a, (a+b)/2, b)]
    edge = cq.Edge.makeThreePointArc(*points)
    plane = cq.Plane(origin=points[0], xDir=(1, 0, 0),
                     normal=(0, -math.sin(a), math.cos(a)))
    return (cq.Workplane(plane).circle(0.65)
            .sweep(cq.Workplane(obj=cq.Wire.assembleEdges([edge]))).val())


def ribbon_fan_bound():
    # The entire 7.9 x 1.3 envelope conservatively contains the actual joined
    # 4.1 mm ribbon and its widening fan before the individually peeled run.
    wire = p.path_wire("ribbon", end_s=p.SPREAD_END_S)
    start = wire.Edges()[0].startPoint()
    plane = cq.Plane(origin=start, xDir=(1, 0, 0), normal=(0, 0, 1))
    return (cq.Workplane(plane).rect(7.9, 1.3)
            .sweep(cq.Workplane(obj=wire), transition="round").val())


BOUND_FUNCTIONS=("_round_cavity_segment","_gland_plane","_gland_world",
                 "_gland_halfspace","build_vent_cavity","_split_plane_halfspace",
                 "_tube_shell_outer_shrunk_sketch","_build_bend_overlap",
                 "_sweep_segment_in_path_local","_bend_overlap_subarc")


def bound_signature():
    tree=ast.parse(Path(f.__file__).read_text())
    functions={node.name:ast.dump(node,include_attributes=False) for node in tree.body
               if isinstance(node,ast.FunctionDef) and node.name in BOUND_FUNCTIONS}
    assert set(functions)==set(BOUND_FUNCTIONS)
    parameters={name:getattr(f,name) for name in (
        "split_junction_rot","split_socket_overlap_len","split_socket_shrink",
        "tube_shell_center_y","tube_shell_outer_r","gn_bend1_r",
        "soda_faucet_tube_y","zone5_z_top","_path_socket_start",
        "_path_socket_mid","_path_junction","_tan_at_socket_start")}
    return hashlib.sha256(json.dumps({"functions":functions,"parameters":parameters},
                                    sort_keys=True).encode()).hexdigest()


def lower_ribbon_signature():
    names=("_lower_signal_stations","_lower_signal_profile","_lower_signal_solid",
           "build_lower_signal_ribbon")
    tree=ast.parse(Path(f.__file__).read_text())
    functions={node.name:ast.dump(node,include_attributes=False) for node in tree.body
               if isinstance(node,ast.FunctionDef) and node.name in names}
    assert set(functions)==set(names)
    parameters={name:getattr(f,name) for name in (
        "signal_lower_exit_x","signal_lower_exit_y","signal_lower_exit_angle",
        "signal_ribbon_max_width","signal_ribbon_max_depth","flavor_tube_depth")}
    assembly_parameters={name:getattr(a,name) for name in (
        "under_counter_plate_bottom_z","union_foot_z","umbilical_bend_radius",
        "cable_width","cable_lane")}
    return hashlib.sha256(json.dumps({"functions":functions,"parameters":parameters,
                                    "assembly_source_sha256":sha(a.__file__),
                                    "assembly_parameters":assembly_parameters},
                                    sort_keys=True).encode()).hexdigest()


def lower_ribbon_motion_bound():
    """Bound the complete tool over rotation and its specified inward removal."""
    major=p.WATER_RADIUS+p.SHELL_CENTER_N
    handle_radius=v.TOOL_HANDLE_OD/2
    # A tangent handle extrusion increases the radial offset by no more than
    # this amount, measured at its smallest possible distance from the axis.
    inflation=math.hypot(major-handle_radius,v.TOOL_HANDLE_LENGTH)-(major-handle_radius)
    minor=handle_radius+inflation
    centre=cq.Vector(0,p.WATER_Y-p.WATER_RADIUS,p.ARC_START_Z)
    torus=cq.Solid.makeTorus(major,minor,pnt=centre,dir=cq.Vector(1,0,0))
    cylinder=cq.Solid.makeCylinder(major,2*minor,
                                   pnt=centre-cq.Vector(minor,0,0),dir=cq.Vector(1,0,0))
    bound=torus.fuse(cylinder)
    lower=a.build_lower_display_ribbon().val()
    # Every tool point lies within this angle of the radial removal direction.
    # Its radius decreases throughout 0..40 mm because shift < 2*r*cos(angle).
    angle=v.TOOL_ARC_LENGTH/(2*p.WATER_RADIUS)+math.atan2(
        v.TOOL_HANDLE_LENGTH,major-handle_radius)
    monotonic_limit=2*(major-handle_radius)*math.cos(angle)
    gap=bound.distance(lower)
    overlap=volume(bound.intersect(lower))
    passed=(bound.isValid() and len(bound.Solids())==1
            and lower.isValid() and len(lower.Solids())==1
            and monotonic_limit>40.0 and overlap<=1e-5 and gap>=0.10)
    return bound,{"bound_valid":bound.isValid(),"bound_solid_count":len(bound.Solids()),
                  "lower_cable_valid":lower.isValid(),"lower_cable_solid_count":len(lower.Solids()),
                  "lower_cable_volume_mm3":volume(lower),
                  "tool_axis_radius_mm":major,"handle_radius_mm":handle_radius,
                  "handle_tangent_length_mm":v.TOOL_HANDLE_LENGTH,
                  "radial_handle_inflation_mm":inflation,"bound_minor_radius_mm":minor,
                  "maximum_point_angle_from_removal_midpoint_rad":angle,
                  "maximum_checked_side_shift_mm":40.0,
                  "radial_monotonic_shift_limit_mm":monotonic_limit,
                  "minimum_native_bound_to_lower_ribbon_gap_mm":gap,
                  "native_bound_lower_ribbon_overlap_mm3":overlap,
                  "passed":passed,
                  "method":"Full 360-degree torus containing the complete curved tool and tangent handle, filled inward by a concentric cylinder. Rotation about the true water-arc axis leaves this bound invariant. The specified inward side translation decreases every tool point's radial distance throughout 0..40 mm, so it stays in the filled bound.",
                  "scope":"Continuous nominal tool motion versus the assembled lower ribbon envelope, including its flat rear mounting exit and below-plate return drawn to Z-50. Casing, upper tubes and finished print handling have separate witnesses."}


def refresh_bounds():
    """Rebind the continuous casing proof without repeating unchanged tube poses."""
    begun=time.time()
    current_paths=source_paths()
    current_sources={name:sha(path) for name,path in current_paths.items()}
    target=HERE/"tool-motion-check.json"
    report=json.loads(target.read_text())
    cached=report.get("native_pose_source_sha256",report["source_sha256"])
    assert sha(p.__file__)==cached["paths"],"Tube paths changed; run complete motion check"
    assert sha(v.__file__)==cached["tool_generator"],"Tool source changed; run complete motion check"
    for name in ("assembly","interface","plate","gasket"):
        assert sha(current_paths[name])==cached.get(name),f"{name} changed; run complete motion check"
    signature=bound_signature()
    lower_signature=lower_ribbon_signature()
    previous_signature=report.get("continuous_bound_geometry_signature_sha256")
    if "continuous_bound_source_sha256" in report:
        prior={"source_sha256":report["continuous_bound_source_sha256"],
               "geometry_signature_sha256":previous_signature,
               "continuous_bounds":report["continuous_bounds"],
               "dependencies_unchanged_during_check":report["continuous_bound_dependencies_unchanged_during_check"],
               "elapsed_seconds":report["continuous_bound_elapsed_seconds"]}
        witnesses=report.setdefault("prior_continuous_bound_witnesses",[])
        if not witnesses or witnesses[-1]!=prior:
            witnesses.append(prior)
    entry_s=-f.split_socket_overlap_len
    origin,_,tangent=p.station_plane(entry_s,center_n=p.SHELL_CENTER_N)
    entry_half=f._split_plane_halfspace(origin,tangent,1).val()
    socket=f._build_bend_overlap(f._tube_shell_outer_shrunk_sketch(f.split_socket_shrink),side="socket")
    void=f.build_vent_cavity().union(socket).val()
    outer=f._round_cavity_segment(entry_s,p.CONVERGE_START_S+5,radius=p.SHELL_RADIUS).val()
    casing=outer.cut(void)
    tool=v.build_perimeter_tool()
    lower_bound,lower_record=lower_ribbon_motion_bound()
    records=[]
    failures=[]
    if not lower_record["passed"]:
        failures.append("continuous complete-tool bound obstructs the current lower ribbon")
    for name,station,upstream in (("upstream",p.UPSTREAM_GLAND_S,True),
                                   ("downstream",p.DOWNSTREAM_GLAND_S,False)):
        # Verify the complete current pose shares the original true arc axis.
        o,xdir,tangent=f._gland_plane(station,0)
        plane=cq.Plane(origin=o,xDir=xdir,normal=tangent)
        centre=cq.Vector(0,-(p.WATER_RADIUS+p.SHELL_CENTER_N),v.BODY_MID_Z).transform(plane.rG)
        expected=cq.Vector(0,p.WATER_Y-p.WATER_RADIUS,p.ARC_START_Z)
        assert (centre-expected).Length<1e-7
        midpoint=cq.Vector(0,0,v.BODY_MID_Z).transform(plane.rG)
        actual_expected=cq.Vector(*p.station_point(station+p.GLAND_MID_SHIFT_S,n=p.SHELL_CENTER_N))
        assert (midpoint-actual_expected).Length<1e-7
        envelope=f._round_cavity_segment(entry_s-2,station+10,v.TOOL_OD/2).cut(
            f._round_cavity_segment(entry_s-2,station+10,v.TOOL_ID/2)).val()
        envelope=envelope.intersect(entry_half).intersect(
            f._gland_halfspace(station,v.BUNG_SEATED_Z,-1).val())
        seated_full=f._gland_world(tool,station).val()
        seated=seated_full.intersect(entry_half)
        row={"gland":name,"nominal_gland_station_mm":station,
             "volume_outside_native_void_mm3":volume(envelope.cut(void)),
             "casing_overlap_mm3":volume(envelope.intersect(casing)),
             "minimum_native_casing_gap_mm":seated_full.distance(casing),
             "annular_bound_casing_distance_diagnostic_mm":envelope.distance(casing),
             "minimum_analytical_keeper_edge_gap_over_rotation_mm":v.check_geometry()["minimum_pusher_keeper_edge_clearance_over_rotation_mm"],
             "fresh_seated_tool_outside_envelope_mm3":volume(seated.cut(envelope)),
             "fresh_seated_tool_casing_overlap_mm3":volume(seated.intersect(casing)),
             "complete_seated_tool_outside_lower_route_motion_bound_mm3":volume(seated_full.cut(lower_bound)),
             "feature_gaps_mm":{}}
        for feature,gland_s,is_us in (("upstream",p.UPSTREAM_GLAND_S,True),
                                     ("downstream",p.DOWNSTREAM_GLAND_S,False)):
            z=0
            for label,length in (("keeper",v.KEEPER_LENGTH),("flange_groove",v.GROOVE_LENGTH),
                                 ("body_seat",v.BODY_LENGTH),("backstop",v.STOP_LENGTH)):
                # Read the actual casing between native gland planes. Move
                # each witness face 0.0001 mm inside to keep the inspection
                # cutter clear of exactly coincident axial cavity faces.
                section=casing.intersect(f._gland_halfspace(gland_s,z+0.0001,1).val())
                section=section.intersect(f._gland_halfspace(gland_s,z+length-0.0001,-1).val())
                assert section.Solids(),(feature,label)
                row["feature_gaps_mm"][feature+"_"+label]=seated_full.distance(section)
                z+=length
        if max(row["volume_outside_native_void_mm3"],row["casing_overlap_mm3"],
               row["fresh_seated_tool_outside_envelope_mm3"],
               row["fresh_seated_tool_casing_overlap_mm3"],
               row["complete_seated_tool_outside_lower_route_motion_bound_mm3"])>1e-5:
            failures.append(name+" has a current native casing obstruction")
        print(json.dumps(row),flush=True)
        records.append(row)
    unchanged=(signature==bound_signature() and lower_signature==lower_ribbon_signature()
               and all(sha(path)==current_sources[name] for name,path in current_paths.items()))
    assert unchanged,"Casing dependencies changed during refresh"
    report["native_pose_source_sha256"]=cached
    report["native_pose_source_unchanged_during_check"]=report.pop(
        "source_unchanged_during_check",report.get("native_pose_source_unchanged_during_check"))
    report["continuous_bound_source_sha256"]=current_sources
    report["continuous_bound_geometry_signature_sha256"]=signature
    report["continuous_bound_geometry_matches_prior_witness"]=previous_signature==signature
    report["continuous_bound_dependencies_unchanged_during_check"]=unchanged
    report["native_pose_paths_and_tool_match_current_sources"]=True
    report["continuous_bounds"]=records
    report["current_lower_ribbon_continuous_motion_witness"]={
        **lower_record,"geometry_signature_sha256":lower_signature,
        "source_sha256":report["continuous_bound_source_sha256"],
        "dependencies_unchanged_during_check":unchanged}
    report["minimum_actual_tool_to_casing_gap_mm"]=min(
        pose["minimum_actual_tool_to_casing_gap_mm"] for pose in report["native_poses"])
    report["minimum_actual_tool_to_tube_gap_mm"]=min(
        min(pose["minimum_tube_gap_mm"].values()) for pose in report["native_poses"])
    report["minimum_analytical_keeper_edge_gap_over_rotation_mm"]=v.check_geometry()[
        "minimum_pusher_keeper_edge_clearance_over_rotation_mm"]
    report["continuous_bound_scope"]="The full annular sleeve bounds every rotational tool pose inside the current native casing. Current final poses and true arc axis are rechecked. Minimum clearance uses the actual tool plus the analytical planar-keeper corner bound; the annular-bound surface distance is diagnostic only. Original upper-tube and side-removal poses retain their own source bindings; their tool and path sources are identical to current inputs. A separate fresh full-rotation, inward-filled complete-tool bound checks the actual current lower ribbon. The port remains conservatively filled with casing in the casing witness."
    report["feature_gap_scope"]="Actual casing clipped by native gland planes, 0.0001 mm inside each axial feature boundary to avoid coincident witness faces."
    manifest=json.loads((HERE/"manifest.json").read_text())
    ds=next(part["cad_volume_mm3"] for part in manifest["parts"] if part["name"]=="asse-vent-downstream-bung")
    passage_area=math.pi/4*(v.UPSTREAM_STOP_ID**2-p.WATER_OD**2-2*p.FLAVOR_OD**2-4*1.3**2)
    report["intentional_elastic_installation"].update({
        "downstream_bung_free_volume_mm3":ds,
        "uniform_22mm_passage_available_area_after_tubes_mm2":passage_area,
        "minimum_uniform_22mm_compressed_axial_length_mm":ds/passage_area,
        "axial_bulge_required_beyond_free_length_mm":ds/passage_area-v.BUNG_LENGTH,
        "upstream_gland_available_axial_length_mm":v.GLAND_LENGTH,
        "drain_tube_during_distal_bung_loading":"D stays outside the tip until the downstream bung is seated; the tool poses additionally checked clearance with the final D geometry present.",
        "scope":"Conservative incompressible volume budget and required flange deflection; TPU snap-through force and retained capture are physical acceptance properties."})
    report["failures"]=failures
    report["passed"]=not failures and unchanged and all(
        pose["casing_overlap_mm3"]<1e-5 and max(pose["tube_overlap_mm3"].values())<1e-5
        for pose in report["native_poses"])
    report["continuous_bound_elapsed_seconds"]=time.time()-begun
    target.write_text(json.dumps(report,indent=2)+"\n")
    if not report["passed"]:
        raise SystemExit(1)


def main():
    begun = time.time()
    sources = source_paths()
    digests = {k: sha(path) for k, path in sources.items()}
    centre = (0, p.WATER_Y-p.WATER_RADIUS, p.ARC_START_Z)
    axis_end = (1, centre[1], centre[2])
    entry_s = -f.split_socket_overlap_len
    origin, _, tangent = p.station_plane(entry_s, center_n=p.SHELL_CENTER_N)
    entry_half = f._split_plane_halfspace(origin, tangent, 1).val()

    print("Building native socket, cavity, casing and tool", flush=True)
    socket = f._build_bend_overlap(
        f._tube_shell_outer_shrunk_sketch(f.split_socket_shrink), side="socket")
    void = f.build_vent_cavity().union(socket).val()
    outer = f._round_cavity_segment(entry_s, p.CONVERGE_START_S+5,
                                    radius=p.SHELL_RADIUS).val()
    casing = outer.cut(void)
    tool = v.build_perimeter_tool()
    assert casing.isValid() and tool.val().isValid()
    lower_bound,lower_record=lower_ribbon_motion_bound()

    print("Building actual nominal tubing and wire witnesses", flush=True)
    tubes = {"S": soda_solid(), "F1": circular_solid("flavor",p.FLAVOR_OD,-1),
             "F2": circular_solid("flavor",p.FLAVOR_OD,1),
             "D": circular_solid("drain",p.DRAIN_OD),
             "ribbon_fan_bound": ribbon_fan_bound()}
    tubes.update({f"wire-{i+1}": peeled_wire(x) for i,x in enumerate(v.WIRE_X)})
    assert all(s.isValid() for s in tubes.values())
    records = []
    envelope_records = []
    removal_records = []
    bad = []
    if not lower_record["passed"]:
        bad.append("continuous complete-tool bound obstructs the current lower ribbon")
    for name, station, retreats in (
            ("downstream",p.DOWNSTREAM_GLAND_S,(90,80,70,60,45,35,29.3,26,22,15,5,2,0)),
            ("upstream",p.UPSTREAM_GLAND_S,(65,55,45,30,15,5,2,0))):
        seated = f._gland_world(tool,station).val()
        if volume(seated.cut(lower_bound))>1e-5:
            bad.append(f"{name}: complete tool extends outside lower-route motion bound")
        # Rotation leaves every sleeve surface on this concentric torus.
        # Its upstream extent is clipped by the real socket entry plane and
        # its distal extent by the final flat flange-bearing plane. The
        # handle stays outside the socket throughout these motion intervals.
        envelope = f._round_cavity_segment(entry_s-2,station+10,v.TOOL_OD/2).cut(
            f._round_cavity_segment(entry_s-2,station+10,v.TOOL_ID/2)).val()
        envelope = envelope.intersect(entry_half).intersect(
            f._gland_halfspace(station,v.BUNG_SEATED_Z,-1).val())
        outside = envelope.cut(void)
        collision = envelope.intersect(casing)
        em = {"gland":name,"volume_outside_native_void_mm3":volume(outside),
              "casing_overlap_mm3":volume(collision),
              "annular_bound_casing_distance_diagnostic_mm":envelope.distance(casing),
              "minimum_actual_seated_tool_to_casing_gap_mm":seated.distance(casing),
              "minimum_analytical_keeper_edge_gap_over_rotation_mm":v.check_geometry()["minimum_pusher_keeper_edge_clearance_over_rotation_mm"]}
        print(json.dumps({"continuous_sleeve_envelope":em}),flush=True)
        envelope_records.append(em)
        if em["casing_overlap_mm3"] > 1e-5:
            bad.append(f"{name}: continuous sleeve envelope hits casing")
        for retreat in retreats:
            placed = seated.rotate(centre,axis_end,-math.degrees(retreat/p.WATER_RADIUS))
            inside = placed.intersect(entry_half)
            cm = volume(inside.intersect(casing)) if inside.Solids() else 0
            outside = volume(inside.cut(void)) if inside.Solids() else 0
            extra = volume(inside.cut(envelope)) if inside.Solids() else 0
            tube_hits = {k:volume(placed.intersect(s)) for k,s in tubes.items()}
            tube_gaps = {k:placed.distance(s) for k,s in tubes.items()}
            record = {"gland":name,"retreat_soda_path_mm":retreat,
                      "rotation_from_seated_deg":-math.degrees(retreat/p.WATER_RADIUS),
                      "tool_inside_socket_mm3":volume(inside),
                      "casing_overlap_mm3":cm,"outside_native_void_mm3":outside,
                      "minimum_actual_tool_to_casing_gap_mm":placed.distance(casing),
                      "outside_continuous_sleeve_bound_mm3":extra,
                      "tube_overlap_mm3":tube_hits,"minimum_tube_gap_mm":tube_gaps}
            print(json.dumps(record),flush=True)
            records.append(record)
            if cm>1e-5 or outside>1e-5 or extra>1e-5 or max(tube_hits.values())>1e-5:
                bad.append(f"{name}: retreat {retreat} has native obstruction")

        # Once withdrawn, the U-section comes off radially through its slot.
        # A single inward translation along the midpoint normal has positive
        # dot product with every local open-side normal over the 76 deg arc.
        retreat = retreats[0]
        withdrawn = seated.rotate(centre,axis_end,-math.degrees(retreat/p.WATER_RADIUS))
        theta = p.JOINT_ANGLE+(station+p.GLAND_MID_SHIFT_S-retreat-v.TOOL_ARC_LENGTH/2)/p.WATER_RADIUS
        inward = (0,-math.cos(theta),-math.sin(theta))
        for shift in (0,5,10,20,30,40):
            displaced = withdrawn.translate(tuple(shift*d for d in inward))
            hits = {k:volume(displaced.intersect(s)) for k,s in tubes.items()}
            rec = {"gland":name,"withdrawal_retreat_mm":retreat,
                   "radial_removal_shift_mm":shift,"translation_direction":inward,
                   "tube_overlap_mm3":hits}
            print(json.dumps({"side_removal":rec}),flush=True)
            removal_records.append(rec)
            if max(hits.values())>1e-5:
                bad.append(f"{name}: side removal shift {shift} has obstruction")

    def handle_forward_bound(station,retreat):
        angle_delta = (station+p.GLAND_MID_SHIFT_S-retreat-v.TOOL_ARC_LENGTH-entry_s)/p.WATER_RADIUS
        return (p.WATER_RADIUS+p.SHELL_CENTER_N-v.TOOL_HANDLE_OD/2)*math.sin(angle_delta)

    unchanged=all(sha(path)==digests[k] for k,path in sources.items())
    report = {"check":"Native vent-tool assembly motion","source_sha256":digests,
              "native_casing":"Circular neck minus actual shell vent-cavity and female-socket cutters; bottom outlet retained as conservative stock",
              "motions":"Rotate about the actual water-arc center, distal bung first. No upstream bung is installed during distal insertion.",
              "rotation_centre_world_mm":centre,"entry_station_mm":entry_s,
              "continuous_bounds":envelope_records,"native_poses":records,
              "current_lower_ribbon_continuous_motion_witness":{
                  **lower_record,"geometry_signature_sha256":lower_ribbon_signature(),
                  "source_sha256":digests,"dependencies_unchanged_during_check":unchanged},
              "side_removal_poses":removal_records,
              "slot_width_mm":v.TOOL_SLOT_WIDTH,
              "nominal_bundle_width_mm":2*(v.FLAVOR_X+p.FLAVOR_OD/2),
              "slot_total_nominal_width_allowance_mm":v.TOOL_SLOT_WIDTH-2*(v.FLAVOR_X+p.FLAVOR_OD/2),
              "handle_forwardmost_signed_distance_to_socket_entry_mm":{
                  "downstream_seated":handle_forward_bound(p.DOWNSTREAM_GLAND_S,0),
                  "upstream_seated":handle_forward_bound(p.UPSTREAM_GLAND_S,0)},
              "intentional_elastic_installation":{
                  "free_flange_od_mm":v.FLANGE_OD,"traversed_aperture_mm":v.KEEPER_ID,
                  "flange_radial_deflection_mm":(v.FLANGE_OD-v.KEEPER_ID)/2,
                  "free_body_radial_deflection_mm":(v.BODY_OD-v.BODY_SEAT_ID)/2,
                  "retaining_groove_radial_capture_mm":(v.GROOVE_ID-v.BODY_SEAT_ID)/2,
                  "requirement":"The soft distal flange snaps through the empty upstream gland; its free STL is intentionally larger than the apertures. No rigid free-STL traversal claim is made."},
              "scope":"Nominal native geometric clearances and assembly-motion bounds. Printed sizes, TPU snap-through force, complete flange capture, water containment and aging remain physical acceptance properties. Individual insulated wires are Ø1.3; before s14 a 7.9x1.3 path-based fan bound is used. A separate continuous complete-tool bound checks the assembled flat lower ribbon and its below-plate return drawn to Z-50. Final annular flange-bearing contact is intentional and excluded from casing/tube interference.",
              "source_unchanged_during_check":unchanged,
              "failures":bad,"passed":not bad and unchanged,"elapsed_seconds":time.time()-begun}
    (HERE/"tool-motion-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"passed":report["passed"],"failures":bad,
                      "source_unchanged":report["source_unchanged_during_check"],
                      "elapsed_seconds":report["elapsed_seconds"]}),flush=True)
    if not report["passed"]:
        raise SystemExit(1)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--refresh-bounds",action="store_true")
    args=parser.parse_args()
    refresh_bounds() if args.refresh_bounds else main()
