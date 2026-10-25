"""The Pour: a compact corner whose surfaces share nine print readings.

Export one body and one captive slide in their shared manufacturing frame.
The native display and overhang kernels retain their radii and tangent rules.
Each whole print uses one recipe; compare recipes across complete prints.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").is_file())
sys.path.insert(0, str(ROOT / "hardware/printed-parts/cadlib"))
sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/enclosure"))
import _swept_top as source_display
from overhang_round import transition, OUTWARD_PER_HEIGHT
import flute_skin

WALL = 3.0
DISPLAY_FLAT = 12.0
RIM_R = source_display.SIDE_RADIUS
ENCLOSURE_SOURCE = ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure.py"


def _local_portal():
    path = HERE / "pip.py"
    spec = importlib.util.spec_from_file_location("pour_corner_portal", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _source_bore():
    """Load the production bore and its four small construction dependencies."""
    tree = ast.parse(ENCLOSURE_SOURCE.read_text())
    function_names = {"_ring", "_xcyl", "_yz_prism", "_teardrop_x"}
    constants = {"lead_bore_r", "teardrop_roof_angle"}
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in function_names
             or isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id in constants for t in node.targets)]
    namespace = {"cq": cq, "math": math}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ENCLOSURE_SOURCE), "exec"), namespace)
    return namespace


def _phase_up(value):
    """Shared 0.20 + n*0.24 datum also lies on the 0.12 and 0.08 grids."""
    return .20 + math.ceil((value-.20)/.24-1e-9)*.24


PORTAL = _local_portal()
BORE = _source_bore()
REFERENCE_BAY = PORTAL.build()
REFERENCE_BOUNDS = REFERENCE_BAY["fixed"].BoundingBox()
LIP_TOP = REFERENCE_BAY["proof"]["contact_planes_z_mm"]["lip_top"]
WIDTH = REFERENCE_BOUNDS.xlen + 2*WALL
_previous_flat = source_display.FLAT
try:
    source_display.FLAT = DISPLAY_FLAT
    _local_profile = source_display.profile((-WIDTH/2, WIDTH/2, 0, 0, 0, 0))
finally:
    source_display.FLAT = _previous_flat
PROFILE_RUN = _local_profile["roof"][0]
PROFILE_RISE = -_local_profile["foot"][1]
CEILING_LAND = RIM_R
NOSE_REVEAL = WALL  # Chosen viewing allowance over the fixed lip, not finger room.
DEPTH = PROFILE_RUN + CEILING_LAND + WALL
HEIGHT = _phase_up(PROFILE_RISE + LIP_TOP + NOSE_REVEAL)
FLUTE_Y0, FLUTE_LENGTH = 7.5, 20.0
FLUTE_Y1 = FLUTE_Y0 + FLUTE_LENGTH
FLUTE_Z0, FLUTE_Z1 = RIM_R, RIM_R+15.0
BORE_R = BORE["lead_bore_r"]
BORE_Y = DEPTH-RIM_R-WALL-BORE_R
BORE_Z = _phase_up(LIP_TOP+BORE_R+PORTAL.Z_AIR)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def _profile():
    """Native R12/30-degree/R18 stations, shortening only its straight field."""
    previous = source_display.FLAT
    try:
        source_display.FLAT = DISPLAY_FLAT
        return source_display.profile((-WIDTH/2, WIDTH/2, 0, DEPTH, 0, HEIGHT))
    finally:
        source_display.FLAT = previous


def envelope():
    p = _profile()
    wire = (cq.Workplane("YZ", origin=(-WIDTH/2, 0, 0))
            .moveTo(0, 0).lineTo(*p["foot"])
            .threePointArc(p["front_mid"], p["start"])
            .lineTo(*p["end"])
            .threePointArc(p["top_mid"], p["roof"])
            .lineTo(DEPTH, HEIGHT).lineTo(DEPTH, 0).close().val())
    raw = cq.Solid.extrudeLinear(wire, [], cq.Vector(WIDTH, 0, 0))
    # This inward/upward-printing side round is the crown's own edge.
    sides = []
    for edge in raw.Edges():
        b = edge.BoundingBox()
        on_side = (abs(b.xmin+WIDTH/2)<1e-6 and abs(b.xmax+WIDTH/2)<1e-6
                   or abs(b.xmin-WIDTH/2)<1e-6 and abs(b.xmax-WIDTH/2)<1e-6)
        if on_side and b.zmin >= p["foot"][1]-1e-6 and b.ymin < DEPTH-1e-6:
            sides.append(edge)
    rounded = raw.fillet(RIM_R, sides)
    # The rear plan round keeps the roof edge square.
    plan = cq.Workplane("XY", origin=(0, DEPTH/2, 0)).rect(WIDTH, DEPTH).val()
    rear_vertices = [v for v in plan.Vertices() if abs(v.Center().y-DEPTH)<1e-6]
    plan = plan.fillet2D(RIM_R, rear_vertices)
    standing = cq.Solid.extrudeLinear(plan, [], cq.Vector(0, 0, HEIGHT))
    rounded = rounded.intersect(standing).clean()
    before_bed_round = rounded
    bed_edges=[]
    for edge in rounded.Edges():
        b=edge.BoundingBox()
        if (abs(b.ymin-DEPTH)<1e-6 and abs(b.ymax-DEPTH)<1e-6
                and abs(b.zmin)<1e-6 and abs(b.zmax)<1e-6 and b.xlen>1):
            bed_edges.append(edge)
    if len(bed_edges)!=1:
        raise ValueError(f"one rear bed edge expected, got {len(bed_edges)}")
    rounded=rounded.fillet(RIM_R,bed_edges)
    # A closed-loop version of native three_side_fill. Both sections offset
    # the entire rounded plan: a corner keeps its true radius-minus-inset,
    # rather than gaining stock from the union of two rectangular caps.
    h,foot=transition(RIM_R)
    def bed_section(z,inset):
        wire=(cq.Workplane("XY",origin=(0,DEPTH/2,z))
              .rect(WIDTH-2*inset,DEPTH-2*inset).val())
        return wire.fillet2D(RIM_R-inset,wire.Vertices())
    fill=cq.Solid.makeLoft([bed_section(0,foot),
                           bed_section(h,foot-OUTWARD_PER_HEIGHT*h)],ruled=True)
    rounded=rounded.fuse(fill.intersect(before_bed_round))
    return rounded.clean(), p


def inner_core():
    """Concentric inner crown and plan curves retain the 3 mm wall section."""
    p = _profile()
    a = math.radians(source_display.ANGLE)
    rb = source_display.FRONT_RADIUS-WALL
    rt = source_display.TOP_RADIUS-WALL
    rr = RIM_R-WALL
    cy, cz = PROFILE_RUN, HEIGHT-source_display.TOP_RADIUS
    mid_angle = math.radians(180-(90-source_display.ANGLE)/2)
    foot = (WALL, p["foot"][1])
    start = (source_display.FRONT_RADIUS-rb*math.sin(a),
             foot[1]+rb*math.cos(a))
    front_mid = (source_display.FRONT_RADIUS+rb*math.cos(mid_angle),
                 foot[1]+rb*math.sin(mid_angle))
    end = (cy-rt*math.sin(a), cz+rt*math.cos(a))
    top_mid = (cy-rt*math.sin(a/2), cz+rt*math.cos(a/2))
    wire = (cq.Workplane("YZ", origin=(-WIDTH/2+WALL, 0, 0))
            .moveTo(WALL, WALL).lineTo(*foot)
            .threePointArc(front_mid, start).lineTo(*end)
            .threePointArc(top_mid, (cy, HEIGHT-WALL))
            .lineTo(DEPTH-WALL, HEIGHT-WALL).lineTo(DEPTH-WALL, WALL)
            .close().val())
    raw = cq.Solid.extrudeLinear(wire, [], cq.Vector(WIDTH-2*WALL, 0, 0))
    sides = []
    for edge in raw.Edges():
        b = edge.BoundingBox()
        on_side = (abs(abs(b.xmin)-(WIDTH/2-WALL))<1e-6 and b.xlen<1e-6)
        if on_side and b.zmin>=foot[1]-1e-6 and b.ymin<DEPTH-WALL-1e-6:
            sides.append(edge)
    core = raw.fillet(rr, sides)
    plan = (cq.Workplane("XY", origin=(0, DEPTH/2, WALL))
            .rect(WIDTH-2*WALL, DEPTH-2*WALL).val())
    vertices = [v for v in plan.Vertices() if abs(v.Center().y-(DEPTH-WALL))<1e-6]
    plan = plan.fillet2D(rr, vertices)
    mask = cq.Solid.extrudeLinear(plan, [], cq.Vector(0, 0, HEIGHT-2*WALL))
    core = core.intersect(mask).clean()
    bed = [edge for edge in core.Edges()
           if abs(edge.BoundingBox().ymin-(DEPTH-WALL))<1e-6
           and edge.BoundingBox().ylen<1e-6
           and abs(edge.BoundingBox().zmin-WALL)<1e-6
           and edge.BoundingBox().zlen<1e-6 and edge.BoundingBox().xlen>1]
    core = core.fillet(rr, bed).clean()
    # The existing right flank keeps 3 mm backing beneath its deepest flute.
    flute_backing=box(WIDTH/2-WALL-1.2,WIDTH/2+1,FLUTE_Y0,FLUTE_Y1,FLUTE_Z0,FLUTE_Z1)
    return core.cut(flute_backing).clean(), core


def teardrop_cut():
    """Production lead-bore profile, carried through the existing left flank."""
    return BORE["_teardrop_x"](BORE_R, BORE_Y, BORE_Z,
                                -WIDTH/2-1, -WIDTH/2+WALL+1)


def build(include_pip=True, *, xy_air=.25, z_air=.48):
    outer, p = envelope()
    core, full_core = inner_core()
    body = outer.cut(core).clean()
    # The lower carrier starts at the fore round's straight station. One
    # complete crop opens the nose without leaving curved mouth end scraps.
    nose_relief=box(-WIDTH/2-1,WIDTH/2+1,-1,RIM_R,-1,p["foot"][1])
    body=body.cut(nose_relief).clean()
    # The rear mouth serves both the gate and the actual crown underside.
    rear_access=box(-WIDTH/2+RIM_R+WALL,WIDTH/2-RIM_R-WALL,
                    DEPTH-WALL-.5,DEPTH+1,RIM_R,HEIGHT-WALL)
    body=body.cut(rear_access).clean()
    body = body.cut(teardrop_cut()).clean()
    moving = None
    pip_proof = None
    if include_pip:
        bay = PORTAL.build(xy_air=xy_air, z_air=z_air)
        # The bay owns its moving-gap topology. These names are its placement
        # contract; retain them in the integrated geometry review.
        fixed = bay["fixed"]
        moving = bay["moving"]
        cuts = bay.get("clearance_cut")
        if cuts is not None:
            body = body.cut(cuts).clean()
        body = body.fuse(fixed).clean()
        pip_proof = bay.get("proof")
        overlap=body.intersect(moving).Volume()
        if pip_proof is not None:
            pip_proof=dict(pip_proof,integrated_nominal_rigid_overlap_mm3=overlap)
    return {"body":body,"moving":moving,"profile":p,"pip":pip_proof,
            "outer":outer,"core":core,"full_core":full_core}


def _bounds(shape):
    b=shape.BoundingBox()
    return {"min":[b.xmin,b.ymin,b.zmin],"max":[b.xmax,b.ymax,b.zmax],
            "dimensions":[b.xlen,b.ylen,b.zlen]}


def native_surface_intent(stl):
    """Native painting indices bound to the actual exported frame triangles."""
    mesh=trimesh.load(stl)
    c,n=mesh.triangles_center,mesh.face_normals
    z=c[:,2]
    h,foot=transition(RIM_R)
    q=np.abs(c[:,:2]-[0,DEPTH/2])-[WIDTH/2-RIM_R,DEPTH/2-RIM_R]
    sd=(np.linalg.norm(np.maximum(q,0),axis=1)
        +np.minimum(np.maximum(q[:,0],q[:,1]),0)-RIM_R)
    inset=np.where(z<=h,foot-OUTWARD_PER_HEIGHT*z,
                   RIM_R-np.sqrt(np.maximum(0,RIM_R**2-(RIM_R-z)**2)))
    downward=(n[:,2]<-.02)&(n[:,2]>-.98)
    bed=(z>=-1e-5)&(z<=RIM_R+.01)&(np.abs(sd+inset)<.075)&downward
    centre=[-WIDTH/2+RIM_R,DEPTH-RIM_R]
    angle=np.degrees(np.arctan2(n[:,1],-n[:,0]))
    distance=np.hypot(c[:,0]-centre[0],c[:,1]-centre[1])
    seam=((c[:,0]<=centre[0]+.1)&(c[:,1]>=centre[1]-.1)
          &(np.abs(distance-RIM_R)<.075)&(np.abs(n[:,2])<.05)
          &(z>=8)&(z<=HEIGHT-RIM_R)&(angle>=40)&(angle<=50))
    support={"body_stl_sha256":hashlib.sha256(stl.read_bytes()).hexdigest(),
             "processed_trimesh_facets":len(mesh.faces),
             "bed_R6_exterior_transition_faces":np.flatnonzero(bed).tolist(),
             "functional_horizontal_faces_excluded":True,
             "paint_normal_threshold_z":[-.98,-.02]}
    seam_record={"standing_left_rear_R6_faces":np.flatnonzero(seam).tolist(),
                 "world_corner_center_xy_mm":centre,
                 "degrees_from_minus_x_towards_plus_y":[40,50],
                 "z_band_mm":[8,HEIGHT-RIM_R]}
    return support,seam_record


def export(include_pip=True, *, xy_air=.25, z_air=.48):
    generated = build(include_pip, xy_air=xy_air, z_air=z_air)
    HERE.mkdir(parents=True, exist_ok=True)
    records = {}
    for name in ("body","moving"):
        shape=generated[name]
        if shape is None: continue
        step=HERE/f"arch-{name}.step"
        stl=HERE/f"arch-{name}.stl"
        cq.exporters.export(shape,str(step))
        cq.exporters.export(shape,str(stl),tolerance=.03,angularTolerance=.1)
        # OCC triangulates a few pole faces with coincident vertices. Remove
        # only zero-area triangles; no nondegenerate vertex is moved here.
        mesh=trimesh.load(stl)
        original_facets=len(mesh.faces)
        mesh.update_faces(mesh.nondegenerate_faces(height=1e-7))
        mesh.remove_unreferenced_vertices()
        removed=original_facets-len(mesh.faces)
        if name=="body":
            rail=flute_skin.Rail(
                at=lambda s:((WIDTH/2,s+FLUTE_Y0),(1.0,0.0)),
                length=FLUTE_LENGTH,start=0.0,closed=False,band=(FLUTE_Z0,FLUTE_Z1))
            mesh=flute_skin.flute(mesh,[rail],5.0,1.2,5.0)
        mesh.export(stl)
        records[name]={"valid":shape.isValid(),"solids":len(shape.Solids()),
                       "volume_mm3":shape.Volume(),"cad_mass_g_at_1_3":shape.Volume()/1000*1.3,
                       "bounds":_bounds(shape),"step":str(step.relative_to(ROOT)),
                       "stl":str(stl.relative_to(ROOT)),
                       "mesh":{"watertight":mesh.is_watertight,"positive_volume":mesh.is_volume,
                               "volume_mm3":mesh.volume,"bounds":mesh.bounds.tolist(),
                               "facets":len(mesh.faces),"zero_area_facets_removed":removed}}
    asm=cq.Assembly(name="The Pour Corner")
    asm.add(generated["body"],name="frame",color=cq.Color(.18,.18,.19))
    if generated["moving"] is not None:
        asm.add(generated["moving"],name="slide",color=cq.Color(.36,.36,.37))
    asm.save(str(HERE/"the-pour.step"))
    support_paint,seam_paint=native_surface_intent(HERE/"arch-body.stl")
    h,f=transition(RIM_R)
    report={"name":"The Pour V5 — Corner","manufacturing_up":[0,0,1],
            "dimensions_mm":[WIDTH,DEPTH,HEIGHT],"nominal_ordinary_stock_mm":WALL,
            "parts":records,"total_volume_mm3":sum(r["volume_mm3"] for r in records.values()),
            "total_cad_mass_g_at_1_3":sum(r["cad_mass_g_at_1_3"] for r in records.values()),
            "display":{"straight_mm":DISPLAY_FLAT,"degrees_from_horizontal":30,
                        "front_radius_mm":12,"roof_radius_mm":18,"side_radius_mm":6,
                        "profile":generated["profile"]},
            "print_down_round":{"radius_mm":6,"outward_per_build_rise":.5,
                                "chamfer_height_mm":h,"foot_inset_mm":f},
            "ceiling":{"source":"inside of the actual rear crown",
                       "reading_rectangle_mm":[-6,6,PROFILE_RUN,DEPTH-WALL,HEIGHT-WALL,HEIGHT-WALL],
                       "rear_access_mm":[-12.25,12.25,DEPTH-WALL-.5,DEPTH+1,RIM_R,HEIGHT-WALL],
                       "expected_paint":"horizontal functional flat; retain automatic support",
                       "reading_record":"prints/the-pour-v5-petgf.print.json"},
            "texture":{"source":"cadlib/flute_skin.py",
                       "mesh_only":True,"pitch_mm":5,"width_mm":4,
                       "depth_mm":1.2,"fade_mm":5,
                       "backing_after_deepest_groove_mm":3,
                       "field_mm":[WIDTH/2,WIDTH/2,FLUTE_Y0,FLUTE_Y1,FLUTE_Z0,FLUTE_Z1]},
            "teardrop":{"source":"enclosure.py:_teardrop_x and lead_bore_r",
                        "radius_mm":BORE_R,"roof_degrees_from_horizontal":BORE["teardrop_roof_angle"],
                        "axis_yz_mm":[BORE_Y,BORE_Z],"axis_direction":[1,0,0]},
            "design":{"width":{"bay_ties_mm":REFERENCE_BOUNDS.xlen,"side_stock_each_mm":WALL},
                      "depth":{"native_crown_run_mm":PROFILE_RUN,"flat_ceiling_land_mm":CEILING_LAND,
                               "rear_stock_mm":WALL},
                      "height":{"native_crown_rise_mm":PROFILE_RISE,"fixed_lip_top_mm":LIP_TOP,
                                "chosen_fore_viewing_reveal_mm":NOSE_REVEAL,
                                "actual_fore_reveal_mm":generated["profile"]["foot"][1]-LIP_TOP,
                                "top_grid_mm":[.20,.24]},
                      "access":"One rear opening reaches the tab and actual crown underside. The fore reveal is for viewing.",
                      "extent_scope":"Sample lengths and viewing allowances are design choices, not qualified minima."},
            "pip":generated["pip"],
            "native_support_paint":support_paint,"native_seam_paint":seam_paint,
            "source_bindings":{str(file.relative_to(ROOT)):hashlib.sha256(file.read_bytes()).hexdigest()
                               for file in (HERE/"reference.py",HERE/"pip.py",
                                   ROOT/"hardware/printed-parts/cadlib/overhang_round.py",
                                   ROOT/"hardware/printed-parts/cadlib/flute_skin.py",
                                   ROOT/"hardware/printed-parts/enclosure/enclosure/_swept_top.py", ENCLOSURE_SOURCE)},
            "sha256":{file.name:hashlib.sha256(file.read_bytes()).hexdigest()
                      for file in [HERE/"the-pour.step", *HERE.glob("arch-*.step"), *HERE.glob("arch-*.stl")]},
            "required_native_readings":["support/contact slabs", "motion-gap and bridge paths"],
            "physical_result":"Unprinted; release, removal and finish remain unmeasured"}
    (HERE/"geometry.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("name","dimensions_mm","total_volume_mm3","physical_result")},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--no-pip",action="store_true")
    parser.add_argument("--xy-air",type=float,default=.25,help="One running clearance per face, in mm")
    parser.add_argument("--z-air",type=float,default=.48,help="One floor and lip release gap, in mm")
    args=parser.parse_args()
    export(not args.no_pip,xy_air=args.xy_air,z_air=args.z_air)
