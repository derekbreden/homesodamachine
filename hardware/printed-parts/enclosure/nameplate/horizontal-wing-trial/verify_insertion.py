"""Bound the wing-entry envelope in a circular-bend cross-section, not its force."""
import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import Polygon, box
import wing_interface as fit

HERE=Path(__file__).resolve().parent


def main():
    h=fit.WIDTH/2; p=fit.PROJECTION; t=fit.THICK; f=fit.FIELD_THICK
    w=fit.WING_THICK; n=f/2
    outline=[(-h-p,0),(h+p,0),(h+p,w),(h,w),(h,t),
             (-h,t),(-h,w),(-h-p,w)]
    points=[]
    for a,b in zip(outline,outline[1:]+outline[:1]):
        count=max(2,math.ceil(math.dist(a,b)/.1))
        points.extend((a[0]+(b[0]-a[0])*k/count,a[1]+(b[1]-a[1])*k/count)
                      for k in range(count))
    receiver=box(-h-p-3,-fit.FLOOR_STOCK,h+p+3,t)
    receiver=receiver.difference(box(-h-fit.FACE_X_AIR,0,h+fit.FACE_X_AIR,t+30))
    for side in (-1,1):
        x0,x1=sorted((side*(h-.1),side*(h+p+fit.TIP_AIR)))
        receiver=receiver.difference(box(x0,0,x1,w+fit.THICKNESS_AIR))
        mouth=h+fit.FACE_SLIP;roof=w+fit.THICKNESS_AIR
        receiver=receiver.difference(Polygon([
            (side*mouth,roof),(side*(mouth+fit.ENTRY_BEVEL_WIDTH),roof),
            (side*mouth,roof+fit.ENTRY_BEVEL_DEPTH)]))
    checks=[]
    for i in range(101):
        angle=.55*i/100
        def bend(x,y):
            if angle==0:return x,y
            radius=h/angle; phi=min(abs(x),h)/radius; offset=y-n
            xx=(radius+offset)*math.sin(phi)
            yy=(radius+offset)*math.cos(phi)-radius*math.cos(angle)+n
            if abs(x)>h:
                xx+=(abs(x)-h)*math.cos(angle)
                yy-=(abs(x)-h)*math.sin(angle)
            return math.copysign(xx,x),yy
        curved=[bend(*point) for point in points]
        lift=.01-min(y for _,y in curved)
        shape=Polygon([(x,y+lift) for x,y in curved])
        overlap=shape.intersection(receiver).area
        assert shape.is_valid and overlap<1e-6,(angle,overlap)
        checks.append({'end_angle_rad':angle,'tip_floor_clearance_mm':.01,
                       'lift_mm':lift,'intersection_area_mm2':overlap,
                       'x_span_mm':shape.bounds[2]-shape.bounds[0]})
    assert checks[-1]['x_span_mm']<fit.WIDTH+2*fit.FACE_X_AIR
    # Once the bent outline fits the mouth, it can translate directly outward.
    record={'pass':True,'samples':len(checks),'checks':checks,
            'motion':'Bend the middle outward while the wing tips stay above the slot floors; release into the seated shape. Reverse for removal through the rear access opening.',
            'scope':'Central X/Y cross-section, ideal circular bending of the plate with straight wings following the end tangent. Rounded wing ends are conservatively rectangular. Full seated CAD clash is checked separately. This is not a force, fatigue, corner-motion or printed-fit qualification.',
            'maximum_section_overlap_mm2':max(c['intersection_area_mm2'] for c in checks),
            'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (Path(__file__),HERE/'wing_interface.py')}}
    (HERE/'insertion-envelope.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'pass':True,'samples':len(checks),'max_overlap_mm2':record['maximum_section_overlap_mm2']}))


if __name__=='__main__':main()
