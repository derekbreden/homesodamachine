"""Clear only the aft upper bay and install the enlarged funnel's native mates.

The installed B-rep remains the source for the accepted front interfaces, lower
core boundary, seams and rear connectors. New bay mounts are integrated by the
study assembly after this stock is prepared. No production source is edited.
"""
from pathlib import Path
import hashlib, json, sys

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p/'hardware/scripts/_cadq_export.py').exists())
HERE = Path(__file__).parent
sys.path[:0] = [str(HERE.parent), str(ROOT/'hardware/scripts'),
               str(ROOT/'hardware/printed-parts/zone-c/funnel')]
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
import baseline, funnel as f, funnel_frame as ff
import enclosure as e, _box_spec
from study_configuration import configuration,save_record
extra,preview,candidate=configuration()

OUT = ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'/'shells'
OUT.mkdir(parents=True, exist_ok=True)
box, _ = _box_spec.read(e.Box, e.Bound, (e.Pack, e.PortField, e.Nameplate),
                       path=ROOT/'hardware/manifold-layout/enclosure-box.json')
inner, outer = box.inner, box.outer
installed = baseline.read(names=['enclosure-front-top', 'enclosure-back-top'])
mating = json.loads((HERE/f'mating-aft-{extra:g}.json').read_text())['interfaces']
tools = {n:cq.Shape.importBrep(str(ROOT/v['brep'])) for n,v in mating.items()}
frame = cq.Shape.importBrep(str(ROOT/candidate['parts']['funnel-frame']['brep']))
silicone = cq.Shape.importBrep(str(ROOT/candidate['parts']['funnel']['brep']))
lid = cq.Shape.importBrep(str(ROOT/candidate['parts']['funnel-cover']['brep']))
cy = candidate['collar_centre_world_mm'][1]
f.collar_d += extra
f.neck_dy = -extra/2
ff.center_y = cy
ff.depth = f.collar_d + 24.6
ff.corbel_foot_half_depth += extra/2

def bounds(shape):
    b=Bnd_Box(); BRepBndLib.AddOptimal_s(shape.wrapped,b,False,False)
    return list(b.Get())

def volume(shape):
    return abs(shape.Volume(tol=1e-9))

def common(a,b):
    return volume(a.intersect(b,tol=.0001))

def export(name,shape,role=None,detail=None):
    brep=OUT/f'{name}.brep'; shape.exportBrep(str(brep))
    record={'brep':str(brep.relative_to(ROOT)), 'sha256':hashlib.sha256(brep.read_bytes()).hexdigest(),
            'bounds_world_mm':bounds(shape), 'volume_mm3':volume(shape),
            'valid':shape.isValid(),'solids':len(shape.Solids())}
    if role:
        step=OUT/f'{name}.step'; cq.exporters.export(shape,str(step))
        mesh=OUT/f'{name}.json'; vertices,triangles=shape.tessellate(.12,.08)
        mesh.write_text(json.dumps({'vertices':[[v.x,v.y,v.z] for v in vertices],
                                   'triangles':[list(t) for t in triangles]},separators=(',',':'))+'\n')
        record.update(step=str(step.relative_to(ROOT)), mesh=str(mesh.relative_to(ROOT)),
                      role=role, detail=detail)
    return record

# All rear connector stock is protected before the bay is cleared. These are
# exact native interface solids, not broad boxes retaining obsolete furniture.
c14=e._c14_tunnel_geometry(inner,outer,box.pack.c14,box.pack.back_ports,160,355,e.BACK_TOP_UP)
keystone=e._keystone_receptacle_geometry(inner,outer,box.pack.keystone,160,355,e.BACK_TOP_UP)
protect={'retained-c14-tunnel-stock':c14[0],
         'retained-keystone-stock':keystone[0].fuse(keystone[2]),
         'retained-nameplate-stock':e._nameplate_fit.receiver().translate(
             (box.pack.nameplate.x,outer[3]-e._nameplate_fit.THICK,box.pack.nameplate.z))}
