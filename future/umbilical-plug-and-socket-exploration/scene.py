"""Scene STEPs for the umbilical plug and socket, with their viewer payloads, into `out/` (ignored):
the socket in a patch of back-top, the plug on its tubes, the two plugged in, a section through the
right-hand column, and the plug in the countertop hole. Prints the clearance check, fills the
README's figures and writes viz-spec.json. The parts themselves are umbilical.py's.

    tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/scene.py
"""
import json
import math
import sys
from pathlib import Path

_HERE = (Path(__file__).resolve() if "__file__" in globals()
         else Path.cwd() / "future/umbilical-plug-and-socket-exploration/scene.py")
sys.path.insert(0, str(_HERE.parent))
import umbilical as u  # noqa: E402
from umbilical import ROOT, cq, cyl, box, PORTS  # noqa: E402

sys.path[:0] = [str(ROOT / "hardware/printed-parts/enclosure/y-wall-of-back-top")]
from _cadq_export import export_assembly, import_step  # noqa: E402
import _materials as M  # noqa: E402
import _y_wall_dimensions as yw  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "out"
OUT.mkdir(parents=True, exist_ok=True)


def rgb(t):
    return cq.Color(*(c / 255.0 for c in t))


C_BOOT = rgb(yw.chip_color("carb"))
C_PORT = C_BOOT
C_MACHINE = M.M_PETGF_BLACK
C_WALL = C_MACHINE
COLOURS = {"flavor-a": rgb(yw.port_colors["flavor"]), "flavor-b": rgb(yw.port_colors["flavor"]),
           "soda": rgb(yw.port_colors["carb"]), "drain": rgb(yw.port_colors["drain"])}
C_SCREW = cq.Color(0.16, 0.16, 0.17)
C_RIBBON = cq.Color(0.62, 0.62, 0.65)
C_COUNTER = cq.Color(0.82, 0.81, 0.78)

PP0408W = import_step(u.U.STEP).val()
SOCKET, RETAINER, PLUG, KEY, PATCH = u.socket(), u.retainer(), u.plug(), u.key(), u.wall_patch()
DRAIN_PROUD = 1.8                          # as drawn; see umbilical.D_PROUD_MIN


def tube(od, idd, y0, y1, x, z):
    return cyl(od, y0, y1, x, z).cut(cyl(idd, y0 - 1, y1 + 1, x, z))


def union_solids(shift=0.0):
    """The four unions at their connected stations, or `shift` toward the plug."""
    out = {}
    for name, (x, z, od) in PORTS.items():
        if od > 5:
            out[name] = PP0408W.moved(u.union_location(x, z, u.COLLET_Q - shift))
        else:
            face = u.DRAIN_STOP - u.D_L + DRAIN_PROUD
            out[name] = u.auc44m(x, z, face - shift, DRAIN_PROUD)
    return out


def add_socket(a, pins=u.P.PIN_PROUD):
    a.add(SOCKET, name="umbilical-socket", color=C_PORT)
    a.add(RETAINER, name="union-retainer", color=C_MACHINE)
    for name, s in union_solids().items():
        label = "jg-pp0408w" if PORTS[name][2] > 5 else "neofit-auc44m"
        a.add(s, name=f"{name}-{label}-union", color=M.M_JG_WHITE_PP if PORTS[name][2] > 5 else M.M_NEOFIT_ACETAL)
    a.add(u.P.build_male(pins).val().moved(u.pogo_location(+1)), name="pogo-4p-male-spring-pins", color=M.C_DOCK)
    for x, bar in u.bars(+1):
        a.add(bar, name=f"kj-sb443-in-socket-{'right' if x > 0 else 'left'}", color=M.M_NICKEL_PLATE)
    for tag, s in u.pogo_hardware(+1):
        a.add(s, name=f"pogo-{tag}-socket", color=M.M_BRASS if tag.startswith("insert") else C_SCREW)
    for zc in u.RETAINER_SCREWS:
        tag = "top" if zc > 0 else "bottom"
        a.add(cyl(4.6, u.REAR - 5.7, u.REAR, 0, zc).cut(cyl(3.0, u.REAR - 6, u.REAR + 1, 0, zc)),
              name=f"m3-insert-{tag}", color=M.M_BRASS)
        head = u.REAR + u.RETAINER_T - 3.2
        a.add(cyl(5.5, head, head + 3.0, 0, zc).fuse(cyl(3.0, head - 8.0, head, 0, zc)),
              name=f"m3x8-screw-{tag}", color=C_SCREW)
    for name, (x, z, od) in PORTS.items():          # the machine's own runs out of each rear collet
        y0 = u.REAR + 2.74 - 16.0 if od > 5 else u.DRAIN_STOP + DRAIN_PROUD - 13.0
        a.add(tube(od, 4.32 if od > 5 else 2.5, y0, u.REAR + 40.0, x, z), name=f"{name}-machine-tube",
              color=COLOURS[name])


