"""Lid-rooted saddle and complete dressed tie for the fixed needle barrel."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/needle'
sys.path.insert(0,str(STUDY));import audit

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def profile(y,z):
    r=7.35;reach=10.6;fore=y-11.15
    return (cq.Workplane('YZ').moveTo(y,z-reach).lineTo(fore,z-reach)
        .lineTo(fore,z+reach).lineTo(y,z+reach).lineTo(y,z+r)
        .threePointArc((y+r,z),(y,z-r)).close().wire())

def band(y,z,width,thickness,x):
    outer=profile(y,z).offset2D(thickness/2).extrude(width).val()
    inner=profile(y,z).offset2D(-thickness/2).extrude(width).val()
    return outer.cut(inner).translate((x-width/2,0,0)).clean()

def main():
    routing=json.loads((STUDY/'routing/candidate.json').read_text())
    x,y,z=routing['ports']['flow-regulator']['inlet']['pos']
    x+=7.;radius=7.1;reach=radius+3;length=9.5
    saddle=box(x-length/2,x+length/2,y-reach,y,z-reach,z+reach)
    saddle=saddle.fuse(box(x-length/2,x+length/2,y-reach,y-reach+3,253.39,z-reach+.01))
    bore=cq.Solid.makeCylinder(radius,length,cq.Vector(x-length/2,y,z),cq.Vector(1,0,0))
    saddle=saddle.cut(bore)
    tunnel=band(y,z,3.5,1.7,x)
    saddle=saddle.cut(tunnel).clean()
    tie=band(y,z,2.5,1,x)
    head=box(x-1.5,x+6.5,y-16.3,y-11.3,z+10.65,z+18.65)
    tie=tie.fuse(head).clean()
    shapes={'needle-lid-seat':saddle,'needle-retention-tie':tie}
    models,records,changed,mates,inputs=audit.collect()
    for folder,file in [('wiring','control-reserves.json'),('wiring','control-fanouts-check.json')]:
        path=STUDY/folder/file
        if path.exists():
            m=json.loads(path.read_text())
            for name,r in m.get('parts',{}).items():models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
    gas=STUDY/'routing/co2-candidate.json'
    if gas.exists():
        for name,r in json.loads(gas.read_text()).get('parts',{}).items():models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
    checks=[];OUT.mkdir(parents=True,exist_ok=True);parts={}
    for name,q in shapes.items():
        hits=[]
        for other,t in models.items():
            if other in shapes or other in ['enclosure-front-top','enclosure-back-top','rear-roof-hatch','cold-core/foam-cap-lid-top']:
                continue
            if not audit.broad(audit.bbox(q),audit.bbox(t),0):continue
            v=audit.common(q,t)
            if v>.01:hits.append({'part':other,'common_mm3':v})
        valid=q.isValid() and len(q.Solids())==1
        f=OUT/(name+'.brep');q.exportBrep(str(f))
        parts[name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
            'bounds':audit.bbox(q),'role':'structure',
            'detail':('Lid-rooted needle barrel saddle: measuredR6.85 body/R7.1 slip,3mm radial bearing,3mm axial end webs,3.5mm dressed tie tunnel.' if name.endswith('seat') else
                'Complete nominal2.5×1mm nylon tie with conservative8×8×5mm locking head; barrel contact and measured round seat are explicit. Purchased head/dressing remain unqualified.')}
        checks.append({'part':name,'single_valid_solid':valid,'interferences':hits,'pass':valid and not hits})
    volume=audit.common(saddle,tie)
    checks.append({'test':'dressed tie clears actual seat tunnel','common_mm3':volume,'pass':volume<.01})
    owner=models['flow-regulator']
    checks.append({'test':'needle complete purchased body clears saddle','common_mm3':audit.common(saddle,owner),
                   'bearing_air_mm':saddle.distance(owner),'pass':audit.common(saddle,owner)<.01})
    result={'parts':parts,'checks':checks,'pass':all(c['pass'] for c in checks),
        'lid_fuse_part_names':['needle-lid-seat'],'shell_fuse_part_names':[],
        'intended_contacts':[['needle-retention-tie','flow-regulator']],
        'retained_component':'flow-regulator','body_axis_mm':[x,y,z],
        'minimum_radial_stock_mm':3,'minimum_axial_end_web_mm':3,
        'manifests_sha256':inputs,'routing_manifest_sha256':hashlib.sha256((STUDY/'routing/candidate.json').read_bytes()).hexdigest(),
        'scope':'Complete nominal seat/tie occupied geometry. Load, creep, vibration and finished tie retention require physical qualification.'}
    (HERE/'needle-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['pass'],'checks':checks},indent=2),flush=True)
    if not result['pass']:raise SystemExit(1)

if __name__=='__main__':main()
