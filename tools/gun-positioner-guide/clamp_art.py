"""Render the two clamp hardware views and a readable metal preparation view.

The hardware comes from the frozen proof fixture, on its actual insertion axes.
Only the stated separations and display scales change for illustration.
"""
from __future__ import annotations

import os
import math
from pathlib import Path

import cadquery as cq

import art


def scenes():
    os.environ.setdefault('HSM_NO_BUILD_LOCK','1')
    gp=art.import_file(art.MECHANICS,'positioner_guide_clamp_geometry')
    fixtures=gp.fixture_assemblies()
    source,receipt=fixtures['hub-clamp-proof']
    flat={n:node for n,node in source.traverse() if node.obj is not None}
    context=cq.Color(.36,.40,.49)
    shaft=cq.Color(.64,.68,.75)
    coral=cq.Color(.84,.25,.31)
    hub_inverse=flat['proof-specimen-hub'].loc.inverse
    result,details={},{}
    for name,exploded in [('hub-clamps-exploded',True),('hub-clamps-fitted',False)]:
        a=cq.Assembly(name='guide-'+name)
        selected=[];offsets={}
        for n,node in flat.items():
            hardware=n.startswith(('proof-clamp-M4-0-','proof-clamp-washer-0-','proof-clamp-nut-0-'))
            if n not in ('proof-specimen-hub','proof-completed-shaft') and not hardware:continue
            shape=node.obj
            if n.startswith('proof-clamp-M4-'):
                # Retain the source's M4 × 50 shaft and insertion origin.
                # Draw the purchased socket-head style in place of its generic
                # source hex-head proxy; this is a visual fitting envelope.
                shank=cq.Workplane('XY').circle(2).extrude(50)
                head=cq.Workplane('XY').circle(3.5).extrude(4).translate((0,0,-4))
                recess=cq.Workplane('XY').polygon(6,3/math.cos(math.pi/6)).extrude(2).translate((0,0,-4))
                shape=shank.union(head.cut(recess))
            if n=='proof-completed-shaft':
                shape=shape.intersect(cq.Workplane('XY').box(30,30,32,centered=(True,True,False)))
            loc=hub_inverse*node.loc
            offset=0
            if exploded and hardware:
                if n.startswith('proof-clamp-M4-'):offset=-55
                elif n.startswith('proof-clamp-nut-'):offset=28
                elif n.endswith('--20.05'):offset=-12
                else:offset=12
                loc=cq.Location(cq.Vector(offset,0,0))*loc
            a.add(shape,name=n,loc=loc,color=coral if hardware else shaft if n=='proof-completed-shaft' else context)
            selected.append(n);offsets[n]=[offset,0,0]
        if len(selected)!=10:raise RuntimeError(f'{name}: missing clamp hardware: {selected}')
        result[name]=(a,dict(cam=(-1,1,.7),size='2400x1700'))
        details[name]=dict(source_fixture='hub-clamp-proof',parts=selected,
            fixture_receipt=[r for r in receipt if r['name'] in selected],
            exploded_offsets_hub_local_mm=offsets,
            scope='Actual specimen hub and two complete M4x50/washer/locking-nut sets from the frozen fixture. View reoriented to hub fabrication coordinates; plain shaft cropped to 32 mm for visibility. The generic source bolt-head proxy is drawn as a cylindrical socket head with an H3 recess. Fastener solids identify stack and insertion axes; received hardware sets exact fitting dimensions.')
    a=cq.Assembly(name='guide-metal-preparation')
    names=['x-bed','drive-bulkhead','shaft-hub','metal-angle-25'];scales={}
    for i,n in enumerate(names):
        shape=gp.PARTS[n]['model'];bb=shape.val().BoundingBox()
        scale=min(140/max(bb.xlen,.01),100/max(bb.ylen,.01),50/max(bb.zlen,.01))
        shape=cq.Workplane(obj=shape.val().scale(scale));bb=shape.val().BoundingBox()
        shape=shape.translate((i%2*175+75-(bb.xmin+bb.xmax)/2,
                               i//2*145+60-(bb.ymin+bb.ymax)/2,-bb.zmin))
        a.add(shape,name=n,color=context);scales[n]=scale
    result['metal-preparation']=(a,dict(cam=(.35,-.55,1),size='2400x1700'))
    details['metal-preparation']=dict(fabrication_parts=names,display_scales=scales,
        scope='Four actual source fabrication solids at independent identification scales. The actual-size templates and STEP files govern dimensions.')
    return result,details


if __name__=='__main__':
    inputs=art.hashes([art.MECHANICS,Path(__file__).resolve(),Path(art.__file__).resolve()])
    rendered,metadata=scenes()
    art.render_scenes(rendered,metadata,inputs)