BUNDLE = 60.0


def add_plug(a, loc=cq.Location()):
    a.add(PLUG, name="umbilical-plug", color=C_BOOT, loc=loc)
    a.add(KEY, name="tube-key", color=C_BOOT, loc=loc)
    a.add(u.P.build_female().val().moved(u.pogo_location(-1)), name="pogo-4p-female-pads", color=M.C_DOCK, loc=loc)
    for x, bar in u.bars(-1):
        a.add(bar, name=f"kj-sb443-in-plug-{'right' if x > 0 else 'left'}", color=M.M_NICKEL_PLATE, loc=loc)
    for tag, s in u.pogo_hardware(-1):
        a.add(s, name=f"pogo-{tag}-plug", color=M.M_BRASS if tag.startswith("insert") else C_SCREW, loc=loc)
    for name, (x, z, od) in PORTS.items():
        tip = u.STUB_Q if od > 5 else u.STUB_D
        a.add(tube(od, 4.32 if od > 5 else 2.5, -u.PLUG_L - BUNDLE, tip, x, z), name=f"{name}-umbilical-tube",
              color=COLOURS[name], loc=loc)
    x, z, _ = PORTS["soda"]
    a.add(tube(25.4, 6.35, -u.PLUG_L - BUNDLE, -u.PLUG_L, x, z), name="soda-tube-foam", color=M.M_NITRILE_BLACK,
          loc=loc)
    zr = sum(u.RIBBON_TOP) / 2
    a.add(box(-u.RIBBON_W / 2, u.RIBBON_W / 2, -u.PLUG_L - BUNDLE, u.RIBBON_DROP[1] - 0.5, zr - u.RIBBON_T / 2,
              zr + u.RIBBON_T / 2), name="display-ribbon", color=C_RIBBON, loc=loc)


def export(name, build):
    a = cq.Assembly(name=f"scene-{name}")
    build(a)
    export_assembly(a, str(OUT / f"umbilical-{name}.step"))


export("socket", lambda a: (a.add(PATCH, name="back-top-wall", color=C_WALL), add_socket(a)))
export("plug", lambda a: add_plug(a, cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)))
MATED_PINS = 2 * u.POGO_RECESS


def mated(a):
    a.add(PATCH, name="back-top-wall", color=C_WALL)
    add_socket(a, MATED_PINS)
    add_plug(a)


export("mated", mated)


def section(a):
    """Everything plugged in, cut on the right-hand column's axes: FLAVOR-B over DRAIN, the cut facing +X."""
    keep = box(-200, u.H, -300, 300, -200, 200)
    tmp = cq.Assembly()
    mated(tmp)
    for child in tmp.children:
        shape = child.obj if isinstance(child.obj, cq.Shape) else child.obj.val()
        moved = shape.moved(child.loc)
        cut = moved.intersect(keep)
        if cut.Volume() > 1e-6:
            a.add(cut, name=child.name, color=child.color)


export("section", section)
COUNTER_T = 30.0


