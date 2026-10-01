"""Read the candidate's solids, retention stops and preserved enclosure stock."""
import hashlib
import itertools
import json
from pathlib import Path

import cadquery as cq
import grip_cover as g


def main():
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
    section=g.box(-108,108,170,258,g.ROOF,g.CROWN)
    seam=g.box(-110,110,g.shell.y_seam-1,g.shell.y_seam+g.shell.lip_len+1,-7,55)
    for n,s in halves.items():
        removed=originals[n].cut(s)
        added=s.cut(originals[n])
        readings[n]={"removed_original_mm3":removed.Volume(),
                     "removed_roof_stock_mm3":removed.intersect(section).Volume(),
                     "added_mm3":added.Volume(),
                     "seam_change_mm3":(added.intersect(seam).Volume() if added.Solids() else 0.)
                                       +removed.intersect(seam).Volume()}
    checks["full_original_roof_stock_retained"] = all(
        r["removed_roof_stock_mm3"]<.001 for r in readings.values())
    checks["no_added_receiver_ledges"] = all(r["added_mm3"]<.001 for r in readings.values())
    checks["joint_and_fastener_region_unchanged"] = all(
        r["seam_change_mm3"]<.001 for r in readings.values())
    checks["halves_do_not_overlap"] = halves["front"].intersect(halves["back"]).Volume()<.001

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
            "minimum_wing_stop_probe_mm3":min(catches),"mesh":mesh_checks,
            "artifacts_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(g.HERE.glob("*.stl"))},
            "scope":"Geometry only. Physical results are recorded separately in physical-acceptance.json."}
    (g.HERE/"geometry-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if report["status"]!="pass":
        raise SystemExit(1)


if __name__=="__main__":
    main()
