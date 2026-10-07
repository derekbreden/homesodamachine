"""Integrate the enlarged funnel, translated rear ports and named new hosts."""
from pathlib import Path
import json,sys,hashlib
import cadquery as cq
from io import BytesIO

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/structure'
sys.path.insert(0,str(STUDY))
from evidence_binding import content_sha256
from audit import common as native_common
from structure.assemble_prints import joined
from structure.pan_slot import make_slot
from structure.water5_key_pocket import make_pocket
from structure.received_native import material_common
from structure.roof_finish import make_roof_finish

def require_valid(shape,label):
    if not shape.isValid():raise ValueError('Invalid native shell after '+label)
    return shape

def cutter_common(shape,cutter,label,repairs):
    """Completed independent material measurements for a stock/tool pair."""
    attempts=[]
    for tolerance in [0,.0001,.00001]:
        try:
            volume=0.
            for first in shape.Solids():
                for second in cutter.Solids():
                    a=first.BoundingBox();b=second.BoundingBox()
                    if any(getattr(a,axis+'max')<getattr(b,axis+'min') or
                           getattr(b,axis+'max')<getattr(a,axis+'min') for axis in ['x','y','z']):
                        continue
                    amount,witness=material_common(first,second,tolerance)
                    if amount>min(first.Volume(tol=1e-9),second.Volume(tol=1e-9))+.001:
                        raise ValueError('Common exceeds complete operand material')
                    volume+=amount
            if attempts:
                repairs.append({'common':label,'attempts':attempts,
                                'completed_tolerance_mm':tolerance,'common_mm3':volume})
                print('Valid independent cutter Common retry: '+label,flush=True)
            return volume
        except (ValueError,RuntimeError) as error:
            attempts.append({'tolerance_mm':tolerance,'error':str(error)})
    raise ValueError('Cannot establish complete cutter Common '+label+': '+str(attempts))

def scoped_tool(cutter,scope,label,repairs):
    require_valid(cutter,'original cutter '+label)
    box=cutter.BoundingBox();limit=scope.BoundingBox()
    if (box.xmin>=limit.xmin and box.xmax<=limit.xmax and
        box.ymin>=limit.ymin and box.ymax<=limit.ymax and
        box.zmin>=limit.zmin and box.zmax<=limit.zmax):
        return cutter
    if len(cutter.Solids())>1:
        members=[scoped_tool(member,scope,label+' member '+str(i),repairs)
                 for i,member in enumerate(cutter.Solids())]
        return cq.Compound.makeCompound([solid for member in members for solid in member.Solids()])
    attempts=[]
    for tolerance in [0,.0001,.00001]:
        result=cutter.copy(mesh=False).intersect(scope.copy(mesh=False),tol=tolerance)
        valid=result.isValid()
        attempts.append({'tolerance_mm':tolerance,'valid':valid})
        if valid:
            if len(attempts)>1:
                repairs.append({'scope':label,'attempts':attempts})
                print('Valid scoped cutter retry: '+label,flush=True)
            return result
    raise ValueError('Cannot make valid scoped cutter '+label+': '+str(attempts))

def cut_valid(shape,cutter,label,repairs):
    require_valid(shape,'input to '+label)
    require_valid(cutter,'scoped cutter '+label)
    if len(cutter.Solids())>1:
        result=shape
        for i,member in enumerate(cutter.Solids()):
            result=cut_valid(result,member,label+' member '+str(i),repairs)
        residue=cutter_common(result,cutter,label,repairs)
        if residue>=.001:raise ValueError('Incomplete compound shell cut '+label+': '+str(residue))
        return result
    # A completed independent native Common with exactly zero material
    # proves this cut is the identity. Keep the complete source unchanged.
    # Many accepted receiver cavities are already open in the source shell.
    if cutter_common(shape,cutter,label+' identity',repairs)==0.:
        return shape
    attempts=[]
    for tolerance in [0,.0001,.00001]:
        try:
            result=shape.copy(mesh=False).cut(cutter.copy(mesh=False),tol=tolerance)
            valid=result.isValid()
            residue=cutter_common(result,cutter,label+' exclusion',repairs) if valid else None
            attempts.append({'tolerance_mm':tolerance,'valid':valid,'cutter_material_residue_mm3':residue})
        except (ValueError,RuntimeError) as error:
            attempts.append({'tolerance_mm':tolerance,'error':str(error)})
            continue
        if valid and residue<.001:
            if len(attempts)>1:
                repairs.append({'cut':label,'attempts':attempts})
                print('Valid native cut retry: '+label,flush=True)
            return result
    raise ValueError('Cannot make complete valid shell cut '+label+': '+str(attempts))