def counter(a):
    slab = (cq.Workplane("XY").box(120, 120, COUNTER_T, centered=(True, True, False)).translate((0, 0, -COUNTER_T))
            .faces(">Z").workplane().hole(u.COUNTER_HOLE).val())
    a.add(slab, name="countertop-1-3-8in-hole", color=C_COUNTER)
    add_plug(a, cq.Location(cq.Vector(0, 0, -COUNTER_T - 14.0), cq.Vector(1, 0, 0), -90))


export("counter", counter)

# --- checks ---------------------------------------------------------------------------------------
checks = {}


def gap(a, b):
    return a.distance(b)


cup_wall = SOCKET.intersect(box(-60, 60, u.FACE - 1, -0.5, -60, 60))
checks["plug_in_cup"] = gap(PLUG, cup_wall)
tx, tz, xf = u.profile_corners(u.PLUG_R, u.PLUG_F)
plug_reach = math.hypot(xf, u.PLUG_F)
checks["countertop_side"] = u.COUNTER_HOLE / 2 - u.PLUG_R
checks["countertop_corner"] = u.COUNTER_HOLE / 2 - plug_reach
unions = union_solids()
checks["union_to_socket"] = min(gap(s, SOCKET) for s in unions.values())
checks["union_to_union"] = min(gap(unions[a], unions[b]) for i, a in enumerate(unions) for b in list(unions)[i + 1:])
checks["union_to_retainer"] = min(gap(s, RETAINER) for s in unions.values())
released = union_solids(u.NOSE_AIR + u.U.COLLET_TRAVEL)
checks["released_ring_to_shoulder"] = min(gap(released[n].intersect(box(-60, 60, u.RING_FROM - 1, 60, -60, 60)),
                                              SOCKET) for n in ("flavor-a", "flavor-b", "soda"))
checks["screw_tip_to_union_cavity"] = u.RING_FROM - u.PILOT_END
male = u.P.build_male(MATED_PINS).val().moved(u.pogo_location(+1))
female = u.P.build_female().val().moved(u.pogo_location(-1))
checks["pogo_noses_apart"] = 2 * u.POGO_RECESS
checks["pogo_pin_compression"] = u.P.PIN_PROUD - MATED_PINS
checks["pogo_to_socket"] = gap(male, SOCKET)
checks["pogo_to_plug"] = gap(female, PLUG)
checks["hook_overlap"] = (u.BODY_R + 1.6) - (u.BODY_R + u.HOLE_CLR)
checks["stub_q_short_of_stop"] = u.COLLET_Q + u.U.INSERTION - u.STUB_Q
checks["key_bite"] = u.KEY_BITE
checks["cup_lead_before_stubs"] = u.CUP_DEPTH - u.STUB_Q
for k, v in checks.items():
    print(f"  {k:28s} {v:7.3f}")


# --- the README's figures and the page's captions -------------------------------------------------
def f2(v):
    return f"{v:.2f}"


