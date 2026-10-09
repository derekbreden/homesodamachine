"""Guided PET-GF boot: packed entry, gradual tube fan, and straight mating nose.

Soft-material solids describe intended compressed shapes, not a material
simulation. Saved coupling print articles are generated separately by umbilical.py.
"""
import math
import umbilical as u

GUIDE_L = 38.0
FAN_L = 45.0
CUFF_L = 15.0
PLUG_L = GUIDE_L + FAN_L + CUFF_L
GUIDE_START = -GUIDE_L
FAN_START = GUIDE_START - FAN_L
ENTRY = -PLUG_L
SHOULDER = u.FACE - 0.3                  # depth marker clear of the flange at the face stop
BODY_R = 17.0
CUFF_R = 13.75
SHOULDER_CHAMFER = 4.0                  # maximum 2 mm outward change over 4 mm of print rise
NOSE_CHAMFER_L = 1.6                    # 0.8 mm lead-in at 0.5 mm outward per mm of print rise
CUFF_LEAD, CUFF_SQUEEZE = 0.15, 0.10
BRAID_WALL = 0.50                        # intended envelope allowance, not measured weave thickness
EXTERNAL_L = 30.0
FREE_R = 17.6
FREE_CENTER = (1.0, -0.5)

# Insulated soda centered low; drain stays to its right, below FLAVOR-B.
# All axes below are X/Z; the guided outlet uses u.PORTS unchanged.
PACK = {'flavor-a': (-6.0, 7.8), 'flavor-b': (6.0, 7.8),
        'soda': (0.0, -3.5), 'drain': (10.7, 2.8)}
FREE_FLAVOR_Z = PACK['soda'][1] + math.sqrt((12.7 + 3.175 + 0.15) ** 2 - 6.0 ** 2)
FREE = {'flavor-a': (-6.0, FREE_FLAVOR_Z), 'flavor-b': (6.0, FREE_FLAVOR_Z),
        'soda': PACK['soda'], 'drain': (15.0, 3.0)}
FOAM_REAR_R, FOAM_END_R = 8.2, 6.65
FOAM_FAN_T = 0.5
FOAM_END = FAN_START + FAN_L * FOAM_FAN_T
FOAM_CLEARANCE = 0.15
RIBBON_REAR_Z = 11.1
GUIDE_Q, GUIDE_D = 6.65, 4.20             # accepted organizer L diameters; longer boot grip untested
FAN_Q, FAN_D = 6.85, 4.50
KEY_BITE = 0.15                          # intended bite after the tube bears on its guide bore
KEY_HALF = u.H + GUIDE_Q / 2 - 6.35 + KEY_BITE
KEY_LUG = u.H + GUIDE_D / 2 - 4.0 + KEY_BITE
DRAIN_PROUD = 1.8                        # illustrative release collar, exact fitting still unconfirmed
STUB_Q = u.COLLET_Q + u.U.INSERTION
STUB_D = u.DRAIN_STOP - u.D_L + DRAIN_PROUD + u.D_INSERTION


def ease(t):
    return t ** 3 * (10 - 15 * t + 6 * t * t)


def point(name, t):
    px, pz = PACK[name]
    x, z, _ = u.PORTS[name]
    s = ease(t)
    return u.cq.Vector(px + (x - px) * s, FAN_START + FAN_L * t, pz + (z - pz) * s)


def tangent(name, t):
    px, pz = PACK[name]
    x, z, _ = u.PORTS[name]
    ds = 30 * t * t * (1 - t) ** 2
    return u.cq.Vector((x - px) * ds, FAN_L, (z - pz) * ds)


def bezier(a, b, y0, length):
    """Exact quintic ease: parallel tangents and zero curvature at both ends."""
    ax, az = a
    bx, bz = b
    return u.cq.Edge.makeBezier([u.cq.Vector(ax + (bx - ax) * s, y0 + length * i / 5,
                                            az + (bz - az) * s)
                                for i, s in enumerate((0, 0, 0, 1, 1, 1))])


def fan(name):
    return bezier(PACK[name], u.PORTS[name][:2], FAN_START, FAN_L)


def circle_wire(r, center, normal=(0, 1, 0)):
    return u.cq.Wire.makeCircle(r, center, normal)


def guide(name):
    q = u.PORTS[name][2] > 5
    return u.cq.Solid.sweep_multi([circle_wire((FAN_Q if q else FAN_D)/2, point(name, 0)),
                                   circle_wire((GUIDE_Q if q else GUIDE_D)/2, point(name, 1))], fan(name))


