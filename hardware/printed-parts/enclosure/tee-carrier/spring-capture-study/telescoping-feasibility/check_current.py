"""Current-carrier local study; deliberately excludes the stale front-top.

Frozen inputs include carrier STEP files and the nearby measured-tee/Kamoer
pack. No production import, source edit, generator or trace is performed.
"""
import hashlib
import json
from pathlib import Path

import cadquery as cq

from evaluate import box, along_y, ycyl, SLEEVE_ID, SLEEVE_OD, MOVING_ID, PROJECTION

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "current-inputs"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def section(body, x, width):
    """Thin native slab converging to a centroidal Y/Z material section.

    The X contribution is subtracted from Iyy/Izz. The residual dependence
    through the thin slab is bounded by a two-width comparison, not assumed.
    """
    slab = body.intersect(box((x-width/2, x+width/2), (70, 160), (150, 250)))
    area = slab.Volume()/width
    inertia = cq.Shape.matrixOfInertia(slab)
    iyy = inertia[1][1]/width - area*width*width/12
    izz = inertia[2][2]/width - area*width*width/12
    iyz = -inertia[1][2]/width
    return {"area_mm2":area, "Iyy_mm4":iyy, "Izz_mm4":izz,
            "Iyz_mm4":iyz, "I_for_pure_Mz_mm4":izz-iyz*iyz/iyy}


def main():
    manifest = json.loads((INPUTS/"manifest.json").read_text())
    assert sha(INPUTS/"interface.json") == manifest["interface_sha256"]
    for row in manifest["bodies"].values():
        assert sha(INPUTS/row["path"]) == row["sha256"], row["path"]
    interface = json.loads((INPUTS/"interface.json").read_text())["carrier_interface"]
    x, z = (interface["spring_stations"][1][k] for k in ("x", "z"))
    floor = interface["fixed_seat_floor_y"]
    end = interface["spring_stations"][1]["bore_floor_y"]
    mouth = interface["spring_bore_mouth_y"]
    r = interface["spring_bore_d"]/2
    u = interface["grip_back_x"] - x
    fill = along_y(((u,-r),(0,-r),(0,r),(u,r-u)), mouth, interface["spring_window_y"][1])
    bore = ycyl(MOVING_ID, interface["grip_rim_y"][0]-.1, end)
    sleeve = ycyl(SLEEVE_OD, floor-.1, floor+PROJECTION).cut(
        ycyl(SLEEVE_ID, floor-.11, floor+PROJECTION+.1)).clean()

    def place(shape, side):
        right = shape.translate((x,0,z))
        return right if side > 0 else right.mirror("YZ")

    native = {}
    for name, row in manifest["bodies"].items():
        path = INPUTS/row["path"]
        native[name] = (cq.importers.importStep(str(path)).val() if path.suffix==".step"
                        else cq.Shape.importBrep(str(path)))
    report = {"scope":manifest["scope"], "script_sha256":sha(__file__),
              "input_manifest_sha256":sha(INPUTS/"manifest.json"),
              "added_sleeve_neighbors":[], "moving_changes":{},
              "section_method":"Thin native X slabs at 0.02 and 0.01 mm; centroidal Y/Z tensor. Local geometric comparison only, not assembled rigidity, contact stiffness or a material/force prediction.",
              "sections":[]}
    candidates = {n:s for n,s in native.items() if not n.startswith("carrier-")}
    moving = {}
    for side, name in ((-1,"left"),(1,"right")):
        old = native["carrier-"+name]
        body = old.fuse(place(fill,side)).cut(place(bore,side)).clean()
        moving[side] = body
        assert body.isValid() and len(body.Solids())==1
        added, removed = body.cut(old), old.cut(body)
        # These original upper/lower flat guide bearings lie outside the
        # spring sleeve section and must retain every byte of native stock.
        top = interface["printed_grip_rim_z"][1]
        top_region = box((-150,150),(70,160),(top-3.0,top+.001))
        bottom = interface["printed_guide_body_z"][0]
        bottom_region = box((-150,150),(70,160),(bottom-.001,bottom+3.0))
        web_region = box((-90,90),(70,160),(150,250))
        report["moving_changes"][str(side)] = {
            "valid":True,"solids":len(body.Solids()),
            "added_mm3":added.Volume(),"removed_mm3":removed.Volume(),
            "removed_upper_flat_guide_mm3":removed.intersect(top_region).Volume(),
            "removed_lower_flat_guide_mm3":removed.intersect(bottom_region).Volume(),
            "removed_main_web_flange_joint_mm3":removed.intersect(web_region).Volume(),
            "removed_behind_spring_floor_mm3":removed.intersect(box((-150,150),(end+.001,160),(150,250))).Volume(),
        }
        fixed = place(sleeve,side)
        neighbors = []
        for label, obstacle in candidates.items():
            gap = fixed.distance(obstacle)
            neighbors.append((label,gap))
            assert fixed.intersect(obstacle).Volume()<1e-5,(side,label)
        report["added_sleeve_neighbors"].append({"side":side,"nearest":sorted(neighbors,key=lambda r:r[1])[:6]})
        report["moving_changes"][str(side)]["added_window_stock_neighbors_at_nominal_connected_pack"] = sorted(
            [(label,added.translate((0,2.15,0)).distance(obstacle)) for label,obstacle in candidates.items()],
            key=lambda r:r[1])[:6]
    before = native["carrier-right"]
    after = moving[1]
    for station in (40.0,90.0,91.5,92.5,93.5,97.535,101.8):
        readings=[]
        for width in (.02,.01):
            a,b=section(before,station,width),section(after,station,width)
            readings.append({"slab_width_mm":width,"before":a,"candidate":b,
                             "area_ratio":b["area_mm2"]/a["area_mm2"],
                             "I_for_pure_Mz_ratio":b["I_for_pure_Mz_mm4"]/a["I_for_pure_Mz_mm4"]})
        report["sections"].append({"x_mm":station,"readings":readings})
    report["qualification"] = {
        "full_current_shell_and_dynamic_assembly":"Not tested; current front-top is stale.",
        "spring_rate_force_rigidity_endurance":"Not inferred.",
        "mechanism_release":"Blocked by the established lateral carrier assembly in the separate matched-fixture check.",
    }
    (HERE/"current-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    main()
