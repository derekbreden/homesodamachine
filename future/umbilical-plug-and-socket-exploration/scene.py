"""Scene STEPs for the umbilical plug and socket exploration: the socket side, the plug, the two
mated, and the plug in the countertop hole, each with its viewer payload, into `out/` (ignored).

Four John Guest PP0408W unions (reference/jg-pp0408w, Ø15.1) side by side at one depth, 8.5 mm of
PET-GF in front of their collets, the YYFKGCP pogo standing on end between the two columns with
its M1.4 inserts and screws, and one K&J B633 bar each side sealed under a 1.20 mm cover. DRAIN's
4 mm tube steps up to a 1/4" stem inside the plug, so all four unions are the same part. The plug
drops through the 1-3/8" countertop hole (faucet_assembly.countertop_hole_diameter = 34.93).

Frame: the socket floor (mating face) is y = 0, outside is -Y, the machine is +Y, up is +Z.

    tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/scene.py
"""
import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "hardware").is_dir())
REF = ROOT / "hardware" / "reference"
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ROOT / "hardware/printed-parts/cadlib"),
                str(ROOT / "hardware/printed-parts/enclosure/y-wall-of-back-top"),
                str(REF / "jg-pp0408w")]

import cadquery as cq  # noqa: E402
from _cadq_export import export_assembly, import_step  # noqa: E402
import _materials as M  # noqa: E402
import _y_wall_dimensions as yw  # noqa: E402
import jg_pp0408w as U  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)


def rgb(t):
    return cq.Color(*(c / 255.0 for c in t))


C_PANEL, C_PLUG = M.M_PETGF_BLACK, M.M_PETG_BLACK
C_TAP, C_FLAVOR, C_DRAIN = rgb(yw.port_colors["carb"]), rgb(yw.port_colors["flavor"]), rgb(yw.port_colors["drain"])
C_UNION = M.M_JG_WHITE_PP
C_RIBBON = cq.Color(0.62, 0.62, 0.65)
C_COUNTER = cq.Color(0.82, 0.81, 0.78)

COUNTER_HOLE = 34.93          # faucet_assembly.countertop_hole_diameter, 1-3/8"
COUNTER_T = 30.0

WEB = 1.5
BORE = 6.68                   # tube-collar bore for 1/4"
WALL = 8.5                    # PET-GF in front of the collets: room for the pogo inserts and screws
UNION_CLR = 0.5
PITCH = U.RING_D + UNION_CLR  # 15.6 between neighbouring union axes
H = PITCH / 2
R_AXIS = H * math.sqrt(2)

# name: (x, z, stub OD, stub ID, stub colour, umbilical OD, umbilical ID, umbilical colour)
PORTS = {
    "flavor-a": (-H, H, 6.35, 4.32, C_FLAVOR, 6.35, 4.32, C_FLAVOR),
    "flavor-b": (H, H, 6.35, 4.32, C_FLAVOR, 6.35, 4.32, C_FLAVOR),
    "tap": (-H, -H, 6.35, 4.32, C_TAP, 6.35, 4.32, C_TAP),
    "drain": (H, -H, 6.35, 4.0, M.M_NEOFIT_ACETAL, 4.0, 2.5, C_DRAIN),   # 1/4" stem of the 4 mm reducer
}
STUB = WALL + U.INSERTION     # 19.0 from the plug face

NOSE_L, NOSE_W, EAR_L = 17.54, 4.00, 23.4
POGO_CLR = 0.2
EAR_PITCH = 20.44                       # YYFKGCP ear holes
# yyfkgcp-pogo-4p/mounting-audit.md: two M1.4 x 4 x Ø2.3 heat-set inserts (Ø2.6 entry) and two
# M1.4 x 8 socket-head screws per half. Head Ø2.6 x 1.4 seats on the ear plate, 2 mm under the face.
INSERT_D, INSERT_L, INSERT_HOLE = 2.3, 4.0, 2.6
SCREW_D, SCREW_L, HEAD_D, HEAD_H = 1.4, 8.0, 2.6, 1.4
INSERT_TOP = 3.2
# K&J B633 bar, 3/8 x 3/16 x 3/16 in, N42, magnetized through thickness: one each side, on the face.
B633 = (9.525, 4.7625, 4.7625)
MAG_X = 8.6
# Sealed like the cartridge's RC62 pair (magnet-retention/README.md): a continuous 1.20 mm PET-GF
# cover on the mating face, the bar dropped in at a print pause against it, 0.48 mm of roof air.
COVER, ROOF_AIR = 1.20, 0.48

