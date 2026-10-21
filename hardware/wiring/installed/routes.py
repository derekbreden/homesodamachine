"""Installed route families and independently editable local route overrides.

Routes name hardware-relative stations. Conductors have separate lanes; a
bundle is the actual sum of those conductors, not N wires on one centreline.
"""
from __future__ import annotations

import json
from pathlib import Path

from .model import STOCK, add, sub, mul, dot, finish
from .terminals import bounds, centre

OVERRIDES = Path(__file__).with_name('route-overrides.json')


def station(spec, attachments):
    return attachments.station(spec)


def routed(connections, attachments):
    t=attachments.terminals
    overrides=json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}
    groups={}
    for c in connections:
        groups.setdefault(c.harness,[]).append(c.id)
    result=[]
    for c in connections:
        from .bundles import core_route
        shared=core_route(c,attachments)
        if shared is not None:
            result.append(shared)
            continue
        a,b=t[c.start],t[c.end]
        guide=guide_points(c,attachments,groups)
        saved=overrides.get(c.id,{})
        if 'stations' in overrides.get(c.id,{}):
            guide=[station(p,attachments) for p in overrides[c.id]['stations']]
        # Relaxed exits are explicit, including at the solder tails. The short
        # local land is not an assumed rigid connector keep-out envelope.
        lead=6.0 if STOCK[c.stock]['awg']==22 else 8.0
        start_lead,end_lead=saved.get('end_lands_mm',[lead,lead])
        if guide and not saved.get('preserve_stations'):
            first=dot(sub(guide[0],a.point),a.outward)
            last=dot(sub(guide[-1],b.point),b.outward)
            if first<lead+4:
                guide[0]=add(guide[0],mul(a.outward,lead+4-first))
            if last<lead+4:
                guide[-1]=add(guide[-1],mul(b.outward,lead+4-last))
        points=[a.point,add(a.point,mul(a.outward,start_lead)),*guide,
                add(b.point,mul(b.outward,end_lead)),b.point]
        route=finish(c,points,saved.get('note',''),saved.get('bend_radius_mm'))
        route.status=saved.get('route_status','proposed')
        result.append(route)
    return result


