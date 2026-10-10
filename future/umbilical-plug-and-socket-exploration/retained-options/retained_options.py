"""Two retained-hardware interface studies; no pressure-qualified connector or print job.

The native scene crops the existing boot at Y=-24. Actual selected contacts,
grooved block magnets, screws/inserts, mounting seats, wire passages, end stops,
guide key and rear tube key are included. Elastomer bores show inserted shape.
"""
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import umbilical as u
import _materials as m
sys.path.insert(0, str(u.ROOT / 'hardware/printed-parts/enclosure/y-wall-of-back-top'))
import _y_wall_dimensions as yw
from _cadq_export import export_assembly

BLUE = u.cq.Color(*(v/255 for v in yw.chip_color('carb')))
TPU = u.cq.Color(.35,.65,.5)
WIRE = u.cq.Color(.55,.55,.58)
SCREW_METAL = u.cq.Color(.70,.71,.73)
OD, RIM, TIP, PUCK_FRONT, PUCK_BACK = 34.,16.,14.,8.,24.
SLIP, BAR_HALF, RAIL_LO, RAIL_H = .15,3.325,1.95,.60


@dataclass(frozen=True)
class Layout:
    name: str
    half_x: float
    half_z: float
    offset_z: float
    guard_id: float
    vertical: bool
    pogo_z: float
    magnets: tuple

    @property
    def ports(self):
        return {'flavor-a':(-self.half_x,self.offset_z+self.half_z,6.35),
                'flavor-b':(self.half_x,self.offset_z+self.half_z,6.35),
                'soda':(-self.half_x,self.offset_z-self.half_z,6.35),
                'drain':(self.half_x,self.offset_z-self.half_z,4.)}


LAYOUTS = [Layout('thicker-guard',6.55,3.6,0.,27.,True,0.,((0.,11.),(0.,-11.))),
           Layout('closer-tubes',4.075,4.075,3.8,28.,False,-7.25,((-3.7,-10.3),(3.7,-10.3)))]


def bounds(a,b):
    return min(a,b),max(a,b)


def transform(shape,l,into):
    result = shape.rotate((0,0,0),(1,0,0),90*into)
    if l.vertical:
        result = result.rotate((0,0,0),(0,1,0),-90)
    return result.translate((0,into*u.POGO_RECESS,l.pogo_z))


def mouth(l,length,width,d0,d1,into):
    return transform(u.P.stadium(length,width,-d1,-d0).val(),l,into)


def mount_axes(l):
    return [(0,z) for z in u.P.ear_xs()] if l.vertical else [(x,l.pogo_z) for x in u.P.ear_xs()]


def pogo_cuts(l,into):
    # Front opens to the full ear plate, as in the accepted production seat.
    tools = [mouth(l,u.P.EAR_L+2*SLIP,u.P.BODY_W+2*SLIP,-.2,3.,into),
             mouth(l,u.P.BODY_L+2*SLIP,u.P.BODY_W+2*SLIP,2.99,4.15,into),
             mouth(l,10.,3.,4.,6.5,into)]
    face = into*u.POGO_RECESS
    for x,z in mount_axes(l):
        tools += [u.cyl(2.6,*bounds(face+into*2.99,face+into*5.01),x,z),
                  u.cyl(2.,*bounds(face+into*4.99,face+into*10.5),x,z)]
    return tools


def fasteners(face,into,x,z):
    # Ear bearing at depth3, insert at5..9, M1.4x8 headØ2.74x1.4.
    head = u.cyl(2.74,*bounds(face+into*.6,face+into*2.),x,z)
    screw = head.fuse(u.cyl(1.4,*bounds(face+into*2.,face+into*10.),x,z)).clean()
    screw = screw.cut(u.cq.Workplane('XZ',origin=(x,face+into*.6,z))
                      .polygon(6,1.3/math.cos(math.pi/6)).extrude(-into*.8).val()).clean()
    insert = u.cyl(2.3,*bounds(face+into*5.,face+into*9.),x,z)
    insert = insert.cut(u.cyl(1.4,*bounds(face+into*4.9,face+into*9.1),x,z)).clean()
    return screw,insert