FACE_R = R_AXIS + BORE / 2 + WEB
PLUG_D = 2 * FACE_R
SOCK_D = PLUG_D + 0.6
SOCK_DEPTH = 15.0
PLATE_W, PLATE_T = 60.0, 6.0
UNION_MID = WALL + U.OVERALL / 2          # union mid-plane depth
CARRIER_END = WALL + U.OVERALL + 1.5
CARRIER_D = 2 * (R_AXIS + U.RING_D / 2 + 2.0)
SPLIT_Y = WALL                            # face part in front, carrier behind


def cyl(d, y0, y1, x=0.0, z=0.0):
    return cq.Solid.makeCylinder(d / 2.0, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def ring(do, di, y0, y1, x=0.0, z=0.0):
    return cyl(do, y0, y1, x, z).cut(cyl(di, y0 - 0.1, y1 + 0.1, x, z))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def stadium_z(length, width, y0, y1):
    """A slot standing on end (long axis Z) at the centre."""
    s = length - width
    b = box(-width / 2, width / 2, y0, y1, -s / 2, s / 2)
    return b.fuse(cyl(width, y0, y1, 0, -s / 2)).fuse(cyl(width, y0, y1, 0, s / 2))


def pogo_pocket(sign):
    def span(a, b):
        return (min(sign * a, sign * b), max(sign * a, sign * b))
    w = NOSE_W + 2 * POGO_CLR
    return [stadium_z(NOSE_L + 2 * POGO_CLR, w, *span(-0.1, 2.0)),
            stadium_z(EAR_L + 2 * POGO_CLR, w, *span(2.0, 3.2)),
            stadium_z(NOSE_L + 2 * POGO_CLR, w, *span(3.2, 5.6))]


def pogo_fasteners(sign):
    """Head counterbores, insert holes and screw clearance at both ear holes. sign: +1 into the panel."""
    def span(a, b):
        return (min(sign * a, sign * b), max(sign * a, sign * b))
    out = []
    for zc in (EAR_PITCH / 2, -EAR_PITCH / 2):
        out += [cyl(HEAD_D + 0.6, *span(-0.1, 2.0), 0, zc),
                cyl(INSERT_HOLE, *span(INSERT_TOP, INSERT_TOP + INSERT_L + 0.5), 0, zc),
                cyl(SCREW_D + 0.1, *span(INSERT_TOP + INSERT_L + 0.5, 2.0 + SCREW_L + 0.5), 0, zc)]
    return out


def magnet_pockets(sign):
    def span(a, b):
        return (min(sign * a, sign * b), max(sign * a, sign * b))
    L, W, T = B633
    return [box(x - L / 2 - 0.05, x + L / 2 + 0.05, *span(COVER, COVER + T + ROOF_AIR), -W / 2 - 0.05, W / 2 + 0.05)
            for x in (-MAG_X, MAG_X)]


def magnets(sign):
    """The two bars, flush with the face. sign: +1 for the panel, -1 for the plug."""
    L, W, T = B633
    def span(a, b):
        return (min(sign * a, sign * b), max(sign * a, sign * b))
    return [(x, box(x - L / 2, x + L / 2, *span(COVER, COVER + T), -W / 2, W / 2)) for x in (-MAG_X, MAG_X)]


def fasteners(sign):
    """Brass inserts and the M1.4 x 8 screws through the ears. sign: +1 for the panel, -1 for the plug."""
    def span(a, b):
        return (min(sign * a, sign * b), max(sign * a, sign * b))
    out = []
    for zc in (EAR_PITCH / 2, -EAR_PITCH / 2):
        out.append(("insert", zc, ring(INSERT_D, SCREW_D, *span(INSERT_TOP, INSERT_TOP + INSERT_L), 0, zc)))
        head = cyl(HEAD_D, *span(2.0 - HEAD_H, 2.0), 0, zc)
        shank = cyl(SCREW_D, *span(2.0, 2.0 + SCREW_L), 0, zc)
        out.append(("screw", zc, head.fuse(shank)))
    return out


C_INSERT = M.M_BRASS
C_SCREW = cq.Color(0.16, 0.16, 0.17)


def cut_all(body, tools):
    for t in tools:
        body = body.cut(t)
    return body.clean()


UNION = import_step(U.STEP).val()
POGO_M = import_step(REF / "yyfkgcp-pogo-4p" / "pogo-4p-male.step").val()
POGO_F = import_step(REF / "yyfkgcp-pogo-4p" / "pogo-4p-female.step").val()


def union_loc(x, z):
    """Axis along Y, near port face WALL behind the floor."""
    return cq.Location(cq.Vector(x, UNION_MID, z), cq.Vector(1, 0, 0), 90)


def on_end(face_dir):
    """Pogo frame (face +Z, long axis X) to face `face_dir` (+-1 along Y) with its long axis on Z."""
    return cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -90) * \
        cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90 if face_dir < 0 else -90)


