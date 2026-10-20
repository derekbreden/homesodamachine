"""Dry wall structure for permanent junctions and purchased PP0308E elbows.

Three flat keepers seat downward on the junction necks. The purchased elbows
join the rear valve ports through short push-fit tubes. Round clearances in
the tray foot leave their fixed bodies and release collets accessible.
"""
from pathlib import Path
import sys
from functools import lru_cache

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path.insert(0, str(HW / 'printed-parts' / 'cadlib'))
import fits
import pump_receiver as receiver
import dock_retention as retention
import fixed_returns as plumbing
sys.path.insert(0,str(HW / "reference" / "jg-pp0308e-elbow"))
import elbow as union

STATIONS = ('west-outer', 'west-inner', 'east-inner', 'east-outer')
# Keepers by the receivers they hold: one per outer receiver, one for the inner pair.
KEEPERS = {'west': ('west-outer',), 'middle': ('west-inner', 'east-inner'),
           'east': ('east-outer',)}
# Plate reach past each held receiver axis; the slot keeps the sliding allowance past it.
KEEPER_REACH = 12.0
# The receiver bay round each rear collar and branch root: radial room and floor.
BAY_HALF = receiver.COLLAR_OD / 2 + 0.5
BAY_FLOOR = 12.0
KEEPER_BELOW = 6.0
KEEPER_ABOVE = receiver.NECK_GRIP_D/2 + 3.0
KEEPER_PARK_AIR = .75


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0,y0,z0))


def ycyl(radius, x, z, y0, y1):
    return cq.Solid.makeCylinder(radius,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))


def fused(parts):
    parts = tuple(parts)
    return (parts[0].fuse(*parts[1:]) if len(parts)>1 else parts[0]).clean()


def keeper_groups(plate):
    """Each keeper's held receiver axes and their common row height."""
    xs = dict(zip(STATIONS, (x for x, _z in plate['holes'])))
    row = plate['holes'][0][1]
    return {name: ([xs[st] for st in held], row) for name, held in KEEPERS.items()}


def keeper_arc_z(plate, *, parked=False):
    row=plate['holes'][0][1]
    if parked:return row + receiver.COLLAR_OD/2 + KEEPER_PARK_AIR + KEEPER_BELOW
    occupied=(receiver.BODY_OD**2+receiver.TUBE_OD**2-receiver.SEAL_BORE_D**2)**.5
    return row + occupied/2 - receiver.NECK_GRIP_D/2


def keeper(plate, name, *, parked=False):
    """One downward-open U keeper, seated by its crown on the occupied neck."""
    xs,_row=keeper_groups(plate)[name]
    arc=keeper_arc_z(plate,parked=parked)
    y0,y1=(plate['fore_y']+y for y in receiver.KEEPER_Y)
    low,high=arc-KEEPER_BELOW,arc+KEEPER_ABOVE
    body=box(min(xs)-KEEPER_REACH,max(xs)+KEEPER_REACH,y0,y1,low,high)
    r=receiver.NECK_GRIP_D/2
    for x in xs:
        body=body.cut(ycyl(r,x,arc,y0-.1,y1+.1).fuse(
            box(x-r,x+r,y0-.1,y1+.1,low-.1,arc)))
    return body.clean()


def _yz_prism(x0, x1, points):
    wire = cq.Wire.makePolygon([cq.Vector(x0, y, z) for y, z in points], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), cq.Vector(x1 - x0, 0, 0))


def keeper_bays(plate):
    """Seam-open keeper slots extend above the collar path for parking."""
    fore, aft = plate['fore_y'], plate['wall_aft_y'] + .1
    bed = plate['fixture_print_bed_z'] - .01
    face = fore + receiver.KEEPER_SLOT_Y[0]
    back = fore + receiver.KEEPER_SLOT_Y[1]
    cuts = []
    for xs, row in keeper_groups(plate).values():
        roof = keeper_arc_z(plate,parked=True)+KEEPER_ABOVE+.5
        slide = fits.running
        cuts.append(_yz_prism(min(xs) - KEEPER_REACH - slide, max(xs) + KEEPER_REACH + slide,
                              [(face, bed), (back, bed), (back, roof + back - face), (face, roof)]))
        for x in xs:
            cuts.append(_yz_prism(x - BAY_HALF, x + BAY_HALF,
                                  [(face, row - BAY_FLOOR), (aft, row - BAY_FLOOR),
                                   (aft, roof + aft - face), (face, roof)]))
    return fused(cuts)


