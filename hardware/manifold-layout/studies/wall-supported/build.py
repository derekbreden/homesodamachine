"""Build the study's integral printed wall supports through tmp/takeover/cadq."""
from pathlib import Path
import importlib.util
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0,y0,z0))


def mesh(name, shape):
    v, f = shape.tessellate(.04,.12)
    v = np.array([p.toTuple() for p in v], np.float32)
    f = np.array(f, np.int32)
    np.savez_compressed(HERE / "parts" / (name+".npz"), v=v, f=f)


def main():
    out = HERE / "parts"; out.mkdir(exist_ok=True)
    exporter = module("supported_export", HERE.parent / "co2-fold/build.py")
    exporter.HERE = HERE
    export = exporter.export
    plan = json.loads((HERE / "context-plan.json").read_text())
    context = module("supported_context", HERE.parent / "co2-tpu/context.py")
    back = context.box(plan["rear_wall"]).cut(context.box(plan["interior_panel_relief"]))
    for p in plan["wet_ports"]:
        back = back.cut(cq.Solid.makeCylinder(p["bore_diameter_mm"]/2,9.02,
            cq.Vector(p["center_x_mm"],462.29,p["center_z_mm"]),cq.Vector(0,1,0)))
    c14 = plan["dry_openings"]["c14"]
    x,y,z = c14["flange_center_mm"]
    for key, start in (("flange_pocket_half_xz_mm", "flange_pocket_ymin_mm"),
                       ("body_opening_half_xz_mm", "body_opening_ymin_mm")):
        hx,hz = c14[key]
        back = back.cut(box(x-hx,x+hx,c14[start],471.31,z-hz,z+hz))
    for dx in (-c14["mount_pitch_mm"]/2,c14["mount_pitch_mm"]/2):
        back = back.cut(cq.Solid.makeCylinder(c14["mount_hole_radius_mm"],9.02,
            cq.Vector(x+dx,462.29,z),cq.Vector(0,1,0)))
    jack = module("supported_keystone", ROOT / "hardware/reference/riteav-keystone/riteav_keystone.py")
    x,y,z = plan["dry_openings"]["keystone"]["face_center_mm"]
    patch,catches = jack.receptacle_boss(x,z,y,462.3)
    cutter,_ = jack.receptacle_cut(x,z,y)
    if patch is not None:
        back = back.fuse(patch)
    back = back.cut(cutter)
    if catches is not None:
        back = back.fuse(catches)
    back = back.clean()

    left = box(-107.5,-98.5,244.,471.3,253.4,346.)
    right = box(98.5,107.5,244.,471.3,253.4,346.)
    bosses, holes, boss_centers = [], [], []
    for cz in (303.,328.):
        for yy in (365.,431.):
            for zz in (cz-6.5,cz+6.5):
                bosses.append(cq.Solid.makeCylinder(4.,4.02,cq.Vector(-98.52,yy,zz),cq.Vector(1,0,0)))
                holes.append(cq.Solid.makeCylinder(2.,7.51,cq.Vector(-94.49,yy,zz),cq.Vector(-1,0,0)))
                boss_centers.append([-94.5,yy,zz])
    relay_features = cq.Compound.makeCompound(bosses)
    for s in bosses:
        left = left.fuse(s)
    for s in holes:
        left = left.cut(s)
    relay_features = relay_features.cut(cq.Compound.makeCompound(holes))

    seat = module("supported_valve_seat", ROOT / "hardware/printed-parts/valve-seat/valve_seat.py")
    support_plan = json.loads((HERE / "support-plan.json").read_text())
    valve_features = {}
    for row in support_plan["valves"]:
        cx,cy,cz = row["post_origin_mm"]
        side = row["side"]
        x0,x1 = (cx-seat.seat_half_x,98.51) if side=="right" else (-98.51,cx+seat.seat_half_x)
        feature = box(x0,x1,cy-4.,cy+seat.seat_top_z,
                      cz-seat.seat_half_y,cz+seat.seat_half_y)
        def carry(s):
            return s.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),180).translate((cx,cy,cz))
        feature = feature.cut(carry(seat.build_sockets().val()))
        feature = feature.cut(carry(seat.build_port_channel(2*seat.seat_half_y+2).val())).clean()
        valve_features[row["name"]] = feature
        if side=="left":
            left = left.fuse(feature)
        else:
            right = right.fuse(feature)
    left,right = left.clean(),right.clean()
    ceiling = module("supported_roof", HERE.parent / "ceiling-fit/ceiling.py").build(HERE / "ceiling-plan.json")
    report = {"units":"mm", "scope":"Native isolated study walls; no production shell replacement",
              "parts":{}, "relay_mounts":{"boss_diameter_mm":8., "projection_mm":4.,
                "pilot_diameter_mm":4.,"pilot_depth_mm":7.5,"outer_cap_mm":5.5,
                "insert":"ruthex RX-M3x5.7", "board_underside_mm":boss_centers,
                "behind_pin_air_mm":2.},
              "valve_supports":support_plan,
              "rj11":{"face_mm":[x,y,z],"lip_mm":jack.LIP_D,"capture_depth_mm":jack.DEPTH,
                        "additional_inboard_reach_mm":jack.DEPTH-9.}}
    for name,shape in (("left-wall",left),("right-wall",right),("back-wall",back),("ceiling",ceiling)):
        report["parts"][name] = export(name,[("integral-body",shape)])
    # These duplicate only the added features for transparent-wall highlighting.
    # They are display meshes, not separately printed or collision-counted pieces.
    mesh("relay-mount-highlight",relay_features)
    for name,shape in valve_features.items():
        mesh(name+"-support-highlight",shape)
    (out / "build-report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
