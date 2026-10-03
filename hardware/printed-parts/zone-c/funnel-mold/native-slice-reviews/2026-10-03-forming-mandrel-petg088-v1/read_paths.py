"""Read nominal deposited paths from the isolated native mandrel G-code."""
from collections import defaultdict
from pathlib import Path
import json, math, sys
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
sys.path.insert(0,str(ROOT/'hardware/scripts'))
import enclosure_support_audit as support

def read(path):
    xy=np.array([0.,0.]);e=0.;relative_e=True;absolute_xy=True
    feature='';width=.42;layer=0;zheight=None;height=.2
    segments=[];layers={};counts=defaultdict(int)
    lo=np.array([math.inf,math.inf]);hi=-lo
    for raw in Path(path).read_text().splitlines():
        line=raw.strip()
        if line.startswith('; layer num/total_layer_count:'):
            layer=int(line.split(':',1)[1].split('/')[0])
        elif line.startswith('; Z_HEIGHT:'):zheight=float(line.split(':',1)[1])
        elif line.startswith('; LAYER_HEIGHT:'):height=float(line.split(':',1)[1])
        elif line.startswith('; HEIGHT:'):height=float(line.split(':',1)[1])
        elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        elif line.startswith('; LINE_WIDTH:'):width=float(line.split(':',1)[1])
        code=line.split(';',1)[0].strip()
        if not code:continue
        command=code.split(None,1)[0]
        words={k:float(v)for k,v in support._WORD.findall(code)}
        if command=='G90':absolute_xy=True;continue
        if command=='G91':absolute_xy=False;continue
        if command=='M82':relative_e=False;continue
        if command=='M83':relative_e=True;continue
        if command=='G92':
            xy=np.array([words.get('X',xy[0]),words.get('Y',xy[1])]);e=words.get('E',e);continue
        if command not in ('G0','G1','G2','G3'):continue
        new=np.array([words.get('X',xy[0]),words.get('Y',xy[1])])if absolute_xy else xy+np.array([words.get('X',0.),words.get('Y',0.)])
        de=words.get('E',0.)if relative_e else words.get('E',e)-e
        if zheight is not None and de>1e-9 and np.linalg.norm(new-xy)>1e-9 and feature not in ('Custom','Flush','Wipe tower',''):
            points=([tuple(new)]if command in ('G0','G1')else support._arc_points(tuple(xy),tuple(new),words,command=='G2'))
            start=xy
            for point in points:
                end=np.array(point)
                lo=np.minimum(lo,np.minimum(start,end)-width/2);hi=np.maximum(hi,np.maximum(start,end)+width/2)
                item={'layer':layer,'top_z_mm':zheight,'height_mm':height,
                      'centre_z_mm':zheight-height/2,'feature':feature,'width_mm':width,
                      'a':start.tolist(),'b':end.tolist()}
                segments.append(item);counts[feature]+=1
                layers[layer]={'top_z_mm':zheight,'height_mm':height,'centre_z_mm':zheight-height/2}
                start=end
        xy=new
        if 'E'in words:e=e+words['E']if relative_e else words['E']
    return {'segments':segments,'layers':layers,'feature_segment_counts':dict(counts),
            'all_deposited_bounds_xy_mm':[lo.tolist(),hi.tolist()]}

def outer_radii(data,axis):
    result={}
    for number,layer in data['layers'].items():
        outer=[s for s in data['segments']if s['layer']==number and s['feature']in ('Outer wall','Overhang wall')]
        if not outer:continue
        radii=[]
        for s in outer:
            a=np.array(s['a'])-axis;b=np.array(s['b'])-axis
            v=b-a;t=np.clip(-np.dot(a,v)/np.dot(v,v),0,1)
            radii.extend([float(np.linalg.norm(a+t*v)+s['width_mm']/2),
                          float(np.linalg.norm(a)+s['width_mm']/2),float(np.linalg.norm(b)+s['width_mm']/2)])
        # Overhang labels may include an inner perimeter. Read the outermost
        # material along each ray so that those paths cannot become a false
        # minimum forming radius.
        envelope=unary_union([LineString([s['a'],s['b']]).buffer(s['width_mm']/2,quad_segs=8)for s in outer])
        def endpoints(g):
            if hasattr(g,'geoms'):
                return [p for part in g.geoms for p in endpoints(part)]
            return list(g.coords)
        outer_samples=[]
        for angle in np.linspace(0,2*math.pi,128,endpoint=False):
            unit=np.array([math.cos(angle),math.sin(angle)])
            ray=LineString([axis,axis+unit*(max(radii)+1)])
            cross=envelope.intersection(ray)
            assert not cross.is_empty,(number,angle)
            outer_samples.append(max(float(np.linalg.norm(np.array(p)-axis))for p in endpoints(cross)))
        model_layer={k:outer[0][k]for k in ('top_z_mm','height_mm','centre_z_mm')}
        result[number]={**model_layer,'nominal_outer_surface_radius_min_mm':min(outer_samples),
                        'nominal_outer_surface_radius_max_mm':max(radii),'outer_wall_segments':len(outer)}
    return result

if __name__=='__main__':
    data=read(Path(sys.argv[1]));out=outer_radii(data,np.array([float(v)for v in sys.argv[2:4]]))
    print(json.dumps({'bounds':data['all_deposited_bounds_xy_mm'],
                     'counts':data['feature_segment_counts'],'layers':out},indent=2))