def magnet(l,x,z,into):
    y0,y1 = bounds(RIM,RIM+into*u.BAR_T)
    bar = u.box(x-u.BAR/2,x+u.BAR/2,y0,y1,z-u.BAR/2,z+u.BAR/2)
    gy0,gy1 = bounds(RIM+into*u.GROOVE_TOP,RIM+into*(u.GROOVE_TOP+u.GROOVE_H))
    for side in [-1,1]:
        edge = x+side*u.BAR/2
        bar = bar.cut(u.box(*bounds(edge,edge-side*u.GROOVE_D),gy0,gy1,z-3.3,z+3.3))
    return bar.clean()


def magnet_channel(x,z,into,open_end=False):
    # Rails fit the common groove interval, accounting for band/groove tolerances.
    reach = BAR_HALF-(u.BAR/2-u.GROOVE_D+.10)
    lo,hi = z-BAR_HALF,z+BAR_HALF
    if open_end:
        limit=18. if into<0 else 22.
        if z>0: hi=limit
        else: lo=-limit
    y0,y1=bounds(RIM-into*.1,RIM+into*(u.BAR_T+.15))
    pocket=u.box(x-BAR_HALF,x+BAR_HALF,y0,y1,lo,hi)
    gy0,gy1=bounds(RIM+into*RAIL_LO,RIM+into*(RAIL_LO+RAIL_H))
    for side in [-1,1]:
        edge=x+side*BAR_HALF
        rail=u.box(*bounds(edge,edge-side*reach),gy0,gy1,lo-.1,hi+.1)
        pocket=pocket.cut(rail)
    return pocket.clean()


def rounded_relief(zsign,radius,y0,y1):
    z=7.675*zsign
    shape=u.box(-3.325-radius,3.325+radius,y0,y1,*bounds(z,30*zsign))
    shape=shape.fuse(u.box(-3.325,3.325,y0,y1,*bounds(z-radius*zsign,30*zsign)))
    for x in [-3.325,3.325]:
        shape=shape.fuse(u.cyl(2*radius,y0,y1,x,z))
    return shape.clean()


def puck_stock(l,clear=0.):
    y0,y1=PUCK_FRONT-.1*bool(clear),26.1 if clear else PUCK_BACK
    if l.vertical:
        shape=u.cyl(23.8+2*clear,y0,y1)
        for sign in [-1,1]:
            shape=shape.cut(rounded_relief(sign,1.-clear,y0-.1,y1+.1))
        shape=shape.cut(u.box(-2.35+clear,2.35-clear,y0-.1,y1+.1,-5.3+clear,5.3-clear))
        return shape.clean()
    r=4.275+clear
    x0,x1=-l.half_x,l.half_x
    z0,z1=l.offset_z-l.half_z,l.offset_z+l.half_z
    shape=u.box(x0-r,x1+r,y0,y1,z0,z1).fuse(u.box(x0,x1,y0,y1,z0-r,z1+r))
    for x,z in itertools.product([x0,x1],[z0,z1]):
        shape=shape.fuse(u.cyl(2*r,y0,y1,x,z))
    return shape.clean()


def puck(l):
    shape=puck_stock(l)
    for x,z,od in l.ports.values():
        bore=u.cyl(od,7.9,24.1,x,z)
        bore=bore.fuse(u.cyl(od+.20,12.,19.,x,z))
        bore=bore.fuse(u.cyl(od+.20,8.,9.,x,z)).fuse(u.cyl(od+.20,22.,24.,x,z))
        shape=shape.cut(bore)
    return shape.clean()