FIG = {
    "UMB_PLUG_D": f2(2 * u.PLUG_R),
    "UMB_PLUG_H": f2(2 * u.PLUG_F),
    "UMB_PLUG_L": f"{u.PLUG_L:g}",
    "UMB_COUNTER_SIDE": f2(checks["countertop_side"]),
    "UMB_COUNTER_CORNER": f2(checks["countertop_corner"]),
    "UMB_PITCH": f2(u.PITCH),
    "UMB_UNION_GAP": f2(u.PITCH - u.U.RING_D),
    "UMB_CUP_DEPTH": f"{u.CUP_DEPTH:g}",
    "UMB_CUP_CLR": f2(u.CUP_CLR),
    "UMB_CUP_LEAD": f"{checks['cup_lead_before_stubs']:.1f}",
    "UMB_STUB_Q": f"{u.STUB_Q:.1f}",
    "UMB_STUB_D": f"{u.STUB_D:.1f}",
    "UMB_RELEASE": f"{u.RELEASE:g}",
    "UMB_NOSE_AIR": f"{u.NOSE_AIR:g}",
    "UMB_FLOAT": f2(u.NOSE_AIR + u.U.COLLET_TRAVEL),
    "UMB_HOLE_Q": f"{u.HOLE_Q:g}",
    "UMB_HOLE_D": f"{u.HOLE_D:g}",
    "UMB_FACE_W": f"{2 * u.FLANGE_R:.1f}",
    "UMB_FACE_H": f"{2 * u.BODY_F:.1f}",
    "UMB_FLANGE_T": f"{u.FLANGE_T:g}",
    "UMB_LEDGE": f"{u.FLANGE_R - u.BODY_R:g}",
    "UMB_HOOK_OVERLAP": f2(checks["hook_overlap"]),
    "UMB_SOCKET_DEPTH": f"{u.REAR + u.RETAINER_T - u.WALL_IN:.0f}",
    "UMB_WEB": f"{u.WEB:g}",
    "UMB_MAG_X": f"{u.MAG_X:.1f}",
    "UMB_KEY_BITE": f"{u.KEY_BITE:g}",
    "UMB_POGO_GAP": f"{2 * u.POGO_RECESS:.3f}",
    "UMB_CLR_UNION": f2(checks["union_to_union"]),
    "UMB_CLR_SCREW": f2(checks["screw_tip_to_union_cavity"]),
}
sys.path.insert(0, str(ROOT / "tools"))
from docgen import substitute_md  # noqa: E402
substitute_md(_HERE.parent / "README.md", FIG)

rel = OUT.resolve().relative_to(ROOT).as_posix()


def step(name):
    return f"{rel}/umbilical-{name}.step"


f = FIG
spec = {
    "title": "One-plug umbilical",
    "lede": "Blue Fiberon PET-GF15 plug and socket in a black enclosure receiver. Exploratory "
            "geometry; the insulation and jacket capture are unfinished.",
    "view": {"az": -70, "el": 20}, "frame": "each", "sync": True,
    "panels": [
        {"name": "Machine side",
         "caption": f"Flush in back-top: a {f['UMB_FACE_W']} x {f['UMB_FACE_H']} face on a "
                    f"{f['UMB_LEDGE']} mm side ledge, held from inside by two snap leaves.",
         "models": [{"step": step("socket"), "ghost": ["back-top-wall"]}]},
        {"name": "Plug",
         "caption": f"Ø{f['UMB_PLUG_D']} across, {f['UMB_PLUG_L']} long. One key clamps all four tubes; "
                    "the foam on the soda tube stops at the plug.",
         "models": [{"step": step("plug")}]},
        {"name": "Plugged in",
         "caption": f"The plug runs {f['UMB_CUP_LEAD']} mm into the {f['UMB_CUP_DEPTH']} mm cup before a stub "
                    "reaches its hole. The bars meet face to face.",
         "models": [{"step": step("mated"), "ghost": ["back-top-wall"]}]},
        {"name": "Release",
         "caption": f"FLAVOR-B over DRAIN. Each union floats {f['UMB_FLOAT']} mm: a pull drags it forward "
                    f"until its collet lands on the floor's back face and lets go. Side shows the cut.",
         "models": [{"step": step("section"), "ghost": ["back-top-wall"]}]},
        {"name": "Through the counter",
         "caption": f"The plug in the 1⅜″ countertop hole: {float(f['UMB_COUNTER_SIDE']):.1f} mm a side, "
                    f"{float(f['UMB_COUNTER_CORNER']):.1f} at its flats' corners.",
         "models": [{"step": step("counter"), "ghost": ["countertop*"]}]},
        {"name": "Machine-side plate", "image": "renders/print-machine-side.png",
         "caption": "The slicer's plate: socket on its flats, retainer, wall coupon roof-down. One pause for "
                    "the socket's bars."},
        {"name": "Plug-side plate", "image": "renders/print-plug-side.png",
         "caption": "The plug upside down on its top flat and the key on end. One pause for the plug's bars."},
    ],
}
(_HERE.parent / "viz-spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n")
print("README figures and viz-spec.json written")
