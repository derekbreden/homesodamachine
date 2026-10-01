"""Read the candidate's solids, retention stops and preserved enclosure stock."""
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import cadquery as cq
import grip_cover as g


def main():
    print("Reading the full candidate solids",flush=True)
    originals=g.originals()
    halves={n:cq.importers.importStep(str(g.HERE/f"grip-candidate-{n}-bottom.step")).val()
            for n in ("front","back")}
    strip=cq.importers.importStep(str(g.HERE/"grip-cover.step")).val()
    checks={}
    checks["all_solids_valid_and_connected"] = all(
        s.isValid() and len(s.Solids())==1 for s in (*halves.values(),strip))
    checks["cover_flat_back_and_wings_on_bed"] = abs(strip.BoundingBox().zmin)<1e-6
    checks["body_dimensions_match"] = all(abs(a-b)<1e-6 for a,b in zip(
        (strip.BoundingBox().xlen,strip.BoundingBox().ylen,strip.BoundingBox().zlen),
        (g.LENGTH+2*g.WING_REACH,g.WIDTH,g.THICK)))

    readings={}
    seam=g.box(-110,110,g.shell.y_seam-1,g.shell.y_seam+g.shell.lip_len+1,-7,55)
    y0,y1=g.shell._handhold_y()
    changes=cq.Compound.makeCompound([g.box(xa,xb,y0-g.shell.handhold_edge_r,
        y1+g.shell.handhold_edge_r,-g.shell.floor_t,g.ROOF+g.shell.handhold_edge_r)
        for xa,xb in ((g.INNER_FACE-g.shell.handhold_wall,g.X_EXT+1),
                      (-g.X_EXT-1,-g.INNER_FACE+g.shell.handhold_wall))])
    show_band=cq.Compound.makeCompound([g.box(xa,xb,y0,y1,g.ROOF-.002,g.ROOF+g.shell.handhold_edge_r)
        for xa,xb in ((g.X_EXT-g.shell.handhold_edge_r,g.X_EXT+1),
                      (-g.X_EXT-1,-g.X_EXT+g.shell.handhold_edge_r))])
    structural_seam=seam.cut(show_band)

    def face_witness(shape):
        """Geometric face identity at 0.1 micron resolution, independent of OCC IDs."""
        rows=[]
        for face in shape.Faces():
            b=face.BoundingBox()
            rows.append((face.geomType(),*(round(v,4) for v in
                (face.Area(),*face.Center().toTuple(),b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))))
        return Counter(rows)

    # Isolate the edited region before Boolean comparisons. Identical complex
    # full shells needlessly send every rear-lettering face through the splitter.
    # The cut-away full-shell remainder is compared face by face independently.
    local_box=cq.Compound.makeCompound([g.box(xa,xb,y0-g.shell.handhold_edge_r-1,
                    y1+g.shell.handhold_edge_r+1,-7,55)
        for xa,xb in ((g.INNER_FACE-g.shell.handhold_wall-1,g.X_EXT+1),
                      (-g.X_EXT-1,-g.INNER_FACE+g.shell.handhold_wall+1))])
    for n,s in list(halves.items()):
        print(f"Checking {n} exterior faces and local handhold stock",flush=True)
        old_out=originals[n].cut(changes).clean()
        new_out=s.cut(changes).clean()
        same_outside=face_witness(old_out)==face_witness(new_out)
        old_local=originals[n].intersect(local_box)
        local=s.intersect(local_box)
        old_joint=old_local.intersect(structural_seam).clean()
        new_joint=local.intersect(structural_seam).clean()
        readings[n]={"local_volume_change_mm3":local.Volume()-old_local.Volume(),
                     "outside_faces_match":same_outside,
                     "outside_face_count":len(new_out.Faces()),
                     "structural_joint_faces_match":face_witness(old_joint)==face_witness(new_joint)}
        halves[n]=local
    checks["changes_confined_to_handhold"] = all(
        r["outside_faces_match"] for r in readings.values())
    checks["structural_joint_and_fastener_region_unchanged"] = all(
        r["structural_joint_faces_match"] for r in readings.values())
    checks["halves_do_not_overlap_at_handholds"] = halves["front"].intersect(halves["back"]).Volume()<.001
    print("Checking the roof sections, catch walls and clearance limits",flush=True)

    def missing(shape):
        for part in halves.values():
            if not shape.Solids(): return 0.
            shape=shape.cut(part)
        return shape.Volume()
    roof_missing=[]
    opening_blocked=[]
    profiles=[]
    post_missing=[]
    legacy_edges=[]
    for side in (-1,1):
        xa,xb=sorted((side*g.INNER_FACE,side*g.OUTER_FLAT))
        bearing=g.box(xa,xb,y0,y1,g.ROOF,g.CROWN)
        _seat,tip,_heat,cap=g.shell._boss_x(side*g.X_EXT,-side)
        xa,xb=sorted((tip,cap-side*g.shell.fits.running))
        joint_end=g.shell.y_seam+g.shell.lip_len
        socket_air=g.box(xa,xb,joint_end,joint_end+g.shell.fits.running,g.ROOF,g.CROWN)
        roof_missing.append(missing(bearing.cut(socket_air)))
        xa,xb=sorted((side*g.INNER_FACE,side*(g.X_EXT+1)))
        entry=g.box(xa,xb,y0,y1,-g.shell.floor_t,g.ROOF)
        opening_blocked.append(sum(s.intersect(entry).Volume() for s in halves.values()))
        air=g.roof_profile_air()
        if side<0:air=air.mirror("YZ")
        profiles.append({"side":side,"excess_mm3":sum(s.intersect(air).Volume() for s in halves.values())})
        # Read the same XZ section through both end regions and the straight run.
        # The enclosure's Y joint is checked separately above.
        xa,xb=sorted((side*g.OUTER_FLAT,side*g.X_EXT))
        for y in (y0+.02,y0+1,y0+3,y0+6,y0+16,y1-16,y1-6,y1-3,y1-1,y1-.02):
            desired=g.box(xa,xb,y,y+.01,g.ROOF,g.ROOF+g.shell.handhold_edge_r).cut(air)
            profiles.append({"side":side,"y_mm":y,"missing_mm3":missing(desired)})
        xa,xb=sorted((side*g.INNER_FACE,side*g.X_EXT))
        for n,end,index in (("front",y0,0),("back",y1,1)):
            a,b=(end-g.shell.handhold_wall,end) if n=="front" else (end,end+g.shell.handhold_wall)
            post=g.box(xa,xb,a,b,-g.shell.floor_t,g.CROWN).cut(g.placed(g.receiver_slots()[index],side))
            post_missing.append(missing(post))
            for edge in halves[n].Edges():
                bb=edge.BoundingBox()
                if (edge.geomType()!="LINE" and bb.xlen<1e-5 and bb.ylen>1 and bb.zlen>1
                    and abs(abs(bb.xmin)-g.X_EXT)<1e-5 and bb.zmin<g.ROOF+g.shell.handhold_edge_r
                    and bb.zmax>g.ROOF-g.shell.handhold_corner_r
                    and bb.ymin<end+g.shell.handhold_edge_r and bb.ymax>end-g.shell.handhold_edge_r):
                    legacy_edges.append({"side":side,"piece":n,"length_mm":edge.Length()})
    checks["full_12mm_roof_retained_outside_joint_clearance"] = max(roof_missing)<.001
    checks["opening_clear_to_square_end_walls"] = max(opening_blocked)<.001
    checks["roof_profile_constant_for_full_grip_length"] = all(
        p.get("excess_mm3",0)<.001 and p.get("missing_mm3",0)<.001 for p in profiles)
    checks["full_3mm_catch_end_walls"] = max(post_missing)<.001
    checks["no_curved_returns_around_grip_ends"] = not legacy_edges

    corner_remnants=[]
    for side in (-1,1):
        xa,xb=sorted((side*g.OUTER_FLAT,side*(g.X_EXT+1)))
        for n,y in zip(("front","back"),g.shell._handhold_y()):
            y0,y1=(y,y+g.shell.handhold_corner_r) if n=="front" else (y-g.shell.handhold_corner_r,y)
            corner=g.box(xa,xb,y0,y1,g.ROOF-g.shell.handhold_corner_r,g.ROOF)
            corner_remnants.append(halves[n].intersect(corner).Volume())
    checks["all_four_outer_corner_remnants_removed"] = max(corner_remnants)<.001

    # Use a local sample for the repeated fit reads; it is cut from the final
    # imported candidate solids, including the actual front/back seam.
    receiver=cq.Compound.makeCompound([g.sample(s) for s in halves.values()])
    # The requested outer-ceiling pick lies under the cover. Its end catches
    # start on the existing end-wall planes, at both ends of both handholds.
    placed=g.placed(strip)
    cover_box=placed.BoundingBox()
    checks["cover_reaches_requested_x_105_195"] = (
        cover_box.xmin<105.195<=cover_box.xmax and cover_box.ymin<222.675<cover_box.ymax)
    mouth_edges=[]
    mouth_z=g.BACK-g.WING_THICK-g.BEARING_AIR-g.ENTRY_DEPTH
    for n,y in zip(("front","back"),g.shell._handhold_y()):
        for side in (-1,1):
            edges=[e for e in halves[n].Edges()
                   if abs(e.Center().y-y)<1e-6 and abs(e.Center().z-mouth_z)<1e-6
                   and abs(e.Center().x-side*g.X_CENTER)<1e-6
                   and abs(e.Length()-(g.WING_SPAN+2*g.WING_END_AIR))<1e-6]
            mouth_edges.append(len(edges)==1)
    checks["all_four_slot_mouths_on_existing_end_walls"] = all(mouth_edges)
    worst=0
    for along,across,drop in itertools.product(
            (-g.BODY_AIR,0,g.BODY_AIR),(-g.WING_END_AIR,0,g.WING_END_AIR),
            (-g.BACK_AIR,0,g.BEARING_AIR)):
        posed=g.placed(strip,drop=drop).translate((across,along,0))
        worst=max(worst,posed.intersect(receiver).Volume())
    checks["no_interference_at_all_clearance_extremes"] = worst<.001

    catches=[]
    for end,along,across in itertools.product((-1,1),(-g.BODY_AIR,g.BODY_AIR),
                                             (-g.WING_END_AIR,g.WING_END_AIR)):
        posed=g.placed(g.wing(end),drop=g.BEARING_AIR+.10).translate((across,along,0))
        catches.append(posed.intersect(receiver).Volume())
    checks["both_wings_caught_at_all_in_plane_extremes"] = min(catches)>.10

    # A single extrusion column has a continuous material interval from Z=0
    # wherever the cover exists: its body and both wings share that bed plane.
    # Mesh checks also catch disconnected shells and a reversed tessellation.
    mesh_checks={}
    for name in ("grip-cover","grip-receiver-front","grip-receiver-back"):
        m=g.trimesh.load_mesh(g.HERE/f"{name}.stl")
        mesh_checks[name]={"watertight":bool(m.is_watertight),
                           "positive_volume":bool(m.volume>0),
                           "bodies":len(m.split(only_watertight=False))}
    checks["print_meshes_closed_single_bodies"] = all(
        r["watertight"] and r["positive_volume"] and r["bodies"]==1 for r in mesh_checks.values())
    report={"status":"pass" if all(checks.values()) else "fail","checks":checks,
            "stock_and_joint":readings,"maximum_interference_mm3":worst,
            "east_cover_x_mm":[cover_box.xmin,cover_box.xmax],
            "slot_mouth_y_mm":list(g.shell._handhold_y()),
            "maximum_outer_corner_remnant_mm3":max(corner_remnants),
            "maximum_missing_roof_mm3":max(roof_missing),
            "maximum_missing_end_wall_mm3":max(post_missing),
            "roof_profile":profiles,"curved_end_returns":legacy_edges,
            "minimum_wing_stop_probe_mm3":min(catches),"mesh":mesh_checks,
            "artifacts_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(g.HERE.glob("*.stl"))},
            "scope":"Geometry only. Cover bending, spring-back, retention force, surface finish and lifting performance are unmeasured."}
    (g.HERE/"geometry-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if report["status"]!="pass":
        raise SystemExit(1)


if __name__=="__main__":
    main()
