"""Publish exact nominal source groove mouths and analytic approach waypoints."""
from pathlib import Path
import hashlib,json
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
ROOF=ROOT/'.cache/pump-first-layout/mounts/roof'
MODES={'wago-h':'fore','wago-n':'fore','wago-g':'fore','wago-v12':'aft','wago-gnd':'fore','wago-reeds-b':'up','wago-reeds-a':'fore','wago-sensors':'fore'}
AXES={'up':[0,0,1],'fore':[0,-1,0],'aft':[0,1,0],'east':[1,0,0],'west':[-1,0,0]}

def main():
    junctions={};hashes={}
    for name,mode in MODES.items():
        path=ROOF/f'expected-{name}.brep';body=cq.Shape.importBrep(str(path));b=body.BoundingBox();hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        poles=5 if name.startswith(('wago-reeds','wago-sensors')) else 3
        xs=[b.xmin+b.xlen/poles*(i+.5) for i in range(poles)]
        ys=[b.ymin+b.ylen*.25,b.ymin+b.ylen*.75] if mode=='up' else [(b.ymin+b.ymax)/2]
        rows=[]
        for row,y in enumerate(ys):
            for i,x in enumerate(xs):
                p=[x,y,b.zmax] if mode=='up' else [x,b.ymin if mode=='fore' else b.ymax,(b.zmin+b.zmax)/2]
                if mode=='up':q=[x,y,p[2]+4];e=[x,y-3.4,p[2]+7.4];f=[x,y-7.4,p[2]+7.4]
                else:
                    sign=-1 if mode=='fore' else 1;q=[x,p[1]+sign*2,p[2]];e=[x,q[1]+sign*3.4,p[2]-3.4];f=[x,e[1],e[2]-.8]
                rows.append({'port_index':row*poles+i+1,'row':row+1,'pole':i+1,'mouth':p,'outward_axis':AXES[mode],
                    'normal_end':q,'quarter_end':e,'free_end':f,'external_normal_mm':4 if mode=='up' else 2,
                    'quarter_radius_mm':3.4,'wire_diameter_mm':1.7 if poles==5 else 3.2})
        junctions[name]=rows
    result={'junctions':junctions,'source_native_sha256':hashes,
      'scope':'Exact rotated retained body; source groove pitch gives nominal clamp-face reservations. Normal leads, R3.4 bends and wire diameters are authored occupied envelopes, not qualified terminations.'}
    (HERE/'junction-port-approaches.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({name:{'mode':MODES[name],'mouths':[p['mouth'] for p in ports]} for name,ports in junctions.items()},indent=2))
if __name__=='__main__':main()