def main():
    source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [Path(__file__),HERE/'build_candidate.py',HERE/'assemble_prints.py',
                             HERE/'pan_slot.py',HERE/'water5_key_pocket.py',HERE/'roof_finish.py',HERE/'received_native.py',
                             STUDY/'evidence_binding.py',STUDY/'audit.py']}
    boolean_repairs=[]
    manifests={};native_inputs={}
    def read_manifest(path):
        raw=path.read_bytes();value=json.loads(raw)
        if path!=HERE/'candidate.json':manifests[str(path.relative_to(ROOT))]=content_sha256(value)
        return value
    def load(record):
        path=ROOT/record['brep'];raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        declared=record.get('sha256')
        if isinstance(declared,dict):declared=declared.get(record['brep'])
        if declared and digest!=declared:raise ValueError('Stale shell native input '+record['brep'])
        native_inputs[record['brep']]={'brep':record['brep'],'sha256':digest}
        return cq.Shape.importBrep(BytesIO(raw))
    def declare_back_cutter(name,cutter,detail):
        require_valid(cutter,'declared rear finish '+name)
        path=OUT/(name+'.brep')
        cutter.exportBrep(str(path))
        record={'brep':str(path.relative_to(ROOT)),
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'print_owner':'enclosure-back-top','scope':detail}
        result.setdefault('clearance_cutters',{})[name]=record
        return cutter
    source=read_manifest(STUDY/'funnel/shells.json')
    result=read_manifest(HERE/'candidate.json')
    routing=read_manifest(STUDY/'routing/candidate.json')
    pump=read_manifest(STUDY/'pump/candidate.json')
    pump_fill=read_manifest(STUDY/'pump/fluid24-candidate.json')
    fluid_path=STUDY/'mounts/fluid-candidate.json'
    fluid=read_manifest(fluid_path) if fluid_path.exists() else {}
    body_path=STUDY/'mounts/body-candidate.json'
    body_mounts=read_manifest(body_path) if body_path.exists() else {}
    extra_manifests=[]
    for path in [STUDY/'mounts/water5-hosts.json',STUDY/'routing/tube-hosts.json']:
        if path.exists():extra_manifests.append(read_manifest(path))
    for n,r in pump['parts'].items():
        if n.startswith(('supply-lid-boss','supply-lid-web')):result['parts'][n]=r
    tools={n:load(r) for n,r in source['interfaces'].items()}
    back=load(source['parts']['enclosure-back-top'])
    front=load(source['parts']['enclosure-front-top'])
    # The valve return crosses the front shell's inner east corner before
    # entering the aft bay. Its exact swept clearance keeps the original
    # three-mm exterior flank and leaves the lower cartridge interfaces intact.
    front_scope=cq.Solid.makeBox(209,200,98.6,cq.Vector(-104.5,95.7,253.4))
    for manifest in [pump,pump_fill,routing]:
        for name,rec in manifest.get('clearance_cutters',{}).items():
            if name.startswith(('tube-','hose-','carb-foam-')):
                front=front.cut(load(rec).intersect(front_scope),tol=.0001)
    # Keep the discharge tube installed during the complete late front slide.
    # Face-bounding prisms conservatively contain each native swept surface;
    # the exact start exterior must also lie entirely in their union. The
    # scoped channel retains the original three-mm outer skin at every pose.
    for name in ['tube-water-5','vk-cradle']:
        record=pump.get('clearance_cutters',{}).get(name,pump['parts'][name])
        occupied=load(record)
        prisms=[]
        surfaces=occupied.Faces() if name=='tube-water-5' else [occupied]
        for surface in surfaces:
            b=surface.BoundingBox();air=0 if name=='tube-water-5' else 1.
            if name=='tube-water-5' and min(b.xlen,b.zlen)<.01:continue
            prisms.append(cq.Solid.makeBox(max(b.xlen+2*air,.001),b.ylen+102.2+2*air,max(b.zlen+2*air,.001),
                cq.Vector(b.xmin-air,b.ymin-air,b.zmin-air)))
        remaining=occupied
        for prism in prisms:
            remaining=remaining.cut(prism,tol=.0001)
            if not remaining.Solids():break
        uncovered=remaining.Volume(tol=1e-9)
        if uncovered>.001:raise ValueError(name+' front slide chase misses native exterior')
        scoped=[]
        for prism in prisms:
            cutter=prism.intersect(front_scope)
            if not cutter.Solids() or cutter.Volume(tol=1e-9)<.001:continue
            front=front.cut(cutter,tol=.0001);scoped.append(cutter)
        chase=cq.Compound.makeCompound(scoped)
        path=OUT/(name+'-front-slide-clearance.brep');chase.exportBrep(str(path))
        result.setdefault('clearance_cutters',{})[name+'-front-slide']={
            'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'print_owner':'enclosure-front-top','travel_mm':102.2,'minimum_exterior_stock_mm':3.,
            'occupied_source':record,'uncovered_native_volume_mm3':uncovered,
            'scope':'Continuous conservative positive-Y face-bounding-prism chase over the complete102.2mm front rail entry; restricted above the unchanged lower cartridge interfaces.'}
    roof=read_manifest(STUDY/'funnel/roof-stock.json')
    record=roof.get('stock',roof.get('part',roof))
    if 'brep' not in record:
        record=next(v for v in roof.values() if isinstance(v,dict) and 'brep' in v)
    back=back.fuse(load(record))
    # Remove obsolete inboard C14 furniture and restore its full rear-wall field.
    oldstock=tools['retained-c14-tunnel-stock']
    back=back.cut(oldstock.intersect(cq.Solid.makeBox(197,246.5,102,cq.Vector(-98.5,218.8,253.4))))
    oldb=oldstock.BoundingBox()
    back=back.fuse(cq.Solid.makeBox(oldb.xlen,6,355-oldb.zmin,cq.Vector(oldb.xmin,465.3,oldb.zmin)))
    skin=cq.Solid.makeBox(197,6,101.6,cq.Vector(-98.5,465.3,253.4))
    # Restore only the obsolete port and pocket voids in the established wall.
    for name in ['original-rear-port-0','original-rear-port-3','original-rear-port-5',
                 'original-rear-chip-pocket-0','original-rear-chip-pocket-1','original-rear-chip-pocket-4',
                 'original-co2-land-relief']:
        back=back.fuse(tools[name].intersect(skin))
    ports=routing['ports']
    water=ports['bulkhead-water']['inboard']['pos']
    carb=ports['bulkhead-carb']['tube-in']['pos']
    co2=ports['co2-inlet']['inboard']['pos']
    shifts={0:(water[0]+78.07,0,water[2]-336.21058083755),
            3:(carb[0]+37.81,0,carb[2]-336.21058083755),
            5:(co2[0]-2.45,0,co2[2]-335.96058083755)}
    for i,delta in shifts.items():
        back=back.cut(tools[f'original-rear-port-{i}'].translate(delta))
    for i,port in [(0,0),(1,3),(4,5)]:
        back=back.cut(tools[f'original-rear-chip-pocket-{i}'].translate(shifts[port]))
    back=back.cut(tools['original-co2-land-relief'].translate(shifts[5]))
    # Translate the complete accepted C14 bore, flange pocket and blind pilots.
    moved=oldstock.translate((-138,0,0))
    back=back.fuse(moved)
    c14tools=[n for n in tools if ('c14' in n and ('bore' in n or 'insert' in n))]
    if not c14tools:raise ValueError('Full accepted C14 mating tools required')
    for name in c14tools:back=back.cut(tools[name].translate((-138,0,0)))
    back=back.cut(tools['original-c14-ceiling-pocket'].translate((-138,0,0)))
    # Move the full keystone pocket, receiving stock and both snap catches.
    keystone_delta=tuple(routing.get('interface_moves',{}).get('keystone',{}).get('translation',(-25.865,0,-.04729046878)))
    back=back.cut(tools['original-keystone-feature'])
    back=back.fuse(tools['original-keystone-cutter'].intersect(skin))
    back=back.fuse(tools['original-keystone-feature'].translate(keystone_delta))
    back=back.cut(tools['original-keystone-cutter'].translate(keystone_delta))
    back=back.fuse(tools['original-keystone-catches'].translate(keystone_delta))
    # Move the complete qualified nameplate receiver by its exact rigid
    # transform. Its slots and release opening govern the local exterior face.
    nameplate=routing.get('interface_moves',{}).get('nameplate')
    if nameplate:
        back=back.cut(load(nameplate['original_receiver_removal']))
        region=load(nameplate['original_receiver_removal']).BoundingBox()
        back=back.fuse(cq.Solid.makeBox(region.xlen,6,region.zlen,
                      cq.Vector(region.xmin,465.3,region.zmin)))
        receiver=load(nameplate['new_receiver']);rb=receiver.BoundingBox()
        if nameplate.get('new_backing'):
            backing=load(nameplate['new_backing'])
        elif nameplate.get('face_axis',[1,0,0])[0]<0:
            backing=cq.Solid.makeBox(-97.49-rb.xmin,rb.ylen,rb.zlen,cq.Vector(rb.xmin,rb.ymin,rb.zmin))
        else:
            backing=cq.Solid.makeBox(rb.xmax-98.49,rb.ylen,rb.zlen,cq.Vector(98.49,rb.ymin,rb.zmin))
        back=back.fuse(backing).fuse(receiver).cut(load(nameplate['new_cutter']))
    # Local service channels are rooted native stock, restricted to this upper
    # bay. All associated fittings retain their complete clearance envelopes.
    for rec in routing.get('shell_stock',{}).values():back=back.fuse(load(rec))
    # The water union's westmost corner has a local pocket in the nine-mm
    # flank, retaining at least three-mm exterior stock; the whole solid is
    # cut so its round receiver remains the controlling section.
    body=load(routing['parts']['bulkhead-water'])
    wb=body.BoundingBox()
    if wb.xmin-1 < -98.5:
        assert wb.xmin-1 >= -104.5,'Water receiver leaves less than3mm west flank'
        back=back.cut(cq.Solid.makeBox(-98.5-(wb.xmin-1),wb.ylen+2,wb.zlen+2,
                       cq.Vector(wb.xmin-1,wb.ymin-1,wb.zmin-1)))
    # The relocated C14 keeps its 3mm blind-end cap at the rear wall.
    back=back.cut(tools['original-c14-land-relief'].translate((-138,0,0)))
    back=back.fuse(moved)
    for name in c14tools:back=back.cut(tools[name].translate((-138,0,0)))
    # Finish every current rear receiver after all rear-wall restoration and
    # C14 stock additions. The same explicit tools are applied again after
    # printed hosts are joined, so those hosts cannot refill a receiver.
    receiver_tools={}
    receiver_shifts={**shifts,4:(-138,0,0)}
    for i in range(7):
        # Rear port4 is the complete accepted C14 aperture.
        receiver_tools['rear-port-finish-'+str(i)]=tools[f'original-rear-port-{i}'].translate(receiver_shifts.get(i,(0,0,0)))
    pocket_shifts={0:shifts[0],1:shifts[3],4:shifts[5]}
    for i in range(5):
        receiver_tools['rear-chip-finish-'+str(i)]=tools[f'original-rear-chip-pocket-{i}'].translate(pocket_shifts.get(i,(0,0,0)))
    receiver_tools['rear-co2-land-finish']=tools['original-co2-land-relief'].translate(shifts[5])
    for name in c14tools+['original-c14-ceiling-pocket','original-c14-land-relief']:
        receiver_tools['rear-'+name+'-finish']=tools[name].translate((-138,0,0))
    # Continue the accepted water receiver through the inboard part of the
    # translated C14 tunnel. Its section and flange pocket stay unchanged.
    water_shift=shifts[0]
    receiver_tools['rear-water-inboard-finish']=tools['original-rear-port-0'].translate((water_shift[0],-3.25,water_shift[2]))
    for name,cutter in receiver_tools.items():
        cutter=declare_back_cutter(name,cutter,
            'Current accepted receiver profile, recut after every rear-wall and host stock addition.')
        back=cut_valid(back,cutter,name,boolean_repairs)
    # New pockets are local; the surrounding established ceiling stays 12mm.
    pcbb=load(result['parts']['pcba']).BoundingBox()
    # Separate the west pocket wall from the radius-four mounting posts.
    # A tangent line between them creates a nonmanifold print surface.
    pcbpocket=cq.Solid.makeBox(pcbb.xlen+2.25,pcbb.ylen+2,9.0,cq.Vector(pcbb.xmin-1.25,pcbb.ymin-1,343))
    back=back.cut(pcbpocket)
    # The ring fan sits on the explicit post's bearing face. Its reference
    # screw continues into the blind pilot; the surrounding roof must not
    # refill that pilot or intersect the washer above the general underside.
    ground=load(result['parts']['ground-stack']);gb=ground.BoundingBox()
    back=back.cut(cq.Solid.makeBox(gb.xlen+2,gb.ylen+2,min(gb.zmax+1,352)-343,
                  cq.Vector(gb.xmin-1,gb.ymin-1,343)))
    for folder in ['routing','pump']:
        m=read_manifest(STUDY/folder/'candidate.json')
        for name,rec in m['parts'].items():
            if rec.get('role') in ['structure','funnel','walls','context']:continue
            if name.startswith(('tube-','hose-','carb-foam-')):continue
            body=load(rec)
            b=body.BoundingBox()
            if b.zmax>342.0 and b.ymax>325.7:
                pocket=cq.Solid.makeBox(b.xlen+2,b.ylen+2,min(b.zmax+1,352)-343,
                         cq.Vector(b.xmin-1,b.ymin-1,343))
                if pocket.BoundingBox().zlen>0:back=back.cut(pocket)
    # The supplied swept clearance cutter follows the actual R15.9 braid,
    # including the 0.2125mm recess into the west flank. Limit the cut to the
    # reorganized bay skin so fixed forward receivers and core mouths stay exact.
    outer=routing.get('bay_outer_extents_mm',[-107.5,107.5])
    aft=read_manifest(STUDY/'funnel/candidate.json')['aft_extension_mm']+235.69150792328
    clearance_scope=cq.Solid.makeBox(outer[1]-outer[0],465.3-aft,352-253.4,cq.Vector(outer[0],aft,253.4))
    factory_scope=cq.Solid.makeBox(outer[1]-outer[0],465.3-200,352-253.4,cq.Vector(outer[0],200,253.4))
    require_valid(back,'hardware pockets')
    for manifest in [pump,routing,fluid,body_mounts,*extra_manifests]:
        for name,rec in manifest.get('clearance_cutters',{}).items():
            if rec.get('print_owner','enclosure-back-top')=='enclosure-back-top':
                scope=factory_scope if rec.get('factory_upper_bay_channel')else clearance_scope
                cutter=scoped_tool(load(rec),scope,name,boolean_repairs)
                back=cut_valid(back,cutter,'fluid clearance '+name,boolean_repairs)
                require_valid(back,'clearance '+name)
    wiring_path=STUDY/'wiring/candidate.json'
    wire_finishes={}
    if wiring_path.exists():
        wiring=read_manifest(wiring_path)
        mounts_for_finish=read_manifest(STUDY/'mounts/candidate.json')
        host_records={n:r for n,r in result['parts'].items()
                      if n.startswith(('controller-roof-boss','ground-roof-boss'))}
        for packet in [mounts_for_finish,fluid,body_mounts,*extra_manifests]:
            names=set(packet.get('shell_fuse_part_names',[]))
            names.update(n for n,owner in packet.get('root_owner_overrides',{}).items()
                         if owner=='enclosure-back-top')
            for host in names:
                if host in packet.get('parts',{}):host_records[host]=packet['parts'][host]
            for host,coupon in packet.get('joined_root_coupons',{}).items():
                if coupon.get('print_owner',coupon.get('owner'))=='enclosure-back-top':
                    host_records[host]=coupon
        protected_shapes={n:load(r) for n,r in host_records.items()}
        for name,rec in wiring.get('clearance_cutters',{}).items():
            if rec.get('print_owner','enclosure-back-top')=='enclosure-back-top':
                cutter=scoped_tool(load(rec),clearance_scope,name,boolean_repairs)
                for index,member in enumerate(cutter.Solids()):
                    label='wiring clearance '+name+' member '+str(index)
                    try:
                        back=cut_valid(back,member,label,boolean_repairs)
                    except (ValueError,RuntimeError) as ordinary_error:
                        # Admit a simple additional pocket only through its
                        # complete independent material and protected-stock
                        # certificate. The unchanged original member must
                        # then have a valid empty Common with the result.
                        original_stock=back
                        back,finish,certificate=make_roof_finish(original_stock,member,protected_shapes)
                        key='wire-roof-finish-'+name+'-'+str(index)
                        declare_back_cutter(key,finish,certificate['scope'])
                        source_path=OUT/(key+'-source-stock.brep')
                        original_stock.exportBrep(str(source_path))
                        source_record={'brep':str(source_path.relative_to(ROOT)),
                            'sha256':hashlib.sha256(source_path.read_bytes()).hexdigest()}
                        native_inputs[key+' source stock']=source_record
                        wire_finishes[key]={**certificate,'source_stock':source_record,
                            'held_tool_record':rec,'held_member_index':index,
                            'ordinary_cut_guard_error':str(ordinary_error)}
                        print('Certified additional roof pocket: '+name+' member '+str(index),flush=True)
                residue=cutter_common(back,cutter,'complete wiring channel '+name,boolean_repairs)
                if residue>=.001:raise ValueError('Incomplete complete wire channel '+name)
    # The flush pull face occupies the west wall as well as the pan basin.
    # Its native rounded silhouette defines the full running aperture and
    # remains above the unchanged cold-core cap. It is not aft-scope cropped.
    pan_slot,pan_certificate=make_slot(load(routing['parts']['asse-drip-pan']))
    pan_slot=declare_back_cutter('pan-full-profile-aperture',pan_slot,
        'Full rounded pan pull-face and basin projection through the west9mm flank;0.25mm sides/top and0.5mm below.')
    back=cut_valid(back,pan_slot,'full rounded pan aperture',boolean_repairs)
    water5=next(manifest for manifest in extra_manifests if 'split_seat_properties' in manifest)
    key_pocket,key_certificate=make_pocket(
        load(water5['parts']['water5-east-drop-key']),
        load(water5['parts']['water5-east-drop-seat']),water5['split_seat_properties'])
    key_pocket=declare_back_cutter('water5-key-running-pocket',key_pocket,
        'Exact curved removable-key envelope with0.25mm radial/axial air and12mm entry; fixed bearing seat and blind pilots preserved.')
    back=cut_valid(back,key_pocket,'Water5 removable key entry',boolean_repairs)
    for manifest in [result,fluid,body_mounts,*extra_manifests]:
        for rec in manifest.get('pilot_cutters',{}).values():
            if rec.get('print_owner')=='enclosure-back-top':back=back.cut(load(rec))
    # Explicit mounting posts are shown independently in the viewer but fused
    # here to prove their stock is connected to the print's actual shell.
    union=back
    for name,rec in result['parts'].items():
        if name.startswith(('controller-roof-boss','ground-roof-boss')):
            union=joined(union,load(rec),'prepared rear shell',name)
    mount_path=STUDY/'mounts/candidate.json'
    if mount_path.exists():
        mm=read_manifest(mount_path)
        for name in mm.get('shell_fuse_part_names',[]):union=joined(union,load(mm['parts'][name]),'prepared rear shell',name)
    for manifest in [result,mm if mount_path.exists() else {},pump,routing,fluid,body_mounts,*extra_manifests]:
        for rec in manifest.get('pilot_cutters',{}).values():
            if rec.get('print_owner')=='enclosure-back-top':union=union.cut(load(rec))
    if not union.isValid():union=union.clean()
    rows={}
    for name,s in [('enclosure-back-top',back),('enclosure-front-top',front)]:
        f=OUT/(name+'.brep');s.exportBrep(str(f));b=s.BoundingBox()
        rows[name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
                    'role':'walls','detail':'Full native shell: 9mm flanks, 6mm rear wall, 12mm ceiling outside local hardware pockets; matching enlarged sliding funnel frame, local service-channel stock and exact relocated fitting/nameplate receivers.',
                    'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]}
    joined_path=OUT/'rear-shell-with-mounts.brep';union.exportBrep(str(joined_path))
    lid=load(pump['parts']['cold-core/foam-cap-lid-top'])
    for name,rec in result['parts'].items():
        if name.startswith(('supply-lid-boss','supply-lid-web')):lid=joined(lid,load(rec),'prepared lid',name)
    lidfile=OUT/'lid-with-supply-mounts.brep';lid.exportBrep(str(lidfile))
    result['parts'].update(rows)
    result['replacement_names']=sorted(set(result['replacement_names'])|set(rows))
    result['shell_checks']={'back_valid':back.isValid(),'front_valid':front.isValid(),
                  'back_solids':len(back.Solids()),'front_solids':len(front.Solids()),
                  'joined_rear_valid':union.isValid(),'joined_rear_solids':len(union.Solids()),
                  'joined_rear_brep':str(joined_path.relative_to(ROOT)),'moved_c14_tools':c14tools}
    result['shell_checks']['native_cut_retries']=boolean_repairs
    result['shell_checks']['pan_aperture']=pan_certificate
    result['shell_checks']['water5_key_pocket']=key_certificate
    result['shell_checks']['wire_roof_finishes']=wire_finishes
    result['shell_checks'].update({'joined_lid_valid':lid.isValid(),'joined_lid_solids':len(lid.Solids()),
                  'joined_lid_brep':str(lidfile.relative_to(ROOT))})
    result['source_inputs']=source_inputs
    result['native_inputs']=native_inputs
    result['manifest_content_sha256']=manifests
    result['source_drift']=[p for p,h in source_inputs.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    result['source_drift'] += [n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    result['manifest_drift']=[p for p,h in manifests.items()if content_sha256(json.loads((ROOT/p).read_bytes()))!=h]
    result['shell_build_pass']=back.isValid() and front.isValid() and not result['source_drift'] and not result['manifest_drift']
    (HERE/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['shell_checks'],indent=2),flush=True)
    if not result['shell_build_pass']:raise ValueError('Shell producer geometry or read-time binding failed')

if __name__=='__main__':main()