bay=e._ybox(-98.5,98.5,218.8,e.back_top_wall_face(),253.40001,352)
cut=bay
for mask in protect.values():
    cut=cut.cut(mask,tol=.0001)
interface_records={n:export(n,s) for n,s in protect.items()}
interface_records['bay-clear-cutter']=export('bay-clear-cutter',cut)
interface_records['nominal-ceiling-stock']=export('nominal-ceiling-stock',e.back_top_ceiling_stock())
interface_records['original-c14-bore-and-pocket']=export('original-c14-bore-and-pocket',c14[1])
for i,shape in enumerate(c14[2]):
    interface_records[f'original-c14-insert-{i}']=export(f'original-c14-insert-{i}',shape)
interface_records['original-keystone-cutter']=export('original-keystone-cutter',keystone[1])
interface_records['original-keystone-feature']=export('original-keystone-feature',keystone[0])
interface_records['original-keystone-catches']=export('original-keystone-catches',keystone[2])
for who,x0,x1,y0,y1,top in box.pack.ceiling_reliefs:
    if who=='c14-inlet':
        cx,cz,_,_,_=e._c14_aperture(box.pack.c14,box.pack.back_ports)
        interface_records['original-c14-ceiling-pocket']=export('original-c14-ceiling-pocket',
            e.c14_pocket_prism(e.c14_pocket_slip,y0,y1).translate((cx,0,cz)).val())

parts={}
checks=[]
for side in ('front','back'):
    name=f'enclosure-{side}-top'
    piece=installed[name]
    print('Clearing and mating',name,flush=True)
    if side=='back':
        piece=piece.cut(cut,tol=.0001)
        # Continuous supporting roof stock follows the production construction.
        # Below the 3 mm roof only the enlarged frame surrounds its own opening;
        # the remaining aft bay roof is the retained 3 mm shell.
        stock=e._ybox(inner[0],inner[1],200,
                     cy+f.collar_d/2+f.brim_overhang+3,346,355)
        piece=piece.fuse(stock.intersect(e._rounded_outer(outer)),tol=.0001)
    piece=piece.fuse(tools[f'{side}-receivers'],tol=.0001)
    for cutter in ('frame-shell-clearance','brim-pocket','collar-throat',f'{side}-rail-channels'):
        piece=piece.cut(tools[cutter],tol=.0001)
    if side=='front':
        piece=piece.cut(tools['front-roof-clearance'],tol=.0001)
        piece=piece.cut(tools['front-seam-relief'],tol=.0001)
    cleaned=piece.clean()
    if cleaned.isValid(): piece=cleaned
    assert piece.isValid() and len(piece.Solids())==1,(name,piece.isValid(),len(piece.Solids()))
    parts[name]=piece
    print('Native shell ready',name,'occupied mm3',volume(piece),flush=True)
    for item,shape in (('frame',frame),('silicone',silicone),('lid',lid)):
        overlap=common(piece,shape)
        checks.append({'test':'installed native shell mate','shell':name,'part':item,
                       'overlap_mm3':overlap,'pass_result':overlap<.01})
        print(name,item,overlap,flush=True)
    # No changed stock may enter the accepted lower storey. Geometry above the
    # bay-front boundary changes only where the enlarged mating cutter reaches.
    below=e._ybox(-110,110,0,475,0,253.4)
    original_below=installed[name].intersect(below,tol=.0001)
    new_below=piece.intersect(below,tol=.0001)
    added=volume(new_below.cut(original_below,tol=.0001))
    removed=volume(original_below.cut(new_below,tol=.0001))
    checks.append({'test':'retained lower core and seam storey','shell':name,
                   'added_mm3':added,'removed_mm3':removed,'pass_result':added+removed<.01})

