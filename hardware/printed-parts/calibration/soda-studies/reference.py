"""The Pour: a compact arch carrying nine local print references.

Export one body and one captive slide in their shared manufacturing frame.
The native display and overhang kernels retain their radii and tangent rules.
Each whole print uses one recipe; compare recipes across complete prints.
"""
from __future__ import annotations

import argparse
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
from overhang_round import roof_rim, transition, OUTWARD_PER_HEIGHT
import flute_skin

WIDTH, DEPTH, HEIGHT = 60.0, 48.0, 60.0
WALL = 3.0
DISPLAY_FLAT = 12.0
WINDOW_HALF_WIDTH = 15.0
WINDOW_ROOF = 34.04
RIM_R = 6.0
FRONT_BACKING = 9.0


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
    # This is the upward-printing side round. Do not copy the production
    # back-top's inverted exterior-roof additive fill onto this top surface.
    sides = []
    for edge in raw.Edges():
        b = edge.BoundingBox()
        on_side = (abs(b.xmin+WIDTH/2)<1e-6 and abs(b.xmax+WIDTH/2)<1e-6
                   or abs(b.xmin-WIDTH/2)<1e-6 and abs(b.xmax-WIDTH/2)<1e-6)
        if on_side and b.zmin >= p["foot"][1]-1e-6 and b.ymin < DEPTH-1e-6:
            sides.append(edge)
    rounded = raw.fillet(RIM_R, sides)
    standing = []
    for edge in rounded.Edges():
        b = edge.BoundingBox()
        if (abs(b.ymin-DEPTH)<1e-6 and abs(b.ymax-DEPTH)<1e-6
                and b.zlen > HEIGHT-2*RIM_R-1 and b.xlen<1e-6):
            standing.append(edge)
    if standing:
        rounded = rounded.fillet(RIM_R, standing)
    before_bed_round = rounded
    bed_edges=[]
    for edge in rounded.Edges():
        b=edge.BoundingBox()
        if (abs(b.ymin)<1e-6 and abs(b.ymax)<1e-6
                and abs(b.zmin)<1e-6 and abs(b.zmax)<1e-6 and b.xlen>1):
            bed_edges.append(edge)
    if len(bed_edges)!=1:
        raise ValueError(f"one front bed edge expected, got {len(bed_edges)}")
    rounded=rounded.fillet(RIM_R,bed_edges)
    # Offset the analytic round before adding its tangent planes. OCC cannot
    # consistently offset the union's tangent seam; the retained round is the
    # backing authority and every subsequent addition increases that backing.
    core_authority=rounded
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
    return rounded.clean(), p, core_authority


def inner_core(outer, core_authority):
    """The exact inward 3 mm offset of the envelope, with a local rim backing."""
    shell = core_authority.shell([], -WALL, kind="intersection")
    shells = sorted(shell.Shells(), key=lambda s:s.Area())
    if len(shells) != 2:
        raise ValueError(f"closed 3 mm stock expected two shells, got {len(shells)}")
    core = cq.Solid.makeSolid(shells[0])
    # Ordinary walls stay 3 mm. Only the local front opening's R6 roll keeps
    # enough source stock for its entire six-millimetre depth and backing.
    rim_stock = box(-WINDOW_HALF_WIDTH-RIM_R, WINDOW_HALF_WIDTH+RIM_R,
                    -1, FRONT_BACKING, -1, WINDOW_ROOF+RIM_R)
    flute_backing=box(WIDTH/2-WALL-1.2,WIDTH/2+1,10,30,18,40)
    return core.cut(rim_stock.fuse(flute_backing)).clean(), core


def aperture():
    """Source handhold's downward-open cut with its R6 upper inside corners."""
    opening = box(-WINDOW_HALF_WIDTH, WINDOW_HALF_WIDTH, -1,
                  FRONT_BACKING+2, -1, WINDOW_ROOF)
    corners = []
    for edge in opening.Edges():
        b = edge.BoundingBox()
        if abs(b.zmin-WINDOW_ROOF)<1e-6 and abs(b.zmax-WINDOW_ROOF)<1e-6 and b.ylen>1:
            corners.append(edge)
    return opening.fillet(RIM_R, corners)


def rounded_aperture(body):
    before = body.cut(aperture()).clean()
    rim = []
    for edge in before.Edges():
        b = edge.BoundingBox()
        if (abs(b.ymin)<1e-6 and abs(b.ymax)<1e-6
                and b.xmin>=-WINDOW_HALF_WIDTH-1e-6
                and b.xmax<=WINDOW_HALF_WIDTH+1e-6
                and b.zmin>=-1e-6 and b.zmax<=WINDOW_ROOF+1e-6
                and b.zmax>1e-6):
            rim.append(edge)
    if not rim:
        raise ValueError("no native lifting rim found")
    rounded = before.fillet(RIM_R, rim)
    # roof_rim's local X is normal to the opening. Rotate +Y-inward into its
    # +X-inward frame, then restore the object after the source loft fill.
    local_before = before.rotate((0,0,0),(0,0,1),-90)
    local_round = rounded.rotate((0,0,0),(0,0,1),-90)
    filled = roof_rim(local_before, local_round, 0, 1,
                      -WINDOW_HALF_WIDTH, WINDOW_HALF_WIDTH,
                      WINDOW_ROOF, RIM_R, RIM_R)
    return filled.rotate((0,0,0),(0,0,1),90).clean()


