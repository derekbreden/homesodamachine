"""Publish the flush shallow tray and its exact native rim-fill cavity volume."""
from pathlib import Path
import argparse, hashlib, json, sys
import cadquery as cq

ROOT=Path(__file__).resolve().parents[3]
S=ROOT/'future/pump-first-layout-study';H=S/'routing'
C=ROOT/'.cache/pump-first-layout/routing'
sys.path[:0]=[str(S),str(ROOT/'hardware/printed-parts/enclosure/asse-drip-pan')]
import baseline, asse_drip_pan as pan

def native_capacity_ml(shape, origin, dimensions):
    """Exact water cavity below the rim, including the R2 floor coves."""
    x,y,z=origin;dx,dy,dz=dimensions
    cavity_prism=cq.Solid.makeBox(dx-2*pan.WALL,dy-2*pan.WALL,dz-pan.FLOOR,
        cq.Vector(x+pan.PULL_FACE_Y_OVERHANG+pan.WALL,
                  y+pan.PULL_FACE_Y_OVERHANG+pan.WALL,z+pan.FLOOR))
    cavity=cavity_prism.cut(shape,tol=.0001)
    if not cavity.isValid() or len(cavity.Solids())!=1:
        raise ValueError('Tray rim-fill cavity must be one valid native volume')
    return cavity.Volume(tol=1e-9)/1000.

def metadata(shape):
    original=baseline.read(['asse-drip-pan'])['asse-drip-pan']
    b=original.BoundingBox()
    original_capacity=native_capacity_ml(original,(b.xmin,b.ymin,b.zmin),(51.,76.,15.))
    return {'translation':[-107.5,279.6,254.4],'basin_mm':[102.5,51,12],
        'capacity_ml':native_capacity_ml(shape,(-107.5,279.6,254.4),(102.5,51.,12.)),
        'capacity_basis':'Exact native rim-fill cavity volume including R2 floor coves; no physical drain-rate or sensing-performance claim.',
        'rectangular_capacity_ml':40.365,'original_capacity_ml':original_capacity,
        'original_rectangular_capacity_ml':39.192,'flat_floor_mm':[93.5,42],
        'atmospheric_fall_mm':13.05,'native_rigid_status':'Declared in the exact SHA-bound strict native route proof.',
        'native_proof':'future/pump-first-layout-study/routing/strict-route-audit.json',
        'slot_owner':'enclosure-back-top'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--metadata-only',action='store_true')
    args=parser.parse_args();m=json.loads((H/'candidate.json').read_bytes())
    if args.metadata_only:
        q=cq.Shape.importBrep(str(ROOT/m['parts']['asse-drip-pan']['brep']))
    else:
        pan.PAN_X,pan.PAN_Y,pan.PAN_Z=102.5,51.,12.
        q=pan.build().val().translate((-107.5,279.6,254.4))
        p=C/'asse-drip-pan.brep';q.exportBrep(str(p));b=q.BoundingBox()
        m['parts']['asse-drip-pan']={'brep':str(p.relative_to(ROOT)),'role':'water',
            'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        plate=baseline.read(['moisture-plate'])['moisture-plate'].rotate((0,0,0),(0,0,1),-90)
        b=plate.BoundingBox();plate=plate.translate((-52.25-(b.xmin+b.xmax)/2,
            309.1-(b.ymin+b.ymax)/2,257.4-b.zmin))
        p=C/'moisture-plate.brep';plate.exportBrep(str(p));b=plate.BoundingBox()
        m['parts']['moisture-plate']={'brep':str(p.relative_to(ROOT)),'role':'water',
            'detail':'Existing54x40probe lies on the3mm floor;1mm fore/aft slip on42mm flat floor.',
            'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    m['pan']=metadata(q)
    m['parts']['asse-drip-pan']['detail']=(
        'Flush102.5x51x12 basin;2.5mm walls,3mm floor,R2 coves, full54x40probe+1mm slip;'
        f"{m['pan']['capacity_ml']:.3f}mL exact native rim-fill cavity;13.05mm atmospheric fall.")
    (H/'candidate.json').write_text(json.dumps(m,indent=2)+'\n')
    print('Native tray capacities',m['pan']['capacity_ml'],m['pan']['original_capacity_ml'],flush=True)

if __name__=='__main__':main()