def key(l,y0,y1):
    upper=l.offset_z+l.half_z+3.325-6.35+.15
    lower=l.offset_z-l.half_z-3.325+6.35-.15
    drain=l.offset_z-l.half_z-2.1+4.-.15
    shape=u.box(-18,18,y0,y1,lower,upper)
    shape=shape.fuse(u.box(l.half_x-2.5,18,y0,y1,min(lower,drain),lower+.01))
    return shape.intersect(u.cyl(OD,y0-.1,y1+.1)).clean()


def wire_path(points,radius,rounded=False):
    vertices=[u._v(*p) for p in points]
    if rounded:
        edges=[]
        current=vertices[0]
        for i,corner in enumerate(vertices[1:-1],1):
            incoming=vertices[i-1]-corner
            outgoing=vertices[i+1]-corner
            trim=min(1.5,incoming.Length*.3,outgoing.Length*.3)
            before=corner+incoming.normalized()*trim
            after=corner+outgoing.normalized()*trim
            edges += [u.cq.Edge.makeLine(current,before),u.cq.Edge.makeBezier([before,corner,after])]
            current=after
        edges.append(u.cq.Edge.makeLine(current,vertices[-1]))
        edge=u.cq.Wire.assembleEdges(edges)
    else:
        edge=u.cq.Edge.makeBezier(vertices)
    start=u._v(*points[0])
    wire=u.cq.Wire.makeCircle(radius,start,edge.tangentAt(0))
    path=edge if isinstance(edge,u.cq.Wire) else u.cq.Wire.assembleEdges([edge])
    return u.cq.Solid.sweep(wire,[],path,True,False)


def wires(l,into,radius):
    out=[]
    for i,station in enumerate(u.P.contact_xs()):
        offset=(i-1.5)
        y=into*(u.POGO_RECESS+u.P.reach_back())
        if into<0:
            if l.vertical:
                points=[(offset,-24,11.9),(offset,-19,11.9),(0,-11,station),(0,y,station)]
            else:
                # Individual leads follow the outside of the tube cluster.
                side_y=-10.7+1.2*offset
                points=[(-offset,-24,11.9),(-offset,side_y,11.9),
                        (8.25,side_y,11.9),(8.25,side_y,-9.8),
                        (station,side_y,-9.8),
                        (station,side_y,l.pogo_z),(station,y,l.pogo_z)]
        elif l.vertical:
            points=[(0,y,station),(0,14,station),(0,34,station)]
        else:
            points=[(station,y,l.pogo_z),(station,7.5,-5.55),(station,34.,-5.55)]
        out.append(wire_path(points,radius,rounded=not l.vertical))
    return out


def cap_specs(l):
    if l.vertical:
        return [(sign,5.,13.35*sign) for sign in [1,-1]]
    return [(-1,0.,-14.75)]


def cap_stock(l,sign):
    if l.vertical:
        slab=u.box(-3.6,8.,11.,16.,*bounds(14.375*sign,18.*sign))
        arm=u.box(3.575,8.,11.,16.,*bounds(11.8*sign,18.*sign))
        shape=slab.fuse(arm)
    else:
        shape=u.box(-7.25,7.25,11.,16.,-18.,-13.775)
    return shape.intersect(u.cyl(OD,10.9,16.1)).clean()


def cap_cuts(x,z):
    return [u.cyl(2.6,10.6,11.1,x,z),u.cyl(2.,5.9,10.61,x,z)]


def cap_hardware(x,z):
    head=u.cyl(2.74,14.6,16.,x,z)
    screw=head.fuse(u.cyl(1.4,6.6,14.6,x,z)).clean()
    screw=screw.cut(u.cq.Workplane('XZ',origin=(x,16.,z))
                    .polygon(6,1.3/math.cos(math.pi/6)).extrude(.8).val()).clean()
    insert=u.cyl(2.3,6.6,10.6,x,z).cut(u.cyl(1.4,6.5,10.7,x,z)).clean()
    return screw,insert


