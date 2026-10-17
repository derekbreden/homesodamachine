"""Read passage-cylinder diameters from exported B-reps; manual only."""
from pathlib import Path
import hashlib
import json
import math
import sys
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'hardware/printed-parts/cold-core'))
import _cold_core_interface as dimensions
FILES = (
 'hardware/printed-parts/cold-core/foam-cap/foam-cap-top.step',
 'hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step',
 'hardware/printed-parts/cold-core/reservoir/reservoir-cap-left.step',
 'hardware/printed-parts/cold-core/reservoir/reservoir-cap-right.step',
 'hardware/printed-parts/cold-core/foam-shell/foam-shell.step',
)

def main():
    result={}
    for rel in FILES:
        path=ROOT/rel
        shape=cq.importers.importStep(str(path)).val()
        axes=set()
        for face in shape.Faces():
            if face.geomType()!='CYLINDER':continue
            cylinder=BRepAdaptor_Surface(face.wrapped).Cylinder()
            if abs(2*cylinder.Radius()-7.5)>1e-6:continue
            p=cylinder.Location();v=cylinder.Axis().Direction()
            direction=[v.X(),v.Y(),v.Z()]
            if next(x for x in direction if abs(x)>1e-8)<0:
                direction=[-x for x in direction]
            point=[p.X(),p.Y(),p.Z()]
            along=sum(a*b for a,b in zip(point,direction))
            foot=[a-along*b for a,b in zip(point,direction)]
            axes.add(tuple(round(a,5) for a in foot+direction))
        result[rel]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'valid':shape.isValid(),'solid_count':len(shape.Solids()),
                     'diameter_mm':7.5,'distinct_cylinder_axes':len(axes),
                     'axes_nearest_origin_xyz_and_direction':sorted(axes)}
        print(path.name,len(axes),'distinct 7.5 mm cylinder axes',flush=True)
    cap=cq.importers.importStep(str(ROOT/FILES[0])).val()
    links=[]
    for first,second in dimensions.cap_conduit_links:
        a,b=dimensions.cap_conduits[first],dimensions.cap_conduits[second]
        angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
        slab=(cq.Workplane('XY').box(.01,5,1).rotate((0,0,0),(0,0,1),angle)
              .translate(((a[0]+b[0])/2,(a[1]+b[1])/2,6)).val())
        width=cap.intersect(slab).Volume()/.01
        links.append({'between':[first,second],'midpoint_web_width_mm':width})
        print(first,second,'web width',width,flush=True)
    result['connecting_webs']=links
    (HERE/'core-passage-measurements.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
