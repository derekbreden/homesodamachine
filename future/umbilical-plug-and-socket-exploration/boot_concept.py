"""Material-packing study for the plug's rear mouth, separate from saved print articles.

The foam is a space envelope, not a simulation of foam deformation. The braid is
a smooth envelope, not individual threads. These solids let the cutaway expose
the proposed tuck and its very tight packing without inventing a proven grip.
"""
import umbilical as u

POCKET_DEPTH = 15.0
JACKET_TUCK = 10.0
MOUTH_WALL = 1.0
BRAID_WALL = 0.35                         # illustrative, not a measured compressed braid thickness
POCKET_R = u.PLUG_R - MOUTH_WALL
POCKET_F = u.PLUG_F - MOUTH_WALL
FOAM_END = -u.PLUG_L + POCKET_DEPTH
JACKET_END = -u.PLUG_L + JACKET_TUCK
TRANSITION = 25.0
FREE_R = 20.4
FREE_CENTER = (-3.0, -3.0)


def circle_wire(r, y, x=0.0, z=0.0):
    return u.cq.Wire.makeCircle(r, u.cq.Vector(x, y, z), u.cq.Vector(0, 1, 0))


def packing_envelope(y0, y1, inset=0.0):
    """Loose circular braid converging to the plug's existing roof profile."""
    at = -u.PLUG_L - TRANSITION
    loose = circle_wire(FREE_R - inset, y0, *FREE_CENTER)
    start = circle_wire(FREE_R - inset, at, *FREE_CENTER)
    mouth = u.profile_wire(POCKET_R - inset, POCKET_F - inset, -u.PLUG_L)
    far = u.cq.Solid.makeLoft([loose, start], True)
    transition = u.cq.Solid.makeLoft([start, mouth], True)
    tucked = u.profile(POCKET_R - inset, POCKET_F - inset, -u.PLUG_L, y1)
    return u.fuse_all(far, [transition, tucked])


def plug():
    """One blind rear pocket, with a plain shoulder before the tube key.

    The 1 mm mouth wall is a packing-study allowance, not qualified stock for
    strain relief. No clip, barb, screw or separate boot is added.
    """
    body = u.plug().fuse(u.profile(u.PLUG_R, u.PLUG_F, -u.PLUG_L, -u.PLUG_L + 1.0))
    return body.cut(u.profile(POCKET_R, POCKET_F, -u.PLUG_L - 0.1, FOAM_END)).clean()


def ribbon(y0):
    zr = sum(u.RIBBON_TOP) / 2
    return u.box(-u.RIBBON_W / 2, u.RIBBON_W / 2, y0, u.RIBBON_DROP[1] - 0.5,
                 zr - u.RIBBON_T / 2, zr + u.RIBBON_T / 2)


def foam(y0):
    """Available compressed-foam volume around the soda tube, ending at the shoulder.

    Clipping shows where material must compress; it does not predict density,
    recovery, insertion force, or the resulting thermal insulation.
    """
    x, z, _ = u.PORTS['soda']
    stock = u.cyl(25.4, y0, FOAM_END, x, z)
    envelope = packing_envelope(y0, FOAM_END, BRAID_WALL)
    stock = stock.intersect(envelope)
    obstacles = [u.cyl(od, y0 - 1, FOAM_END + 1, x, z)
                 for x, z, od in u.PORTS.values()]
    obstacles.append(ribbon(y0 - 1))
    return u.cut_all(stock, obstacles)


def jacket(y0):
    outer = packing_envelope(y0, JACKET_END)
    inner = packing_envelope(y0, JACKET_END, BRAID_WALL)
    return outer.cut(inner).clean()