def rear_magnet_stop(x,z,clear=0.):
    sign=1 if z>0 else -1
    stop=z+sign*(BAR_HALF+.15)
    return u.box(x-2.3-clear,x+2.3+clear,16.15-clear,26.01+clear,
                 *bounds(stop-sign*clear,stop+sign*(2.6+clear)))


def build(l):
    parts=[]
    def add(name,shape,color,role):
        parts.append((name,shape.clean(),color,role))
    body=u.cyl(OD,-24.,0.).fuse(u.cyl(OD,-.01,RIM).cut(u.cyl(l.guard_id,-.1,RIM+.1)))
    for x,z in l.magnets:
        boss=u.box(x-3.8,x+3.8,10.9,16.,z-3.8,z+3.8).intersect(u.cyl(OD,10.8,16.1))
        body=body.fuse(boss)
    if not l.vertical:
        for x,z in mount_axes(l):
            body=body.cut(u.cyl(5.5,-.1,16.1,x,z))
    body=body.fuse(u.box(12.,16.,0.,16.,-1.5,1.5)).clean()
    for _,x,z in cap_specs(l):
        body=body.fuse(u.cyl(4.6,6.,11.,x,z).intersect(u.cyl(OD,5.9,11.1)))
    tools=pogo_cuts(l,-1)+wires(l,-1,.65)
    if l.vertical:
        for x,z in mount_axes(l):
            tools.append(u.cyl(2.9,.1,16.1,x,z))
    for x,z,od in l.ports.values():
        tools.append(u.cyl(6.65 if od>5 else 4.2,-24.1,.1,x,z))
    k=key(l,-22.,-14.)
    tools.append(key(l,-22.15,-13.85))
    for x,z in l.magnets:tools.append(magnet_channel(x,z,-1,True))
    for sign,x,z in cap_specs(l):
        cap=cap_stock(l,sign)
        body=body.cut(cap)
        tools+=cap_cuts(x,z)
        cap=cap.cut(u.cyl(1.7,10.9,16.1,x,z)).cut(u.cyl(3.0,14.6,16.1,x,z))
        add(f'plug-magnet-endstop-{sign}',cap,BLUE,'cap')
        screw,insert=cap_hardware(x,z)
        add(f'cap-screw-{sign}',screw,SCREW_METAL,'cap')
        add(f'cap-insert-{sign}',insert,m.M_BRASS,'plug')
    body=u.cut_all(body,tools)
    add('plug-interface',body,BLUE,'plug')
    add('tube-key',k,BLUE,'plug')

    core_d=l.guard_id-.5
    carrier=u.cyl(core_d,0.,26.)
    if not l.vertical:
        for x,z in mount_axes(l):carrier=carrier.fuse(u.cyl(5.,0.,16.01,x,z))
    carrier=carrier.fuse(u.cyl(42.,16.,26.))
    carrier=carrier.fuse(u.cyl(42.,13.5,16.01).cut(u.cyl(34.5,13.4,16.02))).clean()
    tools=pogo_cuts(l,1)+wires(l,1,.65)
    tools += [puck_stock(l,.10),u.box(11.65,25.,-.1,16.1,-1.65,1.65)]
    for x,z in l.magnets:
        tools.append(u.box(x-3.95,x+3.95,10.75,16.01,z-3.95,z+3.95))
    for _,x,z in cap_specs(l):tools.append(u.cyl(5.2,-.1,11.15,x,z))
    if l.vertical:
        for sign in [-1,1]:
            tools.append(u.box(-3.475,3.475,11.,21.,*bounds(7.5*sign,30*sign)))
            tools.append(u.box(3.425,8.15,10.85,16.1,*bounds(11.65*sign,18.15*sign)))
    else:
        tools.append(u.box(-7.125,7.125,11.,21.,-30.,-6.875))
    for x,z,od in l.ports.values():tools.append(u.cyl(od+.30,-.1,26.1,x,z))
    for x,z in l.magnets:
        tools.append(magnet_channel(x,z,1,True))
        tools.append(rear_magnet_stop(x,z,.15))
    rear_mounts=list(itertools.product([-15.,15.],[-8.,8.]))
    for x,z in rear_mounts:
        tools += [u.cyl(2.6,24.6,26.1,x,z),u.cyl(2.,19.9,24.61,x,z)]
    carrier=u.cut_all(carrier,tools)
    add('socket-carrier',carrier,BLUE,'machine')
    seal=puck(l)
    add('supported-elastomer-puck',seal,TPU,'machine')
    for into,role in [(-1,'plug'),(1,'machine')]:
        contact=u.P.build_female().val() if into<0 else u.P.build_male(2*u.POGO_RECESS).val()
        add('pogo-pad-half' if into<0 else 'pogo-spring-half',transform(contact,l,into),m.C_DOCK,role)
        for i,(x,z) in enumerate(mount_axes(l)):
            screw,insert=fasteners(into*u.POGO_RECESS,into,x,z)
            add(f'pogo-screw-{role}-{i}',screw,SCREW_METAL,role)
            add(f'pogo-insert-{role}-{i}',insert,m.M_BRASS,role)
        for i,(x,z) in enumerate(l.magnets):add(f'SB443-{role}-{i}',magnet(l,x,z,into),m.M_NICKEL_PLATE,role)
        for i,wire in enumerate(wires(l,into,.40)):add(f'insulated-lead-{role}-{i}',wire,WIRE,role)
    retainer=u.cyl(42.,26.,30.).fuse(u.cyl(30.,29.99,42.))
    backing=puck_stock(l).translate((0,16.,0)).intersect(u.box(-22.,22.,24.,26.01,-22.,22.))
    retainer=retainer.fuse(backing)
    for x,z in l.magnets:retainer=retainer.fuse(rear_magnet_stop(x,z))
    tools=[]
    for x,z,od in l.ports.values():
        tools.append(u.cyl(6.65 if od>5 else 4.2,25.9,42.1,x,z))
    rear_key=key(l,32.,40.).intersect(u.cyl(30.,31.9,40.1))
    tools.append(key(l,31.85,40.15))
    for wire in wires(l,1,.65):tools.append(wire)
    for x,z in rear_mounts:
        tools += [u.cyl(1.7,25.9,30.1,x,z),u.cyl(3.,28.6,30.1,x,z)]
        screw,insert=cap_hardware(x,z)
        add(f'retainer-screw-{x}-{z}',screw.translate((0,14.,0)),SCREW_METAL,'machine')
        add(f'retainer-insert-{x}-{z}',insert.translate((0,14.,0)),m.M_BRASS,'machine')
    add('rear-retainer',u.cut_all(retainer,tools),m.M_PETGF_BLACK,'machine')
    add('rear-tube-key',rear_key,m.M_PETGF_BLACK,'machine')
    for name,(x,z,od) in l.ports.items():
        color=u.cq.Color(*(v/255 for v in yw.port_colors['carb' if name=='soda' else 'drain' if name=='drain' else 'flavor']))
        for suffix,y0,y1,role in [('umbilical',-34.,TIP,'plug'),('machine',16.,50.,'machine')]:
            shape=u.cyl(od,y0,y1,x,z).cut(u.cyl(4.32 if od>5 else 2.5,y0-.1,y1+.1,x,z))
            add(name+'-'+suffix+'-tube',shape,color,role)
    wall=u.box(-28.,28.,16.,22.,-25.,25.).cut(u.cyl(42.3,15.9,22.1))
    add('enclosure-context',wall,m.M_PETGF_BLACK,'machine')
    return parts