def cuff(inset=0.0):
    return u.cq.Solid.makeLoft([
        circle_wire(CUFF_R + CUFF_LEAD - inset, u._v(0,ENTRY,0)),
        circle_wire(CUFF_R - CUFF_SQUEEZE - inset, u._v(0,FAN_START,0))])


def foam_fan(clearance=0.0):
    edge = fan('soda').trim(0.0, FOAM_FAN_T)
    return u.cq.Solid.sweep_multi([
        circle_wire(FOAM_REAR_R + clearance, point('soda', 0), tangent('soda', 0)),
        circle_wire(FOAM_END_R + clearance, point('soda', FOAM_FAN_T), tangent('soda', FOAM_FAN_T))], edge)


def ribbon(y0):
    """Covered ribbon rises gently to the nose's existing straight cable channel."""
    z1 = sum(u.RIBBON_TOP) / 2
    rear = u.box(-u.RIBBON_W / 2, u.RIBBON_W / 2, y0, FAN_START,
                 RIBBON_REAR_Z - u.RIBBON_T / 2, RIBBON_REAR_Z + u.RIBBON_T / 2)
    wires = []
    for i in range(9):
        t = i / 8
        z, y = RIBBON_REAR_Z + (z1 - RIBBON_REAR_Z) * ease(t), FAN_START + FAN_L * t
        wires.append(u.cq.Wire.makePolygon([u._v(-u.RIBBON_W/2, y, z-u.RIBBON_T/2),
                                             u._v(u.RIBBON_W/2, y, z-u.RIBBON_T/2),
                                             u._v(u.RIBBON_W/2, y, z+u.RIBBON_T/2),
                                             u._v(-u.RIBBON_W/2, y, z+u.RIBBON_T/2)], close=True))
    front = u.box(-u.RIBBON_W / 2, u.RIBBON_W / 2, GUIDE_START, u.RIBBON_DROP[1] - 0.5,
                  z1 - u.RIBBON_T / 2, z1 + u.RIBBON_T / 2)
    return u.fuse_all(rear, [u.cq.Solid.makeLoft(wires), front])


def cable_channel():
    wires = []
    z1 = sum(u.RIBBON_TOP) / 2
    for i in range(9):
        t = i / 8
        y, z = FAN_START + FAN_L * t, RIBBON_REAR_Z + (z1 - RIBBON_REAR_Z) * ease(t)
        wires.append(u.cq.Wire.makePolygon([u._v(-2.3,y,z-.85),u._v(2.3,y,z-.85),
                                             u._v(2.3,y,z+.85),u._v(-2.3,y,z+.85)], close=True))
    return u.cq.Solid.makeLoft(wires)


def key_slot():
    c = u.KEY_CLR
    x, _, _ = u.PORTS['drain']
    return [u.box(-u.PLUG_R-1,u.PLUG_R+1,u.KEY_Y0-c,u.KEY_Y1+c,-KEY_HALF-c,KEY_HALF+c),
            u.box(x-2.6-c,u.PLUG_R+1,u.KEY_Y0-c,u.KEY_Y1+c,-KEY_LUG-c,-KEY_HALF+.01)]


def key():
    x, _, _ = u.PORTS['drain']
    bar = u.box(-u.PLUG_R-1,u.PLUG_R+1,u.KEY_Y0,u.KEY_Y1,-KEY_HALF,KEY_HALF)
    lug = u.box(x-2.6,x+2.6,u.KEY_Y0,u.KEY_Y1,-KEY_LUG,-KEY_HALF+.01)
    return bar.fuse(lug).intersect(u.key()).clean()


def plug():
    lead = u.cq.Solid.makeLoft([
        u.profile_wire(u.PLUG_R,u.PLUG_F,-NOSE_CHAMFER_L),
        u.profile_wire(u.PLUG_R-.8,u.PLUG_F-.8,0)])
    nose_stock = u.profile(u.PLUG_R,u.PLUG_F,GUIDE_START,-NOSE_CHAMFER_L+.01).fuse(lead).clean()
    nose = u.plug().intersect(nose_stock)
    restore = list(u.key_slot())
    restore += [u.teardrop(u.HOLE_Q if od>5 else u.HOLE_D,GUIDE_START,0,x,z,u.PLUG_UP)
                for x,z,od in u.PORTS.values()]
    nose = u.fuse_all(nose, [s.intersect(nose_stock) for s in restore])
    shoulder = u.cq.Solid.makeLoft([
        circle_wire(BODY_R,u._v(0,SHOULDER-SHOULDER_CHAMFER,0)),
        u.profile_wire(u.PLUG_R,u.PLUG_F,SHOULDER)])
    body = u.fuse_all(nose,[u.cyl(2*BODY_R,ENTRY,SHOULDER-SHOULDER_CHAMFER),shoulder])
    # Recut the straight cable channel through the overlapping shoulder stock.
    w = u.RIBBON_W + 0.9
    tools = [cuff(), foam_fan(FOAM_CLEARANCE), cable_channel(),
             u.box(-w/2,w/2,GUIDE_START-.1,u.RIBBON_DROP[1],*u.RIBBON_TOP)]
    tools += key_slot()
    for name, (x,z,od) in u.PORTS.items():
        d = GUIDE_Q if od > 5 else GUIDE_D
        tools += [u.cyl(d,GUIDE_START-.1,.1,x,z),guide(name)]
    return u.cut_all(body,tools)