# Upper shells ride their retained Y slides; the back-top approaches from aft.
# This local shell/frame fit check excludes the integrated bay hosts.
for side,sign in (('front',-1),('back',1)):
    for travel in (0,.25,1,2,5,10,20,40,70):
        overlap=common(parts[f'enclosure-{side}-top'].translate((0,sign*travel,0)),frame)
        checks.append({'test':'local upper-shell/frame closing fit; bay hardware excluded','shell':side,
                       'approach_travel_mm':travel,'overlap_mm3':overlap,'pass_result':overlap<.01})
        print('shell closing',side,travel,overlap,flush=True)

# The silicone exits vertically with the retained tube left in its cradle.
for item,shape,poses in (('silicone',silicone,(0,.25,.5,1,2,4,6,8,16,32,50,75)),
                         ('lid',lid,(0,.5,2,4,6,8,12))):
    for lift in poses:
        moving=shape.translate((0,0,lift))
        for side in ('front','back'):
            overlap=common(parts[f'enclosure-{side}-top'],moving)
            checks.append({'test':'customer vertical cleaning lift against upper shells',
                           'part':item,'shell':side,'lift_mm':lift,
                           'overlap_mm3':overlap,'pass_result':overlap<.01})

# Parent integration can move only the two upper fluid stations while retaining
# the accepted C14, keystone and nameplate. These are the exact production tools.
for i,(port,cutter) in enumerate(zip(box.pack.back_ports,e._port_cuts(
        box.pack.back_ports,e.back_top_wall_face()-5,outer[3]+5,e.BACK_TOP_UP))):
    record=export(f'original-rear-port-{i}',cutter)
    record['declaration']=list(port)
    interface_records[f'original-rear-port-{i}']=record
for i,(x,z,w,rise) in enumerate(box.pack.port_field.pockets):
    pocket=e._supported_cut(e._port_chip(x,z,w,rise,outer[3]-box.pack.port_field.proud,outer[3]+1),e.BACK_TOP_UP)
    record=export(f'original-rear-chip-pocket-{i}',pocket)
    record['declaration']=[x,z,w,rise]
    interface_records[f'original-rear-chip-pocket-{i}']=record
saved_reliefs=e.back_top_wall_reliefs
e.back_top_wall_reliefs=tuple(x for x in saved_reliefs if x[0]=='co2-inlet')
interface_records['original-co2-land-relief']=export('original-co2-land-relief',
    e._back_top_wall_relief_cut(box.pack.port_field,e.BACK_TOP_UP))
e.back_top_wall_reliefs=tuple(x for x in saved_reliefs if x[0]=='c14-inlet')
interface_records['original-c14-land-relief']=export('original-c14-land-relief',
    e._back_top_wall_relief_cut(box.pack.port_field,e.BACK_TOP_UP))
e.back_top_wall_reliefs=saved_reliefs

records={n:export(n,s,'structure',
    'Native upper shell with aft bay hosts removed above the cold-core lid, enlarged removable funnel/frame mates, retained 9 mm flanks and original rear connector/nameplate/C14 interfaces.')
    for n,s in parts.items()}
result={'aft_extension_mm':extra,'parts':records,'replacement_names':list(records),'interfaces':interface_records,
        'clear_bay':{'x_mm':[-98.5,98.5],'y_mm':[218.8,e.back_top_wall_face()],
                     'z_mm':[253.40001,352], 'rear_wall_thickness_mm':e.back_top_wall_t,
                     'retained_interface_names':list(protect)},
        'checks':checks,'pass_result':all(c['pass_result'] for c in checks),
        'baseline_source_sha256':baseline.prepare()['sha256'],
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (Path(__file__),Path(e.__file__),ROOT/'hardware/manifold-layout/enclosure-box.json')},
        'scope':'Native clear-bay shell stock and enlarged funnel mates. Retained lower, front cartridge, rear C14, keystone and nameplate interfaces remain on their installed datums. New component hosts and rear CO2/CARB station exchange are integrated by the complete study. Geometry is not physical qualification or a print support acceptance.'}
save_record('shells',extra,preview,result)
assert result['pass_result'],[x for x in checks if not x['pass_result']]