def checks(l,parts):
    shapes={name:shape for name,shape,_,_ in parts}
    pairs=[('plug-interface','socket-carrier'),('plug-interface','supported-elastomer-puck'),
           ('socket-carrier','supported-elastomer-puck'),('socket-carrier','rear-retainer'),
           ('rear-retainer','supported-elastomer-puck'),('plug-interface','rear-retainer')]
    for name in list(shapes):
        if '-tube' in name:
            pairs += [('plug-interface',name),('socket-carrier',name),('supported-elastomer-puck',name)]
        if name.startswith('SB443') or name.startswith('pogo-') and 'insert' not in name and 'screw' not in name:
            host='plug-interface' if 'plug' in name or name=='pogo-pad-half' else 'socket-carrier'
            pairs.append((host,name))
    leads=[n for n in shapes if n.startswith('insulated-lead')]
    pairs += list(itertools.combinations(leads,2))
    for lead in leads:
        pairs += [(lead,n) for n in shapes if n.endswith('-tube') or n.startswith('SB443')
                  or n.startswith('pogo-screw') or n.startswith('pogo-insert')
                  or n in ['plug-interface','socket-carrier','supported-elastomer-puck',
                           'tube-key','rear-tube-key','rear-retainer']]
    for cap in [n for n in shapes if n.startswith('plug-magnet-endstop')]:
        pairs += [(cap,n) for n in ['plug-interface','socket-carrier','supported-elastomer-puck']]
    for n in shapes:
        if n.startswith('SB443-machine'):pairs.append(('rear-retainer',n))
    overlap={a+'/'+b:shapes[a].intersect(shapes[b]).Volume() for a,b in pairs}
    # Pogo screw/tool sweep before magnets and end stops are installed.
    access={}
    for x,z in mount_axes(l):
        ray=u.cyl(2.74, -.2,19.,x,z)
        access[f'{x},{z}']=shapes['plug-interface'].intersect(ray).Volume()
    return {'native_bodies':{n:{'valid':s.isValid(),'solids':len(s.Solids())} for n,s,_,_ in parts},
            'unintended_overlap_mm3':{k:v for k,v in overlap.items() if v>1e-6},
            'pogo_head_access_before_magnets_mm3':access,
            'tube_pitch_mm':[2*l.half_x,2*l.half_z],
            'main_guard_wall_mm':(OD-l.guard_id)/2,
            'magnet_corner_stock_mm':min(OD/2-((abs(x)+BAR_HALF)**2+(abs(z)+BAR_HALF)**2)**.5 for x,z in l.magnets),
            'nominal_radial_counter_clearance_mm':(34.93-OD)/2,
            'ear_relief_outer_stock_mm':None if l.vertical else OD/2-(10.22**2+l.pogo_z**2)**.5-2.75,
            'cap_counterbore_outer_stock_mm':min(OD/2-(x*x+z*z)**.5-1.5 for _,x,z in cap_specs(l)),
            'guide_bore_web_between_large_tubes_mm':min(2*l.half_x,2*l.half_z)-6.65,
            'inserted_bore_diameter_mm':[6.35,4.],
            'unloaded_seal_interference':'unspecified',
            'drawing_common_magnet_groove_interval_mm':[1.8542,2.6924],
            'printed_rail_depth_interval_mm':[RAIL_LO,RAIL_LO+RAIL_H],
            'roles':{n:r for n,_,_,r in parts}}


def main():
    out=HERE/'out'
    out.mkdir(exist_ok=True)
    record={'scope':'Native interface options with retained selected hardware; cropped boot; no print or pressure qualification.',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'sources':{str(path.relative_to(u.ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in [HERE/'retained_options.py',Path(u.P.__file__),Path(yw.__file__)]},'options':{}}
    for l in LAYOUTS:
        parts=build(l)
        assembly=u.cq.Assembly(name=l.name)
        for name,shape,color,_ in parts:assembly.add(shape,name=name,color=color)
        export_assembly(assembly,str(out/(l.name+'.step')))
        record['options'][l.name]=checks(l,parts)
    (HERE/'geometry.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({name:{k:v for k,v in data.items() if k not in ['native_bodies','roles']} for name,data in record['options'].items()},indent=2))


if __name__=='__main__':main()