def teardrop_cut():
    """The native Ø11 lead bore's tangent 36-degree crown, across rear stock."""
    r, a, z = 5.5, math.radians(36.0), 47.0
    tangent_x = r*math.sin(a)
    tangent_z = z+r*math.cos(a)
    apex = z+r/math.cos(a)
    wire = (cq.Workplane("XZ", origin=(0, DEPTH+1, 0))
            .moveTo(-tangent_x,tangent_z).threePointArc((0,z-r),(tangent_x,tangent_z))
            .lineTo(0,apex).close().val())
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0,-WALL-2,0))


def build(include_pip=True, *, xy_air=.25, z_air=.48):
    outer, p, core_authority = envelope()
    core, full_core = inner_core(outer, core_authority)
    body = rounded_aperture(outer.cut(core).clean())
    # One rear access cut exposes the actual crown ceiling and permits its
    # automatically generated support to be reached through a broad opening.
    # This also opens the sculpture to the light instead of enclosing a rack.
    rear_access=box(-20,20,DEPTH-WALL-.5,DEPTH+1,6,38)
    body=body.cut(rear_access).clean()
    body = body.cut(teardrop_cut()).clean()
    moving = None
    pip_proof = None
    pip_path = HERE/"pip.py"
    if include_pip and pip_path.exists():
        spec = importlib.util.spec_from_file_location("compact_arch_pip", pip_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        if hasattr(module,"build"):
            bay = module.build(xy_air=xy_air, z_air=z_air)
        elif hasattr(module,"build_bay"):
            bay = module.build_bay()
        else:
            raise ValueError("pip.py must expose build() or build_bay()")
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
    upper=((c[:,1]>=-.01)&(c[:,1]<=RIM_R+.01)
           &(np.abs(c[:,0])<=WINDOW_HALF_WIDTH+RIM_R+.01)
           &(z>=WINDOW_ROOF-RIM_R-.01)&(z<=WINDOW_ROOF+RIM_R+.01)
           &(n[:,1]<-.05)&downward)
    centre=[-WIDTH/2+RIM_R,DEPTH-RIM_R]
    angle=np.degrees(np.arctan2(n[:,1],-n[:,0]))
    distance=np.hypot(c[:,0]-centre[0],c[:,1]-centre[1])
    seam=((c[:,0]<=centre[0]+.1)&(c[:,1]>=centre[1]-.1)
          &(np.abs(distance-RIM_R)<.075)&(np.abs(n[:,2])<.05)
          &(z>=8)&(z<=HEIGHT-RIM_R)&(angle>=40)&(angle<=50))
    support={"body_stl_sha256":hashlib.sha256(stl.read_bytes()).hexdigest(),
             "processed_trimesh_facets":len(mesh.faces),
             "bed_R6_exterior_transition_faces":np.flatnonzero(bed).tolist(),
             "aperture_R6_exterior_transition_faces":np.flatnonzero(upper).tolist(),
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
                at=lambda s:((WIDTH/2,s+7.5),(1.0,0.0)),
                length=20.0,start=2.5,closed=False,band=(18.0,40.0))
            mesh=flute_skin.flute(mesh,[rail],5.0,1.2,5.0)
        mesh.export(stl)
        records[name]={"valid":shape.isValid(),"solids":len(shape.Solids()),
                       "volume_mm3":shape.Volume(),"cad_mass_g_at_1_3":shape.Volume()/1000*1.3,
                       "bounds":_bounds(shape),"step":str(step.relative_to(ROOT)),
                       "stl":str(stl.relative_to(ROOT)),
                       "mesh":{"watertight":mesh.is_watertight,"positive_volume":mesh.is_volume,
                               "volume_mm3":mesh.volume,"bounds":mesh.bounds.tolist(),
                               "facets":len(mesh.faces),"zero_area_facets_removed":removed}}
    asm=cq.Assembly(name="The Arch")
    asm.add(generated["body"],name="frame",color=cq.Color(.18,.18,.19))
    if generated["moving"] is not None:
        asm.add(generated["moving"],name="slide",color=cq.Color(.36,.36,.37))
    asm.save(str(HERE/"the-pour.step"))
    support_paint,seam_paint=native_surface_intent(HERE/"arch-body.stl")
    h,f=transition(RIM_R)
    report={"name":"The Pour V4 — Arch","manufacturing_up":[0,0,1],
            "dimensions_mm":[WIDTH,DEPTH,HEIGHT],"nominal_ordinary_stock_mm":WALL,
            "parts":records,"total_volume_mm3":sum(r["volume_mm3"] for r in records.values()),
            "total_cad_mass_g_at_1_3":sum(r["cad_mass_g_at_1_3"] for r in records.values()),
            "display":{"straight_mm":DISPLAY_FLAT,"degrees_from_horizontal":30,
                        "front_radius_mm":12,"roof_radius_mm":18,"side_radius_mm":6,
                        "profile":generated["profile"]},
            "print_down_round":{"radius_mm":6,"outward_per_build_rise":.5,
                                "chamfer_height_mm":h,"foot_inset_mm":f},
            "ceiling":{"source":"inside of the actual rear crown",
                       "reading_rectangle_mm":[-8,8,28.5,44.5,57,57],
                       "rear_access_mm":[-20,20,44.5,49,6,38],
                       "expected_paint":"horizontal functional flat; retain automatic support",
                       "reading_record":"prints/the-pour-v4-petgf.print.json"},
            "texture":{"source":"cadlib/flute_skin.py",
                       "mesh_only":True,"pitch_mm":5,"width_mm":4,
                       "depth_mm":1.2,"fade_mm":5,
                       "backing_after_deepest_groove_mm":3,
                       "field_mm":[30,30,10,30,18,40]},
            "pip":generated["pip"],
            "native_support_paint":support_paint,"native_seam_paint":seam_paint,
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