def tip(name):
    return STUB_Q if u.PORTS[name][2] > 5 else STUB_D


def tube_path(name,y0):
    fx,fz = FREE[name]
    px,pz = PACK[name]
    x,z,_ = u.PORTS[name]
    edges = [u.cq.Edge.makeLine(u._v(fx,y0,fz),u._v(fx,ENTRY-EXTERNAL_L,fz)),
             bezier(FREE[name],PACK[name],ENTRY-EXTERNAL_L,EXTERNAL_L),
             u.cq.Edge.makeLine(u._v(px,ENTRY,pz),u._v(px,FAN_START,pz)),fan(name),
             u.cq.Edge.makeLine(u._v(x,GUIDE_START,z),u._v(x,tip(name),z))]
    return u.cq.Wire.assembleEdges(edges)


def tube(name,y0,hollow=True):
    x,z = FREE[name]
    od = u.PORTS[name][2]
    center = u._v(x,y0,z)
    inner = [circle_wire((4.32 if od > 5 else 2.5)/2,center)] if hollow else []
    return u.cq.Solid.sweep(circle_wire(od/2,center),inner,tube_path(name,y0))


def foam(y0):
    x,z = PACK['soda']
    loose = u.cyl(25.4,y0,ENTRY-EXTERNAL_L,x,z)
    wires = []
    for i in range(9):
        t = i/8
        wires.append(circle_wire(12.7+(FOAM_REAR_R-12.7)*ease(t),
                                  u._v(x,ENTRY-EXTERNAL_L+EXTERNAL_L*t,z)))
    throat = u.cyl(2*FOAM_REAR_R,ENTRY,FAN_START,x,z)
    outer = u.fuse_all(loose,[u.cq.Solid.makeLoft(wires),throat,foam_fan()])
    return outer.cut(tube('soda',y0,hollow=False)).clean()


def fabric_envelope(y0,inset=0.0):
    at = ENTRY-EXTERNAL_L
    free = u.cyl(2*(FREE_R-inset),y0,at,*FREE_CENTER)
    wires = []
    for i in range(9):
        t,s = i/8,ease(i/8)
        r = FREE_R+(CUFF_R+CUFF_LEAD-FREE_R)*s-inset
        wires.append(circle_wire(r,u._v(FREE_CENTER[0]*(1-s),at+EXTERNAL_L*t,FREE_CENTER[1]*(1-s))))
    return u.fuse_all(free,[u.cq.Solid.makeLoft(wires),cuff(inset)])


def jacket(y0):
    return fabric_envelope(y0).cut(fabric_envelope(y0,BRAID_WALL)).clean()


def section_keep():
    """Viewer cut follows the soda centerline; it is not a manufactured feature."""
    z = -200.0
    rear = u._v(PACK['soda'][0],-300,z)
    edges = [u.cq.Edge.makeLine(rear,u._v(PACK['soda'][0],FAN_START,z))]
    controls = [u._v(PACK['soda'][0]+(u.PORTS['soda'][0]-PACK['soda'][0])*s,
                      FAN_START+FAN_L*i/5,z) for i,s in enumerate((0,0,0,1,1,1))]
    edges += [u.cq.Edge.makeBezier(controls),
              u.cq.Edge.makeLine(controls[-1],u._v(u.PORTS['soda'][0],300,z)),
              u.cq.Edge.makeLine(u._v(u.PORTS['soda'][0],300,z),u._v(-200,300,z)),
              u.cq.Edge.makeLine(u._v(-200,300,z),u._v(-200,-300,z)),
              u.cq.Edge.makeLine(u._v(-200,-300,z),rear)]
    return u.cq.Solid.extrudeLinear(u.cq.Face.makeFromWires(u.cq.Wire.assembleEdges(edges)),u._v(0,0,400))