def union_cavity(x, z):
    c = 0.3
    r0 = WALL
    segs = [(U.COLLET_D, r0, r0 + U.COLLET_PROUD),
            (U.RING_D, r0 + U.COLLET_PROUD, r0 + U.COLLET_PROUD + U.RING_LEN),
            (U.BARREL_D, r0 + U.COLLET_PROUD + U.RING_LEN, r0 + U.COLLET_PROUD + U.RING_LEN + U.BARREL_LEN),
            (U.RING_D, r0 + U.COLLET_PROUD + U.RING_LEN + U.BARREL_LEN, r0 + U.COLLET_PROUD + U.BODY_LEN),
            (U.COLLET_D, r0 + U.COLLET_PROUD + U.BODY_LEN, r0 + U.OVERALL)]
    return [cyl(d + 2 * c, a, b + 0.01, x, z) for d, a, b in segs] + [cyl(BORE, r0 + U.OVERALL, CARRIER_END + 1, x, z)]


def panel_shell():
    plate = (cq.Workplane("XY").box(PLATE_W, PLATE_T, PLATE_W, centered=(True, False, True))
             .translate((0, -SOCK_DEPTH, 0)).edges("|Y").fillet(6).val())
    body = plate.fuse(cyl(CARRIER_D, -SOCK_DEPTH, CARRIER_END)).clean()
    tools = [cyl(SOCK_D, -SOCK_DEPTH - 1, 0.0),
             cq.Solid.makeCone(SOCK_D / 2 + 1.2, SOCK_D / 2, 1.2, cq.Vector(0, -SOCK_DEPTH, 0), cq.Vector(0, 1, 0))]
    tools += pogo_pocket(+1) + pogo_fasteners(+1) + magnet_pockets(+1)
    for (x, z, *_r) in PORTS.values():
        tools.append(cyl(BORE, -0.1, WALL + 0.01, x, z))
        tools += union_cavity(x, z)
    return cut_all(body, tools)


def add_panel(a):
    shell = panel_shell()
    a.add(shell.intersect(box(-200, 200, -100, SPLIT_Y, -200, 200)), name="back-panel-face", color=C_PANEL)
    a.add(shell.intersect(box(-200, 200, SPLIT_Y, 200, -200, 200)), name="back-panel-carrier", color=C_PANEL)
    for name, (x, z, *_r) in PORTS.items():
        a.add(UNION, name=f"{name}-john-guest-pp0408w-union", color=C_UNION, loc=union_loc(x, z))
    a.add(POGO_M, name="pogo-4p-male-spring-pins", color=M.C_DOCK, loc=on_end(-1))
    for x, m in magnets(+1):
        a.add(m, name=f"kj-b633-magnet-panel-{'right' if x > 0 else 'left'}", color=M.M_NICKEL_PLATE)
    for kind, zc, solid in fasteners(+1):
        a.add(solid, name=f"pogo-{kind}-panel-{'top' if zc > 0 else 'bottom'}",
              color=C_INSERT if kind == "insert" else C_SCREW)


