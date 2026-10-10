"""Native visual concept: LLDPE male tubes, one compliant receiver, magnetic retention.

Dimensions describe an illustrative assembly, not selected seal interference or a
qualified pressure connector. TPU bores are drawn in their inserted shape. The ring
magnets are shape placeholders without a force rating or selected supplier. The
existing display contact envelope is shown; its mounting and ribbon termination
are not a production layout. No slice, print, enclosure change or purchase is made.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import umbilical as u
import boot_concept as b

sys.path.insert(0, str(u.ROOT / "hardware/printed-parts/enclosure/y-wall-of-back-top"))
import _materials as m
import _y_wall_dimensions as yw
from _cadq_export import export_assembly

PORTS = {"flavor-a": (-4.75, 6.25, 6.35), "flavor-b": (4.75, 6.25, 6.35),
         "soda": (-4.75, -6.25, 6.35), "drain": (4.75, -6.25, 4.0)}
PUCK_D, PUCK_FRONT, PUCK_BACK = 25.0, 6.0, 24.0
MALE_TIP, MACHINE_TIP = 14.0, 16.0
GUARD_D, GUARD_ID, GUARD_TIP = 34.0, 31.0, 16.0
CORE_D, CUP_D, FRAME_D = 30.5, 34.5, 42.0
MAGNET_OD, MAGNET_ID, MAGNET_T = 30.0, 25.0, 3.0
KEY_HALF = 6.25 + b.GUIDE_Q / 2 - 6.35 + b.KEY_BITE
KEY_LUG = 6.25 + b.GUIDE_D / 2 - 4.0 + b.KEY_BITE
BLUE = u.cq.Color(*(v/255 for v in yw.chip_color("carb")))
COLORS = {"flavor-a": u.cq.Color(*(v/255 for v in yw.port_colors["flavor"])),
          "flavor-b": u.cq.Color(*(v/255 for v in yw.port_colors["flavor"])),
          "soda": u.cq.Color(*(v/255 for v in yw.port_colors["carb"])),
          "drain": u.cq.Color(*(v/255 for v in yw.port_colors["drain"]))}
TPU = u.cq.Color(.28, .52, .47)  # identification color; not a selected spool or compound


def annulus(outer, inner, y0, y1):
    return u.cyl(outer, y0, y1).cut(u.cyl(inner, y0-.1, y1+.1)).clean()


@contextmanager
def bundle_layout():
    names = ["KEY_HALF", "KEY_LUG", "STUB_Q", "STUB_D"]
    original = u.PORTS, {name: getattr(b, name) for name in names}
    u.PORTS = PORTS
    b.KEY_HALF, b.KEY_LUG, b.STUB_Q, b.STUB_D = KEY_HALF, KEY_LUG, MALE_TIP, MALE_TIP
    try:
        yield
    finally:
        u.PORTS = original[0]
        for name, value in original[1].items():
            setattr(b, name, value)


def key_stock():
    body = u.box(-18, 18, u.KEY_Y0, u.KEY_Y1, -KEY_HALF, KEY_HALF)
    x = PORTS["drain"][0]
    body = body.fuse(u.box(x-2.6, 18, u.KEY_Y0, u.KEY_Y1, -KEY_LUG, -KEY_HALF+.01))
    return body.intersect(u.cyl(GUARD_D, u.KEY_Y0-.1, u.KEY_Y1+.1)).clean()


def pogo(sign):
    part = u.P.build_female().val() if sign < 0 else u.P.build_male(2*u.POGO_RECESS).val()
    return part.rotate((0,0,0), (1,0,0), 90*sign).translate((0, sign*u.POGO_RECESS, 0))


def plug():
    body = u.cyl(GUARD_D, b.ENTRY, 0).fuse(annulus(GUARD_D, GUARD_ID, -.01, GUARD_TIP))
    tools = [b.cuff(), b.foam_fan(b.FOAM_CLEARANCE), b.cable_channel()]
    width = u.RIBBON_W + .9
    tools += [u.box(-width/2, width/2, b.GUIDE_START-.1, -10, *u.RIBBON_TOP)]
    tools += [annulus(MAGNET_OD+.2, MAGNET_ID-.2, -MAGNET_T-.2, .1)]
    tools += [u.P.build_female().val().rotate((0,0,0),(1,0,0),-90).translate((0,-u.POGO_RECESS,0))]
    tools += b.key_slot()
    for name, (x,z,od) in PORTS.items():
        tools += [u.cyl(b.GUIDE_Q if od > 5 else b.GUIDE_D, b.GUIDE_START-.1,.1,x,z), b.guide(name)]
    return u.cut_all(body, tools)


def receiver():
    # A rigid cup, central supported puck carrier and rear web, all blue stock.
    body = u.cyl(FRAME_D,-4,26).cut(u.cyl(CUP_D,-4.1,16.5))
    body = body.fuse(u.cyl(CORE_D,0,26)).clean()
    tools = [u.cyl(PUCK_D+.2,PUCK_FRONT,PUCK_BACK+.1),
             annulus(MAGNET_OD+.2,MAGNET_ID-.2,-.1,MAGNET_T+.2), pogo(+1)]
    for x,z,od in PORTS.values():
        tools.append(u.cyl(od+.45,-.1,26.1,x,z))
    return u.cut_all(body,tools)


def puck():
    # Filled elastomer body; bores show the inserted-state contact diameter.
    body = u.cyl(PUCK_D, PUCK_FRONT, PUCK_BACK)
    for x,z,od in PORTS.values():
        bore = u.cyl(od,PUCK_FRONT-.1,PUCK_BACK+.1,x,z)
        bore = bore.fuse(u.cyl(od+.5,7,8,x,z)).fuse(u.cyl(od+.5,11,19,x,z)).fuse(u.cyl(od+.5,22,23,x,z))
        entry = u.cq.Solid.makeCone((od+.9)/2,od/2,1,u._v(x,PUCK_FRONT,z),u._v(0,1,0))
        exit_ = u.cq.Solid.makeCone((od+.9)/2,od/2,1,u._v(x,PUCK_BACK,z),u._v(0,-1,0))
        body = body.cut(bore.fuse(entry).fuse(exit_))
    return body.clean()


def machine_tube(x,z,od):
    return u.cyl(od,MACHINE_TIP,54,x,z).cut(u.cyl(4.32 if od>5 else 2.5,MACHINE_TIP-.1,54.1,x,z))


def build():
    with bundle_layout():
        boot, seal, carrier = plug(), puck(), receiver()
        rear = u.cyl(38,26,30)
        for x,z,od in PORTS.values():
            rear = rear.cut(u.cyl(od+.3,25.9,30.1,x,z))
        wall = u.box(-30,30,-4,2,-27,27).cut(u.cyl(FRAME_D+.3,-4.1,2.1))
        parts = [("umbilical-plug",boot,BLUE,"plug"),
                 ("tube-key",key_stock(),BLUE,"plug"),
                 ("pogo-4p-female-pads",pogo(-1),m.C_DOCK,"plug"),
                 ("magnet-plug-illustrative",annulus(MAGNET_OD,MAGNET_ID,-MAGNET_T,0),m.M_NICKEL_PLATE,"plug"),
                 ("umbilical-socket",carrier,BLUE,"machine"),
                 ("compliant-four-passage-puck",seal,TPU,"machine"),
                 ("rear-tube-retainer",rear.clean(),m.M_PETGF_BLACK,"machine"),
                 ("back-top-wall",wall,m.M_PETGF_BLACK,"machine"),
                 ("pogo-4p-male-spring-pins",pogo(+1),m.C_DOCK,"machine"),
                 ("magnet-socket-illustrative",annulus(MAGNET_OD,MAGNET_ID,0,MAGNET_T),m.M_NICKEL_PLATE,"machine")]
        y0 = b.ENTRY-55
        for name,(x,z,od) in PORTS.items():
            parts += [(f"{name}-umbilical-tube",b.tube(name,y0),COLORS[name],"plug"),
                      (f"{name}-machine-tube",machine_tube(x,z,od),COLORS[name],"machine")]
        parts += [("soda-tube-foam",b.foam(y0),m.M_NITRILE_BLACK,"plug"),
                  ("umbilical-fabric-jacket",b.jacket(y0),m.M_PET_BRAID,"plug"),
                  ("display-ribbon",b.ribbon(y0),u.cq.Color(.62,.62,.65),"plug")]
        return parts


def main():
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    parts = build()
    roles = {}
    for suffix, keep in (("assembly",None),("section",u.box(-200,200,-25,100,-200,6.25))):
        assembly = u.cq.Assembly(name="compliant-receiver-"+suffix)
        for name,shape,color,role in parts:
            drawn = shape if keep is None else shape.intersect(keep)
            if drawn.Volume() > 1e-7:
                assembly.add(drawn,name=name,color=color)
                roles[name] = role
        export_assembly(assembly,str(out / (suffix+".step")))
    bodies = {name:{"valid":shape.isValid(),"solids":len(shape.Solids())} for name,shape,_,_ in parts}
    record = {
        "status":"visual concept; no selected seal interference, material or magnetic force",
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources_sha256":{str(p.relative_to(u.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (HERE.parent/"umbilical.py",HERE.parent/"boot_concept.py",Path(u.P.__file__))},
        "parameters_mm":{"plug_diameter":GUARD_D,"guard_inner_diameter":GUARD_ID,
                         "guard_projection":GUARD_TIP,"male_tube_projection":MALE_TIP,
                         "tube_pitch_x":9.5,"tube_pitch_z":12.5,"puck_diameter":PUCK_D,
                         "puck_thickness":PUCK_BACK-PUCK_FRONT,"seal_land_length":3,
                         "puck_front":PUCK_FRONT,"puck_back":PUCK_BACK,"tip_gap":MACHINE_TIP-MALE_TIP},
        "native_bodies":bodies,"roles":roles,
        "limits":["Bores are drawn in the inserted shape; unloaded interference is unspecified.",
                  "Annular magnets are illustrative placeholders without selected hardware or a force rating.",
                  "Tube grip, rear retention, snap-in receiver, electrical mounting/routing and sealing are unqualified.",
                  "Soft foam, fabric and TPU depict intended envelopes, not deformation simulations.",
                  "No printable project, pressure test, print or production change is included."]}
    (HERE/"concept.json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({"native_bodies":bodies,"parameters_mm":record["parameters_mm"]},indent=2))


if __name__ == "__main__":
    main()