def guide_points(c, at, groups):
    t=at.terminals; a,b=t[c.start],t[c.end]
    p,q=a.point,b.point
    idx=groups[c.harness].index(c.id)
    lane=(idx%5-2)*1.85
    core=at.part('foam-cap-top');clo,chi=bounds(core)
    deck=chi[2]+5.55                 # the clear strip under the installed electronics
    wago_a=centre(at.part('wago-mana'));wago_b=centre(at.part('wago-manb'))
    peel=wago_a[1]+10.

    def board_escape(j, index, x=None):
        # Three physical ribbon layers: J1 5P, J1 4P, descending J2 4P.
        layer=2 if j=='J2' else index//5
        row=index%5
        x=(92.95+layer*1.8) if x is None else x
        z=clo[2]+10.2+row*1.8
        aft=bounds(at.part('pcba'))[1][1]+3.2+(4-row)*1.9
        return [(p[0],aft,p[2]),(x,aft,p[2]),(x,aft,z),(x,peel+index*.15,z)]

    if c.harness in ('J1','J2'):
        j=c.harness
        if c.start.startswith(j+'.') and c.start not in ('J2.OUT3',):
            label=c.start.split('.')[1]
            labels=['COM']+[f'OUT{i}' for i in range(1,9)] if j=='J1' else ['COM','OUT1','OUT2','FAN']
            index=labels.index(label)
            pts=board_escape(j,index)
            if label=='COM':
                return pts+[(79.5,peel+4+index*1.8,q[2]),(79.5,q[1],q[2])]
            origin=pts[-1]
        elif c.start=='J2.OUT3':
            return [(p[0],p[1]+8.,p[2]),(q[0]-4.,p[1]+8.,q[2]),(q[0]-4.,q[1]+8.,q[2])]
        else:
            pts=[];origin=(79.5,p[1]+10.+lane,p[2])
            pts.append((p[0]-6.,p[1],p[2]));pts.append(origin)
        if c.end.startswith('V-'):
            letter=c.end[2]
            if letter in 'ABK':
                z=316.+lane
                return pts+[(76.+lane,origin[1],z),(76.+lane,q[1]-10.,z),
                            (q[0],q[1]-10.,z),(q[0],q[1]-7.,q[2])]
            if letter in 'FI':
                z=289.+lane
                return pts+[(78.+lane,peel+8.,z),(78.+lane,155.+lane,z),
                            (q[0],155.+lane,z),(q[0],q[1],z)]
            if letter in 'EH':
                z=q[2]-9.-(idx%2)*2.
                return pts+[(49.+lane,peel+8.,origin[2]),(49.+lane,peel+8.,z),
                            (49.+lane,q[1],z),(q[0],q[1],z)]
            if letter in 'GJ':
                z=q[2]; y=q[1]+10.+(idx%2)*2.
                return pts+[(49.+lane,peel+11.,origin[2]),(49.+lane,peel+11.,z),
                            (49.+lane,y,z),(q[0],y,z)]
            if letter in 'CD':
                z=q[2]-12.-(idx%2)*2.
                return pts+[(48.+lane,peel+14.,origin[2]),(48.+lane,peel+14.,z),
                            (48.+lane,q[1],z),(q[0],q[1],z)]
        # The donor fan interface remains a boundary, reached above the crown.
        z=q[2]+4.+(idx%2)*2.
        return pts+[(46.+lane,peel+14.,origin[2]),(46.+lane,peel+14.,z),
                    (46.+lane,q[1]+20.,z),(q[0],q[1]+20.,z)]

    if c.harness in ('J13','J9'):
        n=idx%4
        x=65.+n*1.85 if c.harness=='J13' else 54.+n*1.85
        # The two looms cross over the valve banks, then approach the ridge
        # in separate flat lanes below the funnel frame.
        z=292.+(0 if c.harness=='J13' else 8.)
        y=108.+n*1.85 if c.harness=='J13' else 96.+n*1.85
        if c.harness=='J13':
            return [(p[0]-4.,p[1],p[2]),(x,p[1],p[2]),(x,190.,z),
                    (x,y,z),(q[0],y,z),(q[0],q[1]+5.,z)]
        return [(p[0]-4.,p[1],p[2]),(x,p[1],p[2]),(x,190.,z),
                (x,y,z),(q[0],y,q[2])]

    if c.harness=='Cartridge':
        n=idx%4;z=281.5-n*.15
        return [(p[0],p[1]-5.,z),(q[0],p[1]-5.,z),(q[0],q[1]+5.,z)]

    if c.harness=='J11':
        # The gas loom goes around the core, down the west outer dry lane,
        # then forward beside the compressor; it never crosses the can.
        x=-94.8+(idx-1.5)*1.8
        return [(p[0]-6.,p[1],p[2]),(55.,p[1],325.+lane),
                (x,clo[1]+18.,325.+lane),(x,clo[1]+18.,30.+lane),
                (x,q[1]+10.,30.+lane),(q[0],q[1]+10.,q[2])]

    if c.harness in ('J6','J7'):
        if c.start.startswith('reed-'):
            return [(p[0]+4.,p[1],p[2]-8.),(q[0]+4.,q[1],q[2]-10.)]
        if c.end.startswith('wago-'):
            return [(p[0]-5.,p[1],p[2]),(65.,p[1],327.+lane),
                    (-72.+lane,p[1],327.+lane),(-72.+lane,q[1],q[2])]
        bank='a' if 'reed-a-' in c.end else 'b' if 'reed-b-' in c.end else 'carb'
        if bank in ('a','b'):
            # Existing open reed channel and cap conduit share their axis.
            # Five conductors occupy a flat column, rather than one line.
            column_x=q[0]+(idx%5-2)*1.75
            y=q[1]
            top=chi[2]+12.
            return [(p[0]-5.,p[1],p[2]),(65.+lane,p[1],327.+lane),
                    (-65.+lane,y,327.+lane),(column_x,y,top),
                    (column_x,y,q[2]+b.outward[2]*10.),(q[0],y,q[2]+b.outward[2]*10.)]
        # Carbonator reeds are dressed in the foam space outside the cylinder.
        x=12.+lane; z=chi[2]+13.
        return [(p[0]-5.,p[1],p[2]),(64.+lane,p[1],327.+lane),
                (x,q[1]+8.,z),(x,q[1]+8.,q[2]+b.outward[2]*10.),(q[0],q[1]+5.,q[2]+b.outward[2]*10.)]

    if c.harness=='J4':
        if c.start.startswith('temp-carbonator.'):
            z=max(p[2],q[2])+18.+lane
            return [(p[0],p[1]-10.,p[2]-10.),(p[0],p[1]-10.,z),
                    (q[0],q[1]-10.,z),(q[0],q[1]-10.,q[2]-10.)]
        if c.end.startswith('temp-'):
            x=q[0]+(idx%3-1)*2.
            y=q[1]-6.
            return [(p[0]-5.,p[1],p[2]),(58.+lane,p[1],323.+lane),
                    (x,y,chi[2]+12.),(x,y,q[2]-5.),(q[0],y,q[2]-5.)]
        if c.end.startswith('wago-'):
            return [(p[0]-5.,p[1],p[2]),(56.,p[1],325.),(-72.,p[1],325.),(-72.,q[1],q[2])]
        return [(p[0]-5.,p[1],p[2]),(57.+lane,p[1],324.+lane),
                (-62.+lane,q[1]+4.,324.+lane),(-62.+lane,q[1]+4.,q[2])]

    if c.harness=='J3':
        return [(p[0]-5.,p[1],p[2]),(55.+lane,p[1],326.+lane),
                (-62.+lane,p[1],326.+lane),(-62.+lane,q[1]-9.,326.+lane),
                (q[0],q[1]-9.,q[2])]

    if c.harness=='J5':
        x=min(p[0],q[0])-7.-idx*1.85
        return [(x,p[1],p[2]),(x,q[1],q[2])]

    if c.harness in ('AC inlet','PSU primary','12V power','Diaphragm pump'):
        x=min(p[0],q[0])-7.-(idx%4)*3.2
        if c.harness=='Diaphragm pump' and c.end.startswith('diaphragm.'):
            return [(x,p[1],p[2]),(x,q[1]+7.,p[2]),(q[0],q[1]+7.,q[2])]
        return [(x,p[1],p[2]),(x,q[1],q[2])]

    if c.harness=='Compressor':
        # Shared cord corridor with individual conductor fanout at its ends.
        # The jacket is authored separately from the three insulated cores.
        x=58.+(idx%3-1)*2.8;y=clo[1]+13.
        z=225.+(idx%3-1)*2.8
        if c.start.startswith('fuse.'):
            return [(p[0]+7.,p[1],p[2]),(q[0]+7.,q[1],q[2])]
        return [(p[0]-6.,p[1],p[2]),(x,p[1],z),(x,y,z),
                (x,y,q[2]),(q[0]+7.,q[1],q[2])]

    if c.harness=='Earth bonds':
        if c.end=='carbonator.PE':
            return [(p[0]-7.,p[1],p[2]),(74.,p[1],315.),
                    (74.,q[1],chi[2]+10.),(74.,q[1],q[2])]
        return [(p[0]-7.,p[1],p[2]),(q[0]-7.,q[1],q[2])]
    raise ValueError('No installed route family for '+c.id)