# --- the plug, face at y = 0 facing +Y ------------------------------------------------------------
IN_SOCKET = SOCK_DEPTH + 0.5
BODY_LEN, TAIL_LEN, TAIL_END_D = IN_SOCKET + 20.0, 14.0, 22.0
Y_TAIL = -BODY_LEN
Y_END = Y_TAIL - TAIL_LEN


def plug_shell():
    body = cyl(PLUG_D, Y_TAIL, 0.0).fuse(cq.Solid.makeCone(PLUG_D / 2, TAIL_END_D / 2, TAIL_LEN,
                                                         cq.Vector(0, Y_TAIL, 0), cq.Vector(0, -1, 0))).clean()
    tools = [cyl(19.0, Y_END - 0.1, Y_END + 8.0)] + pogo_pocket(-1) + pogo_fasteners(-1) + magnet_pockets(-1)
    for k in range(14):
        a = 2 * math.pi * (k + 0.5) / 14
        tools.append(cyl(3.0, Y_TAIL - 0.1, -IN_SOCKET - 2.0, (PLUG_D / 2 + 0.9) * math.cos(a),
                         (PLUG_D / 2 + 0.9) * math.sin(a)))
    for (x, z, *_r) in PORTS.values():
        tools.append(cyl(BORE, -12.0, 0.1, x, z))
    return cut_all(body, tools)


BEND_R, DOWN = 36.0, 80.0
Y_BEND = Y_END - 30.0
BUNDLE = {"flavor-a": (-5.2, 2.6), "drain": (0.0, 2.6), "flavor-b": (5.2, 2.6), "tap": (0.0, -2.6)}
RIBBON_AT = (0.0, -6.45)


def path(ox, oz, y_start, down):
    rho = BEND_R + oz
    c = cq.Vector(ox, Y_BEND, -BEND_R)
    p1 = cq.Vector(ox, Y_BEND, oz)
    mid = c + cq.Vector(0, -rho * math.sin(math.pi / 4), rho * math.cos(math.pi / 4))
    p2 = c + cq.Vector(0, -rho, 0)
    return cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(ox, y_start, oz), p1),
                                  cq.Edge.makeThreePointArc(p1, mid, p2),
                                  cq.Edge.makeLine(p2, p2 + cq.Vector(0, 0, -down))])


def swept(ox, oz, y_start, profile, down=DOWN):
    plane = cq.Plane(origin=(ox, y_start, oz), xDir=(1, 0, 0), normal=(0, -1, 0))
    return profile(cq.Workplane(plane)).sweep(path(ox, oz, y_start, down), transition="round").val()


def add_plug(a, loc):
    a.add(plug_shell(), name="umbilical-plug", color=C_PLUG, loc=loc)
    a.add(POGO_F, name="pogo-4p-female-flush-pads", color=M.C_DOCK, loc=loc * on_end(+1))
    for x, m in magnets(-1):
        a.add(m, name=f"kj-b633-magnet-plug-{'right' if x > 0 else 'left'}", color=M.M_NICKEL_PLATE, loc=loc)
    for kind, zc, solid in fasteners(-1):
        a.add(solid, name=f"pogo-{kind}-plug-{'top' if zc > 0 else 'bottom'}",
              color=C_INSERT if kind == "insert" else C_SCREW, loc=loc)
    y_in = Y_END + 5.0
    for name, (x, z, sod, sid, scol, uod, uid, ucol) in PORTS.items():
        a.add(ring(sod, sid, -11.5, STUB, x, z), name=f"{name}-stub", color=scol, loc=loc)
        ox, oz = BUNDLE[name]
        a.add(swept(ox, oz, y_in, lambda w, od=uod, idd=uid: w.circle(od / 2).circle(idd / 2)),
              name=f"{name}-tube-umbilical", color=ucol, loc=loc)
    a.add(swept(*RIBBON_AT, y_in, lambda w: w.rect(6.0, 1.0)), name="display-ribbon", color=C_RIBBON, loc=loc)
    a.add(swept(0.0, 0.0, Y_END + 3.0, lambda w: w.circle(10.1).circle(9.6), DOWN - 45.0),
          name="braided-sleeve", color=M.M_PET_BRAID, loc=loc)