def keeper_backing(plate):
    """Per keeper, the wall stock behind its slot that takes the receivers' aft load:
    [x0, x1, y0, y1, z0, z1] from the slot's back face to the wall's aft face."""
    fore, bed = plate['fore_y'], plate['fixture_print_bed_z']
    out = {}
    for name, (xs, row) in keeper_groups(plate).items():
        reach = KEEPER_REACH + fits.running
        out[name] = [min(xs) - reach, max(xs) + reach, fore + receiver.KEEPER_SLOT_Y[1],
                     plate['wall_aft_y'], bed, keeper_arc_z(plate,parked=True)+KEEPER_ABOVE+.5]
    return out


@lru_cache(maxsize=1)
def _scanned_elbow():
    return tuple(part.val() for _name,part in union.build())


def elbow_shape(layout):
    """All three native scanned solids, placed by their measured leg axes."""
    pose=cq.Location(cq.Plane(origin=layout['corner'],xDir=layout['x_axis'],normal=layout['up_axis']))
    return cq.Compound.makeCompound([part.moved(pose) for part in _scanned_elbow()])


def elbow_clearances(plate):
    """Round clearance through the rear tray foot for each elbow's upper leg."""
    tools=[]
    for data in plumbing.layouts(plate).values():
        elbow=data['elbow'];x,y,z=elbow['corner']
        tools.append(cq.Solid.makeCylinder(8.7, plumbing.ELBOW_FACE + .5,
                     cq.Vector(x,y,z), cq.Vector(0,0,1)))
    return fused(tools)


def fixed_features(plate):
    """Closed receiver wall and downward-open keeper slots."""
    cuts=[keeper_bays(plate)]
    for x,z in plate['holes']:
        cuts.append(receiver.receiver_wall_cut(plate['fore_y'],x,z))
    return [],cuts


def parts(plate,*,installed=True):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)]
        out['pump-receiver-'+name]=receiver.build_receiver(plate['fore_y'],x,z,installed=installed,junction=data['junction'])
        out['pump-elbow-'+name]=elbow_shape(data['elbow'])
    for name in KEEPERS:
        out['pump-keeper-'+name]=keeper(plate,name)
    return out


def part_color(name):
    if name.startswith('pump-receiver-'):return receiver.COLOR
    if name.startswith('pump-elbow-'):
        from _materials import M_JG_BLACK_PP
        return M_JG_BLACK_PP
    return cq.Color(.16,.16,.16)


def manufacturing_parts(plate):
    out={};declared=plumbing.layouts(plate)
    for name,(x,z) in zip(STATIONS,plate['holes']):
        data=declared[str(x)];local=receiver._local_junction(data['junction'],(x,plate['fore_y'],z))
        rows={'pump-receiver-'+name:receiver.print_solid(junction=local)}
        for part,shape in rows.items():out['enclosure-'+part]={'shape':shape,'color':part_color(part)}
    # Keepers print flat on their wall face; the two outer keepers are one part.
    for stem,name in (('pump-keeper-outer','west'),('pump-keeper-middle','middle')):
        keep=keeper(plate,name).rotate((0,0,0),(1,0,0),-90)
        b=keep.BoundingBox()
        out['enclosure-'+stem]={'shape':keep.translate((-b.center.x,-b.center.y,-b.zmin)),
                                'color':part_color(stem)}
    return out


def tube_setting_jig(plate, cartridge_face_y):
    """Factory gauge seats on the cartridge back and catches the four tube tips.

    Four open channels admit the stubs; the blind ends are the tip datum.
    The tool is removed before connecting the cartridge to the machine.
    """
    row=plate['holes'][0][1]
    tip=plate['fore_y']+receiver.CUSTOMER_TIP_Y
    body=box(plate['holes'][0][0]-8,plate['holes'][-1][0]+8,
             cartridge_face_y,tip+3,row-8,row+8)
    for x,z in plate['holes']:
        # Full axial bore with open top, ending at the tube's cut-face datum.
        bore=ycyl(3.5,x,z,cartridge_face_y-.1,tip)
        opening=box(x-3.5,x+3.5,cartridge_face_y-.1,tip,z,row+8.1)
        body=body.cut(bore.fuse(opening))
    # The two moving pole columns stand proud of the cartridge back to the wall face. Each
    # clears in one full-height groove 3 mm deep, so its walls are stock and not strips.
    for x,z in retention.column_stations(plate['holes']):
        half=retention.SLOT_HALF+1.0
        body=body.cut(box(x-half,x+half,cartridge_face_y-.1,cartridge_face_y+3,row-9,row+9))
    return body.clean()