panel = cq.Assembly(name="scene-panel")
add_panel(panel)
export_assembly(panel, str(OUT / "umbilical-panel.step"))

plug = cq.Assembly(name="scene-plug")
add_plug(plug, cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180))
export_assembly(plug, str(OUT / "umbilical-plug.step"))

mated = cq.Assembly(name="scene-mated")
add_panel(mated)
add_plug(mated, cq.Location(cq.Vector(0, 0, 0)))
export_assembly(mated, str(OUT / "umbilical-mated.step"))

# Dropping through the countertop: plug face down, the plug part-way through the hole.
counter = cq.Assembly(name="scene-counter")
slab = (cq.Workplane("XY").box(120, 120, COUNTER_T, centered=(True, True, False)).translate((0, 0, -COUNTER_T))
        .faces(">Z").workplane().hole(COUNTER_HOLE).val())
counter.add(slab, name="countertop-1-3-8in-hole", color=C_COUNTER)
add_plug(counter, cq.Location(cq.Vector(0, 0, -COUNTER_T - 12.0), cq.Vector(1, 0, 0), -90))
export_assembly(counter, str(OUT / "umbilical-counter.step"))

# --- checks -------------------------------------------------------------------------------------
pm = POGO_M.moved(on_end(-1)).BoundingBox()
print(f"pitch {PITCH:.2f} r_axis {R_AXIS:.3f} plug_d {PLUG_D:.2f} sock_d {SOCK_D:.2f} stub {STUB:.1f} "
      f"carrier_d {CARRIER_D:.1f} carrier_end {CARRIER_END:.1f}")
print(f"countertop hole {COUNTER_HOLE} - plug {PLUG_D:.2f} = {COUNTER_HOLE - PLUG_D:.2f} "
      f"({(COUNTER_HOLE - PLUG_D) / 2:.2f} a side)")
print(f"pogo male bbox x {pm.xmin:.2f}..{pm.xmax:.2f} y {pm.ymin:.2f}..{pm.ymax:.2f} z {pm.zmin:.2f}..{pm.zmax:.2f}")
placed = {}
for name, (x, z, sod, sid, *_r) in PORTS.items():
    placed[f"{name}:union"] = UNION.moved(union_loc(x, z))
    placed[f"{name}:stub"] = ring(sod, sid, -11.5, STUB, x, z)
placed["pogo:male"] = POGO_M.moved(on_end(-1))
for x, m in magnets(+1):
    placed[f"magnet{'R' if x > 0 else 'L'}:panel"] = m
for kind, zc, solid in fasteners(+1):
    placed[f"{kind}{'T' if zc > 0 else 'B'}:panel"] = solid
placed["pogo:female"] = POGO_F.moved(on_end(+1))
names = sorted(placed)
pairs = []
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if a.split(":")[0] == b.split(":")[0]:
            continue
        ka, kb = a.split(":")[0].rstrip("TBLR"), b.split(":")[0].rstrip("TBLR")
        if "screw" in (ka, kb) and ({ka, kb} & {"insert", "pogo"}) and a[-6:] == b[-6:] or \
                ("screw" in (ka, kb) and "pogo" in (ka, kb)):
            continue                      # a screw is meant to bear on the ear and thread its insert
        pairs.append((placed[a].distance(placed[b]), a, b))
pairs.sort()
print("closest pairs (mm):")
for d, a, b in pairs[:9]:
    print(f"  {d:6.3f}  {a}  vs  {b}")
own = min(placed[f"{n}:union"].distance(placed[f"{n}:stub"]) for n in PORTS)
print(f"stub in its own union socket: min gap {own:.3f}")
